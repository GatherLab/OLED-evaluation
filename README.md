# OLED-evaluation

Software for easy evaluation of previously measured data in the data format of https://github.com/GatherLab/OLED-jvl-measurement

## User Journey

- The user starts with the usual interface that she knows from other gatherlab programs
- The scrollbar on the right is now used as a guide through the program with different options available that should normally be executed in order

1. At the beginning only the top button that is to select a folder where the data files are contained. If a folder was selected, all file names at top level (not in the subfolders of this folder) are read in
   - The files that are read in must obey the file naming convention that is defined by the measurement program, thus

```terminal
<date>_<batch_name>_d<device_no>_p<pixel_no>(_<scan_no>).csv
```

    where the scan number is only set if multiple scans for the same device and pixel exist
    - If the file names are correct and in theory the files should be able to be read in, more buttons on the right can now be clicked.

2. The second button opens a dialog that allows assignment of all available devices to different groups. This is important to ensure ordering of the devices and to obtain statistics for different OLEDs. Since it is usually good practice to have several devices of the same kind.
   - The user can now select which scan she wants to use, in case devices were scanned several times. This is done with a dropdown menu. The maximum value in the dropdown is given by the maximum scan number found in the file names.
   - Furthermore, the user can use a slider to define how many groups she wants to define. The maximum value of the slider is the number of different devices detected from the file names. The value of the slider determines the number of lines below where the user defines the groups.
   - A group definition comprises a group name that briefly explains what the group is, all device numbers that belong to the group, a spectrum file and a color associated with the group.
   - The group name can be entered in a text field
   - The group numbers as well. This is to maintain simplicity and an easy to use interface. Different device numbers are seperated by a comma.
   - A spectrum file can be selected by clicking on a button that allows the user to browse the hard drive and select files with .csv or .txt ending. The spectrum file also has to obey the conventions set by the measurement program for spectrum files, especially when it comes to file structure (columns for wavelength, background & intensity). Otherwise, the user should be able to select a full goniometer spectrum file with which a correction factor for the emission can be calculated. This shall be done seamlessly and the program shall automatically decide if the input is a full angle resolved spectrum or a simple spectrum.
   - The color is optional but might be used for plotting later on and can be selected from a colorpicker
   - On saving the groups all parameters are saved in a dataframe and hand over to the main window. Furthermore, if angle resolved spectra are selected, the correction factor shall be calculated and printed to the terminal for each group (print the entire dataframe).
   - On saving the data of all selected devices shall be read in (in a single dataframe for simplicity) and all relevant calculations shall be already done here.
3. Now that the groups are assigned, the user shall be able to plot JVL curves for each group or each device depending on the previous definition. This is done with this dialog. The user shall go through all curves and by simply clicking on the legend in the graph he shall be able to unselect a certain device for the statistic calculations later on. Unselected devices' data is also not saved to file later on. An additional button or a right click on a graph shall allow the user to plot all four relevant graphs for the device as subplots in the main plotting area. The user can go back from this view by clicking on plot in the still open dialog.
4. This button is to plot statistics for all selected devices. What the statistics really imply must be defined later on but current density at 4V as well as luminence at 4 V is set. The statistics shall be shown as a boxplot with each data point visible, however.
5. Button 5 is meant for the spectrum analysis and shall allow the user to plot the selected spectra seperately. This shall be done using an additional dialog that shows buttons for the different groups. The way the spectra shall be plotted can be selected (just plot the heatmap for goniometer, the spectra for single spectra, or a angle map).
6. Lastly the user shall be able to save the evaluated data. Each evaluation data is saved to seperate files (for each device, pixel combination). Additionally, a summary file shall be provided were all the important parameters for each pixel are summarised for future reference. From this file it shall be possible to load the status of the evaluation program (defined groups, selected pixels etc) again at a later point of time.

Some important evaluation parameters can be set in a "global setting" style dialog at the top menubar, where also a logging file and the documentation here in this readme file can be selected.

## Initial Design Choices

- The calibration files are in the programs folder. On the long run, they must be selected within the GUI but for the beginning they can just sit in one of the program folders.
- The calculation logic should be strictly kept in seperate functions (maybe classes but currently I don't see any point of having classes here) so that it can also be integrated directly into the measurement program.
- The settings for the batch (e.g. photodiode gain, measurement distance etc.) can be kept in a seperate settings top menubar option. Some default parameters for this shall be provided and the costum ones saved in the folder where the data is in a seperate evaluation folder for reference.
- How to deal with multiple measurements?

## Data Structures

In general data is organised in pandas dataframe in a relational database manner. One key defines the relationship of the dataframe to others. However, the relationship can be 1:n. The primary key is for all dataframes the index that shall allow to relate the dataframes among eachother and is marked with (PM) in the following.

- data_df: Contains the JVl data for all selected devices. The scan in the index should be the same for all of them since this is only after the user selected the relevant scan. Importantly, not all contained lists have the same length. For instance voltage, current and pd_voltage have the same length but 

| index (PM) | device_number | voltage   | current   | current_density | pd_voltage | luminance | eqe      | luminous_efficiency | current_efficiency | power_density |
| ---------- | ------------- | --------- | --------- | --------------- | ---------- | --------- | -------- | ------------------- | ------------------ | ------------- |
| d21p1s1    | 21            | [1,2,3, ] | [2,3,4, ] | [2,3,4, ]       | [5,6,7, ]  | [1, 2, ]  | [1, 2, ] | [1, 2, ]            | [1, 2, ]           | [1, 2, ]      |
| d21p4s1    | 21            | [1,2,3, ] | [2,3,4, ] | [2,3,4, ]       | [5,6,7, ]  | [1, 2, ]  | [1, 2, ] | [1, 2, ]            | [1, 2, ]           | [1, 2, ]      |
| d24p6s1    | 24            | [1,2,3, ] | [2,3,4, ] | [2,3,4, ]       | [5,6,7, ]  | [1, 2, ]  | [1, 2, ] | [1, 2, ]            | [1, 2, ]           | [1, 2, ]      |

- spectrum_data_df: Contains all the spectrum data for the different groups

| index (PM) | wavelength     | background     | intensity      |
| ---------- | -------------- | -------------- | -------------- |
| 21         | [1, 2, 3, ...] | [3, 4, 5, ...] | [6, 7, 8, ...] |
| 24         | [1, 2, 3, ...] | [3, 4, 5, ...] | [6, 7, 8, ...] |
| 31         | [1, 2, 3, ...] | [3, 4, 5, ...] | [6, 7, 8, ...] |
| 34         | [1, 2, 3, ...] | [3, 4, 5, ...] | [6, 7, 8, ...] |
| 41         | [1, 2, 3, ...] | [3, 4, 5, ...] | [6, 7, 8, ...] |
| 44         | [1, 2, 3, ...] | [3, 4, 5, ...] | [6, 7, 8, ...] |

- files_df: Contains the file names and all relevant information extracted from them for all files in the selected folder

| index (PM) | file_name                                          | device_number | pixel_number | scan_number |
| ---------- | -------------------------------------------------- | ------------- | ------------ | ----------- |
| d1p2s1     | "user/documents/data/2021-02-04_test_d1_p2.csv     | 1             | 2            | 1           |
| d1p2s2     | "user/documents/data/2021-02-04_test_d1_p2_02.csv  | 1             | 2            | 2           |
| d2p6s1     | "user/documents/data/2021-02-04_test_d2_p6.csv     | 2             | 6            | 1           |
| d11p5s5    | "user/documents/data/2021-02-04_test_d11_p5_05.csv | 5             | 5            | 5           | d11p5s5 |

- assigned_groups_df: Contains all information that was provided in the assigned groups dialog (except for the scan number)

| index (PM) | group_name | spectrum_path                                         | color   |
| ---------- | ---------- | ----------------------------------------------------- | ------- |
| 21         | Bphen      | "user/documents/data/2021-02-04_test_d21_p2_spec.csv" | #FFFFFF |
| 24         | Bphen      | "user/documents/data/2021-02-04_test_d21_p2_spec.csv" | #FFFFFF |
| 31         | Bphen:Cs   | "user/documents/data/2021-02-04_test_d31_p2_spec.csv" | #FFFFF0 |
| 34         | Bphen:Cs   | "user/documents/data/2021-02-04_test_d31_p2_spec.csv" | #FFFFF0 |
| 41         | Bphen:CsC  | "user/documents/data/2021-02-04_test_d41_p2_spec.csv" | #FFFFF1 |
| 44         | Bphen:CsC  | "user/documents/data/2021-02-04_test_d41_p2_spec.csv" | #FFFFF1 |


- spectrum_data_df and assigned_groups_df have a 1:1 relationship and are only kept seperate for logical reasons but could in principle be merged in a single dataframe.
- files_df and data_df have the same primary key and can be directly related with eachother. However, the primary keys of data_df are a subset of files_df since only the data of selected files is read in by the program and not all present in the folder. Device, pixel and scan number can be easily found out for each row by comparing to the files_df dataframe (join the dataframes basically).
