import board
import digitalio
from PIL import Image
import adafruit_rgb_display.st7789 as st7789

spi = board.SPI()
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)

disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    width=135,
    height=240,
    rotation=90,
    x_offset=53,
    y_offset=40,
    baudrate=24000000
)

width = disp.height
height = disp.width
blank_image = Image.new("RGB", (width, height), color=(0, 0, 0))

backlight = digitalio.DigitalInOut(board.D18)
backlight.direction = digitalio.Direction.OUTPUT
backlight.value = False

def show_image(image):
    image = image.resize((width, height))
    disp.image(image)

def clear_display():
    disp.image(blank_image)

def set_backlight(state: bool):
    backlight.value = state

