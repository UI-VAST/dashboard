#!/bin/bash

# data sent thru curl command needs to be hex-encoded.
# TODO: take in human readable string, like this:
RAWDATA=$GPGGA,120308.916,4674.12804417,N,11705.4428043,W,2,06,1.7,109.0,M,47.6,M,1.5,0000*71
# somehow convert the above to hex; then update in loop every time to send new packets.
DATA=2447504747412c3132303330382e3931362c343637342e31323830343431372c4e2c31313730352e343432383034332c572c322c30362c312e372c3130392e302c4d2c34372e362c4d2c312e352c303030302a3731

URL=http://michael-atkinson.com/dashboard/PostReceiver/PostReceiver.php

while true; do
	curl -d "imei=1234" -d "data=$DATA" $URL;
	sleep 11
done


