#!/usr/bin/python2

import time
import os
import argparse
import sys

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-d', '--dir', required=True, help='Directory containing CSV file')
flags = parser.parse_args()

# Path to CSV log
packetPath = os.path.join(flags.dir, 'packets.csv')
   
print("logreader reading at ",packetPath);
# Files not currently open for reading
packet = None

# Flag to be set to True when EOF reached
packetEnd = False

while 1:
    # check if CSV is already open
    if packet:
        packetLocation = packet.tell()
        packetLine = packet.readline()
        if not packetLine:
            packet.seek(packetLocation)
            packetEnd = True
        else:
            print(packetLine)
            sys.stdout.flush()
    else:
        if os.path.exists(packetPath):
            packet = open(packetPath, 'r')
            
    if(packetEnd):  
        time.sleep(1);
