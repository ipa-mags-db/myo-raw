from myo_raw import MyoRaw
import time
import csv
import os
import sys
import threading
import curses
from datetime import datetime

# Phidget Libraries
from Phidget22.Devices.VoltageInput import *
from Phidget22.PhidgetException import *
from Phidget22.Phidget import *
from Phidget22.Net import *

# IMU Libraries
from tinkerforge.ip_connection import IPConnection
from tinkerforge.brick_imu import BrickIMU


class logger:
    def __init__(self,name, bufferSize=100):
        # create filename from date
        timestr = time.strftime("%Y%m%d-%H%M%S")
        try:
            os.mkdir("data")
        except Exception:
            pass
        self.fileName =  "data/" + name + "-" + timestr
        self.fileNameIMU = "data/" + name + "imu-" + timestr
        self.fileNameAux = "data/" + name + "aux-" + timestr
        with open(self.fileName,'w') as csvfile:
            writer = csv.writer(csvfile,delimiter='\t', quotechar='\'',quoting=csv.QUOTE_MINIMAL)
            writer.writerow(  ["t","EMG0", "EMG1", "EMG2", "EMG3", "EMG4", "EMG5", "EMG6","EMG7"] )
        with open(self.fileNameAux,'w') as csvfile:
            writer = csv.writer(csvfile,delimiter='\t', quotechar='\'',quoting=csv.QUOTE_MINIMAL)
            writer.writerow(  ["t","V0", "V1", "V2", "ACCX_EXT", "ACCY_EXT", "ACCZ_EXT","QW_EXT", "QX_EXT", "QY_EXT", "QZ_EXT"] )
        with open(self.fileNameIMU,'w') as csvfile:
            writer = csv.writer(csvfile,delimiter='\t', quotechar='\'',quoting=csv.QUOTE_MINIMAL)
            writer.writerow(  ["t","QW_IMU", "QX_IMU", "QY_IMU", "QZ_IMU" ,"ACCX", "ACCY", "ACCZ","GX", "GY", "GZ" ] )
        self.bufferSize = bufferSize
        self.bufferSizeAux = bufferSize
        self.bufferSizeIMU = bufferSize
        self.bufferIMU = []
        self.bufferAux = []
        self.buffer = []
        self.count = 0
        self.countAux = 0
        self.countIMU = 0

        self.HOST = "localhost"
        self.PORT = 4223
        self.UID = "61SpV5" # find out by starting brickv
        self.intervall = 1

        try:
            # Create List of handlers for every (currently 3) phidget channel
            self.chL = [VoltageInput() for i in range(0,3)]

            # Connect to IMU Brick
            self.ipcon = IPConnection() # Create IP connection
            self.imu = BrickIMU(self.UID, self.ipcon) # Create device object
            self.ipcon.connect(self.HOST, self.PORT) # Connect to brickd

            # Register quaternion callback to function cb_quaternion
            #
            # Set period for quaternion callback to 1s (1000ms)
            self.imu.set_acceleration_period(self.intervall)
            self.imu.set_quaternion_period(self.intervall)

        except RuntimeError as e:
            print("Runtime Exception %s" % e.details)
            print("Press Enter to Exit...\n")
            readin = sys.stdin.read(1)
            exit(1)

        for i,ch in enumerate(self.chL):
            print("Now attaching " + str(i))
            print(type(ch))
            ch.setChannel(i)
            ch.setOnAttachHandler(self.VoltageInputAttached)
            ch.setOnDetachHandler(self.VoltageInputDetached)
            ch.setOnErrorHandler(self.ErrorEvent)
            ch.openWaitForAttachment(5000)

    def __enter__(self):
        return self

    def __exit__(self,exc_type, exc_val, exc_tb):
        print ("#####################")
        print ("stopping logger ... \n")
        with open(self.fileName,'a') as csvfile:
            writer = csv.writer(csvfile,delimiter='\t', quotechar='\'',quoting=csv.QUOTE_MINIMAL)
            print ('{:10s} {:10d}'.format('Final logged #Samples:',len(self.buffer)))
            for row in self.buffer:
                writer.writerow(row)
        with open(self.fileNameAux,'a') as csvfile:
            writer = csv.writer(csvfile,delimiter='\t', quotechar='\'',quoting=csv.QUOTE_MINIMAL)
            print ('{:10s} {:10d}'.format('Final logged #Samples:',len(self.bufferAux)))
            for row in self.bufferAux:
                writer.writerow(row)
        with open(self.fileNameIMU,'a') as csvfile:
            writer = csv.writer(csvfile,delimiter='\t', quotechar='\'',quoting=csv.QUOTE_MINIMAL)
            print ('{:10s} {:10d}'.format('Final logged #Samples:',len(self.bufferIMU)))
            for row in self.bufferIMU:
                writer.writerow(row)
        print ("#####################\n")

        for ch in self.chL:
            ch.close()
        self.ipcon.disconnect()

    def getTimeStamp(self):
        return datetime.now().timestamp()

    def callback(self,data,moving,times=[]):
        self.buffer.append([self.getTimeStamp(),*data])
        self.count +=1
        if self.count > self.bufferSize:
            # reset counter
            self.count = 0
            # write new data and append it
            with open(self.fileName,'a') as csvfile:
                writer = csv.writer(csvfile,delimiter='\t', quotechar='\'',quoting=csv.QUOTE_MINIMAL)
                for row in self.buffer:
                    writer.writerow(row)

                # clear buffer
                self.buffer = []

    def callback_imu(self, quat, acc, gyro):
        self.bufferIMU.append([self.getTimeStamp(),*quat,*acc,*gyro])
        self.countIMU +=1
        if self.countIMU > self.bufferSizeIMU:
            # reset counter
            self.countIMU = 0
            # write new data and append it
            with open(self.fileNameIMU,'a') as csvfile:
                writer = csv.writer(csvfile,delimiter='\t', quotechar='\'',quoting=csv.QUOTE_MINIMAL)
                for row in self.bufferIMU:
                    writer.writerow(row)

                # clear buffer
                self.bufferIMU = []

    def startExtCallback(self):
        self.imu.register_callback(self.imu.CALLBACK_ACCELERATION, self.callbackExt)

    def callbackExt(self, x, y, z):
        tmp = list()
        tmp.append(self.getTimeStamp())
        for i, ch in enumerate(self.chL):
            tmp.append(ch.getVoltage())

        quat = self.imu.get_quaternion()
        tmp.extend([x,y,z,*quat])
        self.bufferAux.append(tmp)
        self.countAux +=1
        if self.countAux > self.bufferSizeAux:
            # reset counter
            self.countAux = 0
            # write new data and append it
            with open(self.fileNameAux,'a') as csvfile:
                writer = csv.writer(csvfile,delimiter='\t', quotechar='\'',quoting=csv.QUOTE_MINIMAL)
                for row in self.bufferAux:
                    writer.writerow(row)

                # clear buffer
                self.bufferAux = []

    def VoltageInputAttached(self, e):
        try:
            attached = e
            print("\nAttach Event Detected (Information Below)\n")
            print("===========================================\n")
            print("Library Version: %s\n" % attached.getLibraryVersion())
            print("Serial Number: %d\n" % attached.getDeviceSerialNumber())
            print("Channel: %d\n" % attached.getChannel())
            print("Channel Class: %s\n" % attached.getChannelClass())
            print("Channel Name: %s\n" % attached.getChannelName())
            print("Device ID: %d\n" % attached.getDeviceID())
            print("Device Version: %d\n" % attached.getDeviceVersion())
            print("Device Name: %s\n" % attached.getDeviceName())
            print("Device Class: %d\n" % attached.getDeviceClass())
            print("Data Intervall: %d\n" % attached.getDataInterval())
            print("\n")
            attached.setDataInterval(self.intervall)

        except PhidgetException as e:
            print("Phidget Exception %i: %s" % (e.code, e.details))
            print("Press Enter to Exit...\n")
            readin = sys.stdin.read(1)
            exit(1)

    def VoltageInputDetached(self, e):
        detached = e
        try:
            print("\nDetach event on Port %d Channel %d" % (detached.getHubPort(), detached.getChannel()))
        except PhidgetException as e:
            print("Phidget Exception %i: %s" % (e.code, e.details))
            print("Press Enter to Exit...\n")
            readin = sys.stdin.read(1)
            exit(1)

    def ErrorEvent(self, e, eCode, description):
        print("Error %i : %s" % (eCode, description))

    def VoltageChangeHandler(self, e, voltage):
        print("Voltage at channel %d: %f\n" % (e.getChannel(), voltage))

    def SensorChangeHandler(self, e, sensorValue, sensorUnit):
        print("Sensor Value: %f" % sensorValue)




def runner(stop_event,name):
    m = MyoRaw()
    with logger(name) as a:
        m.add_emg_handler(a.callback)
        m.add_imu_handler(a.callback_imu)
        a.startExtCallback()
        m.connect()
        while not stop_event.is_set():
            m.run(1)
        m.disconnect()

def printToScreen(stdscr,string,name):
    stdscr.clear()
    stdscr.refresh()
    stdscr.move(0,0)
    stdscr.addstr("Command List\n")
    stdscr.addstr("-------------\n")
    stdscr.addstr("Filename: " + str(name) + "\n")
    stdscr.addstr("NumberKeys - Start new logger appended with <key>\n")
    stdscr.addstr("P          - Pause all logging\n")
    stdscr.addstr("ESC        - Stop logger & return to console\n")
    stdscr.addstr("-------------\n\n")
    stdscr.addstr(str(string)+"\n\n\n")

def main(stdscr,name):
    global t_stop
    t_stop = threading.Event()
    t_stop.set()
    # t = threading.Thread(target=runner, args=(t_stop,name))
    k = "paused"
    printToScreen(stdscr,k,name)

    while True:
        c = stdscr.getch()
        if c != -1:
            if c >= 48 and c <= 57:
                k = c - 48
                # t_stop True -> stopped logger
                # if not stopped -> stop and reset
                if not t_stop.is_set():
                    t_stop.set()
                    print("\nrestarting logger...")
                    t.join()
                # if stopped -> just start
                t_stop.clear()
                t = threading.Thread(target=runner,args=(t_stop,name+"_"+str(k)))
                t.start()
            if c == 112:
                k = "paused"
                if not t_stop.is_set():
                    t_stop.set()
                    t.join()
            if c == 27:
                if not t_stop.is_set():
                    t_stop.set()
                    t.join()
                return

        printToScreen(stdscr,k, name)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        name = sys.argv[1]
    else:
        print("Using standard name: data-[...]")
        name = "data"

    # curses
    curses.wrapper(main,name)
