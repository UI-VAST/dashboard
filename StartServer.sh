#!/bin/bash

if [[ $# -lt 1 ]]; then
	echo "Usage: ./StartServer label [required] directory [optional]";
	exit 1;
fi

LABEL=$1
DIRECTORY=$2
RISE_DIR=$(pwd)

IPADDR=`hostname -I | cut -d ' ' -f1`

if [[ -z "$DIRECTORY" ]]; then
    printf "no directory set; setting to current\n"
    DIRECTORY=$RISE_DIR
fi

# start LogReader through websocket on port 8080
cd $RISE_DIR/scripts/websocketd
./websocketd --port=8080 --address="$IPADDR" python $RISE_DIR/scripts/LogReader/LogReader.py -d $DIRECTORY/$LABEL &

# tell PostReceiver which directory to save into
echo "<?php \$PacketsPath=\"$DIRECTORY/$LABEL/\"; ?>" > $RISE_DIR/PostReceiver/logfile.php


# if testing, start fakePacketSender
#cd $RISE_DIR/scripts/PacketSender
#./PacketSender.py
# ./PacketSender.sh

# start PacketDownloader
#cd $RISE_DIR/scripts/PacketDownloader
#./PacketDownloader.py -l $LABEL -d $DIRECTORY &
#./fakePacketDownloader.py -d $DIRECTORY/$LABEL &
