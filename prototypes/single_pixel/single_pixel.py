import time
import board
import digitalio

import busio  # Use busio for I2C communication
from adafruit_as7341 import AS7341

import neopixel

# Define I2C using specific pins for the Raspberry Pi Pico
# blue qt stemma cable goes to 16
# yellow qt stemma calbe goes to 17
i2c = busio.I2C(scl=board.GP17, sda=board.GP16)  # Replace with the correct pins

sensor = AS7341(i2c) #color sensor on a breakout board

class Button:
    def __init__(self, pin):
        self.button = digitalio.DigitalInOut(pin)
        self.button.switch_to_input(pull=digitalio.Pull.DOWN)
        self.previous_state = False  # Stores the last state
        self.on = False

    def is_pressed(self):
        """Returns True if button is currently pressed."""
        return self.button.value

    def is_released(self):
        """Returns True only when the button is released after being pressed."""
        current_state = self.button.value
        if not current_state and self.previous_state:
            self.previous_state = current_state
            self.on = not self.on #toggle on/off state
            return True
        self.previous_state = current_state
        return False

def bar_graph(read_value):
    scaled = int(read_value / 1000)
    return "[%5d] " % read_value + (scaled * "*")

def rgb():
    channels = get_channels() # a dict, ignoring the data you don't need

    # print(channels)
    # print(maxValue)
    normalized = normalize(channels)
    # print(normalized)

    r = 0.3 * normalized["F6"] + 0.5 * normalized["F7"] + 0.7 * normalized["F8"]
    g = 0.3 * normalized["F4"] + 0.7 * normalized["F5"]
    b = 0.5 * normalized["F2"] + 0.5 * normalized["F3"]

    # Normalize RGB values if any exceed 1.0
    max_rgb = max(r, g, b)
    if max_rgb > 1.0:
        r /= max_rgb
        g /= max_rgb
        b /= max_rgb

    # convert to a 0-255 scale:
    r_int = int(r * 255)
    g_int = int(g * 255)
    b_int = int(b * 255)

    return {"r": r_int, "g": g_int, "b": b_int}

def get_channels(): #package the channels as a dict
    data = {"F1": sensor.channel_415nm,
            "F2": sensor.channel_445nm,
            "F3": sensor.channel_480nm,
            "F4": sensor.channel_515nm,
            "F5": sensor.channel_555nm,
            "F6": sensor.channel_590nm,
            "F7": sensor.channel_630nm,
            "F8": sensor.channel_680nm
            }

    return data

def normalize(channels): #normalize according to the highest value
    max_val = max(channels.values()) # calc the max for normalizing
    return {key: value / max_val for key, value in channels.items()}

# Define buttons on different pins
capture = Button(board.GP13)
play = Button(board.GP14)
clear = Button(board.GP15)

colors = []

num_pixels = 1
pixel = board.GP12
on = False

pixels = neopixel.NeoPixel(pixel, num_pixels)
pixels.brightness = 0.2

while True:
    if capture.is_released():
        print("capture Released")
        color = rgb()
        colors.append(color)
        # print(colors)
        pixels.fill((color['r'], color['g'], color['b']))
        time.sleep(1);
        pixels.fill((0, 0, 0))

    if play.is_released():
        print("play Released")

    if clear.is_released():
        colors = [] #clear the colors
        print("clear  Released")

    # if(play.on):
    #     print("playing")
    #     for color in colors:
    #         pixels.fill((color['r'], color['g'], color['b']))
    #         time.sleep(0.2);

    while play.on:  # Only run the animation loop while play.on is True
        if len(colors) == 0:
            play.on = False
            break

        print("playing")
        for color in colors:
            pixels.fill((color['r'], color['g'], color['b']))
            time.sleep(0.2)

        # Check if the button is pressed again to stop the animation
            if play.is_released() :
                play.on = False  # Stop playing when button is pressed again
                pixels.fill((0, 0, 0))  # Turn off LEDs
                print("Stopped Playing")
                break  # Exit the for loop

            if clear.is_released():
                play.on = False
                pixels.fill((0, 0, 0))  # Turn off LEDs
                colors = [] #clear the colors
                break

    time.sleep(0.05)  # Small debounce delay
