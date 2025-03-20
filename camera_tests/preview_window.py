# starts the pi camera 
# if a button is pressed the preview stops

import RPi.GPIO as GPIO
import time

from picamera2 import Picamera2, Preview 
from libcamera import Transform
import time 

# Define the GPIO pin
BUTTON_PIN = 14  # Change this if your button is on a different pin

# Setup GPIO
GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Enable internal pull-up resistor

picam2 = Picamera2()
# picam2.start_preview(Preview.QTGL, x = 100, y =200, width=800, height=600, transform=Transform(hflip=1))
picam2.start_preview(Preview.QT, x = 100, y =200, width=800, height=600, transform=Transform(hflip=1))
picam2.start()

try:
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:  # Button pressed (LOW because of pull-up)
            time.sleep(0.2)  # Debounce delay
            picam2.stop_preview()
        else:
            time.sleep(0.1)  # Short delay to avoid excessive CPU usage
except KeyboardInterrupt:
    print("\nExiting...")
finally:
    GPIO.cleanup()  # Cleanup GPIO on exit


