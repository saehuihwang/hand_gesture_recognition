from arduinoInterface import Arduino

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from datetime import datetime
import keyboard

from skimage import io
import cv2
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.metrics import accuracy_score
from sklearn import svm


"""
Saves n vectors into a file as a numpy array
"""
def saveMode(arduino, args):
    if len(args) < 3:
        print('There are two required arguments: n, filename')
        return

    try:
        n = int(args[1])
    except ValueError:
        print('First argument must be an integer')
        return

    im = setupPlot()

    print('Obtaining data matrix...')
    matrix = []
    for i in range(n):
        if keyboard.is_pressed('esc'):
            break
        print('[{0}] {1}%'.format(datetime.now(), 100 * i/n))
        vec = arduino.readAdjVector()
        matrix.append(vec)
        updatePlot(im, vec)
    print('Finished getting matrix')

    np.save(args[2], np.asarray(matrix))
    print('Saved data as {0}'.format(args[2]))

"""
Displays output vectors as matplot plot
"""
def plotMode(arduino, args):
    im = setupPlot()

    while True:
        if keyboard.is_pressed('esc'):
            return
        vec = arduino.readAdjVector()
        updatePlot(im, vec)

"""Resets plot and returns handle"""
def setupPlot():
    # Plot variables
    data = np.zeros(shape=(6,6))
    _, ax = plt.subplots()
    im = ax.imshow(data, 'gray', origin='upper', interpolation='none', norm=matplotlib.colors.Normalize(0,3))

    return im

"""Updates the plot with new data, then refreshes the plot"""
def updatePlot(im, newData, delay=1e-5):
    im.set_data(np.array([newData[0:6],
                          newData[6:12],
                          newData[12:18],
                          newData[18:24],
                          newData[24:30],
                          newData[30:36]]))
    plt.draw()
    plt.pause(delay)

"""
Tries to recognize hand shapes in input data
"""
def recognizeMode(arduino, args):
    im = setupPlot()
    model = trainModel()

    while True:
        if keyboard.is_pressed('esc'):
            break

        # Reads vector
        vec = arduino.readAdjVector()
        
        # Generates prediction of hand gesture
        prediction = model.predict([vec])[0]

        try:
            result = int(prediction)
        except ValueError:
            result = 3

        # Prints the prediction and sends it to the arduino
        print(invDic[result])
        arduino.send(result)

        # Plots the vector that was just read
        updatePlot(im, vec)
         
"""Adds labels to train data"""
def addLabel(data, label):
    label = np.ones((5000,1)) * dic[label] # correctly link labels to matrices
    data = np.reshape(np.append(data, label, axis = 1), (5000,37))
    return (data)

"""Trains model based on premade data"""
def trainModel():
    Cdata = addLabel(loadData('Cdata.npy'), 'C')
    Tdata = addLabel(loadData('Tdata.npy'), 'T')
    Vdata = addLabel(loadData('Vdata.npy'), 'V')

    # combine the three hand positions and shuffle randomly
    data = np.concatenate([Cdata, Tdata, Vdata])
    np.random.shuffle(data)

    X = data[:, :36] # actual data
    Y = data[:, 36] # labels


    clf = svm.SVC()
    clf.fit(X, Y)

    return clf

"""Loads data from the specified file and normalizes each vector"""
def loadData(filename):
    data = np.load(filename)
    adjData = []
    for vector in data:
        maxVolt = max(vector)
        adjVector = [volt / maxVolt for volt in vector]
        adjData.append(adjVector)

    return np.array(adjData)

"""
Calibrates the dark current
"""
def calibrate(arduino, args):
    n = 20
    if len(args) > 1:
        try:
            n = int(args[1])
        except ValueError:
            n = 20
    
    print('Starting calibration over {0} vectors'.format(n))
    arduino.calibrate(n)
    print('Finished calibrating')

"""
Reads a data matrix from a file and displays it
"""
def playbackMode(arduino, args):
    if len(args) < 2:
        print('Expected second argument: playback `filename`')
        return
    try:
        dataIn = np.load(args[1])
    except:
        print('Failed to read numpy matrix from file {0}'.format(args[1]))
        return

    im = setupPlot()
    for vector in dataIn:
        if keyboard.is_pressed('esc'):
            break
        updatePlot(im, vector, .01)


"""
Main control - Simply loops and allows user to select a mode
"""
if __name__ == '__main__':
    """
    Constants
    """
    cmdList = {
        'save'  : saveMode,
        'plot'  : plotMode,
        'rec'   : recognizeMode,
        'cal'   : calibrate,
        'play'  : playbackMode
    }

    # Maps from gestures to integers and vice versa
    dic     = {'C':1,'T':2,'V':3}
    invDic  = {1:'C', 2:'T', 3:'V'}

    # Initialize arduino interface
    try:
        arduino = Arduino()
    except:
        print('Failed to connect with arduino - only data playback will work')
        arduino = 0

    """
    Command loop
    """
    while True:
        cmd = input('> ').lower()
        args = cmd.split()
        if len(args) < 1:
            continue

        if args[0] == 'quit' or args[0] == 'exit':
            break

        if args[0] in cmdList.keys():
            cmdList[args[0]](arduino, args)     # Run the desired command
            plt.close('all')                    # Close any plots opened
    