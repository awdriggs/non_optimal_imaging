#take a reading from the color sensor and converts it to rgb.

from time import sleep
import board
import busio  # Use busio for I2C communication
from adafruit_as7341 import AS7341

# Define I2C using specific pins for the Raspberry Pi Pico
# blue qt stemma cable goes to 16
# yellow qt stemma calbe goes to 17
i2c = busio.I2C(scl=board.GP17, sda=board.GP16)  # Replace with the correct pins

sensor = AS7341(i2c) #color sensor on a breakout board


def bar_graph(read_value):
    scaled = int(read_value / 1000)
    return "[%5d] " % read_value + (scaled * "*")

def rgb():
    channels = get_channels() # a dict, ignoring the data you don't need

    print(channels)
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

while True:
    print(rgb())
    print("\n------------------------------------------------")
    sleep(1)
