
import board
import neopixel

# Update this to match the number of NeoPixel LEDs connected to your board.
num_pixels = 1 
pixel = board.GP13

pixels = neopixel.NeoPixel(pixel, num_pixels)
pixels.brightness = 0.2 #tune

while True:
    pixels.fill((102, 255, 153))

