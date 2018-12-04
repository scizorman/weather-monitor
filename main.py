#!/usr/bin/env python3
# coding: utf-8
import os
import sys
import time
import signal
import yaml
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from influxdb import InfluxDBClient
from weathermonitor.communicator import SocketCom
from weathermonitor.device import TLan08VmHandler
from weathermonitor.utils import or_of_bits


DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

# Constants for ADC
DEVICE_CONFIG_PATH = "./device_config.yaml"
HOST = os.environ["DEVICE_HOST"]
PORT = int(os.environ["DEVICE_PORT"])

with open(DEVICE_CONFIG_PATH) as f:
    device_conf_dict = yaml.load(f)

    CH_ROLE_DICT     = device_conf_dict["ch_role"]
    CONV_FACTOR_DICT = device_conf_dict["conv_factor"]
    VOLT_RANGE_DICT  = device_conf_dict["volt_range"]
    MEAS_CH_LIST     = device_conf_dict["meas_chs"]
    MEAS_CYCLE_SEC   = device_conf_dict["meas_cycle_sec"]
    NUM_BUFFER       = device_conf_dict["num_buffer"]
    NUM_RPT          = device_conf_dict["num_rpt"]

    CH_BIT = or_of_bits(*MEAS_CH_LIST)
    CH_INTERVAL = int(device_conf_dict["ch_interval_sec"] * 10) # Unit: 100 ms
    MEAS_CYCLE = int(MEAS_CYCLE_SEC * 10)                       # Unit: 100 ms
    NUM_CH = len(MEAS_CH_LIST)
    READ_CYCLE_SEC = MEAS_CYCLE_SEC * NUM_BUFFER

    INIT_ARGS = (CH_BIT, VOLT_RANGE_DICT, CH_INTERVAL, MEAS_CYCLE, NUM_RPT)

    del(device_conf_dict)

# Constants for Database
DB_HOST        = os.environ["DB_HOST"]
DB_PORT        = int(os.environ["DB_PORT"])
DB_USERNAME    = os.environ["DB_USERNAME"]
DB_PASSWORD    = os.environ["DB_PASSWORD"]
DB_TABLENAME   = os.environ["DB_TABLENAME"]
DB_MEASUREMENT = os.environ["DB_MEASUREMENT"]


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

def convert_buffer(buffer, conv_factor):
    conv_buffer = list(map(lambda x: x * conv_factor, buffer))
    return conv_buffer

def create_jsonbody(buffer_lst):
    print(list(CH_ROLE_DICT.values()))
    print(buffer_lst)
    fields_lst = [
        dict(zip(val, buffer))
        for val, buffer in zip(CH_ROLE_DICT.values(), buffer_lst)
    ]
    jsonbody_lst = []
    for timestamp, fields, in zip(timestamps, fields_lst):
        jsonbody = {
            "time": timestamp,
            "fields": fields,
            "measurement": DB_MEASUREMENT,
        }
        jsonbody_lst.append(jsonbody)
    return jsonbody_lst


def process_manager(signum, frame):
    with ThreadPoolExecutor(max_workers=NUM_CH) as executor:
        futures = [
            executor.submit(device.read_buffer, ch)
            for ch in MEAS_CH_LIST
        ]
    generate_timestamp()
    update_starttime()

    conv_buffer = [
        convert_buffer(future.result(), factor)
        for future, factor in zip(futures, CONV_FACTOR_DICT.values())
    ]
    buffer_lst = list(zip(*(buffer for buffer in conv_buffer)))
    json_body = create_jsonbody(buffer_lst)

    client.write_points(json_body)

    if stop_flag:
        device.stop()
        sys.exit()
    return


if __name__ == "__main__":
    # Setting variables which are used by functions in this script
    client = InfluxDBClient(
        DB_HOST,
        DB_PORT,
        DB_USERNAME,
        DB_PASSWORD,
        DB_TABLENAME,
    )
    com = SocketCom(HOST, PORT)
    device = TLan08VmHandler(com)
    starttime = None
    stop_flag = False

    # Setup InfluxDB
    dbs = client.get_list_database()
    weathermonitor_db = {"name": "WeatherMonitor"}
    if weathermonitor_db not in dbs:
        client.create_database(weathermonitor_db["name"])

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