from gpiozero import LED, Button
from signal import pause

tilt = Button(17)  # Tilt switch
led = LED(13)      # LED on GPIO 13

tilt.when_pressed = led.on
tilt.when_released = led.off

pause()

