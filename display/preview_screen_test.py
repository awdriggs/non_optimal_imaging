from picamera2 import Picamera2
import digitalio
import board
import time
from PIL import Image, ImageDraw
from adafruit_rgb_display import st7789  # pylint: disable=unused-import

# Configuration for CS and DC pins (these are PiTFT defaults):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 24000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

disp = st7789.ST7789(
    spi, 
    rotation=90, 
    width=135, 
    height=240, 
    # rotation=90,
    # width=240,
    # height=135,
    x_offset=53, 
    y_offset=40, # 1.14" ST7789
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
if disp.rotation % 180 == 90:
    height = disp.width  # we swap height/width to rotate it to landscape!
    width = disp.height
else:
    width = disp.width  # we swap height/width to rotate it to landscape!
    height = disp.height

print(f"Width: {width}, Height: {height}")
print(f"Display Width: {disp.width}, Display Height: {disp.height}")

image = Image.new("RGB", (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image)


# Scale the image to the smaller screen dimension
# image_ratio = image.width / image.height
# screen_ratio = width / height
# if screen_ratio < image_ratio:
#     scaled_width = image.width * height // image.height
#     scaled_height = height
# else:
#     scaled_width = width
#     scaled_height = image.height * width // image.width

# image = image.resize((scaled_width, scaled_height), Image.BICUBIC)

# Crop and center the image
# x = scaled_width // 2 - width // 2
# y = scaled_height // 2 - height // 2
# image = image.crop((x, y, x + width, y + height))
# draw.text((10, 120), "Hello, Pi!", fill=(255, 255, 0))


# # Display image.
# disp.image(image)

# Setup camera
picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration(main={"size": (240, 135)}))
picam2.start()
time.sleep(1)  # Give camera time to warm up

# Display live preview
while True:
    frame = picam2.capture_array("main")  # RGB frame as numpy array
    image = Image.fromarray(frame, 'RGB')  # Convert to PIL image
    disp.image(image)  # Draw to screen
