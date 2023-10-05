#!/usr/bin/env python3
from I3Tray import I3Tray
from icecube import icetray, dataio, dataclasses, radcube
from icecube.icetray import I3Units

import os
import matplotlib.pyplot as plt
import numpy as np
import sys
import argparse

# Input i3 file with the data 
parser = argparse.ArgumentParser()
parser.add_argument("input", type=str, help="Name of .i3.gz file")
args = parser.parse_args()

filename = args.input

tray = I3Tray()

tray.AddModule("I3Reader", "reader",
         FilenameList = [filename])
 
# Choosing soft trigger data 
def select_soft(frame):
    trigger_info = frame['SurfaceFilters']
    return trigger_info["soft_flag"].condition_passed

# add module to the tray
tray.Add(select_soft, "select_soft",
         streams=[icetray.I3Frame.DAQ])

# Module that saves the Taxi_time data 
class TaxiTimeData(icetray.I3Module):
    
# The init method is the constructor for the class. It initializes the object and sets up the necessary parameters.
# In this case, it defines the inputName parameter as an empty string and adds it as a module parameter using AddParameter(). The AddParameter() method allows users to set the value of inputName when configuring the module.

  def __init__(self,ctx):
    icetray.I3Module.__init__(self,ctx)
    self.inputName = ""
    self.timeValues = [] # Array to store SNR values
    self.AddParameter("InputName", "Input antenna data map", self.inputName)
   
# The configure retrieves the user-defined parameter value for inputName using GetParameter() and assigns it to the corresponding class attribute.
  def Configure(self):
    self.inputName = self.GetParameter("InputName")
  
# to get information from the Q frames you would do so in the DAQ class function
  def DAQ(self, frame):
    if self.inputName in frame:
        time_value = frame[self.inputName]
        self.timeValues.append(time_value)
        
# save all the time values in a txt file
  def Finish(self):
        time_values = [str(time) for time in self.timeValues]
        with open('time_values.txt', 'w') as file:
            file.write('\n'.join(time_values))    
    
tray.AddModule(TaxiTimeData, "Savingtimevalues", InputName="RadioTaxiTime")

tray.Execute() 
