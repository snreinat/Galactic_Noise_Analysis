#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.dates
from datetime import datetime
import pandas as pd
from scipy.optimize import leastsq
from scipy.optimize import curve_fit
from icecube.icetray import I3Units
from datetime import datetime

from astropy.visualization import astropy_mpl_style, quantity_support
plt.style.use(astropy_mpl_style)
quantity_support()

import astropy.units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, Angle

import matplotlib.pyplot as plt
import argparse

#Input i3 file with the data 
parser = argparse.ArgumentParser()
parser.add_argument("input", type=str, help="Name of .npz file")
args = parser.parse_args()

filename = args.input

data = np.load(filename, allow_pickle=True)

# Get the data arrays
time = data['time']
rms10 = data['rms10']
rms11 = data['rms11']
rms20 = data['rms20']
rms21 = data['rms21']
rms30 = data['rms30']
rms31 = data['rms31']


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

# Get the indices of datetime objects for the target days
filtered_indices = [index for index, dt in enumerate(time) if dt.date() in [day.date() for day in target_days]]

time_filtered = time[filtered_indices]
rms10_filtered = rms10[filtered_indices]
rms11_filtered = rms11[filtered_indices]
rms20_filtered = rms20[filtered_indices]
rms21_filtered = rms21[filtered_indices]
rms30_filtered = rms30[filtered_indices]
rms31_filtered = rms31[filtered_indices]


plt.figure(figsize=(20, 15))

# Subplot 1: rms10 y rms11
plt.subplot(3, 1, 1)
plt.plot(time_filtered, rms10_filtered, '.', markersize=1, color='tab:green', label='Channel 1', alpha=0.5)
plt.plot(time_filtered, rms11_filtered, '.', markersize=1, color='tab:blue', label='Channel 2', alpha=0.5)
#plt.xlabel('Time')
plt.ylabel('RMS')
#plt.ylim(0, 20)
plt.title('Antenna 1')
plt.legend()
plt.grid(True)

# Subplot 2: rms20 y rms21
plt.subplot(3, 1, 2)
plt.plot(time_filtered, rms20_filtered, '.', markersize=1, color='tab:green', label='Channel 1', alpha=0.5)
plt.plot(time_filtered, rms21_filtered, '.', markersize=1, color='tab:blue', label='Channel 2', alpha=0.5)
plt.xlabel('Time')
plt.ylabel('RMS')
#plt.ylim(0, 20)
plt.title('Antenna 2')
plt.legend()
plt.grid(True)


# Subplot 3: rms30 y rms31
plt.subplot(3, 1, 3)
plt.plot(time_filtered, rms30_filtered, '.', markersize=1, color='tab:green', label='Channel 1', alpha=0.5)
plt.plot(time_filtered, rms31_filtered, '.', markersize=1, color='tab:blue', label='Channel 2', alpha=0.5)
plt.xlabel('Time')
plt.ylabel('RMS')
#plt.ylim(0, 20)
plt.title('Antenna 3')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.savefig('AugeDataRMS.png')

