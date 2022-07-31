
import serial
import time
from datetime import datetime

com_port = 'COM6'
budrate = 9600

ser = serial.Serial(com_port, budrate, timeout=5)


time_range = 3600 * 8



time_start = time.time()
time_stop = time_start + time_range
time_now = time.time()
times = []
temps = []
humds = []

while time_now < time_stop:
    time_now = time.time()
    ser.flushOutput()
    line = ser.readline()
    line_split = str(line).split(' ')
    if line_split[0] == "b'Humidity:" and line_split[-1] == "*C\\r\\n'":
        hum, temp = float(line_split[1]), float(line_split[-2])
        times.append(time_now)
        humds.append(hum)
        temps.append(temp)
        fmt_time = datetime.fromtimestamp(time_now).strftime('%Y-%m-%d %H:%M:%S')
        print(f'Time:{fmt_time}; Humidity: {hum}%; Temperature: {temp} C')


import pandas as pd


data_df = pd.DataFrame(data=dict(time=times, temperature=temps, humidity=humds))

data_df.to_csv(r'./temp_hum_data.csv')