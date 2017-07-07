import numpy as np
from myo_raw import MyoRaw
import keras
from keras.models import load_model
import os

buffer = list()
counter = 0

def callback(emg, moving, times=[]):
    global buffer
    global counter

    buffer.append(np.squeeze(m2.predict(np.expand_dims(np.expand_dims(np.array(emg,ndmin=2),axis=1),axis=-1))))

    counter += 1

    if counter > 25:
        a = np.mean(np.vstack(buffer),axis=0)
        if a[0] > a[1]:
            print("LOSE")
        else:
            print("GRIP")
        counter = 0

    if len(buffer) > 100:
        buffer.pop(0)

if __name__ == '__main__':
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"   # see issue #152
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    m2 = load_model("/home/myo/models/network_1_194_178_9811.h5")

    print(m2.summary())
    m = MyoRaw()

    m.add_emg_handler(callback)

    m.connect()

    while True:
        m.run(1)

    m.disconnect()
