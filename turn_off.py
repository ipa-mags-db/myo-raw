from myo_raw import MyoRaw

var = input("Really turning off? [y/n]")

if var == 'y' or var == 'Y':
    print("Shutting Myo Armband down...")
    m = MyoRaw()
    m.connect()
    m.power_off()
    #m.vibrate(3)
    m.disconnect()


    print("... done")
    print("RESTART by plugging it into a PC")

else:
    print("aborting...")
