# coding: utf-8
"""
Created by Gather Lab

This is the code for the analysis of EL measurements. It corrects the IVL measurement for non-Lambertian emission. The spectral intensities within 180deg (or 90deg)
were measured with the spectrometer and from this the characteristics is corrected. 
For the analysis the data from 0 to 90deg is considered (not-90 to 0deg), care should be taken that the cut-out of the holder is positioned accordingly.

Required files:
	- 'library' folder with 
		- "Responsivity_PD.txt" 
		- "Photopic_response.txt"
		- "NormCurves_400-800.txt"
		- 'CalibrationData.txt'(converison from counts into intensity)
	- 'data' folder
	  with sample folder
		-'batch' folder
		with sample folder again
	- in both sample folders:
			'datetime' folder
				'raw' folder
					'keithleydata' and 'spectrumdata' folder
						*'keithleydata' there should be the files: keithleyOLEDvoltages.txt, keithleyPDvoltages.txt, specifickeithleyPDvoltages.txt
						For ANALYSIS especially the keithleyPDvoltages.txt file can be copied into the folder as a PD measurement might not be needed for every single device
						*'spectrumdata' there should be the text files (depending on your recodring choice) from Angle-90.txt over Angle0.txt to Angle90.txt
						AND a background file (all recorded within the run)				

The default values for the parameters in this code are          
	- distance of PD and OLED 0.115m
	- PDarea = 0.000075 # m2; area of the used photodiode
	- PDres = 4.75e5 # Ohm; at 50dB gain
	- our analysis software subtracts the background spectrum, and smoothens the spectrum, typically by applying a 10 nm sliding average filter (line 327). Depending on the signal-to-noise ratio this smoothing can be commented out
		   
The output of this program is created in the sample folder in the 'data' folder (sample folder in 'batch' is kept unchanged):    
    - creates a 'processedEL' folder with the results
		'sample_name'_effdata_LAM.txt
			Measurement code : 'sample name''datetime'
			Calculation programme :	NonLamLIV-EQE_vfinal.py
			Credits :	GatherLab, University of St Andrews, 2020
			Measurement time : 201907031258	Analysis time :201907031524
			OLED active area:     4e-06 m2
			Distance OLED - Photodiode:   0.115 m
			Photodiode area:    7.54296396127e-05m2
			Maximum intensity at:     570.0 nm
			CIE coordinates:      (0.522, 0.476)
			V            I           J         Abs(J)        L         EQE        LE         CE        PoD
		'sample_name'_effdata_NONLAM.txt
			V            I           J         Abs(J)        L         AvLum    EQE        LE         CE        PoD
		'sample_name'_lamdata.txt (this includes not only the angle-dependent emission but also a correction for the photopic response due to spectral changes)
		'sample_name'_specdata.txt
		'sample_name'_specdatafull_LAM.txt
		'sample_name'_specdatahalf.txt
		and
		7 PNG files containing some of the comparison between NONLAM and LAM.

Important parameters for the analysis:    
    - distance PD to OLED: fixed in EL setup to 0.115m
    - PD paramters: PDA100A2 (area: 75mm2, PDgain (usually 50dB))
	- size of OLED

"""

"IMPORTING REQUIRED MODULES"
# General Modules
# import os, shutil
# import re, string
import os
import re
import math
import numpy as np
import pandas as pd
import datetime as dt

import scipy.constants as sc  # natural constants


# def movingaverage(interval, window_size):
#     """
#     Smoothing function
#     """
#     window = np.ones(int(window_size)) / float(window_size)
#     return np.convolve(interval, window, "same")


# def set_gain(gain):
#     """
#     Set calculation parameters according to gain of photodiode.

#     gain: int (0, 10, 20, 30, 40, 50, 60, 70)
#         Gain of photodiode which was used to measure the luminance.

#     returns:
#         PDres: float
#             resistance of the transimpedance amplifier used to amplify and
#             convert the photocurrent of the diode into a voltage.
#         PDcutoff: float
#             cutoff voltage of photodiode below which only noise is expected.
#     """
#     if (
#         gain == 0
#     ):  # set resistance of the transimpedance amplifier used to amplify and convert PD current into voltage
#         PDres = 1.51e3  # Ohm; High-Z
#         PDcutoff = 1e-6  # V
#     elif gain == 10:
#         PDres = 4.75e3  # Ohm; High-Z
#         PDcutoff = 3e-6  # V
#     elif gain == 20:
#         PDres = 1.5e4  # Ohm; High-Z
#         PDcutoff = 5e-6  # V
#     elif gain == 30:
#         PDres = 4.75e4  # Ohm; High-Z
#         PDcutoff = 1e-5  # V
#     elif gain == 40:
#         PDres = 1.51e5  # Ohm; High-Z
#         PDcutoff = 3e-4  # V
#     elif gain == 50:
#         PDres = 4.75e5  # Ohm; High-Z
#         PDcutoff = 9e-4  # V
#     elif gain == 60:
#         PDres = 1.5e6  # Ohm; High-Z
#         PDcutoff = 4e-3  # V
#     elif gain == 70:
#         PDres = 4.75e6  # Ohm; High-Z
#         PDcutoff = 2e-3  # V
#     elif gain == 80:
#         PDres = 2.2e6  # Ohm; High-Z
#         PDcutoff = 2e-5  # V

#     else:
#         print(
#             "Error: Not a valid gain."
#             + "\nThe Thorlabs PDA100A2 supports the following gains:"
#             + "\n0 dB, 10 dB, 20 dB, 30 dB, 40 dB, 50 dB, 60 dB, 70 dB"
#             + "\nCheck photodiode gain in your data header."
#         )
#     return PDres, PDcutoff


# "SETTING KNOWN PARAMETERS"
# Setting Variables
# OLEDwidth = 2e-3  # OLED width or height in m;
# pixel_area = (OLEDwidth) ** 2
# PDarea = 0.000075  # Photodiode area in m2
# PDradius = np.sqrt(PDarea / np.pi)  # Photodiode Radius in m
# PDresis, PDcutoff = set_gain(70)  # Resistance if gain = 70dB and high load resistance
# distance = 0.115  # Distance between OLED and PD in m
# now = dt.datetime.now()  # Set the start time
# start_time = str(
#     now.strftime("%Y-%m-%d %H:%M").replace(" ", "").replace(":", "").replace("-", "")
# )


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

    # # interpolate spectrometer calibration factor onto correct axis
    # calibration = np.interp(
    #     photopic_response["wavelength"].to_numpy(),
    #     spectrometer_calibration["wavelength"].to_numpy(),
    #     spectrometer_calibration["sensitivity"].to_numpy(),
    # )

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


# Loading the V(λ) and R(λ) spectra against wavelength
# wavelength = np.loadtxt(
# os.path.join(os.path.dirname(__file__), "library", "Photopic_response.txt")
# )[:, 0]
# Vlambda= np.loadtxt(
# os.path.join(os.path.dirname(__file__), "library", "Photopic_response.txt")
# )[:, 1]
# Rlambda= np.loadtxt(
# os.path.join(os.path.dirname(__file__), "library", "Responsivity_PD.txt")
# )[:, 1]

# Loading the CIE Normcurves
# XCIE = np.loadtxt(
# os.path.join(os.path.dirname(__file__), "library", "NormCurves_400-800.txt")
# )[:, 2]
# YCIE = np.loadtxt(
# os.path.join(os.path.dirname(__file__), "library", "NormCurves_400-800.txt")
# )[:, 3]
# ZCIE = np.loadtxt(
# os.path.join(os.path.dirname(__file__), "library", "NormCurves_400-800.txt")
# )[:, 4]

# Loading the spectrometer calibration factors -  this converts the counts/nm/sr into W/nm/sr (responsivity function of the spectrometer and transmission of the fibre)
# calibrationwvl = np.array(
#     np.loadtxt(
#         os.path.join(os.path.dirname(__file__), "library", "CalibrationData.txt")
#     )[:, 0]
# )
# calibration = np.array(
#     np.loadtxt(
#         os.path.join(os.path.dirname(__file__), "library", "CalibrationData.txt")
#     )[:, 1]
# )


# sc.physical_constants["luminous efficacy"][0] = 683  # Peak response in lm/W

# Setting Constants
# sc.h = sc.sc.h  # Planck's Constant in Js
# sc.c = sc.sc.c  # Speed of Light in m/s
# sc.e = sc.sc.e  # Magnitude of fundamental charge in As

# batch = os.path.abspath(os.path.join(os.path.dirname(__file__), "data", "batch"))
# print(os.listdir(batch))

# for sample in os.listdir(batch):
# # for datetime in os.listdir(os.path.abspath(os.path.join(batch, sample))):
# sampledirectory = os.path.abspath(
# os.path.join(os.path.dirname(__file__), "data", sample, datetime)
# )
# rawdirectory = os.path.abspath(os.path.join(sampledirectory, "raw"))
# if os.path.isdir(rawdirectory):
# pass
# else:
# print("No data found for this measurement code.")
# os.sys.exit()

# "SETTING DIRECTORY FOR EXPORTING DATA"
# processdirectory = os.path.abspath(os.path.join(sampledirectory, "processedEL"))
# process = True
# while process == True:
#     if os.path.isdir(processdirectory):
#         cont = "Y"  # str(raw_input("Processed data already exists for this measurement code. Proceed with analysis? (Y/N)  "))
#         if cont == str("Y"):
#             cont = "Y"  # str(raw_input("Do you wish to overwrite current analysis data? (Y/N)   "))
#             if cont == str("Y"):
#                 s = open(os.path.join(processdirectory, "_specdata.txt"), "w")
#                 s.close()  # Makes sure the file is closed before deleting the folder
#                 shutil.rmtree(processdirectory)
#                 os.mkdir(processdirectory)
#                 process = False
#                 break
#             elif cont == str("N"):
#                 for n in range(
#                     1, 5, 1
#                 ):  # Makes a new directory with a different name so the old one isn't overwritten
#                     process = "processed" + str(n)
#                     processdirectory = os.path.abspath(
#                         os.path.join(sampledirectory, process)
#                     )
#                     if not os.path.isdir(processdirectory):
#                         os.mkdir(processdirectory)
#                         process = False
#                         break
#             else:
#                 print("Invalid input.")
#         elif cont == str("N"):
#             print("Finished. No analysis performed.")
#             os.sys.exit()
#         else:
#             print("Invalid input.")
#     else:
#         os.makedirs(processdirectory)
#         process = False
#         break

# "FINDING EXISTING DATA AND PERFORMING ANALYSIS"
# mayafilepath = "spectrumdata"  # setting spectra directory
# keithleyfilepath = "keithleydata"  # setting keithley directory
# mayafilepath = os.path.abspath(os.path.join(rawdirectory, mayafilepath))
# keithleyfilepath = os.path.abspath(os.path.join(rawdirectory, keithleyfilepath))
# spec_header = 11
# voltage_header = 11
# print(
#     "Spectrum files found for this measurement :   ", os.listdir(mayafilepath)
# )
# print(
#     "Keithley files found for this measurement :   ",
#     os.listdir(keithleyfilepath),
# )

# print("\nIMPORTING DATA...")

# Importing spectrum data
# mayadata = os.listdir(mayafilepath)  # lists all files in folder spectrum data
# spectrumdata = [a for a in mayadata if a.startswith("Angle")]
# background = [a for a in mayadata if not a.startswith("Angle")]
# spectrumdata.sort(
#     key=lambda x: (float(x.split("Angle")[1].split(".txt")[0]), x)
# )
# print("\nSpectrum files in use are: ", spectrumdata)
# print("\nBackground file in use is:", background)
# Background spectrum

#######################################################################################
################################ Spectrum Related #####################################
#######################################################################################

# The following should be generic for both, a simple spectrum and a massive
# angle resolved spectrum
# spectrum = pd.read_csv(
#     "/home/julianb/Documents/01-Studium/03-Promotion/02-Data/example-data/2021-02-04_test_d24_p2_gon-spec.csv",
#     # "C:/Users/GatherLab-Julian/Documents/Nextcloud/01-Studium/03-Promotion/02-Data/example-data/2021-02-04_test_d24_p2_gon-spec.csv",
#     sep="\t",
#     skiprows=3,
# )


# # Read in calibration files
# (
#     photopic_response,
#     pd_responsivity,
#     cie_reference,
#     calibration,
# ) = read_calibration_files()


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


# Calculate correction factors
# e_correction_factor = calculate_e_correction(spectrum_corrected)
# v_correction_factor = calculate_v_correction(spectrum_corrected, photopic_response)

# Normalise each column
# I think this is also not needed for the calculations
# spectrum_normalised = (
#     spectrum_corrected.drop(["0_deg", "wavelength"], axis=1)
#     / spectrum_corrected.drop(["0_deg", "wavelength"], axis=1).max()
# )
# Lambertian Spectrum (never used again, why do I need this??)
# lambertian_spectrum = np.cos(np.deg2rad(angles))
# non_lambertian_spectrum = ri / ri[np.where(angles == np.min(angles))[0][0]]
# non_lambertian_spectrum_v = li / li[np.where(angles == np.min(angles))[0][0]]


# Not really needed, I might get rid of this later on
# goniometer_jvl = pd.read_csv(
#     "/home/julianb/Documents/01-Studium/03-Promotion/02-Data/example-data/2021-02-04_test_d24_p2_gon-jvl.csv",
#     # "C:/Users/GatherLab-Julian/Documents/Nextcloud/01-Studium/03-Promotion/02-Data/example-data/2021-02-04_test_d24_p2_gon-jvl.csv",
#     sep="\t",
#     skiprows=7,
#     names=["angle", "voltage", "current"],
# )

# Formatting the data for the intensity map and spectrum.


# This must be interpolated over the available wavelength of photopic response
# spectrum_interpolated = np.interp(
# photopic_response["wavelength"].to_numpy(),
# spectrum["wavelength"].to_numpy(),
# spectrum["background"].to_numpy(),
# )

# bgwvl = np.array(
#     np.loadtxt(os.path.join(mayafilepath, background[0]), skiprows=spec_header)[:, 0]
# )  # Loading background spectrum
# bginte = np.array(
#     np.loadtxt(os.path.join(mayafilepath, background[0]), skiprows=spec_header)[:, 1]
# )  # Loading background spectrum
# bginte = np.interp(
#     wavelength, bgwvl, bginte
# )  # interpolate background onto correct axis
# print("\nBackground spectrum loaded...")
# Selecting which angle which will be read first

##
## From here they go over each angle seperately
##


# first_angle = float(
# string.split(str(string.split(spectrumdata[0], ".txt")[0]), "Angle")[1]
# )  # gets the string 'Angle_' from the filename
# print("\nThe first angle to be analysed is:   " + str(first_angle) + "...")
# Saving the data for the forward spectrum
# try:
# specwvl = np.array(
#     np.loadtxt(os.path.join(mayafilepath, "Angle0.0.txt"), skiprows=spec_header)[
#         :, 0
#     ]
# )
# rawspecinte = np.array(
#     np.loadtxt(os.path.join(mayafilepath, "Angle0.0.txt"), skiprows=spec_header)[
#         :, 1
#     ]
# )  # load wavelengths and raw intensity
# rawspecinte = np.interp(
#     wavelength, specwvl, rawspecinte
# )  # interpolate spectrum onto correct axis
# spec = np.array(rawspecinte) - np.array(
#     spectrum_interpolated
# )  # subtract background intensity
# intensity = (
#     spec * calibration
# )  # multiply by spectrometer calibration factor to get intensity in W/nm/sr
# perp_intensity = movingaverage(intensity, 10)
# print("\nPerpendicular spectrum loaded...")
# except:
# try:
#     specwvl = np.array(
#         np.loadtxt(
#             os.path.join(mayafilepath, "Angle000.txt"), skiprows=spec_header
#         )[:, 0]
#     )
#     rawspecinte = np.array(
#         np.loadtxt(
#             os.path.join(mayafilepath, "Angle000.txt"), skiprows=spec_header
#         )[:, 1]
#     )  # load wavelengths and raw intensity
#     rawspecinte = np.interp(
#         wavelength, specwvl, rawspecintespectrum_interpolated
#     )  # interpolate spectrum onto correct axis
#     spec = np.array(rawspecinte) - np.array(
#         spectrum_interpolated
#     )  # subtract background intensity
#     intensity = (
#         spec * calibration
#     )  # multiply by spectrometer calibration factor to get intensity in W/nm/sr
#     perp_intensity = movingaverage(intensity, 10)
#     print("\nPerpendicular spectrum loaded...")
# except:
#     print("No perpendicular spectrum. Unable to perform analysis.")
#     os.sys.exit()


# angles = np.array(
#     np.loadtxt(
#         os.path.join(keithleyfilepath, "keithleyOLEDvoltages.txt"),
#         skiprows=voltage_header,
#     )[:, 0]
# )
# OLEDvoltage_spec = np.array(
#     np.loadtxt(
#         os.path.join(keithleyfilepath, "keithleyOLEDvoltages.txt"),
#         skiprows=voltage_header,
#     )[:, 1]
# )
# OLEDcurrent_spec = np.array(
#     np.loadtxt(
#         os.path.join(keithleyfilepath, "keithleyOLEDvoltages.txt"),
#         skiprows=voltage_header,
#     )[:, 2]
# )

# Loading the Keithley data
# jvl_data = pd.read_csv(
#     "/home/julianb/Documents/01-Studium/03-Promotion/02-Data/example-data/2021-02-04_test_d21_p2_jvl.csv",
#     # "C:/Users/GatherLab-Julian/Documents/Nextcloud/01-Studium/03-Promotion/02-Data/example-data/2021-02-04_test_d21_p2_jvl.csv",
#     sep="\t",
#     skiprows=7,
#     names=["voltage", "current", "pd_voltage"],
# )


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
        return self.pd_voltage / self.pd_resistance / self.sqsinalpha * 2

    def calculate_non_lambertian_v_coeff(self):
        """
        Calculate v_coeff
        """
        return (
            sc.physical_constants["luminous efficacy"][0]
            * self.pd_voltage
            / self.pd_resistance
            / self.sqsinalpha
            * 2
        )

    def calculate_non_lambertian_eqe(self, e_coeff, e_correction_factor):
        """
        Function to calculate the eqe
        """

        # e_coeff = self.calculate_non_lambertian_e_coeff(jvl_data)

        eqe = 100 * (
            sc.e
            / 1e9
            / sc.h
            / sc.c
            / self.current
            * e_coeff
            * self.integral_1
            / self.integral_4
            * e_correction_factor
        )

        return eqe

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
        return (
            1
            / self.voltage
            / self.current
            * v_coeff
            * self.integral_3
            / self.integral_4
            * v_correction_factor
        )

    def calculate_current_efficiency(self):
        """
        Calculate current efficiency
        """
        # In case of the current being zero, set a helper current to nan so
        # that the result of the division becomes nan instead of infinite

        return self.pixel_area / self.current * self.luminance

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
        return self.pd_voltage / self.pd_resistance / self.sqsinalpha

    def calculate_lambertian_v_coeff(self):
        """
        Calculate v_coeff
        """
        return (
            sc.physical_constants["luminous efficacy"][0]
            * self.pd_voltage
            / self.pd_resistance
            / self.sqsinalpha
        )

    def calculate_lambertian_eqe(self, e_coeff):
        """
        Function to calculate the eqe
        """

        # e_coeff = calculate_lambertian_eqe(jvl_data)

        return 100 * (
            sc.e
            / 1e9
            / sc.h
            / sc.c
            / self.current
            * e_coeff
            * self.integral_1
            / self.integral_4
        )

    def calculate_lambertian_luminance(self, v_coeff):
        """
        Calculate luminance
        """
        # v_coeff = calculate_lambertian_v_coeff(jvl_data)
        return 1 / np.pi / self.pixel_area * v_coeff * self.integral_3 / self.integral_4

    def calculate_lambertian_luminous_efficacy(self, v_coeff):
        """
        Calculate luminous efficiency
        """

        # v_coeff = calculate_lambertian_v_coeff(self, jvl_data)
        return (
            1
            / self.voltage
            / self.current
            * v_coeff
            * self.integral_3
            / self.integral_4
        )

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


# jvl = JVLData(
#     jvl_data,
#     spectrum_corrected[["wavelength", "0.0"]].rename(columns={"0.0": "intensity"}),
#     photopic_response,
#     pd_responsivity,
#     True,
#     correction_factor=[e_correction_factor, v_correction_factor],
# )
# print("Stop")

# currentdata = os.listdir(keithleyfilepath)
# currentdata.sort()
# OLEDdata = currentdata[0]
# PDdata = currentdata[1]
# print("\nOLED Current and Voltage file in use is:", OLEDdata)
# print("\nPhotodiode Voltage file in use is:", PDdata)
# Current / Voltage / Luminance IVL Readings from Photodiode
# OLEDvoltage = np.array(
# np.loadtxt(
# os.path.join(keithleyfilepath, "keithleyPDvoltages.txt"),
# skiprows=voltage_header,
# )[:, 0]
# )
# OLEDcurrent_mA = np.array(
# np.loadtxt(
# os.path.join(keithleyfilepath, "keithleyPDvoltages.txt"),
# skiprows=voltage_header,
# )[:, 1]
# )
# OLEDcurrent = OLEDcurrent_mA * 1e-3
# PDvoltage = np.array(
#     np.loadtxt(
#         os.path.join(keithleyfilepath, "keithleyPDvoltages.txt"),
#         skiprows=voltage_header,
#     )[:, 2]
# )
# This checks for 180 or 90 degree measurement

# n = len(angles) - 1
# min_angle = angles[0]
# max_angle = angles[n]
# step_angle = (max_angle - min_angle) / n
# print("\nSpectra taken for the following angles : ", angles)

# print("\nPicking out the perpendicular (0 degree) reading... ")
# if max_angle == 90:
#     try:
#         min_index = 0.0
#         max_index = 90.0
#     except ValueError:
#         print("Can't find perpendicular reading")
# elif max_angle == 180:
#     try:
#         min_index = 90.0
#         max_index = 180.0
#     except ValueError:
#         print("Can't find perpendicular reading")
# else:
#     print("\nCheck angle range of data.")


# "Setting all empty arrays for later data collection"
# ints = {}  # Dictionary for every spectrum at each angle
# intensities = (
#     []
# )  # 2d array of all intensities across all angles and for all wavelengths
# Integral1 = []
# Integral2 = []
# Integral3 = []
# Integral4 = []
# e_correction_factor = []
# v_correction_factor = []
# RI = []
# LI = []
# eCoeff = np.zeros(PDvoltage.shape)
# vCoeff = np.zeros(PDvoltage.shape)
# EQE = np.zeros(PDvoltage.shape)
# Lum = np.zeros(PDvoltage.shape)
# LE = np.zeros(PDvoltage.shape)
# CE = np.zeros(PDvoltage.shape)
# POW = np.zeros(PDvoltage.shape)


# LOADING ALL OF THE SPECTRUM DATA AND FORMATTING
# for title in spectrumdata:
# name = str(
#     string.split(title, ".txt")[0]
# )  # gets the string 'Angle_' from the filename
# angle = float(
#     string.split(name, "Angle")[1]
# )  # gets the string 'Angle_' from the filename

# "PROCESSING THE SPECTRUM DATA - SUBTRACT BACKGROUND AND MULTIPLY BY CALIBRATION"
# specwvl = np.array(
#     np.loadtxt(os.path.join(mayafilepath, title), skiprows=spec_header)[:, 0]
# )
# rawspecinte = np.array(
#     np.loadtxt(os.path.join(mayafilepath, title), skiprows=spec_header)[:, 1]
# )  # load wavelengths and raw intensity
# rawspecinte = np.interp(
#     wavelength, specwvl, rawspecinte
# )  # interpolate spectrum onto correct axis
# spec = np.array(rawspecinte) - np.array(
#     spectrum_interpolated
# )  # subtract background intensity
# intensity = (
#     spec * calibration
# )  # multiply by spectrometer calibration factor to get intensity W/nm/sr
# intensity = movingaverage(intensity, 10)  # smoothing
# ints[angle] = intensity  # saves individual spectra to a directory of all


# RI.append(float(sc.h * sc.c / 1e-9 * np.sum(intensity)))
# LI.append(
#     float(
#         sc.physical_constants["luminous efficacy"][0]
#         * sc.h
#         * sc.c
#         / 1e-9
#         * np.sum(intensity * photopic_response["photopic_response"].to_numpy())
#     )
# )

# if angle == first_angle:  # Stacking intensities into a 2D matrix
#     intensities.append((np.array(intensity)))
# else:
# intensities = np.vstack((intensities, np.array(intensity)))

# if angle in np.arange(min_index, max_index, step_angle):


# e_correction_factor.append(
# sum(intensity * wavelength) / sum(perp_intensity * wavelength)
# )  # This replaces cos(theta) in I = I0*cos(theta)
# v_correction_factor.append(
# sum(intensity * photopic_response["photopic_response"].to_numpy())
# / sum(perp_intensity * photopic_response["photopic_response"].to_numpy())
# )  # This replaces cos(theta) in I = I0*cos(theta)


# specangles = np.hstack([0, angles])
# normintensities = np.array(intensities) / np.amax(np.array(intensities))
# intensitydata = np.vstack((wavelength, normintensities))
# intensitydata = np.hstack((specangles.reshape(specangles.shape[0], 1), intensitydata))

# Calculating key integrals for intensity in forward direction and correction factors F_E and F_V for all angles
# Integral1 = np.sum(perp_intensity * wavelength)
# integral_1 = np.sum(spectrum_corrected["0.0"] * spectrum_corrected["wavelength"])
# # Integral2 = np.sum(perp_intensity)
# integral_2 = np.sum(spectrum_corrected["0.0"])
# # Integral3 = np.sum(perp_intensity * photopic_response["photopic_response"].to_numpy())
# integral_3 = np.sum(
#     spectrum_corrected["0.0"] * photopic_response["photopic_response"].to_numpy()
# )
# # Integral4 = np.sum(perp_intensity * pd_responsivity["pd_responsivity"].to_numpy())
# integral_4 = np.sum(
#     spectrum_corrected["0.0"] * pd_responsivity["pd_responsivity"].to_numpy()
# )


# e_correction_factor = np.sum(
# np.array(e_correction_factor)
# * np.sin(np.deg2rad(np.arange(min_index, max_index, step_angle)))
# * np.deg2rad(step_angle)
# )
# v_correction_factor = np.sum(
# np.array(v_correction_factor)
# * np.sin(np.deg2rad(np.arange(min_index, max_index, step_angle)))
# * np.deg2rad(step_angle)
# )
# print(e_correction_factor)
# print(v_correction_factor)


# Ilam = []
# for i in range(len(angles)):
#     Ilam.append(np.cos(np.deg2rad(angles[i])))
# Inonlam = np.array(RI) / RI[np.where(angles == min_index)[0][0]]
# Inonlam_v = (
#     np.array(LI) / LI[np.where(angles == min_index)[0][0]]
# )  # emission in terms of photometric response, so taking into account the spectral shifts and sensitivity of the eye/photopic response
# lamdata = np.stack((angles, Ilam, Inonlam, Inonlam_v))

# Current density calculations
# currentdensity = (
# OLEDcurrent * 1e3 / (pixel_area * 1e4)
# )  # calculate current density in mA/cm2
# abscurrentdensity = abs(
# np.array(currentdensity)
# )  # calculates the absolute value of the current density


# print("Calculating Lambertian efficiency data...")
# for v in range(len(PDvoltage)):
# if PDvoltage[v] > PDcutoff:
# eCoeff[v] = PDvoltage[v] / PDresis / sqsinalpha
# vCoeff[v] = (
# sc.physical_constants["luminous efficacy"][0]
# * PDvoltage[v]
# / PDresis
# / sqsinalpha
# )
# EQE[v] = 100 * (
#     sc.e
#     / 1e9
#     / sc.h
#     / sc.c
#     / OLEDcurrent[v]
#     * eCoeff[v]
#     * Integral1
#     / Integral4
# )
# Lum[v] = 1 / np.pi / pixel_area * vCoeff[v] * Integral3 / Integral4
#         LE[v] = 1 / OLEDvoltage[v] / OLEDcurrent[v] * vCoeff[v] * Integral3 / Integral4
#         CE[v] = pixel_area / OLEDcurrent[v] * Lum[v]
#         POW[v] = 1 / (pixel_area * 1e6) * eCoeff[v] * Integral2 / Integral4 * 1e3
# # Formatting the efficiency data
# dataeff_LAM = np.stack(
#     (
#         OLEDvoltage,
#         OLEDcurrent * 1e3,
#         currentdensity,
#         abscurrentdensity,
#         Lum,
#         EQE,
#         LE,
#         CE,
#         POW,
#     )
# )  # Converges the individual arrays into one array

# "#####################################################################"
# "#####################EXPORTING FORMATTED DATA########################"
# "#####################################################################"
# print("\nEXPORTING...")

# # Header Parameters
# line01 = "Measurement code : " + sample + datetime
# line02 = "Calculation programme :	NonLamLIV-EQE.py"
# linex = "Credits :	GatherLab, University of St Andrews, 2019"
# linexx = "Measurement time : " + datetime + "\tAnalysis time :" + start_time
# line03 = "OLED active area:     " + str(pixel_area) + " m2"
# line04 = "Distance OLED - Photodiode:   " + str(distance) + " m"
# line05 = "Photodiode area:    " + str(PDarea) + "m2"
# line06 = "Maximum intensity at:     " + str(lambdamax) + " nm"
# line07 = "CIE coordinates:      " + str(CIEformatted)
# line08 = ""
# line09 = ""
# line10 = "### Formatted data ###"
# line11 = "V            I           J         Abs(J)        L         EQE        LE         CE        PoD"
# line12 = "V            mA       mA/cm2      mA/cm2       cd/m2        %        lm/W        cd/A      mW/mm2"
# line13 = "Intensity for all Wavelengths / Angles"
# line14 = "angles    Lambertian    Actual    Actual_v"
# line15 = "degree    a.u.    a.u.    a.u."

# header_lines = [
#     line01,
#     line02,
#     linex,
#     linexx,
#     line03,
#     line04,
#     line05,
#     line06,
#     line07,
#     line08,
#     line09,
#     line10,
#     line11,
#     line12,
# ]
# header_lines2 = [
#     line01,
#     line02,
#     linex,
#     linexx,
#     line03,
#     line04,
#     line05,
#     line06,
#     line07,
#     line08,
#     line09,
#     line10,
#     line13,
# ]
# header_lines3 = [
#     line01,
#     line02,
#     linex,
#     linexx,
#     line03,
#     line04,
#     line05,
#     line06,
#     line07,
#     line08,
#     line09,
#     line10,
#     line14,
#     line15,
# ]

# n = 1
# # Plotting an intensity grid over all angles and wavelengths
# mpl.figure(n, figsize=(10, 8))
# intemap = mpl.contourf(angles, wavelength, normintensities.T, 50, cmap=mpl.cm.jet)
# mpl.title("Normalised Intensity over all Angles and Wavelengths\n", fontsize=20)
# mpl.xlabel("Angle (degrees)", fontsize=20)
# mpl.ylabel("Wavelength (nm)", fontsize=20)
# mpl.colorbar(intemap)
# mpl.tick_params(axis="both", labelsize=20)
# mpl.savefig(os.path.join(processdirectory, sample + "_map.png"), dpi=500)

# # Plotting perpendicular spectrum
# mpl.figure(n + 1, figsize=(16, 9))
# mpl.plot(wavelength, perp_intensity, linewidth=1.0, label="Angle" + str(angle))
# mpl.title("Perpendicular Spectrum\n", fontsize=20)
# mpl.xlabel("Wavelength (nm)", fontsize=20)
# mpl.xlim(
#     400, 800
# )  # this limits the x-range displayed,view full range before cutting down
# mpl.ylabel("Intensity (W/nm/sr)", fontsize=20)
# mpl.minorticks_on()
# mpl.grid(True, which="major", color="0.5")
# mpl.grid(True, which="minor", color="0.8")
# mpl.tick_params(axis="both", labelsize=14)
# mpl.savefig(os.path.join(processdirectory, sample + "_perpspec.png"), dpi=500)

# # Plotting a combined graph of spectra at every angle
# for angle in angles:
#     mpl.figure(n + 2, figsize=(16, 9))
#     mpl.plot(wavelength, ints[angle], linewidth=1.0, label="Angle" + str(angle))
#     mpl.title("Angular Dependence of Spectra\n", fontsize=20)
#     mpl.xlabel("Wavelength (nm)", fontsize=20)
#     mpl.xlim(
#         400, 800
#     )  # this limits the x-range displayed,view full range before cutting down
#     mpl.ylabel("Intensity (W/nm/sr)", fontsize=20)
#     mpl.minorticks_on()
#     mpl.grid(True, which="major", color="0.5")
#     mpl.grid(True, which="minor", color="0.8")
# mpl.tick_params(axis="both", labelsize=14)
# mpl.savefig(os.path.join(processdirectory, sample + "_spec.png"), dpi=500)
# np.savetxt(
#     os.path.join(processdirectory, sample + "_specdatafull.txt"),
#     intensitydata.T,
#     fmt="%.6f",
#     delimiter="\t",
#     header="\n".join(header_lines2),
#     comments="",
# )
# s = open(os.path.join(processdirectory, sample + "_specdata.txt"), "w")
# for w in wavelength:
#     s.write(str(w))
#     s.write(" ")
# s.write("\n")
# for i in normintensities:
#     s.write(str(i))
#     s.write(" ")
# s.close()
# s = open(os.path.join(processdirectory, sample + "_specdata.txt"), "r")
# s.close()

# # Plotting Lambertian emission against Actual Emission
# mpl.figure(n + 3, figsize=(10, 8))
# mpl.plot(angles[5:-3], Inonlam[5:-3], linewidth=1.0, label="Actual Emission")  # Actual
# mpl.plot(
#     angles[5:-3], Inonlam_v[5:-3], linewidth=1.0, label="Actual Emission_v"
# )  # Actual
# mpl.plot(
#     angles[5:-3], Ilam[5:-3], linewidth=1.0, label="Lambertian Emission"
# )  # Lambertian
# mpl.title("Lambertian Emission vs Actual Emission\n", fontsize=20)
# mpl.xlabel("Angle (degrees)", fontsize=20)
# mpl.ylabel("Intensity (a.u.)", fontsize=20)
# mpl.legend(loc="upper right", fontsize=14)
# mpl.tick_params(axis="both", labelsize=14)
# mpl.xlim(-90, 90)
# mpl.savefig(os.path.join(processdirectory, sample + "_lam.png"), dpi=500)
# np.savetxt(
#     os.path.join(processdirectory, sample + "_lamdata.txt"),
#     lamdata.T,
#     fmt="%.2f %.4f %.4f %.4f",
#     delimiter="\t",
#     header="\n".join(header_lines3),
#     comments="",
# )

# # IVL Graph
# mpl.figure(n + 4, figsize=(10, 8))
# mpl.title("IVL Characteristics\n", fontsize=20)
# fig, ax1 = mpl.subplots(figsize=(10, 8))
# ax1.semilogy(
#     OLEDvoltage, dataeff_LAM[3], "b", linewidth=1.0, label="Current Density"
# )  # Lambertian
# ax1.set_ylabel("Current Density (mA/cm$^2$)", color="b", fontsize=20)
# ax1.set_xlabel("Voltage (V)", fontsize=20)
# ax1.set_xlim(0, 4)
# ax1.set_ylim(10e-7, 10e2)
# ax2 = ax1.twinx()
# ax2.semilogy(
#     OLEDvoltage, dataeff_LAM[4], "r-", linewidth=1.0, label="Lambertian Lum"
# )  # Lambertian
# ax2.set_ylabel("Luminance (cd/m$^2$)", color="r", fontsize=20)
# ax2.set_ylim(10e-1, 10e4)
# ax1.legend(loc="upper left", fontsize=14)
# ax2.legend(loc="upper right", fontsize=14)
# ax1.tick_params(axis="both", labelsize=14)
# ax2.tick_params(axis="both", labelsize=14)
# mpl.savefig(os.path.join(processdirectory, sample + "_ivl.png"), dpi=500)

# # EQE Graph
# mpl.figure(n + 5, figsize=(10, 8))
# mpl.title("EQE and LE\n", fontsize=20)
# fig, ax1 = mpl.subplots(figsize=(10, 8))
# ax1.semilogx(
#     dataeff_NONLAM[4], dataeff_NONLAM[5], "b", linewidth=1.0, label="Actual EQE"
# )  # Actual
# ax1.semilogx(
#     dataeff_LAM[4],
#     dataeff_LAM[5],
#     "b-",
#     dashes=[6, 2],
#     linewidth=1.0,
#     label="Lambertian EQE",
# )  # Lambertian
# ax1.set_ylabel("EQE (%)", color="b", fontsize=20)
# ax1.set_xlabel("Luminance (cd/m$^2$)", fontsize=20)
# ax1.set_xlim(10e0, 10e3)
# ax2 = ax1.twinx()
# ax2.semilogx(
#     dataeff_NONLAM[4], dataeff_NONLAM[6], "r", linewidth=1.0, label="Actual LE"
# )  # Actual
# ax2.semilogx(
#     dataeff_LAM[4],
#     dataeff_LAM[6],
#     "r-",
#     dashes=[6, 2],
#     linewidth=1.0,
#     label="Lambertian LE",
# )  # Lambertian
# ax2.set_ylabel("Luminous Efficiency (lm/W)", color="r", fontsize=20)
# ax1.legend(loc="upper left", fontsize=14)
# ax2.legend(loc="upper right", fontsize=14)
# ax1.tick_params(axis="both", labelsize=14)
# ax2.tick_params(axis="both", labelsize=14)
# mpl.savefig(os.path.join(processdirectory, sample + "_eqe.png"), dpi=500)

# # Densities Graph
# mpl.figure(n + 6, figsize=(10, 8))
# fig, ax1 = mpl.subplots(figsize=(10, 8))
# ax1.plot(dataeff_LAM[3], dataeff_LAM[7], "b", linewidth=1.0, label="CE")  # Lambertian
# ax1.set_ylabel("Current Efficiency (cd/A)", color="b", fontsize=20)
# ax1.set_xlabel("Current Density (mA/cm$^2$)", fontsize=20)
# ax2 = ax1.twinx()
# ax2.plot(
#     dataeff_NONLAM[3], dataeff_NONLAM[8], "r", linewidth=1.0, label="Actual PD"
# )  # Actual
# ax2.plot(
#     dataeff_LAM[3],
#     dataeff_LAM[8],
#     "r-",
#     dashes=[6, 2],
#     linewidth=1.0,
#     label="Lambertian PD",
# )  # Lambertian
# ax2.set_ylabel("Power Density (mW/mm$^2$)", color="r", fontsize=20)
# ax1.legend(loc="upper left", fontsize=14)
# ax2.legend(loc="upper right", fontsize=14)
# ax1.tick_params(axis="both", labelsize=14)
# ax2.tick_params(axis="both", labelsize=14)
# mpl.savefig(os.path.join(processdirectory, sample + "_density.png"), dpi=500)

# # Saving efficiency data
# np.savetxt(
#     os.path.join(processdirectory, sample + "_effdata_NONLAM.txt"),
#     dataeff_NONLAM.T,
#     fmt="{: ^8}".format("%.6e"),
#     header="\n".join(header_lines),
#     comments="",
# )
# np.savetxt(
#     os.path.join(processdirectory, sample + "_effdata_LAM.txt"),
#     dataeff_LAM.T,
#     fmt="{: ^8}".format("%.6e"),
#     header="\n".join(header_lines),
#     comments="",
# )

# print("FINISHED.")

################################################################################


# """
# Define Functions for calculations
# """


# def calculate_cie_coordinates(df_corrected_spectrum, df_norm_curves):
#     """
#     Calculates wavelength of maximum spectral intensity and the CIE color coordinates
#     """
#     for i, j in enumerate(df_corrected_spectrum.interpolated_intensity):
#         if j == max(df_corrected_spectrum.interpolated_intensity):
#             max_intensity_wavelength = df_corrected_spectrum.wavelength[i]

#     X = sum(df_corrected_spectrum.corrected_intensity * df_norm_curves.xcie)
#     Y = sum(df_corrected_spectrum.corrected_intensity * df_norm_curves.ycie)
#     Z = sum(df_corrected_spectrum.corrected_intensity * df_norm_curves.zcie)

#     CIE = np.array([X / (X + Y + Z), Y / (X + Y + Z)])
#     # CIE[0] = X / (X + Y + Z)
#     # CIE[1] = Y / (X + Y + Z)
#     return (
#         max_intensity_wavelength,
#         ("(" + ", ".join(["%.3f"] * 2) + ")") % tuple(CIE),
#     )


# def calculate_eqe(
#     df_corrected_spectrum, df_jvl_data, df_basic_data, measurement_parameters
# ):
#     """
#     Calculate external quantum efficiency
#     """
#     # calculate average quantum efficiency of the detector
#     detector_quantum_efficiency = (
#         sc.h
#         * sc.sc.c
#         / sc.sc.e
#         * np.sum(
#             df_corrected_spectrum.corrected_intensity
#             * df_basic_data.photodiode_sensitivity
#             / df_basic_data.wavelength
#         )
#         / np.sum(df_corrected_spectrum.corrected_intensity)
#         * 1e9
#     )
#     eqe = np.zeros(len(df_jvl_data.pd_voltage))
#     for v in range(len(df_jvl_data.pd_voltage)):
#         # eqe is only calculated if the photodiode detects a reasonable response
#         if df_jvl_data.pd_voltage[v] > 0.00005:
#             eqe[v] = (
#                 100
#                 * df_jvl_data.pd_voltage[v]
#                 / measurement_parameters["pd_resistance"]
#                 / measurement_parameters["sq_sin_alpha"]
#                 / df_jvl_data.current[v]
#                 / detector_quantum_efficiency
#             )  # calculate eqe in %

#     return eqe


# def calculate_luminance(
#     df_corrected_spectrum, df_jvl_data, df_basic_data, measurement_parameters
# ):
#     """
#     Calculate luminance
#     """
#     # A/lm; photopic response
#     photopic_response = (
#         np.sum(
#             df_corrected_spectrum.corrected_intensity
#             * df_basic_data.photodiode_sensitivity
#             / df_basic_data.wavelength
#         )
#         / np.sum(
#             df_basic_data.v_lambda
#             * df_corrected_spectrum.corrected_intensity
#             / df_basic_data.wavelength
#         )
#         / measurement_parameters["pd_peak_response"]
#     )
#     luminance = np.zeros(len(df_jvl_data.pd_voltage))
#     for v in range(len(df_jvl_data.pd_voltage)):
#         # luminance is only calculated if the photodiode detects a reasonable response
#         if df_jvl_data.pd_voltage[v] > measurement_parameters["threshold_pd_voltage"]:
#             luminance[v] = (
#                 1
#                 / math.pi
#                 / measurement_parameters["sq_sin_alpha"]
#                 / photopic_response
#                 * df_jvl_data.pd_voltage[v]
#                 / measurement_parameters["pd_resistance"]
#                 / (measurement_parameters["pixel_area"] * 1e-6)
#             )  # cd/m2; luminace

#     return photopic_response, luminance


# def calculate_luminous_efficacy(df_jvl_data, photopic_response, measurement_parameters):
#     """
#     Calculate luminous efficacy
#     """
#     luminous_efficacy = np.zeros(len(df_jvl_data.pd_voltage))
#     for v in range(len(df_jvl_data.pd_voltage)):
#         # luminous_efficacy is only calculated if the photodiode detects a reasonable response
#         if df_jvl_data.pd_voltage[v] > measurement_parameters["threshold_pd_voltage"]:
#             luminous_efficacy[v] = (
#                 1
#                 / measurement_parameters["sq_sin_alpha"]
#                 / photopic_response
#                 * df_jvl_data.pd_voltage[v]
#                 / measurement_parameters["pd_resistance"]
#                 / df_jvl_data.voltage[v]
#                 / df_jvl_data.current[v]
#             )  # lm/W; luminous efficacy
#     return luminous_efficacy


# def calculate_current_efficiency(df_jvl_data, measurement_parameters):
#     """
#     Calculate current efficiency
#     """
#     current_efficiency = np.zeros(len(df_jvl_data.pd_voltage))
#     for v in range(len(df_jvl_data.pd_voltage)):
#         # current_efficiency is only calculated if the photodiode detects a reasonable response
#         if df_jvl_data.pd_voltage[v] > measurement_parameters["threshold_pd_voltage"]:
#             # cd/A; current efficiency
#             current_efficiency[v] = (
#                 df_jvl_data.luminance[v]
#                 * (measurement_parameters["pixel_area"] * 1e-6)
#                 / df_jvl_data.current[v]
#             )
#     return current_efficiency


# def calculate_power_density(
#     df_corrected_spectrum, df_jvl_data, df_basic_data, measurement_parameters
# ):
#     """
#     Calculate power density
#     """
#     Rfl = np.sum(
#         df_corrected_spectrum.corrected_intensity
#         * df_basic_data.photodiode_sensitivity
#         / df_basic_data.wavelength
#     ) / np.sum(df_corrected_spectrum.corrected_intensity / df_basic_data.wavelength)
#     power_density = np.zeros(len(df_jvl_data.pd_voltage))
#     for v in range(len(df_jvl_data.pd_voltage)):
#         if df_jvl_data.pd_voltage[v] > measurement_parameters["threshold_pd_voltage"]:
#             power_density[v] = (
#                 1
#                 / measurement_parameters["sq_sin_alpha"]
#                 / Rfl
#                 * df_jvl_data.pd_voltage[v]
#                 / measurement_parameters["pd_resistance"]
#                 / measurement_parameters["pixel_area"]
#                 * 1e3
#             )  # mW/mm2; Power density (Radiant Flux density)
#     return power_density


# def moving_average(interval, window_size):
#     """
#     Smoothing function
#     """
#     window = np.ones(int(window_size)) / float(window_size)
#     return np.convolve(interval, window, "same")


# def calculate_angle_correction(
#     angle_resolved_spectrum_df,
#     calibration,
#     perp_intensity,
#     df_basic_data,
#     df_norm_curves,
# ):
#     """
#     Function to calculate the correction factor in the case of angular
#     resolved emission spectra
#     """

#     # Temporal dataframe that drops the columns that might hinder calculations
#     # with background subtracted and calibration multiplied
#     temp_df = (
#         angle_resolved_spectrum_df.drop(
#             ["background", "wavelength", "0_deg"], axis=1
#         ).subtract(angle_resolved_spectrum_df["background"], axis=0)
#         * calibration
#     )

#     # Smoothen the data
#     temp_df = temp_df.apply(moving_average, args=(10,), axis=0)

#     # Determine the measurement parameters from the dataframe column names
#     minimum_angle = float(np.min(temp_df.columns))
#     maximum_angle = float(np.max(temp_df.columns))
#     step_angle = float(temp_df.columns[1]) - float(temp_df.columns[0])

#     perp_intensity = df_corrected_spectrum.corrected_intensity

#     # E-factor
#     e_factor = np.sum(
#         temp_df * angle_resolved_spectrum_df["wavelength"], axis=0
#     ) / np.sum(perp_intensity * angle_resolved_spectrum_df["wavelength"], axis=0)

#     e_correction_factor = np.sum(
#         e_factor
#         * np.sin(np.deg2rad(np.arange(minimum_angle, maximum_angle, step_angle)))
#         * np.deg2rad(step_angle)
#     )

#     # V-factor
#     v_factor = np.sum(temp_df * df_basic_data.v_lambda) / np.sum(
#         perp_intensity * df_basic_data.v_lambda
#     )

#     v_correction_factor = np.sum(
#         v_factor
#         * np.sin(np.deg2rad(np.arange(minimum_angle, maximum_angle, step_angle)))
#         * np.deg2rad(step_angle)
#     )

#     return e_correction_factor, v_correction_factor


# def generate_output_files(
#     df_jvl_data,
#     df_corrected_spectrum,
#     luminance,
#     eqe,
#     luminous_efficacy,
#     current_efficiency,
#     power_density,
#     max_intensity_wavelength,
#     cie_color_coordinates,
# ):
#     """
#     Generate Output files
#     """

#     # Make evaluation directory if it does not yet exist
#     if not os.path.exists(root_directory + "eval"):
#         os.makedirs(root_directory + "eval")

#     # Res-file with JVL and efficiencies
#     # Converges the individual arrays into one array
#     dataeff = np.stack(
#         (
#             df_jvl_data.voltage,
#             df_jvl_data.current * 1000,
#             df_jvl_data.current_density * 1000,
#             df_jvl_data.absolute_current_density * 1000,
#             luminance,
#             eqe,
#             luminous_efficacy,
#             current_efficiency,
#             power_density,
#         )
#     )

#     eff01 = (  # header lines
#         "Calculation programme:		OLED-Efficiency-Calculator_vfinal.py"
#     )
#     eff02 = "OLED active pixel_area:		" + str(pixel_area) + " mm2"
#     eff03 = "Distance OLED - Photodiode:	196 mm"
#     eff04 = "Photodiode pixel_area:		75 mm2"
#     eff05 = "Maximum intensity at:		" + str(max_intensity_wavelength) + " nm"
#     eff06 = "CIE coordinates:		" + str(cie_color_coordinates)
#     eff13 = "V	I	J	Abs(J)	L	eqe	luminous_efficacy	current_efficiency	P/A"
#     eff14 = "V	mA	mA/cm2	mA/cm2	cd/m2	%	lm/W	cd/A	mW/mm2"

#     np.savetxt(
#         root_directory + "eval/Eff_" + file_name,
#         dataeff.T,
#         fmt="%.2f %.4e %.4e %.4e %.2f %.2f %.2f %.2f %.4e",
#         delimiter="\t",
#         header="\n".join([eff01, eff02, eff03, eff04, eff05, eff06, eff13, eff14]),
#         comments="",
#     )

#     # Spectrum file with normalized, df_background subtracted df_spectrum and full wavelength range as detected by the camera

#     # dataspec = np.stack((specwl,rawspecback/max(rawspecback)))  # Converges the individual arrays into one array
#     normspectra = np.array(df_corrected_spectrum.spectrum_m_background) / np.amax(
#         np.array(df_corrected_spectrum.spectrum_m_background)
#     )
#     dataspec = np.vstack((df_basic_data.wavelength, normspectra))

#     spec01 = (  # header lines
#         "Calculation programme:		OLED-Efficiency-Calculator_vfinal.py"
#     )
#     spec02 = "OLED active pixel_area:		" + str(pixel_area) + " mm2"
#     spec03 = "Maximum intensity at:		" + str(max_intensity_wavelength) + " nm"
#     spec04 = "CIE coordinates:		" + str(cie_color_coordinates)
#     spec13 = "Wavelength	Spectrum"
#     spec14 = "nm	a.u."

#     np.savetxt(
#         root_directory + "eval/Spec_" + file_name,
#         dataspec.T,
#         fmt="%.2f %.4f",
#         delimiter="\t",
#         header="\n".join([spec01, spec02, spec03, spec04, spec13, spec14]),
#         comments="",
#     )
