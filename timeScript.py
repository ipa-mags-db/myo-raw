import time
from myo_test import classifier

counter1 = 0
counter2 = 0
flag = 0

timeout = 0.05

name = "/home/myo/models/network_1_194_178_9811.h5"

classAvg = 0
runAvg = 0

updateRate = 0.2

with classifier(name) as CF:
    while True:
        counter1 += 1
        cfrun_start = time.time()
        CF.run(timeout)
        cfrun_end   = time.time()

        cfclass_start = time.time()
        a= CF.classify()
        print("classification: " + str(a))

        cfclass_end   = time.time()

        classAvg = updateRate * ( cfclass_end - cfclass_start ) + ( 1 - updateRate ) * classAvg
        runAvg   = updateRate * ( cfrun_end   - cfrun_start   ) + ( 1 - updateRate ) * runAvg

        if counter1 > 100:
            print("classTime: {0:1.8f} | runAvg: {1:1.8f}".format(classAvg*1000, runAvg*1000))
            counter1 = 0
            counter2 += 1

        if counter2 > 5:
            counter2 = 0
            if timeout > 2:
                flag = 1
            elif timeout < 0.05:
                flag = 0
            if flag == 1:
                timeout -= 0.01
            elif flag == 0:
                timeout += 0.01
            print("Increase timeout to " + str(timeout))
