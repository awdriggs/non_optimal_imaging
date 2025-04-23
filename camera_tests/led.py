import RPi.GPIO as GPIO
import time

# Use BCM pin numbering
GPIO.setmode(GPIO.BCM)

# Set GPIO 19 as output
GPIO.setup(13, GPIO.OUT)

while True: 
    # Turn the LED on
    GPIO.output(13, GPIO.HIGH)

    # Keep it on for 5 seconds
    time.sleep(1)

    GPIO.output(13, GPIO.LOW)
    time.sleep(1)

# Clean up GPIO settings
GPIO.cleanup()

