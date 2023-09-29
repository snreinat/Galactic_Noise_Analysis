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
parser.add_argument("input", type=str, help="Name of .i3.gz file")
args = parser.parse_args()

filename = args.input

class NoiseCalculation(icetray.I3Module):
    def __init__(self, ctx):
        icetray.I3Module.__init__(self, ctx)
        self.AddParameter('InputName', 'InputName', 'InputName')

    def Configure(self):
        self.inputName = self.GetParameter('InputName')
        self.counts = 0
        self.colors = ["c", "b", "m", "r", "y", "g"]
        
        self.noise_rms_step = []
        self.noise_rms_window = []

    def GetNoise(self, frame):
        self.counts += 1
        antennaDataMap = frame[self.inputName]
        for iant, antkey in enumerate(antennaDataMap.keys()):
            channelMap = antennaDataMap[antkey]
            for ichan, chkey in enumerate(channelMap.keys()):
                fft = channelMap[ichan].GetFFTData()
                timeSeries = fft.GetTimeSeries()
                # Noise RMS 
                self.noise_rms_window.append(radcube.GetRMS(timeSeries))
                
                #Subtraces Method
                noise_rms_step, noise_power_step = [], []
                steps = np.arange(0, len(timeSeries), 64)
                numberOfSubTraces = len(timeSeries)//64
                for i in range(numberOfSubTraces - 1):
                    noise_chopped = timeSeries.GetSubset(
                        int(steps[i]), int(steps[i + 1])
                    )
                    noise_rms_step.append(
                        radcube.GetRMS(noise_chopped)
                        )
                # We keep only 10 minimum value and average them.
                # The rational is that RFI screw up the noise, but we can hardly have lower noise
                noise_rms_step.sort()
                self.noise_rms_step.append(
                    np.median(noise_rms_step[:10]))
                    

    def Physics(self, frame):
            self.GetNoise(frame)
           

    def Finish(self):
        noise_step = np.asarray(self.noise_rms_step).reshape(self.counts, 3, 2)
        noise_std = np.asarray(self.noise_rms_window).reshape(self.counts, 3, 2)
        # Plotting the Histograms of the noise level
        fig, ax = plt.subplots(
                figsize=[10, 8], nrows=1, ncols=1, tight_layout=True
                )
        for iant in range(3):
            for ich in range(2):
                #Rms
                ax.hist(
                    noise_std[:, iant, ich], histtype="stepfilled", alpha=0.45,
                    color=self.colors[2*iant + ich], bins="fd",
                    label=f"Antenna {iant+1}, Channel {ich+1}",
                    density=True
                    )
                #subtraces
                ax.hist(
                    noise_step[:, iant, ich], histtype="step", alpha=1,
                    color=self.colors[2*iant + ich], bins="fd",
                    label=f"Antenna {iant+1}, Channel {ich+1}, Subtraces",
                    density=True
                    )
        ax.set_xlabel("Amplitude / ADC")
        ax.set_ylabel("Normilized Counts")
        ax.legend(ncol=2)
        
        # Save the plot to a file 
        plt.title("Distributions of the noise level in the traces for each antenna channel")
        plot_filename = "noise_histogram.png"
        fig.savefig(plot_filename)
        

tray = I3Tray()

tray.AddModule("I3Reader", "reader",
         FilenameList = [filename])

#Choosing soft trigger only 
def select_soft(frame):
    trigger_info = frame['SurfaceFilters']
    return trigger_info["soft_flag"].condition_passed

# add the module to the tray
tray.Add(select_soft, "select_soft",
         streams=[icetray.I3Frame.DAQ])

def select_TraceLength(frame):
    TraceLength = frame['RadioTraceLength'].value

    if TraceLength != 0:
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

"""def select_RMS(frame):
    RMS = dataclasses.I3Double()
    waveform = frame["ArtifactsRemoved"]
    key = waveform.keys()[0]
    wave_ant1 = waveform[key]
    wave_ant1_ch0 = wave_ant1[0]
    fft = wave_ant1_ch0.GetFFTData()
    ts = fft.GetTimeSeries()
    RMS = radcube.GetRMS(ts)
    frame.Put("RMS", dataclasses.I3Double(RMS))
    if RMS < 9000:
        return True  # This will indicate that the frame should be saved to the selected stream
    else:
        return False
    
tray.Add(select_RMS, "select_RMS",
         streams=[icetray.I3Frame.DAQ])"""

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
               FilterLimits=[140*I3Units.megahertz, 190*I3Units.megahertz] # note the use of I3Units!
               )

"""# let's plot the waveforms from one antenna in different stages of processing with an existing plotting module
tray.AddModule(radcube.modules.RadcubePlotter, "plotter",
               AntennaID = 1,
               StationID = 1,
               OutputDir = "/home/storres/work/GalacticNoiseAnalysis/",
               ZoomToPulse = 0,
               DataToPlot = [["RadioTAXIWaveform", 1, "Recorded waveforms", True, "dB"],
                             ["ArtifactsRemoved", 1, "Artifacts removed", True, "dB"],
                             ["MedFilteredMap", 1, "Median Foltered", True, "dB"],
                             ["FilteredMap", 1, "After Bandpass Filter", True, "dB"],
                            ]
               )
"""

#Calculating RMS values and their histogram 
tray.AddModule(
        NoiseCalculation, "TheNoiseCalculator",
        InputName="FilteredMap"
        )

"""# save the I3 files with all new objects to a new file, so we can use it for later processing or plotting
tray.AddModule("I3Writer", "writer",
                filename="/home/storres/work/GalacticNoiseAnalysis/newfile.i3",
                streams=[icetray.I3Frame.DAQ, icetray.I3Frame.Physics] # we'll only save Q and P frames
              )"""

tray.Execute()
        
   