from gpiozero import LED, Button
from signal import pause
from threading import Timer

shake_one = Button(27)
shake_two = Button(22)
led = LED(13)

led_timeout = 1.0  # seconds to keep LED on after a shake
led_timer = None

def turn_off_led():
    led.off()
    print("no shake")

def update_led():
    global led_timer
    led.on()
    print("shake")
    if led_timer:
        led_timer.cancel()
    led_timer = Timer(led_timeout, turn_off_led)
    led_timer.start()

shake_one.when_pressed = update_led
shake_two.when_pressed = update_led

pause()

