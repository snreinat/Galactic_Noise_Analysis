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

from astropy.visualization import astropy_mpl_style, quantity_support
plt.style.use(astropy_mpl_style)
quantity_support()

import astropy.units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, Angle

import matplotlib.pyplot as plt


year1 = "2023"
year2 = "2023"
#inputName ="/data/user/rturcotte/analysis/background/comparisonDAQs/GalOscillation_Deconvolved_2020.npz"
inputName = "/home/storres/work/GalacticNoiseAnalysis/GalOscillation_Deconvolved_110-130.npz"

# This class reads the NPZ file with the RMS values and creates a DataFrame, then 
# it cleans the data and calculates a moving average to finally fits a sinusoidal function.
class BackgroundOscillation():
    
    def __init__(self, filename):
        self.time = []
        self.rms = []
        self.ant = 3
        self.pol = 2
        self.window = 150
        self.df = pd.DataFrame()
        self.readNpz(filename)
        print("reading the data ... from ", filename)
        
    def readNpz(self, filename):
        data = np.load(filename, allow_pickle=True)
        self.time = data["time"]
        self.rms = np.array([
            data["rms10"],
            data["rms11"],
            data["rms20"],
            data["rms21"],
            data["rms30"],
            data["rms31"]])

    # proessData calls the toPandas method to convert the data into a Pandas DataFrame format.
    # Then calls the movingAverage method to calculate moving averages.
    def processData(self):
        self.toPandas()
        self.cleanData() 
        self.movingAverage()
        print("processing the data...")

    def setWindow(self, value):
        self.window = value

    # Function toPandas converts the loaded data into a structured Pandas DataFrame.
    def toPandas(self):
        self.df["time"] = self.time
        for iant in range(self.ant):
            for ich in range(self.pol):
                idx = "rms{0}{1}".format(1+iant, ich)
                self.df[idx] = self.rms[2*iant + ich]
                
    # This method is responsible for cleaning the data by removing outliers or erroneous values.
    # The method takes an optional argument n and calculates a threshold value by adding n to
    # the minimum RMS.
    def cleanData(self, n=17):
        for iant in range(self.ant):
            for ich in range(self.pol):
                idx = "rms{0}{1}".format(1+iant, ich)
                self.df = self.df[self.df[idx] <= np.min(self.df[idx]) + n]
    
    # MovingAverage calculates the moving average of RMS values using the rolling method of Pandas DataFrames.
    # The calculated moving averages are stored in new columns named "average{ant}{pol}".
    def movingAverage(self):
        for iant in range(self.ant):
            for ich in range(self.pol):
                idx = "{0}{1}".format(1+iant, ich)
                self.df["average"+idx] = self.df["rms"+idx].rolling(self.window).mean()
                
    
    def setTimeWindow(self, startTime, endTime):
        self.startTime = startTime
        self.endTime = endTime
        self.df = self.df.sort_values("time", axis=0, ascending=True)
        self.df = self.df.loc[self.df['time'] > startTime]
        self.df = self.df.loc[self.df['time'] < endTime]
        

    def fitSinus(self, time, rms):
        t = np.array([val.timestamp() for val in time])
        
        # Initial Parameters
        guess_mean = 0
        guess_std = np.std(rms)
        guess_phase = 0
        guess_amp = guess_std / np.sqrt(2)
        freq = 0.00001160576 #sidereal frequency = 1/{(23h*60min*60s)+(56min*60s)+4,0916s}
        
        guess_std2 = np.std(rms)
        guess_phase2 = 0.5
        guess_amp2 = 0.001
        freq2 = 0.00001157407 #solar frequency = 1/(24h*60min*60s)

        def sinusoidal_func(t, amp, phase, amp2, phase2, mean):
            return amp * np.sin(2 * np.pi * freq * t + phase) + amp2 * np.sin(2 * np.pi * freq2 * t + phase2) + mean


        # Parameter estimation using curve fit
        initial_guess = [guess_amp, guess_phase, guess_amp2, guess_phase2, guess_mean]
        popt, pcov = curve_fit(sinusoidal_func, t, rms, p0=initial_guess)

        # Deviation standart of the parameters
        perr = np.sqrt(np.diag(pcov))

        est_amp, est_phase, est_amp2, est_phase2, est_mean = popt
        est_amp_err, est_phase_err, est_amp2_err, est_phase2_err, est_mean_err= perr

        # Recreate the fitted curve using the optimized parameters
        data_fit = sinusoidal_func(t, est_amp, est_phase, est_amp2, est_phase2, est_mean)

        print("Estimated Parameters:")
        print("Amplitude 1: {0} +/- {1}".format(est_amp, est_amp_err))
        print("Phase 1: {0} +/- {1}".format(est_phase, est_phase_err))
        print("Mean: {0} +/- {1}".format(est_mean, est_mean_err))
        print("Amplitude 2: {0} +/- {1}".format(est_amp2, est_amp2_err))
        print("Phase 2: {0} +/- {1}".format(est_phase2, est_phase2_err))

        return data_fit
    

    def plotSinusFit(self, ax, time, data_fit, **kwargs):
        ax.plot_date(time, data_fit, **kwargs)
        
    def plotOnePol(self, ax, iant, ich):
        color = ["c", "y"]
        color2 = ["tab:orange", "tab:blue"]
        idx = "{0}{1}".format(1+iant, ich)
        
        # Centered the data 
        averageRms = self.df["average"+idx] - np.mean(self.df["average"+idx])
        time = self.df["time"]
        rms_centered = self.df["rms"+idx] - np.mean(self.df["rms"+idx])
        
        # Ploting the data 
        ax.plot_date(time, rms_centered, marker=",", c=color[ich], alpha=0.1, label="Ant. {0}, Pol. {1}".format(1+iant, ich))
        ax.plot_date(time, averageRms, marker=",", c=color2[ich], alpha=0.5, label="Moving average")
        print("Ant. {0}, Pol. {1}".format(1+iant, ich))
        data_fit = self.fitSinus(time, averageRms)
        self.plotSinusFit(ax, time, data_fit, ls="--", lw=2, marker="", label='sinus fitting rms', color="k")
       
        # Calculate the squared differences between original and fitted data
        squared_diff = (averageRms - data_fit) ** 2
        # Calculate the Mean Squared Error (MSE)
        mse = np.mean(squared_diff)

        print("Mean Squared Error:", mse)
       
        
    def plotAll(self):
        fig = plt.figure(figsize=[20, 15])
        spec = gridspec.GridSpec(ncols=1, nrows=3)
        for iant in range(self.ant):
            ax = fig.add_subplot(spec[iant])
            for ich in range(self.pol):
                self.plotOnePol(ax, iant, ich)
            ax.set_ylabel("RMS")
            plt.legend(loc="upper right")
            plt.setp(ax.get_xticklabels(), visible=True)
        plt.tight_layout()

bg = BackgroundOscillation(inputName)
startTime = '{0}-04-05'.format(year1)
endTime = '{0}-04-15'.format(year2)

bg.processData()
bg.setTimeWindow(startTime=startTime, endTime=endTime)
bg.plotAll()
plt.savefig("/home/storres/work/GalacticNoiseAnalysis/May.png")
plt.close()

