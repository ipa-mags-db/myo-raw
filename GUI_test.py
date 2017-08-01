import PyQt5.QtGui
import PyQt5.QtCore
import PyQt5.QtWidgets
import sys
import logging
from myo_test import classifier

import mock
from mock import Mock
import random,math,time

class mockClassifier:
    counter = 0
    bufferSize = 10

    def __init__(self,name):
        logging.debug("Trying to load model: " + name)

    def __enter__(self):
        logging.debug("Entering Context manager for classifier")
        return self

    def __exit__(self, type, value, traceback):
        logging.debug("Exiting Context manager for classifier")

    def changeBufferSize(self,bs):
        self.bufferSize = bs
        logging.debug("wanted to change bufferSize to " + str(bs))

    def run(self):
        self.counter += 1
        if self.counter > 100:
            self.counter = 0
        time.sleep(0.01)

    def classify(self):
        a = min( random.random()*10 + self.bufferSize, 100)/100
        return [a, 1-a]

class Threader(PyQt5.QtCore.QThread):
    classProbs_sig = PyQt5.QtCore.pyqtSignal(list)
    bufferSize_sig = PyQt5.QtCore.pyqtSignal(int)
    breakFlag_sig = PyQt5.QtCore.pyqtSignal()
    bufferSize = 50
    breakFlag = False

    def __init__(self,name):
        PyQt5.QtCore.QThread.__init__(self)
        self.bufferSize_sig.connect(self.changeBufferSize)
        self.breakFlag_sig.connect(self.abort)
        self.name = name

    def abort(self):
        self.breakFlag = True

    def changeBufferSize(self,bs):
        self.bufferSize = bs
        try:
            self.CF.changeBufferSize(bs)
        except:
            logging.debug("failed to set logger size")
        logging.debug("logger size: " + str(bs))

    def run(self):
        logging.debug("starting up classifier")
        with classifier(self.name) as self.CF:
            counter = 0

            while not self.breakFlag:
                self.CF.run()
                counter += 1
                if counter > 10:
                    self.classProbs_sig.emit(self.CF.classify())
                    counter = 0

            logging.debug("wrapping up classifier")
        logging.debug("ending runner")


class GripGUI:

    _connectState = False

    def __init__(self, geo):

        self.app = PyQt5.QtWidgets.QApplication(sys.argv)
        self.widget = PyQt5.QtWidgets.QWidget()

        # Debug Label TODO Remove if not needed anymore
        self.label = list()
        for i in range(0,20):
            self.label.append(PyQt5.QtWidgets.QLabel("<h1><b> " + str(i)  +" </b></h1>"))
            self.label[i].setAlignment(PyQt5.QtCore.Qt.AlignCenter)


        # Labels for Grip / No grip
        self.gripLabel = PyQt5.QtWidgets.QLabel("<h1><b> GRIP </b></h1>")
        self.gripLabel.setAlignment(PyQt5.QtCore.Qt.AlignCenter)

        self.noLabel   = PyQt5.QtWidgets.QLabel("<h1><b> NO </b></h1>")
        self.noLabel.setAlignment(PyQt5.QtCore.Qt.AlignCenter)

        # label for slider
        self.sliderTextLabel    = PyQt5.QtWidgets.QLabel("<b>Buffer Size:</b>")
        self.sliderLabel        = PyQt5.QtWidgets.QLabel("<b>10</b>")
        self.sliderLabel.setAlignment(PyQt5.QtCore.Qt.AlignCenter)

        # Bar for detection probability
        self.gripbar = PyQt5.QtWidgets.QProgressBar()
        self.gripbar.setOrientation(PyQt5.QtCore.Qt.Vertical)
        self.gripbar.setAlignment(PyQt5.QtCore.Qt.AlignCenter)

        # Buttons
        self.startButton  = PyQt5.QtWidgets.QPushButton("Start")
        self.startButton.clicked.connect(self._onStartButtonClick)

        self.chooseButton = PyQt5.QtWidgets.QPushButton("Choose")
        self.chooseButton.clicked.connect(self._onChooseButtonClick)

        # Slider
        self.slider = PyQt5.QtWidgets.QSlider(PyQt5.QtCore.Qt.Horizontal)
        self.slider.setMaximum(100)
        self.slider.setMinimum(1)
        self.slider.valueChanged.connect(self._onSliderChange)
        self.slider.setTickInterval(5)
        self.slider.setValue(50)

        # Layout stuff
        self.vbox0 = PyQt5.QtWidgets.QVBoxLayout()

        self.hbox0_0 = PyQt5.QtWidgets.QHBoxLayout()
        self.vbox0_0_0 = PyQt5.QtWidgets.QVBoxLayout()
        self.vbox0_0_1 = PyQt5.QtWidgets.QVBoxLayout()

        self.hbox0_1 = PyQt5.QtWidgets.QHBoxLayout()
        self.vbox0_1_0 = PyQt5.QtWidgets.QVBoxLayout()
        self.vbox0_1_1 = PyQt5.QtWidgets.QVBoxLayout()

        self.vbox0.addLayout(self.hbox0_0)
        self.vbox0.addLayout(self.hbox0_1)

        self.hbox0_0.addWidget(self.gripLabel)
        self.hbox0_0.addWidget(self.gripbar)
        self.hbox0_0.addWidget(self.noLabel)

        #self.hbox0_1.addLayout(self.vbox0_1_0)
        self.hbox0_1.addLayout(self.vbox0_1_1)

        self.vbox0_1_0.addWidget(self.chooseButton)
        self.vbox0_1_0.addWidget(self.label[2])

        self.vbox0_1_1.addWidget(self.sliderLabel)
        self.vbox0_1_1.addWidget(self.slider)
        self.vbox0_1_1.addWidget(self.startButton)


        self.widget.setLayout(self.vbox0)
        self.widget.setGeometry(*geo)

        # Init variables
        self.bufferSize = self.slider.value()

    def _onChooseButtonClick(self):
        # TODO actually implement choose dialog
        logging.debug('Choose Button Clicked')
        pass



    def _onStartButtonClick(self):
        logging.debug('Start Button Clicked')
        if self._connectState:
            self.startButton.setText("Exit")
            self.workerThread.breakFlag_sig.emit()
            self._connectState = False
            del self.workerThread

        elif not self._connectState:
            #name = "/home/myo/models/network_1_194_178_9811.h5"
            #name = "/home/myo/models/network_1_175_75_9848.h5"
            name = "/home/myo/models/network_1_100_50_10000.h5"
            self.startButton.setText("Stop")
            self.workerThread = Threader(name)
            self.workerThread.classProbs_sig.connect(self._updateBar)
            self.workerThread.bufferSize_sig.emit(self.slider.value())
            #self.workerThread.bufferSize = self.slider.value()

            self.workerThread.start()
            self._connectState = True

    def _updateBar(self,probs):
        a = 0
        for i in probs:
            a += i

        for i,p in enumerate(probs):
            probs[i] = p/a


        #logging.debug("probs["+str(0)+"] = " + str(probs[0]) + "  || " + "probs[" + str(1) + "] = " + str(probs[1]))
        self.gripbar.setValue(int(probs[0]*100))


        if probs[1] > 0.6:
            self.gripLabel.setStyleSheet('color: green')
        elif probs[1] < 0.4:
            self.gripLabel.setStyleSheet('color: white')
        else:
            self.gripLabel.setStyleSheet('color: grey')


        if probs[0] > 0.6:
            self.noLabel.setStyleSheet('color: green')
        elif probs[0] < 0.4:
            self.noLabel.setStyleSheet('color: white')
        else:
            self.noLabel.setStyleSheet('color: grey')






    def _onSliderChange(self):
        self.bufferSize = self.slider.value()
        self.sliderLabel.setText("<b>" + str(self.slider.value()) + "</b>")
        try:
            self.workerThread.bufferSize_sig.emit(self.slider.value())
        except:
            logging.debug('workerThread doesnt seem to exist yet')
        logging.debug('BufferSize changed to %d', self.bufferSize)



    def show(self):
        """Function to actually draw the app and execute it

        This needs to run in its own thread and is responsible for the callbacks
        """
        self.widget.show()
        self.app.exec_()
        sys.exit()


if __name__ == '__main__':
    print(sys.argv)
    if len(sys.argv) > 1:
        if sys.argv[1] == '--debug':
            print("debug")
            logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
            print(classifier.__module__ +"."+ classifier.__class__.__name__)
            classifier = mockClassifier

    else:
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    logging.debug('Welcome to the Jungle')
    gui = GripGUI([300,300,300,300])
    gui.show()
