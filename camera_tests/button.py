import RPi.GPIO as GPIO
import time

# Define the GPIO pin
BUTTON_PIN = 14  # Change this if your button is on a different pin

#Setup GPIO
GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Enable internal pull-up resistor

print("Press the button to test... (Ctrl+C to exit)")

try:
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:  # Button pressed (LOW because of pull-up)
            print("Button Pressed!")
            time.sleep(0.2)  # Debounce delay
        else:
            print("Button Not Pressed")
        time.sleep(0.1)  # Short delay to avoid excessive CPU usage
except KeyboardInterrupt:
    print("\nExiting...")
finally:
    GPIO.cleanup()  # Cleanup GPIO on exit

