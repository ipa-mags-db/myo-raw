"""
Module for IMU brick
"""

import sys
import time

# Phidget Libraries
from Phidget22.Devices.VoltageInput import *
from Phidget22.PhidgetException import *
from Phidget22.Phidget import *
from Phidget22.Net import *

# IMU Libraries
from tinkerforge.ip_connection import IPConnection
from tinkerforge.brick_imu import BrickIMU

# Config Data for IMU
HOST = "localhost"
PORT = 4223
UID = "61SpV5" # find out by starting brickv


intervall = 100



############################
# Class
############################

class InputHandler:
    def __init__(self):
        # Config Data for IMU
        self.HOST = "localhost"
        self.PORT = 4223
        self.UID = "61SpV5" # find out by starting brickv
        self.intervall = 100

        try:
            # Create List of handlers for every (currently 3) phidget channel
            self.chL = [VoltageInput() for i in range(0,3)]

            # Connect to IMU Brick
            self.ipcon = IPConnection() # Create IP connection
            self.imu = BrickIMU(UID, self.ipcon) # Create device object
            self.ipcon.connect(self.HOST, self.PORT) # Connect to brickd

            # Register quaternion callback to function cb_quaternion
            #
            # Set period for quaternion callback to 1s (1000ms)
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

    def startLogging(self):
        self.imu.register_callback(self.imu.CALLBACK_QUATERNION, self.cb_quaternion)

    def cb_quaternion(self, x, y, z, w):
        print("Quaternion[X]: " + str(x))
        print("Quaternion[Y]: " + str(y))
        print("Quaternion[Z]: " + str(z))
        print("Quaternion[W]: " + str(w))
        for i, ch in enumerate(self.chL):
            print("Voltage " + str(i) + ": " + str(ch.getVoltage()))
        print("")

    def VoltageInputAttached(self, e):
        try:
            attached = e
            print("\nAttach Event Detected (Information Below)")
            print("===========================================")
            print("Library Version: %s" % attached.getLibraryVersion())
            print("Serial Number: %d" % attached.getDeviceSerialNumber())
            print("Channel: %d" % attached.getChannel())
            print("Channel Class: %s" % attached.getChannelClass())
            print("Channel Name: %s" % attached.getChannelName())
            print("Device ID: %d" % attached.getDeviceID())
            print("Device Version: %d" % attached.getDeviceVersion())
            print("Device Name: %s" % attached.getDeviceName())
            print("Device Class: %d" % attached.getDeviceClass())
            print("Data Intervall: %d" % attached.getDataInterval())
            print("\n")
            attached.setDataInterval(intervall)

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





if __name__ == "__main__":

    a = InputHandler()
    a.startLogging()
    input("Press key to exit\n")
