#!/usr/bin/env python3

from icecube.icetray import I3Units
from icecube.taxi_reader import taxi_tools
from I3Tray import I3Tray
from icecube import icetray, dataio, dataclasses, taxi_reader, radcube
from icecube.icetray.i3logging import log_info
import matplotlib.gridspec as gridspec


import os
import matplotlib.pyplot as plt
import numpy as np
import sys
import argparse


#Input i3 file with the data 
parser = argparse.ArgumentParser()
parser.add_argument("input", type=str, help="Name of .i3.gz file")
args = parser.parse_args()

filename = args.input

#Input i3 file with the data 

#Set the trace length
WaveformLengths = [1024] 

# This class take the spectrum average over all the Q frames 
class AnalyzeQframes(icetray.I3Module):
    def __init__(self, ctx):  
        icetray.I3Module.__init__(self, ctx) 
        self.NEntries = 0
        self.NFreqBins = int(WaveformLengths[0]/ 2 + 1)
        self.plotdBm = np.zeros(self.NFreqBins)
        self.plotFreqs = np.zeros(self.NFreqBins)
        self.channel_averages = {}  # Dictionary to store the average spectrum for each channel

    def SpectrumAverage(self, frame, name):
        antennaDataMap = frame[name]  # This is a container that holds all antenna info
        for iant, antkey in enumerate(antennaDataMap.keys()):
            channelMap = antennaDataMap[antkey]
            for ichan, chkey in enumerate(channelMap.keys()):
                fft = channelMap[chkey].GetFFTData()  # This container holds time series and spectrum
                spectrum = fft.GetFrequencySpectrum()
                freqs, amps = radcube.RadTraceToPythonList(spectrum)
                amps = [radcube.GetDbmHzFromFourierAmplitude(abs(thisAmp), spectrum.binning, 50 * I3Units.ohm) for thisAmp in amps]

                # Use (iant, ichan) as the key to differentiate data for each antenna and channel
                if (iant, ichan) not in self.channel_averages:
                # Create separate lists for each antenna and channel if not present
                    self.channel_averages[(iant, ichan)] = {
                        'sumFreqs': np.zeros(self.NFreqBins),
                        'sumdBm': np.zeros(self.NFreqBins),
                        'NEntries': 0
                    }
                # Sum the frequencies and dBm values for each channel of each antenna
                self.channel_averages[(iant, ichan)]['sumFreqs'] += np.array(freqs)
                self.channel_averages[(iant, ichan)]['sumdBm'] += np.array(amps)
                self.channel_averages[(iant, ichan)]['NEntries'] += 1
        
 
    def Physics(self, frame):
        self.SpectrumAverage(frame, "ArtifactsRemoved")
        
    def Finish(self):
        plt.figure(figsize=(20, 15))
        for iant in range(3):
            for ichan in range(2):
                channel_data = self.channel_averages[(iant, ichan)]
                avg_freqs = channel_data['sumFreqs'] / channel_data['NEntries']
                avg_dBm = channel_data['sumdBm'] / channel_data['NEntries']
                # Create a subplot for the current antenna
                plt.subplot(3, 1, iant+1)
                if ichan == 0:
                    plt.plot(avg_freqs/ I3Units.megahertz, avg_dBm, label=f"Antenna {iant+1}, Channel {ichan+1}", color='steelblue')
                else:
                    plt.plot(avg_freqs/ I3Units.megahertz, avg_dBm, label=f"Antenna {iant+1}, Channel {ichan+1}", color='indianred')
                   
                plt.xlim(0, np.max(avg_freqs/ I3Units.megahertz)) 
                interval = 10
                x_ticks = np.arange(0, np.max(avg_freqs)/ I3Units.megahertz, interval)
                plt.xticks(x_ticks)
                plt.title(f"Spectral Average - Antenna {iant+1}")
                plt.ylabel("Spectral power [dBm/Hz]")
        
        plt.xlabel("Frequency [MHz]")
        plt.legend()
        plt.savefig("spectral_average_antenna.png")
     
    

tray = I3Tray()

tray.AddModule("I3Reader", "reader",
         FilenameList = [filename]) 

# Choosing soft trigger only 
def select_soft(frame):
    trigger_info = frame['SurfaceFilters']
    return trigger_info["soft_flag"].condition_passed

# Add the module to the tray
tray.Add(select_soft, "select_soft",
         streams=[icetray.I3Frame.DAQ])

# Select data with trace length equal to 1024
def select_TraceLength(frame):
    TraceLength = frame['RadioTraceLength'].value

    if TraceLength == 1024:
        return True  # This will indicate that the frame should be saved to the selected stream
    else:
        return False  
    
# Add the module to the tray
tray.Add(select_TraceLength, "select_TraceLength",
         streams=[icetray.I3Frame.DAQ])

# Removing TAXI artifacts 
tray.Add(
    radcube.modules.RemoveTAXIArtifacts, "ArtifactRemover",
    InputName="RadioTAXIWaveform",
    OutputName="ArtifactsRemoved",
    medianOverCascades=True,
    BaselineValue=0,
    RemoveBinSpikes=True,
    BinSpikeDeviance=int(2**12),
    RemoveNegativeBins=True
    )

tray.AddModule("I3NullSplitter","splitter",
               SubEventStreamName="RadioEvent"
               )

tray.AddModule(AnalyzeQframes, "Plotter")

tray.Execute()
