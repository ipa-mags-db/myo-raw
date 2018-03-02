"""
Startup script for data recording
Starts several recording session based on typelist, name and recording time as well as positions
"""



import os
# <Tool>P<Position>S<Session>_<Orientation>

#<Name><type>P<Position>S<Session>_1

##############
# Parameters #
##############
name = "felix1"
recordingTime = 15
#typeList = [('screwdriver',1),('empty',1),('weight',1),('empty',2),('hammer',1)]
typeList = [ [('force',1),('empty',1),('form',1),('empty',2),('handle',1)],
             [('force',2),('empty',3),('form',2),('empty',4),('handle',2)] ]
pos = [1,2,3,4]



if not all(isinstance(el, list) for el in typeList):
    typeList = [typeList]

for types in typeList:
    for k in pos:
        for element in types:
            filename = "{0}{1}P{2}S{3}".format(name,element[0],k,element[1])
            #print(filename)
            os.system("python data_logger.py " + filename + " " + str(recordingTime))
