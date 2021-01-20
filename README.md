# OLED-evaluation

Software for easy evaluation of previously measured data in the data format of https://github.com/GatherLab/OLED-jvl-measurement

## User Journey

- User starts the program and sees a window with a matplotlib graph place holder in the middle and two tabs. One for the autotube evaluation and the other one for the goniometer
- On the menubar to the right, the user can press on the "Select Folder" button and select from a File dialog a folder this is the same dialog for both different tabs.
- When the user selected a folder that shall be evaluated, the programm automatically detects the right files that match the selected evaluation (by file endings that are defined by the measurement program)

### Autotube Evaluation

- This can be very similar to what I did during my Master's. The user can now press on the second button on the right menu bar that only now is enabled. A Pop-up dialog opens up and now the user can name different groups and assign each group their pixels as well as each group or pixel its correct spectrum. I do not know how I want to do the spectrum selection at this moment but it would be interesting to talk to Sabina about the best way here (one spectrum per device I believe). This could be done with the assignement of the groups as well if it is only one spectrum per group.
- The third button directly yields box plots of key parameters (e.g. average or key EQE, maximum Luminance etc.) of the different groups to get an overview how they compare to each other without doing much.
- The fourth button plots in the main graph window the four relevant graphs of standard OLED characterisation: 1. J-V-L curve, 2. EQE vs current density, 3. power over voltage and 4. spectrum. It shall only show the graphs for a single pixel and the user shall be able to click through them. There might be a point in doing this in groups as well but I am not sure about that at the moment. It could possibly make sense to mark the crappy pixels that didn't work at all at least to exclude them from the statistics. Maybe also for something else.
- The fifth button enables to export the evaluated data (the four graphs basically) of the currently visible pixel so that it can later be easily plotted with origin or another program that facilitates makeing nice-looking graphs.

### Goniometer Evaluation

- I have to go through the program here and mainly need input from the others. Maybe it makes sense to go for the autotube evaluation first. Also maybe it makes sense to team up with someone (2 x 500 lines files is not too bad but as for now, I have never used this script before).

## Initial Design Choices

- The calibration files are in the programs folder. On the long run, they must be selected within the GUI but for the beginning they can just sit in one of the program folders.
- The calculation logic should be strictly kept in seperate functions (maybe classes but currently I don't see any point of having classes here) so that it can also be integrated directly into the measurement program.
- The settings for the batch (e.g. photodiode gain, measurement distance etc.) can be kept in a seperate settings top menubar option. Some default parameters for this shall be provided and the costum ones saved in the folder where the data is in a seperate evaluation folder for reference.
