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

# --- Optional font setup ---
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
except:
    font = ImageFont.load_default()

# --- Draw centered text ---
text = "Hello, asshole!"
# Get text bounding box (left, top, right, bottom)
bbox = draw.textbbox((0, 0), text, font=font)

text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]

# Center the text
x = (width - text_width) // 2
y = (height - text_height) // 2

# Draw text
draw.text((x, y), text, font=font, fill=(255, 255, 0))

# --- Show it on the display ---
disp.image(image)

