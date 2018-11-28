#!/usr/bin/env python3
# coding: utf-8
import os
import sys
import time
import signal
import threading
from datetime import datetime, timedelta
from weathermonitor.communicator import SocketCom
from weathermonitor.device import TLan08VmHandler
from weathermonitor.utils import extract_bits


HOST = os.environ["HOST"]
PORT = int(os.environ["PORT"])
CH_BIT = int(os.environ["CH_BIT"])
VOLT_RANGE = int(os.environ["VOLT_RANGE"])
MEAS_CYCLE = int(os.environ["MEAS_CYCLE"])
CH_INTERVAL = int(os.environ["CH_INTERVAL"])
MEAS_CYCLE_SEC = MEAS_CYCLE * 0.1
NUM_CH = 8
NUM_RPT = 0
NUM_BUFFER = 10
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
MEAS_CHS = extract_bits(CH_BIT, NUM_CH)
READ_CYCLE_SEC = MEAS_CYCLE_SEC * NUM_BUFFER
INIT_ARGS = (CH_BIT, VOLT_RANGE, CH_INTERVAL, MEAS_CYCLE, NUM_RPT)


# def buffer_data():
#     device.start()
#     while True:
#         ret = device.get_status()
#         if ret == "DONE":
#             break
#     for ch in MEAS_CHS:
#         buffer_dict[ch].append(device.read_buffer(ch))

# def insert_to_db(ch):
#     while True:
#         if len(buffer_dict[ch]) == NUM_BUFFER:
#             ret = buffer_dict[ch]
#             buffer_dict[ch] = []
#             print(dict(zip(timestamps, ret)))
#             print(ch, len(ret))
#             break

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

def process_manager(signum, frame):
    threads = [
        threading.Thread(target=insert_to_db, args=(ch, ))
        for ch in MEAS_CHS
    ]
    generate_timestamp()
    update_starttime()
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    if stop_flag is not None:
        device.stop()
        sys.exit()
    return

def create_data_dict(ch):
    """
    """
    data_lst = device.read_buffer(ch)
    # if len(data_lst) != NUM_BUFFER:
    #     global stop_flag
    #     stop_flag = "wahhoi"
    #     raise AssertionError("wahhoi")
    data_dict = dict(zip(timestamps, data_lst))
    return data_dict

# NOTE: Temporary
def insert_to_db(ch):
    """
    """
    data_dict = create_data_dict(ch)
    print(data_dict)
    print(ch, len(data_dict.keys()))


if __name__ == "__main__":
    com = SocketCom(HOST, PORT)
    device = TLan08VmHandler(com)

    # Setup "TLAN-08VM"
    device.initialize(*INIT_ARGS)

    # Start measurement
    device.start()
    time.sleep(MEAS_CYCLE_SEC / 2)
    starttime = datetime.now()
    signal.signal(signalnum=signal.SIGALRM, handler=process_manager)
    signal.setitimer(signal.ITIMER_REAL, READ_CYCLE_SEC, READ_CYCLE_SEC)

    stop_flag = None
    while True:
        stop_flag = input()


# def update_starttime():
#     global starttime
#     starttime = datetime.strptime(timestamps[-1], DATETIME_FORMAT) + \
#                 timedelta(seconds=MEAS_CYCLE_SEC)
#     return

# def process_manager(signum, frame):
#     threads = [
#         threading.Thread(target=insert_to_db, args=(ch, ))
#         for ch in MEAS_CHS
#     ]
#     generate_timestamp()
#     update_starttime()
#     for thread in threads:
#         thread.start()
#     # for thread in threads:
#     #     thread.join()

#     # if stop_flag is not None:
#     #     device.stop()
#     #     sys.exit()


# if __name__ == "__main__":
#     com = SocketCom(HOST, PORT)
#     device = TLan08VmHandler(com)

#     # Setup the measurement
#     device.initialize(*INIT_ARGS)
#     buffer_dict = {}
#     for ch in MEAS_CHS:
#         buffer_dict[ch] = []

#     # Start the measurement
#     starttime = datetime.now()
#     signal.signal(signalnum=signal.SIGALRM, handler=process_manager)
#     # signal.setitimer(signal.ITIMER_REAL, READ_CYCLE_SEC, READ_CYCLE_SEC)
#  #
#     while True:
#         buffer_data()
#     # stop_flag = None
#     # while True:
#     #     stop_flag = input()