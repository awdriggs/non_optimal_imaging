# leds_test.py
from gpiozero import LED

# Define LEDs
yellow_led = LED(13)
green_led = LED(19)

print("🧹 LED reset: turn off the leds...")

green_led.off()
yellow_led.off()

