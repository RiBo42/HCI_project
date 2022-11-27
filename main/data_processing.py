import heartpy as hp
import neurokit2 as nk
import numpy as np
import pandas as pd
import json
from collections import deque
from django.utils import timezone
import sqlite3
from .models import PPG

con = sqlite3.connect("db.sqlite3")
cur = con.cursor()


# SAMPLING_RATE = 1e9
# INTERVAL = 1 / SAMPLING_RATE * 1e9


def csv_data_loader(file, data_queue):
    data = pd.read_csv(file)


def enqueue(data_queue, data):
    if not isinstance(data, dict):
        data = json.loads(data)
    data_dict = {"time": data["time"], "event": data["total_event"], "ts": data["time_stamp"],
            "ppg": data["data1"]}
    # print(data['data1'])
    queue = data_queue
    # if len(queue):
    #     queue.popleft()
    queue.append(data_dict)
    return queue


def get_ppg(data_queue, window_size, data_freq=100):
    sampling_rate = 100
    signal = []
    length = len(data_queue)
    # data_queue.popleft()
    print("Length here", length)
    window_size = window_size
    if length > window_size:
        print("arrived")
        timer = []
        for i in range(length - window_size):
            data_queue.popleft()  # should save
        for i in range(len(data_queue)):
            timer += data_queue[i]["ts"]
            signal += data_queue[i]["ppg"]
        sampling_rate = int(len(signal) / (timer[-1] - timer[0]) * 1e9)
        # print(sampling_rate)
    return sampling_rate, signal, data_queue


def insert(data):
    if not isinstance(data, dict):
        data = json.loads(data)
    ppg = PPG(date=timezone.now(), time_stamp=data['time_stamp'], ppg_signal=data['data1'])
    ppg.save()


def hrv_generator(measures, signal, sampling_rate=100):
    print(sampling_rate)
    working_data = -1
    measures = measures
    if len(signal):
        ppg_clean = nk.ppg_clean(signal, sampling_rate=sampling_rate)
        # print(ppg_clean)
        working_data, measures = hp.process(ppg_clean, sampling_rate, calc_freq=True)
    return working_data, measures


if __name__ == "__main__":
    test_data = {"total_event": 36, "sensor_type": "com.google.wear.sensor.ppg", "time": "2022-07-24T21:40:04.253",
                 "time_stamp": 81376855103961, "data0": 24729472, "data1": 3723379, "data2": 0}
    json_data = json.dumps(test_data)
    # json_data = json.loads(json_data)
    data_queue = deque()
    data_queue = enqueue(test_data, data_queue)
    print(data_queue)
# not functional when called on command line
