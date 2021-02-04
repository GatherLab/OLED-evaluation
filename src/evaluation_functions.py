# coding: utf-8

import os
import re
import math
import numpy as np
import pandas as pd

# import gather_core as gc  # our own framework
import scipy.constants as sc  # natural constants

"""
User Input
"""
pixel_area = 16  # in mm^2
batch_name = "2020-11-13_MADN-TBPe-glass"
root_directory = "/home/julianb/Documents/01-Studium/03-Promotion/02-Data/2020-10-28_MADN-TBPe-glass-encapsulation/"
threshold_pd_voltage = 0.0005
# Select df_spectrum that shall be taken as reference. If the parameter is set to
# None, the individual df_spectrum of each device is taken. The df_spectrum files
# have to contain _d1_ e.g. for device 1
spectrum_file = None  # "d21_p2.txt"

"""
Copy files from folders and rename them
"""
# Walk through folders and copy files to top directory
# and rename them for better readability
# gc.copy_files(root_directory + "JVL-data/", batch_name)

"""
Define Geometrical Parameters
"""

# it is in mm here, this is the fixed distance in the autotube
distance = 196
# m2; pixel_area of the photodiode
photodiode_area = 0.000075
# Ohm; resistance of the transimpedance amplifier used to amplify and convert PD current into voltage
photodiode_resistance = 4.75e5
# lm/W; peak response
photodiode_peak_response = 683
# Photodiode radius
photodiode_radius = math.sqrt(photodiode_area / math.pi)
# Sinus square of the opening angle between OLED and photodiode, which
# resembles the light detected by the PD assuming Lambertian emission
sq_sin_alpha = photodiode_radius ** 2 / (
    (distance * 1e-3) ** 2 + photodiode_radius ** 2
)

"""
Define Functions for calculations
"""


def calculate_cie_coordinates(df_corrected_spectrum):
    """
    Calculates wavelength of maximum spectral intensity and the CIE color coordinates
    """
    for i, j in enumerate(df_corrected_spectrum.spectrum_intensity):
        if j == max(df_corrected_spectrum.spectrum_intensity):
            max_intensity_wavelength = df_spectrum.wavelength[i]

    X = sum(df_corrected_spectrum.intensity * df_norm_curves.xcie)
    Y = sum(df_corrected_spectrum.intensity * df_norm_curves.ycie)
    Z = sum(df_corrected_spectrum.intensity * df_norm_curves.zcie)

    CIE = np.array([X / (X + Y + Z), Y / (X + Y + Z)])
    # CIE[0] = X / (X + Y + Z)
    # CIE[1] = Y / (X + Y + Z)
    return (
        max_intensity_wavelength,
        ("(" + ", ".join(["%.3f"] * 2) + ")") % tuple(CIE),
    )


def calculate_eqe(df_corrected_spectrum, df_jvl_data):
    """
    Calculate external quantum efficiency
    """
    # calculate average quantum efficiency of the detector
    detector_quantum_efficiency = (
        sc.h
        * sc.c
        / sc.e
        * np.sum(
            df_corrected_spectrum.intensity
            * df_basic_data.photodiode_sensitivity
            / df_basic_data.wavelength
        )
        / np.sum(df_corrected_spectrum.intensity)
        * 1e9
    )
    eqe = np.zeros(df_jvl_data.photodiode_voltage.shape)
    for v in range(len(df_jvl_data.photodiode_voltage)):
        # eqe is only calculated if the photodiode detects a reasonable response
        if df_jvl_data.photodiode_voltage[v] > 0.00005:
            eqe[v] = (
                100
                * df_jvl_data.photodiode_voltage[v]
                / photodiode_resistance
                / sq_sin_alpha
                / df_jvl_data.current[v]
                / detector_quantum_efficiency
            )  # calculate eqe in %

    return eqe


def calculate_luminance(df_corrected_spectrum, df_jvl_data):
    """
    Calculate luminance
    """
    # A/lm; photopic response
    photopic_response = (
        np.sum(
            df_corrected_spectrum.intensity
            * df_basic_data.photodiode_sensitivity
            / df_basic_data.wavelength
        )
        / np.sum(
            df_basic_data.v_lambda
            * df_corrected_spectrum.intensity
            / df_basic_data.wavelength
        )
        / photodiode_peak_response
    )
    luminance = np.zeros(df_jvl_data.photodiode_voltage.shape)
    for v in range(len(df_jvl_data.photodiode_voltage)):
        # luminance is only calculated if the photodiode detects a reasonable response
        if df_jvl_data.photodiode_voltage[v] > threshold_pd_voltage:
            luminance[v] = (
                1
                / math.pi
                / sq_sin_alpha
                / photopic_response
                * df_jvl_data.photodiode_voltage[v]
                / photodiode_resistance
                / (pixel_area * 1e-6)
            )  # cd/m2; luminace

    return photopic_response, luminance


def calculate_luminous_efficacy(df_jvl_data, photopic_response):
    """
    Calculate luminous efficacy
    """
    luminous_efficiency = np.zeros(df_jvl_data.photodiode_voltage.shape)
    for v in range(len(df_jvl_data.photodiode_voltage)):
        # luminous_efficiency is only calculated if the photodiode detects a reasonable response
        if df_jvl_data.photodiode_voltage[v] > threshold_pd_voltage:
            luminous_efficiency[v] = (
                1
                / sq_sin_alpha
                / photopic_response
                * df_jvl_data.photodiode_voltage[v]
                / photodiode_resistance
                / df_jvl_data.voltage[v]
                / df_jvl_data.current[v]
            )  # lm/W; luminous efficacy
    return luminous_efficiency


def calculate_current_efficiency(df_jvl_data, luminance):
    """
    Calculate current efficiency
    """
    current_efficiency = np.zeros(df_jvl_data.photodiode_voltage.shape)
    for v in range(len(df_jvl_data.photodiode_voltage)):
        # current_efficiency is only calculated if the photodiode detects a reasonable response
        if df_jvl_data.photodiode_voltage[v] > threshold_pd_voltage:
            # cd/A; current efficiency
            current_efficiency[v] = (
                luminance[v] * (pixel_area * 1e-6) / df_jvl_data.current[v]
            )
    return current_efficiency


def calculate_power_density(df_corrected_spectrum, df_jvl_data):
    """
    Calculate power density
    """
    Rfl = np.sum(
        df_corrected_spectrum.intensity
        * df_basic_data.photodiode_sensitivity
        / df_basic_data.wavelength
    ) / np.sum(df_corrected_spectrum.intensity / df_basic_data.wavelength)
    power_density = np.zeros(df_jvl_data.photodiode_voltage.shape)
    for v in range(len(df_jvl_data.photodiode_voltage)):
        if df_jvl_data.photodiode_voltage[v] > threshold_pd_voltage:
            power_density[v] = (
                1
                / sq_sin_alpha
                / Rfl
                * df_jvl_data.photodiode_voltage[v]
                / photodiode_resistance
                / pixel_area
                * 1e3
            )  # mW/mm2; Power density (Radiant Flux density)
    return power_density


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
