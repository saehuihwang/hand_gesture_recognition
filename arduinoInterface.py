import serial

"""
Used to interface with the arduino
 - Provides methods to read, read a vector, write, write a string,
    calibrate dark current, and adjust a vector according to dark current
"""
class Arduino (object):
    def __init__(self, port='COM3', baudrate=9600, timeout=5):
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        self.calibrate(0)

    """
    Reading
    """
    def calibrate(self, n):
        self.darkAvg = self.averageVec(n)

    # Wrapper to read one line from serial and decode the output
    def readSer(self):
        return self.ser.readline().decode('utf-8').strip()

    # Reads numbers from serial until an 'e' (end) byte is reached
    # This assumes a 'v' was just read
    def readVector(self):
        vec = []

        # Keeps reading lines from the serial port until a 'v' is encountered
        while self.readSer() != 'v':
            continue

        # Since 'v' signalled the start of a vector, we read numbers until
        # we get an 'e', which signals the end of a vector
        reading = self.readSer()
        while reading != 'e':
            try:
                # Try reading a number from serial
                vec.append(float(reading))
            except ValueError:
                # Use a zero if the reading is not a number
                vec.append(0)
            # Read another line to either get a voltage or an 'e'
            reading = self.readSer()
        return vec

    # Reads n vectors and returns their average
    def averageVec(self, n):
        sumVec = self.readVector()

        # We need this special case for n==0 so we can return the correct
        # length of vector
        if n == 0:
            return [0 for _ in range(len(sumVec))]
        if n == 1:
            return sumVec

        for _ in range(n-1):
            reading = self.readVector()
            for i in range(len(reading)):
                if i >= len(sumVec):
                    sumVec.append(reading[i])
                else:
                    sumVec[i] += reading[i]

        return [voltage / n for voltage in sumVec]

    # Adjusts the input vector by the scale factor and dark average
    def adjustVec(self, vec):
        adjustedVec = []

        # Subtracts dark current
        for i in range(len(vec)):
            adjustedVec.append(vec[i]-self.darkAvg[i])

        # Normalizes such that the max voltage is a 1
        maxVolt = max(adjustedVec)
        for i in range(len(adjustedVec)):
            adjustedVec[i] = adjustedVec[i] / maxVolt

        return adjustedVec

    # Returns a pre-adjusted vector from arduino
    def readAdjVector(self):
        return self.adjustVec(self.readVector())

    """
    Writing
    """
    def sendln(self, msg, flush=True):
        self.ser.write('{msg}\n'.encode('utf-8'))
        if flush:
            self.doFlush()

    def send(self, intMsg : int, flush=True):
        assert 0 <= intMsg < 256

        self.ser.write(bytes([intMsg]))
        if flush:
            self.doFlush()

    def doFlush(self):
        self.ser.flush()

if __name__ == '__main__':
    Arduino()