# Galactic Noise Analysis
This repository focuses on analyzing signal data collected by the antennas of the IceCube prototype station, located at the Pierre Auger Observatory in Argentina, with the specific objective of observing galactic radio emission and its modulation. For data processing, the IceTray framework of the IceCube Neutrino Observatory project is employed.

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

## Others Files 

Descripción de su proyecto;
funcionalidades;
Cómo pueden usarlo los usuarios;
Donde los usuarios pueden encontrar ayuda sobre su proyecto;
Autores del proyecto.
