import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789

# --- Display pin setup ---
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)

# --- SPI config ---
BAUDRATE = 24000000
spi = board.SPI()

# --- Display setup for 1.14" TFT (240x135) ---
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
    baudrate=BAUDRATE,
)

# --- Get display size (depends on rotation) ---
if disp.rotation % 180 == 90:
    height = disp.width
    width = disp.height
else:
    width = disp.width
    height = disp.height

# --- Create blank image and draw object ---
image = Image.new("RGB", (width, height), (0, 0, 0))
draw = ImageDraw.Draw(image)
draw.rectangle((0, 0, width, height), fill=(255, 0, 255))

# --- Show it on the display ---
disp.image(image)
