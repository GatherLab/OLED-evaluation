# coding: utf-8
# General Modules
# import os, shutil
# import re, string
import os
import re
import math
import numpy as np
import pandas as pd
import datetime as dt
import copy


import scipy.constants as sc  # natural constants


def read_calibration_files(
    photopic_response_path,
    pd_responsivity_path,
    cie_reference_path,
    spectrometer_calibration_path,
):
    """
    Function that wraps reading in the calibration files and returns them as dataframes
    """
    photopic_response = pd.read_csv(
        # os.path.join(
        #     os.path.dirname(os.path.dirname(__file__)),
        #     "library",
        #     "Photopic_response.txt",
        # ),
        photopic_response_path,
        sep="\t",
        names=["wavelength", "photopic_response"],
    )

    pd_responsivity = pd.read_csv(
        # os.path.join(
        #     os.path.dirname(os.path.dirname(__file__)), "library", "Responsivity_PD.txt"
        # ),
        pd_responsivity_path,
        sep="\t",
        names=["wavelength", "pd_responsivity"],
    )

    cie_reference = pd.read_csv(
        # os.path.join(
        #     os.path.dirname(os.path.dirname(__file__)),
        #     "library",
        #     "NormCurves_400-800.txt",
        # ),
        cie_reference_path,
        sep="\t",
        names=["wavelength", "none", "x_cie", "y_cie", "z_cie"],
    )

    spectrometer_calibration = pd.read_csv(
        # os.path.join(
        #     os.path.dirname(os.path.dirname(__file__)), "library", "CalibrationData.txt"
        # ),
        spectrometer_calibration_path,
        sep="\t",
        names=["wavelength", "sensitivity"],
    )

    # Only take the part of the calibration files that is in the range of the
    # spectrometer calibration file. Otherwise all future interpolations will
    # interpolate on data that does not exist. I think it doesn't make a
    # difference because this kind of data is set to zero anyways by the
    # interpolate function but it is more logic to get rid of the unwanted data
    # here already
    photopic_response_range = photopic_response.loc[
        np.logical_and(
            photopic_response["wavelength"]
            <= spectrometer_calibration["wavelength"].max(),
            photopic_response["wavelength"]
            >= spectrometer_calibration["wavelength"].min(),
        )
    ]
    pd_responsivity_range = pd_responsivity.loc[
        np.logical_and(
            pd_responsivity["wavelength"]
            <= spectrometer_calibration["wavelength"].max(),
            pd_responsivity["wavelength"]
            >= spectrometer_calibration["wavelength"].min(),
        )
    ]
    cie_reference_range = cie_reference.loc[
        np.logical_and(
            cie_reference["wavelength"] <= spectrometer_calibration["wavelength"].max(),
            cie_reference["wavelength"] >= spectrometer_calibration["wavelength"].min(),
        )
    ]

    return (
        photopic_response_range,
        pd_responsivity_range,
        cie_reference_range,
        spectrometer_calibration,
    )


def interpolate_spectrum(spectrum, photopic_response):
    """
    Function that does the interpolation of a given pandas dataframe on the
    photopic response calibration wavelengths. This is later needed for the
    integrals.
    """

    def interpolate(column):
        """
        Helper function to do the numpy interpolate on an entire dataframe
        """
        return np.interp(
            photopic_response["wavelength"].to_numpy(),
            spectrum["wavelength"].to_numpy(),
            column,
        )

    # Now interpolate the entire dataframe on the wavelengths that are present in
    # the photopic_response file
    spectrum_interpolated_df = spectrum.apply(interpolate)

    return spectrum_interpolated_df


def calibrate_spectrum(spectrum, calibration):
    """
    Function that takes a pandas dataframe spectrum and corrects it according to
    the calibration files
    """
    # interpolate spectrometer calibration factor onto correct axis (so that it
    # can be multiplied with the spectrum itself)
    interpolated_calibration = np.interp(
        spectrum["wavelength"].to_numpy(dtype=np.float),
        calibration["wavelength"].to_numpy(dtype=np.float),
        calibration["sensitivity"].to_numpy(dtype=np.float),
    )

    # Now subtract background and multiply with calibration
    spectrum_corrected = (
        spectrum.loc[:, ~np.isin(spectrum.columns, ["background", "wavelength"])]
        .subtract(spectrum["background"], axis=0)
        .multiply(interpolated_calibration, axis=0)
    )

    spectrum_corrected["wavelength"] = spectrum["wavelength"]

    return spectrum_corrected


# Now interpolate and correct the spectrum
# spectrum_corrected = interpolate_and_correct_spectrum(spectrum)


#######################################################################################
######################## Only Angle Resolved Spectrum Related #########################
#######################################################################################


def calculate_ri(column):
    """
    Function that calculates radiant intensity
    """
    return float(sc.h * sc.c / 1e-9 * np.sum(column))


def calculate_li(column, photopic_response):
    """
    Function that calculates the luminous intensity
    Emission in terms of photometric response, so taking into account the
    spectral shifts and sensitivity of the eye/photopic response
    """
    return float(
        sc.physical_constants["luminous efficacy"][0]
        * sc.h
        * sc.c
        / 1e-9
        * np.sum(column * photopic_response["photopic_response"].to_numpy())
    )


# ri = spectrum_corrected.drop(["0_deg", "wavelength"], axis=1).apply(
#     calculate_ri, axis=0
# )
# li = spectrum_corrected.drop(["0_deg", "wavelength"], axis=1).apply(
#     calculate_li, axis=0
# )


def calculate_e_correction(df):
    """
    Closure to calculate the e correction factor from a dataframe
    """
    # Get angles from column names first
    try:
        angles = df.drop(["0_deg", "wavelength"], axis=1).columns.to_numpy(float)
    except:
        angles = df.drop(["wavelength"], axis=1).columns.to_numpy(float)

    def calculate_efactor(column):
        """
        Function to calculate efactor, perp_intensity is just the intensity at 0°
        """
        return sum(column * df["wavelength"]) / sum(df["0.0"] * df["wavelength"])

    try:
        e_factor = df.drop(["0_deg", "wavelength"], axis=1).apply(calculate_efactor)
    except:
        e_factor = df.drop(["wavelength"], axis=1).apply(calculate_efactor)

    # It is now important to only integrate from 0 to 90° and not the entire spectrum
    # It is probably smarter to pull this at some point up but this works.
    relevant_e_factors = e_factor.loc[
        np.logical_and(
            np.array(e_factor.index).astype(float) >= 0,
            np.array(e_factor.index).astype(float) <= 90,
        )
    ]

    relevant_angles = np.array(
        e_factor.loc[
            np.logical_and(
                np.array(e_factor.index).astype(float) >= 0,
                np.array(e_factor.index).astype(float) <= 90,
            )
        ].index
    ).astype(float)

    return np.sum(
        relevant_e_factors
        * np.sin(np.deg2rad(relevant_angles))
        * np.deg2rad(np.diff(relevant_angles)[0])
    )


def calculate_v_correction(df, photopic_response):
    """
    Closure to calculate the e correction factor from a dataframe
    """

    # Get angles from column names first
    try:
        angles = df.drop(["0_deg", "wavelength"], axis=1).columns.to_numpy(float)
    except:
        angles = df.drop(["wavelength"], axis=1).columns.to_numpy(float)

    def calculate_vfactor(column):
        """
        Function to calculate the vfactor
        """
        return sum(column * photopic_response["photopic_response"].to_numpy()) / sum(
            df["0.0"] * photopic_response["photopic_response"].to_numpy()
        )

    try:
        v_factor = df.drop(["0_deg", "wavelength"], axis=1).apply(calculate_vfactor)
    except:
        v_factor = df.drop(["wavelength"], axis=1).apply(calculate_vfactor)

    # It is now important to only integrate from 0 to 90° and not the entire spectrum
    # It is probably smarter to pull this at some point up but this works.
    relevant_v_factor = v_factor.loc[
        np.logical_and(
            np.array(v_factor.index).astype(float) >= 0,
            np.array(v_factor.index).astype(float) <= 90,
        )
    ]

    relevant_angles = np.array(
        v_factor.loc[
            np.logical_and(
                np.array(v_factor.index).astype(float) >= 0,
                np.array(v_factor.index).astype(float) <= 90,
            )
        ].index
    ).astype(float)

    return np.sum(
        relevant_v_factor
        * np.sin(np.deg2rad(relevant_angles))
        * np.deg2rad(np.diff(relevant_angles)[0])
    )


class JVLData:
    """
    At this point I think it is easier to have a class that allows for easy
    calculation of the characteristics
    """

    def __init__(
        self,
        jvl_data,
        perpendicular_spectrum,
        photopic_response,
        pd_responsivity,
        cie_reference,
        angle_resolved,
        pixel_area,
        pd_resistance,
        pd_radius,
        pd_distance,
        pd_cutoff,
        correction_factor=[],
    ):
        """
        All data must be provided in SI units!
        The calculated quantities are, however, directly in their final
        (usual) units.
        - voltage: volts
        - current: mA
        - current density: mA/cm2
        - absolute current density: mA/cm2
        - luminance: cd/m2
        - eqe: %
        - luminous_efficacy: lm/W
        - current_efficiency: cd/A
        - power density: mW/mm2
        """
        self.pd_resistance = pd_resistance
        self.pixel_area = pixel_area
        # Taking into account finite size of PD
        self.sqsinalpha = pd_radius ** 2 / (pd_distance ** 2 + pd_radius ** 2)

        self.voltage = np.array(jvl_data["voltage"])
        self.pd_voltage = np.array(jvl_data["pd_voltage"])

        # All pd voltages that are below cutoff are now cut off and set to zero.
        # This is done using a helper array to preserve the original data
        self.pd_voltage_cutoff = copy.copy(self.pd_voltage)
        self.pd_voltage_cutoff[self.pd_voltage_cutoff <= pd_cutoff] = 0

        self.current = np.array(jvl_data["current"]) / 1000
        # Current density directly in mA/cm^2
        self.current_density = np.array(jvl_data["current"]) / (pixel_area * 1e4)
        self.absolute_current_density = np.array(abs(self.current_density))

        self.cie_coordinates = self.calculate_cie_coordinates(
            perpendicular_spectrum,
            cie_reference,
        )
        self.calculate_integrals(
            perpendicular_spectrum,
            photopic_response["photopic_response"],
            pd_responsivity["pd_responsivity"],
        )

        if angle_resolved == True:
            # Non lambertian case
            e_coeff = self.calculate_non_lambertian_e_coeff()
            v_coeff = self.calculate_non_lambertian_v_coeff()

            self.eqe = self.calculate_non_lambertian_eqe(e_coeff, correction_factor[0])
            self.luminance = self.calculate_non_lambertian_luminance(v_coeff)
            self.luminous_efficacy = self.calculate_non_lambertian_luminous_efficacy(
                v_coeff, correction_factor[1]
            )
            self.power_density = self.calculate_non_lambertian_power_density(
                e_coeff, correction_factor[0]
            )
        else:
            # Lambertian case
            e_coeff = self.calculate_lambertian_e_coeff()
            v_coeff = self.calculate_lambertian_v_coeff()

            self.eqe = self.calculate_lambertian_eqe(e_coeff)
            self.luminance = self.calculate_lambertian_luminance(v_coeff)
            self.luminous_efficacy = self.calculate_lambertian_luminous_efficacy(
                v_coeff
            )
            self.power_density = self.calculate_lambertian_power_density(e_coeff)

        self.current_efficiency = self.calculate_current_efficiency()

    def calculate_integrals(
        self, perpendicular_spectrum, photopic_response, pd_responsivity
    ):
        """
        Function that calculates the important integrals
        """
        self.integral_1 = np.sum(
            perpendicular_spectrum["intensity"] * perpendicular_spectrum["wavelength"]
        )
        # Integral2 = np.sum(perp_intensity)
        self.integral_2 = np.sum(perpendicular_spectrum["intensity"])
        # Integral3 = np.sum(perp_intensity * photopic_response["photopic_response"].to_numpy())
        self.integral_3 = np.sum(
            perpendicular_spectrum["intensity"].to_numpy()
            * photopic_response.to_numpy()
        )
        # Integral4 = np.sum(perp_intensity * pd_responsivity["pd_responsivity"].to_numpy())
        self.integral_4 = np.sum(
            perpendicular_spectrum["intensity"] * pd_responsivity.to_numpy()
        )

    # Calculating CIE coordinates
    def calculate_cie_coordinates(self, perpendicular_spectrum, cie_reference):
        """
        Calculates wavelength of maximum spectral intensity and the CIE color coordinates
        """
        # max_intensity_wavelength = perpendicular_spectrum.loc[
        #     perpendicular_spectrum.intensity == perpendicular_spectrum.intensity.max(),
        #     "wavelength",
        # ].to_list()[0]

        X = sum(perpendicular_spectrum.intensity * cie_reference.x_cie)
        Y = sum(perpendicular_spectrum.intensity * cie_reference.y_cie)
        Z = sum(perpendicular_spectrum.intensity * cie_reference.z_cie)

        CIE = np.array([X / (X + Y + Z), Y / (X + Y + Z)])

        return CIE

    def calculate_non_lambertian_e_coeff(self):
        """
        Calculate e_coeff
        """
        return self.pd_voltage_cutoff / self.pd_resistance / self.sqsinalpha * 2

    def calculate_non_lambertian_v_coeff(self):
        """
        Calculate v_coeff
        """
        return (
            sc.physical_constants["luminous efficacy"][0]
            * self.pd_voltage_cutoff
            / self.pd_resistance
            / self.sqsinalpha
            * 2
        )

    def calculate_non_lambertian_eqe(self, e_coeff, e_correction_factor):
        """
        Function to calculate the eqe
        """

        # e_coeff = self.calculate_non_lambertian_e_coeff(jvl_data)

        return np.divide(
            100 * sc.e * e_coeff * self.integral_1 * e_correction_factor,
            1e9 * sc.h * sc.c * self.current * self.integral_4,
            out=np.zeros_like(
                100 * sc.e * e_coeff * self.integral_1 * e_correction_factor
            ),
            where=1e9 * sc.h * sc.c * self.current * self.integral_4 != 0,
        )
        # eqe = 100 * (
        #     sc.e
        #     / 1e9
        #     / sc.h
        #     / sc.c
        #     / self.current
        #     * e_coeff
        #     * self.integral_1
        #     / self.integral_4
        #     * e_correction_factor
        # )

        # return eqe

    def calculate_non_lambertian_luminance(self, v_coeff):
        """
        Calculate luminance
        """
        # v_coeff = self.calculate_non_lambertian_v_coeff(jvl_data)
        return (
            1
            / np.pi
            / self.pixel_area
            * v_coeff
            / 2
            * self.integral_3
            / self.integral_4
        )

    def calculate_non_lambertian_luminous_efficacy(self, v_coeff, v_correction_factor):
        """
        Calculate luminous efficiency
        """

        # v_coeff = self.calculate_non_lambertian_v_coeff(jvl_data)
        return np.divide(
            v_coeff * self.integral_3 * v_correction_factor,
            self.voltage * self.current * self.integral_4,
            out=np.zeros_like(v_coeff * self.integral_3 * v_correction_factor),
            where=self.voltage * self.current * self.integral_4 != 0,
        )

    def calculate_current_efficiency(self):
        """
        Calculate current efficiency
        """
        # In case of the current being zero, set a helper current to nan so
        # that the result of the division becomes nan instead of infinite

        return np.divide(
            self.pixel_area * self.luminance,
            self.current,
            out=np.zeros_like(self.pixel_area * self.luminance),
            where=self.current != 0,
        )
        # b = self.pixel_area / self.current * self.luminance

    def calculate_non_lambertian_power_density(self, e_coeff, e_correction_factor):
        """
        Calculate power density
        """
        # e_coeff = self.calculate_non_lambertian_e_coeff(jvl_data)
        return (
            1
            / (self.pixel_area * 1e6)
            * e_coeff
            * self.integral_2
            / self.integral_4
            * e_correction_factor
            * 1e3
        )

    def calculate_lambertian_e_coeff(self):
        """
        Calculate e_coeff
        """
        return self.pd_voltage_cutoff / self.pd_resistance / self.sqsinalpha

    def calculate_lambertian_v_coeff(self):
        """
        Calculate v_coeff
        """
        return (
            sc.physical_constants["luminous efficacy"][0]
            * self.pd_voltage_cutoff
            / self.pd_resistance
            / self.sqsinalpha
        )

    def calculate_lambertian_eqe(self, e_coeff):
        """
        Function to calculate the eqe
        """

        # e_coeff = calculate_lambertian_eqe(jvl_data)

        return np.divide(
            100 * sc.e * e_coeff * self.integral_1,
            1e9 * sc.h * sc.c * self.current * self.integral_4,
            out=np.zeros_like(100 * sc.e * e_coeff * self.integral_1),
            where=1e9 * sc.h * sc.c * self.current * self.integral_4 != 0,
        )
        # return 100 * (
        #     sc.e
        #     / 1e9
        #     / sc.h
        #     / sc.c
        #     / self.current
        #     * e_coeff
        #     * self.integral_1
        #     / self.integral_4
        # )

    def calculate_lambertian_luminance(self, v_coeff):
        """
        Calculate luminance
        """
        # v_coeff = calculate_lambertian_v_coeff(jvl_data)
        return np.divide(
            1 * v_coeff * self.integral_3,
            np.pi * self.pixel_area * self.integral_4,
            out=np.zeros_like(1 * v_coeff * self.integral_3),
            where=np.pi * self.pixel_area * self.integral_4 != 0,
        )
        # return 1 / np.pi / self.pixel_area * v_coeff * self.integral_3 / self.integral_4

    def calculate_lambertian_luminous_efficacy(self, v_coeff):
        """
        Calculate luminous efficiency
        """

        # v_coeff = calculate_lambertian_v_coeff(self, jvl_data)
        return np.divide(
            1 * v_coeff * self.integral_3,
            self.voltage * self.current * self.integral_4,
            out=np.zeros_like(1 * v_coeff * self.integral_3),
            where=self.voltage * self.current * self.integral_4 != 0,
        )
        # return (
        #     1 / self.voltage / self.current * v_coeff * self.integral_3 / self.integral_4
        # )

    def calculate_lambertian_power_density(self, e_coeff):
        """
        Calculate power density
        """
        # e_coeff = calculate_lambertian_e_coeff(jvl_data)
        return (
            1
            / (self.pixel_area * 1e6)
            * e_coeff
            * self.integral_2
            / self.integral_4
            * 1e3
        )

    def to_series(self):
        """
        return the variables of the class as dataframe
        """
        df = pd.Series()
        df["voltage"] = self.voltage
        df["pd_voltage"] = self.pd_voltage
        df["current"] = self.current
        df["current_density"] = self.current_density
        df["absolute_current_density"] = self.absolute_current_density
        df["cie"] = self.cie_coordinates
        df["luminance"] = self.luminance
        df["eqe"] = self.eqe
        df["luminous_efficacy"] = self.luminous_efficacy
        df["current_efficiency"] = self.current_efficiency
        df["power_density"] = self.power_density

        return df
