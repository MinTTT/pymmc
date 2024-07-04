# %%
import serial
import time
from datetime import datetime
from typing import List
# import pandas as pd
import csv
import numpy as np
# import matplotlib

from magicgui import widgets
from magicgui.widgets import FloatRangeSlider, Container, FloatSpinBox, Label
from threading import Thread, Lock

ThreadLock = Lock()




def fmt_timeNow():
    fmt_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H-%M-%S')
    return fmt_time


def run_in_thread(fn):
    def run(*k, **kw):
        t = Thread(target=fn, args=k, kwargs=kw)
        t.start()
        return t  # <-- this is new!

    return run


#
# communicate_Flag = False
# def waiting_comm():
#     global communicate_Flag
#     while communicate_Flag:
#         time.sleep(.0001)
#     communicate_Flag = True
#     return None
#
#
# def comm_close():
#     global communicate_Flag
#     communicate_Flag = False


class ArduinoPID:
    """

    Arduino Command:
    Tx: T   Rcv: Current Temperature
    Rx: H   Rcv: Current Humidity
    Tx: X[value]    Rcv: 1  # set Temperature to [Value]
    Tx: Y[value]    Rcv: 1  # set Humidity to [Value]
    Tx: M  Rcv: [Hum_read] [Temp_read] [tempPIDvalue] [humPIDvalue] [set_temperature] [set_humidity]

    Ref: https://www.reddit.com/r/arduino/comments/17eqg3t/how_to_send_an_array_of_float_values_from_python/?onetap_auto=true&one_tap=true
    """
    com: str
    baudrate: int

    def __init__(self, com: str, baudrate: int, auto=True, buffer=40000) -> None:
        self.com = com
        self.baudrate = baudrate
        self.serial_arduino: serial.Serial = serial.Serial(port=self.com, baudrate=self.baudrate,
                                                           timeout=1)  # type serial.Serial
        # waiting_comm()
        time.sleep(2)
        msg = self.serial_arduino.read_until()
        print(msg.decode())
        while self.serial_arduino.in_waiting:
            time.sleep(.001)
        # comm_close()

        self.Temp_sv: float = 30
        self.Humd_sv: float = 60
        self.Humd_crt: float = 0
        self.Temp_crt: float = 0
        self.Temp_PID: float = 0
        self.Humd_PID: float = 0
        self.Temp_SV_UI = 30.
        self.Humd_SV_UI = 60.
        self.timeStart = time.time()

        self.timeBuffer = np.ones(buffer) * np.nan
        self.tempBuffer = np.ones(buffer) * np.nan
        self.humdBuffer = np.ones(buffer) * np.nan
        self.bufferSize = buffer
        self.index = 0

        if auto:
            self.update()

    def rec_temp(self, temp):
        self.Temp_SV_UI = temp

    def rec_Humd(self, humd):
        self.Humd_SV_UI = humd

    def set_temp(self, temp):
        # waiting_comm()
        value = f'X{temp}'
        # waiting_comm()
        self.serial_arduino.write(value.encode())
        while self.serial_arduino.in_waiting:
            time.sleep(.001)

    def set_humd(self, hum):

        value = f'Y{hum}'

        self.serial_arduino.flushInput()
        self.serial_arduino.write(value.encode('ascii'))
        while self.serial_arduino.in_waiting:
            time.sleep(.001)

    def getArduinoMsg(self):
        self.serial_arduino.flushOutput()
        while True:
            # print('Sending M')
            self.serial_arduino.write('M'.encode())
            time.sleep(.1)
            line = self.serial_arduino.read_until()
            line_split = line.decode().strip(' \r\n').split(' ')
            print(line_split)
            if len(line_split) == 6:
                break

        if len(line_split) >= 3:
            line_split = [float(val) for val in line_split]
            if len(line_split) == 6:
                self.set_msg(line_split)
                print(line_split)
        return None

    def update(self):
        def _update():
            while True:
                if abs(self.Humd_SV_UI - self.Humd_sv) > 0.1:
                    print(self.Humd_SV_UI)
                    print(self.Humd_sv)
                    self.set_humd(self.Humd_SV_UI)
                if abs(self.Temp_SV_UI - self.Temp_sv) > 0.1:
                    print(self.Temp_SV_UI)
                    print(self.Temp_sv)
                    self.set_temp(self.Temp_SV_UI)
                self.getArduinoMsg()
                time.sleep(.2)

        worker = Thread(target=_update)
        worker.start()

    def set_msg(self, value: List[float]):
        self.Humd_crt = value[0]
        self.Temp_crt = value[1]
        self.Temp_PID = value[2]
        self.Humd_PID = value[3]
        self.Temp_sv = value[4]
        self.Humd_sv = value[5]
        self.timeBuffer[self.index] = time.time()
        self.humdBuffer[self.index] = self.Humd_crt
        self.tempBuffer[self.index] = self.Temp_crt
        self.index = (self.index + 1) % self.bufferSize

    def __del__(self):
        self.serial_arduino.close()
        self.serial_arduino.__del__()


class ArduinoPID_GUI(Container):
    """
    """

    def __init__(self, arduino_obj: ArduinoPID):
        super().__init__()
        # self.fig, self.ax1 = plt.subplots()
        # self.ax2 = plt.twinx(self.ax1)
        # self.native.layout().addWidget(FigureCanvas(self.fig))
        self.SetTemp = FloatSpinBox(value=30, min=21, max=45, step=.5)

        self.SetTempBox = Container(widgets=[Label(value='Set_Temperature (℃): '),
                                             self.SetTemp], layout='horizontal')
        self.SetHumd = FloatSpinBox(value=55, min=10, max=100, step=1)

        self.SetHumdBox = Container(widgets=[Label(value='Set_Humidity (%): '),
                                             self.SetHumd], layout='horizontal')

        self.CurTemp = Label(value='NA')
        self.CurHumd = Label(value='NA')
        self.HeatingIndc = Label(value='x.x')
        self.HumdIndc = Label(value='x.x')
        self.TempSV = Label(value='NA')
        self.HumdSV = Label(value='NA')
        # self.MSG = Label(value='Waiting init Device.')

        self.append(self.SetTempBox)
        self.append(self.SetHumdBox)
        self.append(Container(widgets=[Label(value='Current Temperature: '),
                                       self.CurTemp], layout='horizontal'))
        self.append(Container(widgets=[Label(value='Current Humidity: '),
                                       self.CurHumd], layout='horizontal'))
        self.append(Container(widgets=[Label(value='Heating State: '), self.HeatingIndc],
                              layout='horizontal'))
        self.append(Container(widgets=[Label(value='Humidifying State: '), self.HumdIndc],
                              layout='horizontal'))
        self.append(Container(widgets=[Label(value='SV Temp: '), self.TempSV,
                                       Label(value='SV Humd: '), self.HumdSV],
                              layout='horizontal'))
        # link events
        self.arduino: ArduinoPID = arduino_obj
        self.SetTemp.changed.connect(self.arduino.rec_temp)
        self.SetHumd.changed.connect(self.arduino.rec_Humd)
        self.update = False
        self.updateState()

    # def update_graph(self, ):
    #     """Re-plot when a parameter changes.
    #
    #     Note
    #     ----
    #     For big data, this could be slow, maybe `auto_call` should
    #     not be true in the method above...
    #     """
    #     # self.ax.cla()
    #     # sig.plot(ax=self.ax)
    #     # self.fig.canvas.draw()
    #
    #     self.ax1.cla()
    #     self.ax2.cla()
    #     self.ax1.plot(self.arduino.timeBuffer, self.arduino.tempBuffer, 'r--')
    #     # ax1.scatter(times_plot, temps_plot, color='r')
    #     # self.ax1.set_ylim(36, 38)
    #     self.ax2.plot(self.arduino.timeBuffer, self.arduino.humdBuffer, 'b-')
    #     # ax2.scatter(times_plot, humds_plot, color='b')
    #     # self.ax2.set_ylim(55, 65)
    #     self.fig.canvas.draw()




    def _updateState(self):
        while self.update:
            self.CurHumd.value = self.arduino.Humd_crt
            self.CurTemp.value = self.arduino.Temp_crt
            self.HeatingIndc.value = self.arduino.Temp_PID
            self.HumdIndc.value = self.arduino.Humd_PID
            self.TempSV.value = self.arduino.Temp_sv
            self.HumdSV.value = self.arduino.Humd_sv
            # self.update_graph()
            time.sleep(.5)

    def updateState(self):
        self.update = True
        worker = Thread(target=self._updateState)
        worker.start()
        # worker.join()


def logFile(file_path, temperature, humidity):
    with open(file=file_path, mode='a') as file:
        fmt_time = time.strftime("%Y-%m-%d %H:%m:%S")
        file.write(f"{fmt_time}\tT: {temperature}\t H: {humidity}\n")

    return None


# com_port = 'COM8'
# baudrate = 9600
#
# arduino = ArduinoPID(com=com_port, baudrate=baudrate, auto=False)


# %%
if __name__ == "__main__":
    com_port = 'COM8'
    baudrate = 9600

    arduino = ArduinoPID(com=com_port, baudrate=baudrate, auto=True)

    # arduino.getArduinoMsg()

    gui = ArduinoPID_GUI(arduino)

    gui.show(run=True)
    exit(0)
# # %%
# com_port = 'COM8'
# budrate = 9600
# csvFilePath = f'./temp_hum_data_{fmt_timeNow()}.csv'
# ser = serial.Serial(com_port, budrate, timeout=5)
# time_range = 3600 * 6


# def getArduinoMsg():
#     ser.flushOutput()
#     line = ser.readline()
#     line_split = str(line).split(' ')
#     return line_split


# time_start = time.time()
# time_stop = time_start + time_range
# time_now = time.time()
# times = []
# temps = []
# humds = []

# fig1, ax1 = plt.subplots(1, 1)
# ax2 = plt.twinx(ax1)

# # write head
# with open(csvFilePath, 'w') as csv_file:
#     table_writer = csv.DictWriter(csv_file, fieldnames=['time', 'temperature', 'humidity'])
#     table_writer.writeheader()


# def writeCSV(filePath, time, temp, humd):
#     with open(filePath, 'a') as csv_file:
#         table_writer = csv.DictWriter(csv_file, fieldnames=['time', 'temperature', 'humidity'])
#         table_writer.writerow(dict(time=time, temperature=temp, humidity=humd))


# start_time = time.time()


# def updateData(index):
#     time_now = time.time()
#     # ser.flushOutput()
#     # line = ser.readline()
#     # line_split = str(line).split(' ')
#     line_split = getArduinoMsg()
#     if line_split[0] == "b'Humidity:" and line_split[-1] == "\\n'":
#         hum, temp = float(line_split[1]), float(line_split[3])
#         PIDhum, PIDtemp = float(line_split[-2]), float(line_split[-4])
#         times.append((time_now - start_time) / 3600.)   # hour
#         humds.append(hum)
#         temps.append(temp)
#         fmt_time = datetime.fromtimestamp(time_now).strftime('%Y-%m-%d %H:%M:%S')
#         writeCSV(csvFilePath, times[-1], temps[-1], humds[-1])
#         print(f'Time:{fmt_time}; Humidity: {hum}%; Temperature: {temp} Celsius; '
#               f'Hum PID: {PIDhum}; Temp PID {PIDtemp}.')

#         times_plot = np.array(times) - times[0]
#         ponits_num = 500
#         if len(times_plot) > ponits_num:
#             time_final = times_plot[-1]
#             step = int(len(times_plot) / ponits_num)
#             times_plot = times_plot[::step]
#             temps_plot = np.array(temps)[::step]
#             humds_plot = np.array(humds)[::step]
#             times_plot[-1] = time_final
#             temps_plot[-1] = temps[-1]
#             humds_plot[-1] = humds[-1]
#         else:
#             temps_plot = np.array(temps)
#             humds_plot = np.array(humds)

#         ax1.cla()
#         ax2.cla()
#         ax1.plot(times_plot, temps_plot, 'r--')
#         # ax1.scatter(times_plot, temps_plot, color='r')
#         ax1.set_ylim(36, 38)
#         ax2.plot(times_plot, humds_plot, 'b-')
#         # ax2.scatter(times_plot, humds_plot, color='b')
#         ax2.set_ylim(55, 65)


# ani = FuncAnimation(fig1, updateData, interval=1000)

# plt.show()
# # while time_now < time_stop:
# #     time_now = time.time()
# #     ser.flushOutput()
# #     line = ser.readline()
# #     line_split = str(line).split(' ')
# #     if line_split[0] == "b'Humidity:" and line_split[-1] == "*C\\r\\n'":
# #         hum, temp = float(line_split[1]), float(line_split[-2])
# #         times.append(time_now)
# #         humds.append(hum)
# #         temps.append(temp)
# #         fmt_time = datetime.fromtimestamp(time_now).strftime('%Y-%m-%d %H:%M:%S')
# #         print(f'Time:{fmt_time}; Humidity: {hum}%; Temperature: {temp} Celsius.')


# #
# #
# # data_df = pd.DataFrame(data=dict(time=times, temperature=temps, humidity=humds))
# #
# # data_df.to_csv(r'./temp_hum_data.csv')

# %%
