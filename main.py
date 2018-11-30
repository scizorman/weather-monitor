#!/usr/bin/env python3
# coding: utf-8
import os
import sys
import time
import signal
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from influxdb import InfluxDBClient
from weathermonitor.communicator import SocketCom
from weathermonitor.device import TLan08VmHandler
from weathermonitor.utils import extract_bits


# Constants for Database
DB_HOST = "localhost"
DB_PORT = 8086
DB_USER = "root"
DB_PASSWORD = "root"
DB_TABLE = "WeatherMonitor"
DB_MEASUREMENT = "Aerovane"

# Constants for ADC
HOST = os.environ["HOST"]
PORT = int(os.environ["PORT"])
CH_BIT = int(os.environ["CH_BIT"])
VOLT_RANGE = int(os.environ["VOLT_RANGE"])
MEAS_CYCLE = int(os.environ["MEAS_CYCLE"])
CH_INTERVAL = int(os.environ["CH_INTERVAL"])
CH_KEYS = ("wind_spd", "wind_dir")
MEAS_CYCLE_SEC = MEAS_CYCLE * 0.1
NUM_CH = 8
NUM_RPT = 0
NUM_BUFFER = 10
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
MEAS_CHS = extract_bits(CH_BIT, NUM_CH)
READ_CYCLE_SEC = MEAS_CYCLE_SEC * NUM_BUFFER
INIT_ARGS = (CH_BIT, VOLT_RANGE, CH_INTERVAL, MEAS_CYCLE, NUM_RPT)


def generate_timestamp():
    global timestamps
    timestamps = [
        datetime.strftime(
            starttime + timedelta(seconds=MEAS_CYCLE_SEC * i),
            DATETIME_FORMAT,
        )
        for i in range(NUM_BUFFER)
    ]
    return

def update_starttime():
    global starttime
    starttime = datetime.strptime(timestamps[-1], DATETIME_FORMAT) + \
                timedelta(seconds=MEAS_CYCLE_SEC)
    return

def format_data(buffer_lst):
    fields_lst = [dict(zip(CH_KEYS, buffer)) for buffer in buffer_lst]
    formated_lst = []
    for timestamp, fields, in zip(timestamps, fields_lst):
        data_dict = {
            "time": timestamp,
            "fields": fields,
            "measurement": DB_MEASUREMENT,
        }
        formated_lst.append(data_dict)
    return formated_lst


def process_manager(signum, frame):
    with ThreadPoolExecutor(max_workers=NUM_CH) as executor:
        futures = [executor.submit(device.read_buffer, ch) for ch in MEAS_CHS]
    generate_timestamp()
    update_starttime()

    buffer_lst = list(zip(*(f.result() for f in futures)))
    formated_lst = format_data(buffer_lst)

    for json_body in formated_lst:
        client.write_points(json_body)

    if stop_flag:
        device.stop()
        sys.exit()
    return


if __name__ == "__main__":
    # Setting variables which are used by functions in this script
    client = InfluxDBClient(DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_TABLE)
    com = SocketCom(HOST, PORT)
    device = TLan08VmHandler(com)
    starttime = None
    stop_flag = False

    # Setup "TLAN-08VM"
    device.initialize(*INIT_ARGS)

    # Start measurement
    device.start()
    time.sleep(MEAS_CYCLE_SEC / 2)
    starttime = datetime.now()
    signal.signal(signalnum=signal.SIGALRM, handler=process_manager)
    signal.setitimer(signal.ITIMER_REAL, READ_CYCLE_SEC, READ_CYCLE_SEC)

    try:
        while True:
            pass
    except KeyboardInterrupt:
        stop_flag = True
        while True:
            pass