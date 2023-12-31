#!/usr/bin/env python3
from icecube.icetray import I3Units
from icecube.taxi_reader import taxi_tools
from I3Tray import I3Tray
from icecube import icetray, dataio, dataclasses, taxi_reader, radcube
from icecube.icetray.i3logging import log_info
import matplotlib.gridspec as gridspec
from datetime import datetime
from icecube.icetray.i3logging import log_warn, log_info, log_fatal

import os
import matplotlib.pyplot as plt
import numpy as np
import sys
import argparse

#Input i3 file with the data 
parser = argparse.ArgumentParser()
parser.add_argument("input", type=str, nargs="+", default=[], help="List of i3 files")
args = parser.parse_args()

filename = args.input


#Subtraces method
def cutTraces(radTrace, lengthSubTraces=64, mode="rms"):
    steps = np.arange(0, len(radTrace), lengthSubTraces)
    nbSubTraces = len(radTrace) / lengthSubTraces
    temp = []
    for i in range(int(nbSubTraces)-1):
        chopped = radTrace.GetSubset(int(steps[i]), int(steps[i + 1]))
        temp.append(radcube.GetRMS(chopped))
        temp.sort()
    return temp

#This class uses the subtraces method to obtain the RMS values in each antenna and channel, and stores them in a .npz file
class GalacticBackground(icetray.I3Module):
    def __init__(self, ctx):
        icetray.I3Module.__init__(self, ctx)
        self.AddParameter('InputName', 'InputName', "InputName")
        self.AddParameter('Output', 'Output', "Output")
        self.AddParameter("ApplyInDAQ", "ApplyInDAQ", False)
    
    def Configure(self):
        self.inputName = self.GetParameter('InputName')
        self.output = self.GetParameter('Output')
        self.applyinDAQ = self.GetParameter("ApplyInDAQ")

        self.timeOutput = []
        self.baselineRms = []
        
        print("... I am starting")

    def RunForOneFrame(self, frame):
        time = frame["RadioTaxiTime"]
        time_new = np.datetime64(time.date_time).astype(datetime)
        self.timeOutput.append(time_new)

        antennaDataMap = frame[self.inputName]
        rmsTraces = []
        for iant, antkey in enumerate(antennaDataMap.keys()):
            channelMap = antennaDataMap[antkey]
            antenna_polarization_data = []
            for ichan, chkey in enumerate(channelMap.keys()):
                fft = channelMap[ichan].GetFFTData()
                timeSeries = fft.GetTimeSeries()
                noises = cutTraces(timeSeries, lengthSubTraces=64)
                rms_value = np.mean(noises[:10]) 
                self.baselineRms.append(rms_value)
                
 
    def DAQ(self, frame):
        if self.applyinDAQ:
            self.RunForOneFrame(frame)
            
    def Physics(self, frame):
        if not self.applyinDAQ:
            self.RunForOneFrame(frame)
            
    def Finish(self):
        timeOutput = np.asarray(self.timeOutput)
        baselineRms = np.asarray(self.baselineRms)
        # Reshape baselineRms to have dimensions (self.counts, 3, 2)
        baselineRms_reshaped = baselineRms.reshape(-1, 3, 2)
        # Save the data
        np.savez(self.output,
                 time=timeOutput,
                 # Extract data for each antenna and polarization
                 rms10 = baselineRms_reshaped[:, 0, 0],
                 rms11 = baselineRms_reshaped[:, 0, 1],
                 rms20 = baselineRms_reshaped[:, 1, 0],
                 rms21 = baselineRms_reshaped[:, 1, 1],
                 rms30 = baselineRms_reshaped[:, 2, 0],
                 rms31 = baselineRms_reshaped[:, 2, 1]
                 )

tray = I3Tray()

tray.AddModule("I3Reader", "reader",
         FilenameList = filename) 

#Choosing soft trigger only 
def select_soft(frame):
    trigger_info = frame['SurfaceFilters']
    return trigger_info["soft_flag"].condition_passed

# add the module to the tray
tray.Add(select_soft, "select_soft",
         streams=[icetray.I3Frame.DAQ])

#Select data with trace length different than 0
def select_TraceLength(frame):
    TraceLength = frame['RadioTraceLength'].value

    if TraceLength == 1024:
        return True  # This will indicate that the frame should be saved to the selected stream
    else:
        return False  
    
#add the module to the tray
tray.Add(select_TraceLength, "select_TraceLength",
         streams=[icetray.I3Frame.DAQ])


#Removing TAXI artifacts 
tray.Add(
    radcube.modules.RemoveTAXIArtifacts, "ArtifactRemover",
    InputName="RadioTAXIWaveform",
    OutputName="ArtifactsRemoved",
    medianOverCascades=True,
    RemoveBinSpikes=True,
    BinSpikeDeviance=int(2**12),
    RemoveNegativeBins=True
    )

tray.AddModule("I3NullSplitter","splitter",
               SubEventStreamName="RadioEvent"
               )

tray.AddModule("MedianFrequencyFilter", "MedianFilter",
            InputName="ArtifactsRemoved",
            FilterWindowWidth=20,
            OutputName="MedFilteredMap")

# let's apply a bandpass filter to our signals
tray.AddModule("BandpassFilter", "filter",
               InputName="MedFilteredMap",
               OutputName="FilteredMap",
               ApplyInDAQ=False,
               FilterType=radcube.eButterworth,
               ButterworthOrder=13,
               #FilterType=radcube.eBox,
               FilterLimits=[140*I3Units.megahertz, 190*I3Units.megahertz] 
               )

tray.AddModule(GalacticBackground, "TheGalaxyObserverDeconvolved",
               InputName="FilteredMap",
               Output="GalOscillation_Deconvolved_140-190_New.npz"
               )

tray.Execute()

