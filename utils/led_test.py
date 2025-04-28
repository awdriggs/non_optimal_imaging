# led_test.py

from gpiozero import LED
import time

# Define LEDs
yellow_led = LED(13)
green_led = LED(19)

print("🧪 LED Test: Alternating flash on GPIO13 and GPIO19...")

while True:
    yellow_led.on()
    green_led.off()
    time.sleep(0.5)

    yellow_led.off()
    green_led.on()
    time.sleep(0.5)

