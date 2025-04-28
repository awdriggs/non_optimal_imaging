# display_reset.py

import board
import digitalio
from PIL import Image
import adafruit_rgb_display.st7789 as st7789

# === TFT Setup ===
spi = board.SPI()
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D20)
reset_pin = digitalio.DigitalInOut(board.D21)

disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    width=135,
    height=240,
    rotation=270,
    x_offset=53,
    y_offset=40,
    baudrate=24000000
)

width = disp.height
height = disp.width

# === Backlight Setup ===
backlight = digitalio.DigitalInOut(board.D16)
backlight.direction = digitalio.Direction.OUTPUT

# === Create Blank Black Image ===
blank_image = Image.new("RGB", (width, height), color=(0, 0, 0))

# === Display Blank Screen ===
disp.image(blank_image)

# === Turn OFF Backlight ===
backlight.value = False

print("🧹 Display reset: Screen blanked, backlight OFF.")

