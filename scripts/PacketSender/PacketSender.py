#!/usr/bin/python3

import datetime
import time
import random
import requests


# example data packet as string; split into array.
rawdata="RB0012851,120308.916,4674.12804417,N,11705.4428043,W,827.4,M,72.0,55.0,101.325".split(',')

# url receiving post requests.
URL="http://michael-atkinson.com/dashboard/PostReceiver/PostReceiver.php"

# encode string in hex
datahex = (',').join(rawdata).encode('utf-8').hex()

dt = datetime.datetime

# data to be sent; imitates actual packet sent by iridium.
# only important fields are imei and data...and maybe transmit_time (UTC)
params = {
        "imei":300234066438270,
        "momsn":12345,
        "transmit_time":dt.now().strftime("%y-%m-%d %H:%M:%S"),
        "iridium_latitude":0.0,
        "iridium_longitude":0.0,
        "iridium_cep":0,
        "data":datahex}

while 1:
    # update transmit time, and increment data timestamp and location fields.
    params["transmit_time"] = dt.now().strftime("%y-%m-%d %H:%M:%S")
    rawdata[1] = str(float(rawdata[1])+100)
    rawdata[2] = str(float(rawdata[2])+random.uniform(-1,10))
    rawdata[4] = str(float(rawdata[4])+random.uniform(-1,10))
    params["data"] = (',').join(rawdata).encode('utf-8').hex()
    print((',').join(rawdata))

    # requests module makes an http post request to provided URL, 
    # containing our data fields.
    r = requests.post(url = URL,data=params)

    # returned status code should be 200 for success.
    #print(r.status_code)
    time.sleep(11)
