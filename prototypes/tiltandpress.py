# this works, but it can also take "portrait" shots straighon.
# from gpiozero import LED, Button
from signal import pause

tilt = Button(17)  # Tilt switch
led = LED(13)      # LED on GPIO 13
trigger = Button(4) # capture button

def handle_capture():
    if tilt.is_pressed:
        print("take photo")
    else:
        print("no tilt")
    

tilt.when_pressed = led.on
tilt.when_released = led.off

trigger.when_pressed = handle_capture

pause()

