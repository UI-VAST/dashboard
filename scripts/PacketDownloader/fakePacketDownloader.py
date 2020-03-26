#!/usr/bin/python

import time
import random
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-d','--dir',required=True,help='Directory for downloading files')
flags = parser.parse_args()

if not os.path.exists(flags.dir):
    os.makedirs(flags.dir)

print(flags.dir)
downloadPath = os.path.join(flags.dir, 'packets.csv')

fakePacket = "$GPGGA,120208.916,4673.00000,N,11701.1435,W,2,06,1.7,109.0,M,47.6,M,1.5,0000*71\n".split(',')

while 1:
    fakePacket[1] = str(float(fakePacket[1])+100)
    fakePacket[2] = str(float(fakePacket[2])+random.uniform(-1,10))
    fakePacket[4] = str(float(fakePacket[4])+random.uniform(-1,10))

    with open(downloadPath,'a') as f:
        f.write((',').join(fakePacket))
    time.sleep(11)
