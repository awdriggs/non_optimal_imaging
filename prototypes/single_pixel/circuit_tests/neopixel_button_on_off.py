import board
import neopixel
import time
import digitalio


button = digitalio.DigitalInOut(board.GP13)
button.switch_to_input(pull=digitalio.Pull.DOWN)

previous_state = False  # Track the previous button state

# Update this to match the number of NeoPixel LEDs connected to your board.
num_pixels = 1 
pixel = board.GP12
on = False

pixels = neopixel.NeoPixel(pixel, num_pixels)
pixels.brightness = 0.2

while True:
    current_state = button.value  # Read current button state

    if current_state and not previous_state:
        print("Pressed")  # Button just pressed
    elif not current_state and previous_state:
        on = not on
        print("Released")  # Button just released

    previous_state = current_state  # Update the previous state

    if on:
        pixels.fill((102, 255, 153))
    else:
        pixels.fill((0, 0, 0))


    time.sleep(0.05)  # Small delay to debounce the button
