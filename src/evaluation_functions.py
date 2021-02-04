# coding: utf-8

import os
import re
import math
import numpy as np
import pandas as pd

# import gather_core as gc  # our own framework
import scipy.constants as sc  # natural constants

"""
Define Functions for calculations
"""


def calculate_cie_coordinates(df_corrected_spectrum, df_norm_curves):
    """
    Calculates wavelength of maximum spectral intensity and the CIE color coordinates
    """
    for i, j in enumerate(df_corrected_spectrum.interpolated_intensity):
        if j == max(df_corrected_spectrum.interpolated_intensity):
            max_intensity_wavelength = df_corrected_spectrum.wavelength[i]

    X = sum(df_corrected_spectrum.corrected_intensity * df_norm_curves.xcie)
    Y = sum(df_corrected_spectrum.corrected_intensity * df_norm_curves.ycie)
    Z = sum(df_corrected_spectrum.corrected_intensity * df_norm_curves.zcie)

    CIE = np.array([X / (X + Y + Z), Y / (X + Y + Z)])
    # CIE[0] = X / (X + Y + Z)
    # CIE[1] = Y / (X + Y + Z)
    return (
        max_intensity_wavelength,
        ("(" + ", ".join(["%.3f"] * 2) + ")") % tuple(CIE),
    )


def calculate_eqe(
    df_corrected_spectrum, df_jvl_data, df_basic_data, measurement_parameters
):
    """
    Calculate external quantum efficiency
    """
    # calculate average quantum efficiency of the detector
    detector_quantum_efficiency = (
        sc.h
        * sc.c
        / sc.e
        * np.sum(
            df_corrected_spectrum.corrected_intensity
            * df_basic_data.photodiode_sensitivity
            / df_basic_data.wavelength
        )
        / np.sum(df_corrected_spectrum.corrected_intensity)
        * 1e9
    )
    eqe = np.zeros(len(df_jvl_data.pd_voltage))
    for v in range(len(df_jvl_data.pd_voltage)):
        # eqe is only calculated if the photodiode detects a reasonable response
        if df_jvl_data.pd_voltage[v] > 0.00005:
            eqe[v] = (
                100
                * df_jvl_data.pd_voltage[v]
                / measurement_parameters["pd_resistance"]
                / measurement_parameters["sq_sin_alpha"]
                / df_jvl_data.current[v]
                / detector_quantum_efficiency
            )  # calculate eqe in %

    return eqe


def calculate_luminance(
    df_corrected_spectrum, df_jvl_data, df_basic_data, measurement_parameters
):
    """
    Calculate luminance
    """
    # A/lm; photopic response
    photopic_response = (
        np.sum(
            df_corrected_spectrum.corrected_intensity
            * df_basic_data.photodiode_sensitivity
            / df_basic_data.wavelength
        )
        / np.sum(
            df_basic_data.v_lambda
            * df_corrected_spectrum.corrected_intensity
            / df_basic_data.wavelength
        )
        / measurement_parameters["pd_peak_response"]
    )
    luminance = np.zeros(len(df_jvl_data.pd_voltage))
    for v in range(len(df_jvl_data.pd_voltage)):
        # luminance is only calculated if the photodiode detects a reasonable response
        if df_jvl_data.pd_voltage[v] > measurement_parameters["threshold_pd_voltage"]:
            luminance[v] = (
                1
                / math.pi
                / measurement_parameters["sq_sin_alpha"]
                / photopic_response
                * df_jvl_data.pd_voltage[v]
                / measurement_parameters["pd_resistance"]
                / (measurement_parameters["pixel_area"] * 1e-6)
            )  # cd/m2; luminace

    return photopic_response, luminance


def calculate_luminous_efficacy(df_jvl_data, photopic_response, measurement_parameters):
    """
    Calculate luminous efficacy
    """
    luminous_efficiency = np.zeros(len(df_jvl_data.pd_voltage))
    for v in range(len(df_jvl_data.pd_voltage)):
        # luminous_efficiency is only calculated if the photodiode detects a reasonable response
        if df_jvl_data.pd_voltage[v] > measurement_parameters["threshold_pd_voltage"]:
            luminous_efficiency[v] = (
                1
                / measurement_parameters["sq_sin_alpha"]
                / photopic_response
                * df_jvl_data.pd_voltage[v]
                / measurement_parameters["pd_resistance"]
                / df_jvl_data.voltage[v]
                / df_jvl_data.current[v]
            )  # lm/W; luminous efficacy
    return luminous_efficiency


def calculate_current_efficiency(df_jvl_data, measurement_parameters):
    """
    Calculate current efficiency
    """
    current_efficiency = np.zeros(len(df_jvl_data.pd_voltage))
    for v in range(len(df_jvl_data.pd_voltage)):
        # current_efficiency is only calculated if the photodiode detects a reasonable response
        if df_jvl_data.pd_voltage[v] > measurement_parameters["threshold_pd_voltage"]:
            # cd/A; current efficiency
            current_efficiency[v] = (
                df_jvl_data.luminance[v]
                * (measurement_parameters["pixel_area"] * 1e-6)
                / df_jvl_data.current[v]
            )
    return current_efficiency


def calculate_power_density(
    df_corrected_spectrum, df_jvl_data, df_basic_data, measurement_parameters
):
    """
    Calculate power density
    """
    Rfl = np.sum(
        df_corrected_spectrum.corrected_intensity
        * df_basic_data.photodiode_sensitivity
        / df_basic_data.wavelength
    ) / np.sum(df_corrected_spectrum.corrected_intensity / df_basic_data.wavelength)
    power_density = np.zeros(len(df_jvl_data.pd_voltage))
    for v in range(len(df_jvl_data.pd_voltage)):
        if df_jvl_data.pd_voltage[v] > measurement_parameters["threshold_pd_voltage"]:
            power_density[v] = (
                1
                / measurement_parameters["sq_sin_alpha"]
                / Rfl
                * df_jvl_data.pd_voltage[v]
                / measurement_parameters["pd_resistance"]
                / measurement_parameters["pixel_area"]
                * 1e3
            )  # mW/mm2; Power density (Radiant Flux density)
    return power_density


def moving_average(interval, window_size):
    """
    Smoothing function
    """
    window = np.ones(int(window_size)) / float(window_size)
    return np.convolve(interval, window, "same")


def calculate_angle_correction(
    angle_resolved_spectrum_df,
    calibration,
    perp_intensity,
    df_basic_data,
    df_norm_curves,
):
    """
    Function to calculate the correction factor in the case of angular
    resolved emission spectra
    """

    # Temporal dataframe that drops the columns that might hinder calculations
    # with background subtracted and calibration multiplied
    temp_df = (
        angle_resolved_spectrum_df.drop(
            ["background", "wavelength", "0_deg"], axis=1
        ).subtract(angle_resolved_spectrum_df["background"], axis=0)
        * calibration
    )

    # Smoothen the data
    temp_df = temp_df.apply(moving_average, args=(10,), axis=0)

    # Determine the measurement parameters from the dataframe column names
    minimum_angle = float(np.min(temp_df.columns))
    maximum_angle = float(np.max(temp_df.columns))
    step_angle = float(temp_df.columns[1]) - float(temp_df.columns[0])

    perp_intensity = df_corrected_spectrum.corrected_intensity

    # E-factor
    e_factor = np.sum(
        temp_df * angle_resolved_spectrum_df["wavelength"], axis=0
    ) / np.sum(perp_intensity * angle_resolved_spectrum_df["wavelength"], axis=0)

    eFACTOR = np.sum(
        e_factor
        * np.sin(np.deg2rad(np.arange(minimum_angle, maximum_angle, step_angle)))
        * np.deg2rad(step_angle)
    )

    # V-factor
    v_factor = np.sum(temp_df * df_basic_data.v_lambda) / np.sum(
        perp_intensity * df_basic_data.v_lambda
    )

    vFACTOR = np.sum(
        v_factor
        * np.sin(np.deg2rad(np.arange(minimum_angle, maximum_angle, step_angle)))
        * np.deg2rad(step_angle)
    )

    return eFACTOR, vFACTOR


def generate_output_files(
    df_jvl_data,
    df_corrected_spectrum,
    luminance,
    eqe,
    luminous_efficiency,
    current_efficiency,
    power_density,
    max_intensity_wavelength,
    cie_color_coordinates,
):
    """
    Generate Output files
    """

    # Make evaluation directory if it does not yet exist
    if not os.path.exists(root_directory + "eval"):
        os.makedirs(root_directory + "eval")

    # Res-file with JVL and efficiencies
    # Converges the individual arrays into one array
    dataeff = np.stack(
        (
            df_jvl_data.voltage,
            df_jvl_data.current * 1000,
            df_jvl_data.current_density * 1000,
            df_jvl_data.absolute_current_density * 1000,
            luminance,
            eqe,
            luminous_efficiency,
            current_efficiency,
            power_density,
        )
    )

    eff01 = (  # header lines
        "Calculation programme:		OLED-Efficiency-Calculator_vfinal.py"
    )
    eff02 = "OLED active pixel_area:		" + str(pixel_area) + " mm2"
    eff03 = "Distance OLED - Photodiode:	196 mm"
    eff04 = "Photodiode pixel_area:		75 mm2"
    eff05 = "Maximum intensity at:		" + str(max_intensity_wavelength) + " nm"
    eff06 = "CIE coordinates:		" + str(cie_color_coordinates)
    eff13 = "V	I	J	Abs(J)	L	eqe	luminous_efficiency	current_efficiency	P/A"
    eff14 = "V	mA	mA/cm2	mA/cm2	cd/m2	%	lm/W	cd/A	mW/mm2"

    np.savetxt(
        root_directory + "eval/Eff_" + file_name,
        dataeff.T,
        fmt="%.2f %.4e %.4e %.4e %.2f %.2f %.2f %.2f %.4e",
        delimiter="\t",
        header="\n".join([eff01, eff02, eff03, eff04, eff05, eff06, eff13, eff14]),
        comments="",
    )

    # Spectrum file with normalized, df_background subtracted df_spectrum and full wavelength range as detected by the camera

    # dataspec = np.stack((specwl,rawspecback/max(rawspecback)))  # Converges the individual arrays into one array
    normspectra = np.array(df_corrected_spectrum.spectrum_m_background) / np.amax(
        np.array(df_corrected_spectrum.spectrum_m_background)
    )
    dataspec = np.vstack((df_basic_data.wavelength, normspectra))

    spec01 = (  # header lines
        "Calculation programme:		OLED-Efficiency-Calculator_vfinal.py"
    )
    spec02 = "OLED active pixel_area:		" + str(pixel_area) + " mm2"
    spec03 = "Maximum intensity at:		" + str(max_intensity_wavelength) + " nm"
    spec04 = "CIE coordinates:		" + str(cie_color_coordinates)
    spec13 = "Wavelength	Spectrum"
    spec14 = "nm	a.u."

    np.savetxt(
        root_directory + "eval/Spec_" + file_name,
        dataspec.T,
        fmt="%.2f %.4f",
        delimiter="\t",
        header="\n".join([spec01, spec02, spec03, spec04, spec13, spec14]),
        comments="",
    )
