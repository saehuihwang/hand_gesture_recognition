# Hand Gesture Recognition

This repo contains the code necessary to use Python's sklearn library to recognize hand gestures based on input from an array of photodiodes.

## Setup Outline
Below are the necessities to get gesture recognition working
* 6x6 Array of photodiodes
  * Other sizes will work but will require significant rewrites to Arduino code - Python code should be fine
* Each diode is connected via a transistor to a TIA (trans impedance amplifer)
  * The output of this TIA is connected to an analog input pin on the Arduino
  * The base/gate of each transistor is connected to a GPIO pin on the Arduino
    * This could also be done with less pins using a MUX
* Lighting on the diodes is controlled such that your hands cast well defined shadows on the diodes
* +5V supplied to photodiodes
* If using an OpAmp in your TIA, +5V and -5V supply will be required

## LED Array Output
This repo also includes code for outputting the results of the gesture recognition onto a NeoPixel LED array. While this is optional additional setup is required.
* LED array Din is connected to a PWM pin on the Arduino
* +5V supply to LED array

As an additional note, the grounds for the TIA, Arduino, and LED array must all be connected.

Worked with Josh Anderson () on this project.
