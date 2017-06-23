import numpy as np
from myo_raw import MyoRaw
import keras
from keras.models import load_model

buffer = list()
counter = 0

def callback(emg, moving, times=[]):
    global buffer
    global counter

    buffer.append(np.squeeze(m2.predict(np.array(emg,ndmin=2))))

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
    m2 = load_model("/home/myo/models/v1.h5")
    print(m2.summary())
    m = MyoRaw()

    m.add_emg_handler(callback)

    m.connect()

    while True:
        m.run(1)

    m.disconnect()
