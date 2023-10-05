# Galactic Noise Analysis

This repository focuses on analyzing signal data collected by the antennas of the IceCube prototype station, located at the Pierre Auger Observatory in Argentina, with the specific objective of observing galactic radio emission and its modulation. For data processing, the IceTray framework of the IceCube Neutrino Observatory project is employed.
Several of the scripts are based on the work done by Roxanne Turcotte-Tardif in Radio Measurements of Cosmic Rays at the South Pole, and her work can be found at  https://github.com/rturcottetardif/backgroundAnalysis 

## Converting Binary Files to I3 Files 
This file was created by Benjamin Flaggs and it makes I3 files from TAXI binaries.
Run with command:
```Bash
./BinToI3File_UsingTAXIScripts.py BIN_FILE_NAME --output OUTPUT_NAME
```
## Average Spectrum 
This script calculates the average spectrum over all the Q frames in the I3 files.
Run with command:
```Bash
./AverageFrames.py I3_FILE_NAME
```
## Histograms for the level of noise 
This script shows the distributions of the noise level in the traces for each antenna and channel using the subtraces method and the standard RMS window.
Run with command:
```Bash
./Histogram.py I3_FILE_NAME
```
## Subtraces Method 
This script uses the subtraces method to obtain the RMS values in each antenna and channel, and stores them in a .npz file
Run with command:
```Bash
./NPZ.py I3_FILE_NAME
```
## Plotting the Noise 
This is a simple script for visualize the noise in each antenna and channel.  
For running it is necesary to modify the dates for the target days: 
```Python
# Define the target days
target_days = [
    datetime(2023, 4, 5),
    datetime(2023, 4, 6),
    datetime(2023, 4, 7),
    datetime(2023, 4, 8),
    datetime(2023, 4, 9),
    datetime(2023, 4, 10),
    datetime(2023, 4, 11),
    datetime(2023, 4, 12),
    datetime(2023, 4, 13),
    datetime(2023, 4, 14),
    datetime(2023, 4, 15)
             ]
```
It uses the NPZ created with the subtraces method. 
Run with command: 
```Bash
./PlottingRMS.py NPZ_FILE_NAME
```
## Sinusoidal Fitting 

This script receives an NPZ file, take the moving average of the RMS data and then fit a sinusoidal function to it. 

$$A_1\sin({2\pi t \over T_{sideral}}+ \phi_1)+ A_2\sin({2\pi t \over T_{solar}}+ \phi_2) + B$$

Essentially, the function includes terms that depend on both the sidereal day and the solar day. When observing galactic noise, it is expected that the sidereal term will predominate, and this period should be visible in the graphs.

This script requires changing the initial date (starTime) and the final date (endTime) to specify the period you want to fit. 

Run with command: 
```Bash
./CurveFit.py NPZ_FILE_NAME
```

## Others Files 

You also can find a presentation with the main results in the file named Presentation.pdf

There is a file called TimeValues.py to get all the dates for the Q frames in the I3 files 


