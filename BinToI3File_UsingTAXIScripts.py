#!/usr/bin/env python3
"""
Test to make I3 files from TAXI binaries.

Run with command (use no file extension for the OUTPUT_NAME):
./BinToI3File_UsingTAXIScripts.py BIN_FILE_NAME --output OUTPUT_NAME

- BSF 14/07/2023
"""

import argparse
import numpy as np
import os
import tarfile
from os import listdir
from os.path import isfile, join


ABS_PATH_HERE = str(os.path.dirname(os.path.realpath(__file__)))

from icecube import dataclasses, dataio, icetray
from icecube.icetray.i3logging import log_info, log_debug, log_warn, log_fatal
from icecube.taxi_reader import taxi_tools
from icecube.taxi_reader.data_processing import i3_converter


parser = argparse.ArgumentParser()
parser.add_argument("input", type=str, help="Name of .bin file to convert")
parser.add_argument("--serdesDelayFile", type=str, default=None, help="Name of file for Serdes delay (if applicable)")
parser.add_argument("--output", type=str, default=None, help="Name of the output file")
args = parser.parse_args()

infilename = args.input
outfilename = "Data"

if not isfile(args.input):
    raise ValueError("Input file does not exist... Try again.")

if args.serdesDelayFile is None:
    delay = None
    timestamps = None


# Right now just define serdes_delay and serdes_timestamps as None b/c I don't think they are needed...
i3_converter.radio2i3(infilename, outfilename, serdes_delay=None, serdes_timestamps=None)

#This is for a .bin.tgz file:

"""
#Extract the .bin.tgz file
input_tgz = args.input
output_directory="/home/storres/work/Carmen_data/BackgroundAnalysis/NewData/prueba"

with tarfile.open(input_tgz, "r:gz") as tar:
    tar.extractall(path=output_directory)

print(f"{input_tgz} extracted successfully to {output_directory}")

input_bin = os.path.join(output_directory, os.path.splitext(os.path.basename(input_tgz))[0])
output_i3 = os.path.join(output_directory, os.path.splitext(os.path.basename(input_bin))[0])


if args.serdesDelayFile is None:
    delay = None
    timestamps = None

    
# Right now just define serdes_delay and serdes_timestamps as None b/c I don't think they are needed...
i3_converter.radio2i3(input_bin, output_i3, serdes_delay=None, serdes_timestamps=None)

print(f"{input_bin} converted to {output_i3}")
"""
