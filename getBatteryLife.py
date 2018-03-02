def batPrinter(battery_level):
    print("Battery Level is %d" % battery_level)


from myo_raw import MyoRaw
import time

print("Connecting to Myo Armband...")
m = MyoRaw()
m.connect()
m.add_battery_handler(batPrinter)
connectTime = time.time()

print("connected.. now starting 20s loop")
while time.time() - connectTime < 20:
    m.run(1)


m.power_off()
#m.vibrate(3)
m.disconnect()
