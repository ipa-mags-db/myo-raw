from myo_raw import MyoRaw
import time
import csv
import os
import sys
import threading
import curses
from datetime import datetime

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

        with open(self.fileName,'w') as csvfile:
            writer = csv.writer(csvfile,delimiter='\t', quotechar='\'',quoting=csv.QUOTE_MINIMAL)
            writer.writerow(  ["t","EMG0", "EMG1", "EMG2", "EMG3", "EMG4", "EMG5", "EMG6","EMG7"] )
        with open(self.fileNameIMU,'w') as csvfile:
            writer = csv.writer(csvfile,delimiter='\t', quotechar='\'',quoting=csv.QUOTE_MINIMAL)
            writer.writerow(  ["t","QX_IMU", "QY_IMU", "QZ_IMU", "QW_IMU" ,"ACCX", "ACCY", "ACCZ","GX", "GY", "GZ" ] )
        self.bufferSize = bufferSize
        self.bufferSizeIMU = bufferSize

        self.buffer = []
        self.bufferIMU = []

        self.count = 0
        self.countIMU = 0

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
        print ("#####################\n")

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

def runner(stop_event,name):
    m = MyoRaw()
    with logger(name) as a:
        m.add_emg_handler(a.callback)
        m.add_imu_handler(a.callback_imu)
        m.connect()
        while not stop_event.is_set():
            m.run(1)
        m.disconnect()

def printToScreen(stdscr,string):
    stdscr.clear()
    stdscr.refresh()
    stdscr.move(0,0)
    stdscr.addstr("Command List\n")
    stdscr.addstr("-------------\n")
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
    printToScreen(stdscr,k)

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

        printToScreen(stdscr,k)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        name = sys.argv[1]
    else:
        print("Using standard name: data-[...]")
        name = "data"

    # curses
    curses.wrapper(main,name)
