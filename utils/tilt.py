from gpiozero import Button, LED
from signal import pause

# Tilt sensors (closed = connected to GND, so enable pull_up)
sensor1 = Button(17, pull_up=True)
sensor2 = Button(27, pull_up=True)

# LED
led = LED(13)

def update_led():
    # Both sensors closed (i.e. pressed) → LED on
    if sensor1.is_pressed and sensor2.is_pressed:
        led.on()
    else:
        led.off()

# Hook up events
for sensor in (sensor1, sensor2):
    sensor.when_pressed = update_led
    sensor.when_released = update_led

# Set initial state
update_led()

# Wait for events
pause()

