from gpiozero import LED, PWMLED

status_led = PWMLED(13) # Use PWMLED for yellow since we want dimming/flashing
share_led = LED(19)
