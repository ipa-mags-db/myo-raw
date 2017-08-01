import numpy as np
from myo_raw import MyoRaw
import keras
from keras.models import load_model
import os
import sys
import collections, itertools

class classifier:
    def __init__(self,modelPath,bufferSize=25,GPU=False):
        self.buffer = collections.deque(maxlen=200)
        self.predictBuffer = collections.deque(maxlen=200)
        self.counter = 0
        self.bufferSize=bufferSize
        self.probs = np.array([0.5, 0.5])

        if not GPU:
            os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"   # see issue #152
            os.environ["CUDA_VISIBLE_DEVICES"] = ""

        if modelPath == None:
            self.model = None
        else:
            self.model = load_model(modelPath)

            print("loading model: ", modelPath)
            print("----------------------------\nModel Summary:")
            print(self.model.summary())
            print("----------------------------\n")

        self.handler = MyoRaw()

        self.handler.add_emg_handler(self.callback)

    def __enter__(self):
        self.handler.connect()
        return self

    def __exit__(self,exc_type,exc_val,exc_tb):
        self.handler.disconnect()

    def run(self,timeout=None):
        if not (timeout == None):
            self.handler.run(timeout)
        else:
            self.handler.run()

    def changeBufferSize(self,bufferSize):
        self.bufferSize = bufferSize

    def classify(self):
        if self.counter > 20:
            for i in range(0,20):
                self.predictBuffer.append(self.predict(self.buffer[i]))
            self.probs = np.mean(np.vstack(list(itertools.islice(self.predictBuffer,0,self.bufferSize))),axis=0)
            self.counter = 0
        return list(self.probs)

    def predict(self, emg):
        if not self.model == None:
            return np.squeeze(self.model.predict(np.expand_dims(np.expand_dims(np.array(emg,ndmin=2),axis=1),axis=-1)))

    def callback(self,emg, moving, times=[]):
        self.buffer.append(emg)
        self.counter += 1


if __name__ == '__main__':
    if len(sys.argv) > 2:
        name = sys.argv[1]
    else:
        print("Using default path")
        name = "/home/myo/models/network_1_194_178_9811.h5"
    a = classifier(name)
    a.run()
