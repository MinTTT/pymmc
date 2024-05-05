#%%
import serial
import time
from datetime import datetime

# import pandas as pd
import csv
import numpy as np
import matplotlib
matplotlib.use('TKAgg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
def fmt_timeNow():
    fmt_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H-%M-%S')
    return fmt_time



# %%
com_port = 'COM8'
budrate = 9600
csvFilePath = f'./temp_hum_data_{fmt_timeNow()}.csv'
ser = serial.Serial(com_port, budrate, timeout=5)
time_range = 3600 * 6


def getArduinoMsg():
    ser.flushOutput()
    line = ser.readline()
    line_split = str(line).split(' ')
    return line_split



time_start = time.time()
time_stop = time_start + time_range
time_now = time.time()
times = []
temps = []
humds = []

fig1, ax1 = plt.subplots(1, 1)
ax2 = plt.twinx(ax1)

# write head
with open(csvFilePath, 'w') as csv_file:
    table_writer = csv.DictWriter(csv_file, fieldnames=['time', 'temperature', 'humidity'])
    table_writer.writeheader()


def writeCSV(filePath, time, temp, humd):
    with open(filePath, 'a') as csv_file:
        table_writer = csv.DictWriter(csv_file, fieldnames=['time', 'temperature', 'humidity'])
        table_writer.writerow(dict(time=time, temperature=temp, humidity=humd))


start_time = time.time()


def updateData(index):
    time_now = time.time()
    # ser.flushOutput()
    # line = ser.readline()
    # line_split = str(line).split(' ')
    line_split = getArduinoMsg()
    if line_split[0] == "b'Humidity:" and line_split[-1] == "\\n'":
        hum, temp = float(line_split[1]), float(line_split[3])
        PIDhum, PIDtemp = float(line_split[-2]), float(line_split[-4])
        times.append((time_now - start_time) / 3600.)   # hour
        humds.append(hum)
        temps.append(temp)
        fmt_time = datetime.fromtimestamp(time_now).strftime('%Y-%m-%d %H:%M:%S')
        writeCSV(csvFilePath, times[-1], temps[-1], humds[-1])
        print(f'Time:{fmt_time}; Humidity: {hum}%; Temperature: {temp} Celsius; '
              f'Hum PID: {PIDhum}; Temp PID {PIDtemp}.')

        times_plot = np.array(times) - times[0]
        ponits_num = 500
        if len(times_plot) > ponits_num:
            time_final = times_plot[-1]
            step = int(len(times_plot) / ponits_num)
            times_plot = times_plot[::step]
            temps_plot = np.array(temps)[::step]
            humds_plot = np.array(humds)[::step]
            times_plot[-1] = time_final
            temps_plot[-1] = temps[-1]
            humds_plot[-1] = humds[-1]
        else:
            temps_plot = np.array(temps)
            humds_plot = np.array(humds)

        ax1.cla()
        ax2.cla()
        ax1.plot(times_plot, temps_plot, 'r--')
        # ax1.scatter(times_plot, temps_plot, color='r')
        ax1.set_ylim(36, 38)
        ax2.plot(times_plot, humds_plot, 'b-')
        # ax2.scatter(times_plot, humds_plot, color='b')
        ax2.set_ylim(55, 65)


ani = FuncAnimation(fig1, updateData, interval=1000)

plt.show()
# while time_now < time_stop:
#     time_now = time.time()
#     ser.flushOutput()
#     line = ser.readline()
#     line_split = str(line).split(' ')
#     if line_split[0] == "b'Humidity:" and line_split[-1] == "*C\\r\\n'":
#         hum, temp = float(line_split[1]), float(line_split[-2])
#         times.append(time_now)
#         humds.append(hum)
#         temps.append(temp)
#         fmt_time = datetime.fromtimestamp(time_now).strftime('%Y-%m-%d %H:%M:%S')
#         print(f'Time:{fmt_time}; Humidity: {hum}%; Temperature: {temp} Celsius.')


#
#
# data_df = pd.DataFrame(data=dict(time=times, temperature=temps, humidity=humds))
#
# data_df.to_csv(r'./temp_hum_data.csv')