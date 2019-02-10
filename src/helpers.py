"""
    Helper functions to control GPIO.

    Functions:
        blink(pin, time)
            Blink LED on `pin` for `time` seconds.
        
        read_temperature(pin, units)
            read_temperature from sensor connected to pin `pin` and return in `units` 

        move_servo(pin, location)
            move servo connected to `pin` to `location<min/mid/max>`

        play_buzzer(pin, stream, high_time)
            play the bistream `stream` on the buzzer at `pin` with `high_time` ms between each beep.
"""

from gpiozero import LED, Servo, Buzzer
from time import sleep
import Adafruit_DHT

def blink(pin, time):
    """ Initiliaze LED """
    our_led = LED(pin)

    """ Turn the LED ON """
    our_led.on()
    
    """ Wait for the required time """
    sleep(time)

    """ Turn the LED Off """
    our_led.off()

def read_temperature(pin, units):
    """ Initialize the sensor """
    sensor = Adafruit_DHT.DHT22  
    
    """ Read the temperature """
    _, temperature = Adafruit_DHT.read_retry(sensor, pin)
    if temperature is None: # Handle edge case when temperature isnt returned
        return None
    
    """ Store in required units """
    convert_temp = {
        'C': temperature,
        'F': (9/5*temperature + 32)
    }
    temperature = convert_temp[units]

    """ Return the temperature """
    return temperature

def move_servo(pin, location):
    """ Initialize the servo """
    servo = Servo(pin)

    """ Set functions for Location """
    location_methods = {
        'min': servo.min,
        'mid': servo.mid,
        'max': servo.max
    }
    
    """ Execute the required function """
    location_methods[location]() # Strategy Pattern

def play_buzzer(pin, stream, high_time):
    """ Initialize Buzzer """
    buzzer = Buzzer(pin)

    """ Turn the buzzer On on receiving a 1 """"
    """ Turn the buzzer Off on receiving a 0 """
    stream_methods  = {
        '1': buzzer.on,
        '0': buzzer.off
    }

    """ Iterate through the stream  """
    for item in stream:
        stream_methods[item]() # Execute Required Function
        sleep(high_time) # sleep for required time

    buzzer.off() # Turn off the Buzzer