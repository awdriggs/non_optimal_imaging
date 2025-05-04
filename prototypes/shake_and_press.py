from gpiozero import LED, Button
from signal import pause
from threading import Timer

shake_one = Button(27)
shake_two = Button(22)
trigger_button = Button(4)
led = LED(13)

led_timeout = 0.8
shake_window = 0.2
led_timer = None
shake_active = False
shake_timer = None
button_ready = True

def turn_off_led():
    led.off()
    print("no shake")

def reset_shake():
    global shake_active
    shake_active = False

def shake_detected():
    global shake_active, shake_timer
    shake_active = True
    print("shake")
    led.on()
    if shake_timer:
        shake_timer.cancel()
    shake_timer = Timer(shake_window, reset_shake)
    shake_timer.start()

    global led_timer
    if led_timer:
        led_timer.cancel()
    led_timer = Timer(led_timeout, turn_off_led)
    led_timer.start()

def trigger_pressed():
    global button_ready
    if button_ready and shake_active:
        print("capture")
        button_ready = False

def trigger_released():
    global button_ready
    button_ready = True

shake_one.when_pressed = shake_detected
shake_two.when_pressed = shake_detected
trigger_button.when_pressed = trigger_pressed
trigger_button.when_released = trigger_released

pause()

