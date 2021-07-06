#include <Adafruit_NeoPixel.h>

/*
 * RGB Settings
 */
// Which pin on the Arduino is connected to the NeoPixels
#define PIN        12

// How many NeoPixels are attached to the Arduino
#define NUMPIXELS 256

// Stores LED array parameters
Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB);

/*
 * Transistor controls
 */
// Pin number of the analog input
const int analogPin = A0;

// The number of readings to take from a diode when averaging
const unsigned int nReadings = 150;

// Number of control pins - this should match the size of the arrays below
const int cPinsSize = 36;

// Array of all control pin numbers
const int controlPins[] = {
    32, 33, 45, 44, 52, 2,
    30, 31, 43, 42, 50, 3,
    28, 29, 41, 40, 53, 4,
    26, 27, 39, 38, 51, 5,
    24, 25, 37, 36, 49, 7,
    22, 23, 35, 34, 47, 8
    };

// LED Mapping
// The readings taken from controlPins[i] will be displayed on orderedLED[i]
const int orderedLEDs[] = {
    5,  4,  3,  2,  1,  0,
    26, 27, 28, 29, 30, 31,
    37, 36, 35, 34, 33, 32,
    58, 59, 60, 61, 62, 63,
    69, 68, 67, 66, 65, 64,
    90, 91, 92, 93, 94, 95
    };

// C Shape - 1
const int cLEDs[] = {13, 12, 17, 20, 46, 49, 78, 75, 82, 83};

// T Shape - 2
const int tLEDs[] = {175, 176, 207, 208, 209, 210, 211, 212, 213, 239, 238, 237, 240, 241, 242};

// V Shape - 3
const int vLEDs[] = {164, 162, 187, 189,196, 194, 219, 220, 221, 228, 227, 226, 251, 252, 253, 254};


/*
 * Program variables - do not change
 */
// Tracks which pin is currently selected
int selectedPin = 0;

/*
 * Initiates serial port and sets each control pin to write mode
 * Initiates RGB controls
 */
void setup() {  
  // Initialize NeoPixel object
  pixels.begin();

  // Selects no signs which sets all sign LEDs to red
  selectSign(0);

  // Update pixels
  pixels.show();
  
  // Initiate serial port
  Serial.begin(9600);

  // Arbitrarily selects the first control pin to give system a known state
  selectedPin = controlPins[0];

  // Set each control pin to write mode, sets selected pin to active low,
  // sets other pins to high
  for (int cPin : controlPins) {
    pinMode(cPin, OUTPUT);
    if (cPin != selectedPin) {
      digitalWrite(cPin, HIGH);
    } else {
      digitalWrite(cPin, LOW);
    }
  }
}

/*
 * Iterates through each photodiode, takes readings into a vector,
 * then prints the vector to the serial port
*/ 
void loop() {
  // Writes to serial port readings from each diode and saves vector into vec
  unsigned int vec[cPinsSize] = {0};
  outputVector(vec, nReadings);

  // Displays vector on LEDs
  unsigned int maxVal = getMax(vec);
  for (int i = 0; i < cPinsSize; i++) {
    pixels.setPixelColor(orderedLEDs[i], vec[i], maxVal-vec[i], maxVal-vec[i]);
  }

  // Read all available serial messages
  int result = 0;
  while (Serial.available() > 0) {
    result = Serial.read();
  }

  // Take the last serial message and display the result
  if (result != 0) {
    selectSign(result);
  }
  
  // Update pixels
  pixels.show();
}

// For each of C, T, V set LEDs to green if selected and red otherwise
void selectSign(int sign) {
  for (int pix : cLEDs) {
    pixels.setPixelColor(pix, sign==1?0:128, sign==1?128:0, 0);
  }
  for (int pix : tLEDs) {
    pixels.setPixelColor(pix, sign==2?0:128, sign==2?128:0, 0);
  }
  for (int pix : vLEDs) {
    pixels.setPixelColor(pix, sign==3?0:128, sign==3?128:0, 0);
  }
}

/* Takes pin number as input.
 * Sets last selected pin to not active (high), then sets the new
 * selected pin to active (low)
 */
void selectPin(int sPin) {
  digitalWrite(selectedPin, HIGH);
  digitalWrite(sPin, LOW);

  selectedPin = sPin;
}

/* Simply finds and returns the max integer in the array 
*/
unsigned int getMax(unsigned int vec[cPinsSize]) {
  unsigned int maximum = 0;
  for (int i = 0; i < cPinsSize; i++) {
    if (vec[i] > maximum) {
      maximum = vec[i];
    }
  }
  return maximum;
}

/* Reads the analog input n times, takes the average of all
 * readings. Note that the floor of the average is returned.
 * Outputs range from 0 to 1023.
 */
unsigned int avgAnalog(unsigned int n) {
  unsigned long readingSum = 0;
  
  // Read the analog input n times and add each reading to the sum
  for (unsigned int i=0; i < n; i++) {
    readingSum += analogRead(analogPin);
  }

  // Find and return the average reading
  return readingSum / n;
}

/* Generates a vector of the output voltages for each diode.
 * Selects each diode iterively, takes the average of
 * n readings, prints each voltage to the serial port
 * Returns the readings as a parameter (vector)
 */
void outputVector(unsigned int vector[cPinsSize], unsigned int n) {
  // Prints a 'v' byte to signal a vector is being sent
  Serial.println('v');
  
  for (int i=0; i < cPinsSize; i++) {
    selectPin(controlPins[i]);              // Select pin
    unsigned int avgReading = avgAnalog(n); // Take the average reading
    Serial.println(avgReading);             // Print reading to serial port
    vector[i] = avgReading;                 // Store reading into vector
  }
  
  // Sends 'e' byte to signal end of vector
  Serial.println('e');
}
