from picamera2 import Picamera2
from PIL import Image
import time
import threading
from signal import pause
from gpiozero import Button
import board
import digitalio
import adafruit_rgb_display.st7789 as st7789
from threading import Lock

# === TFT Setup ===
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

# === Camera Setup ===
picam2 = Picamera2()
preview_config = picam2.create_still_configuration(main={"size": (240, 135)})
capture_config = picam2.create_still_configuration(main={"size": (1024, 768)})  # or higher

picam2.configure(preview_config)
picam2.start()
time.sleep(1)

# === Button Setup ===
button = Button(14, bounce_time=0.1)
toggle_button = Button(16, bounce_time=0.1)

camera_lock = Lock()

display_on_off = False #start with the display off
# Backlight control
backlight = digitalio.DigitalInOut(board.D18)
backlight.direction = digitalio.Direction.OUTPUT
backlight.value = False  # Backlight ON

# === Preview Loop in a Background Thread ===
def update_display():
    while True:
        if display_on_off:
            with camera_lock:
                frame = picam2.capture_array("main")
        # frame = picam2.capture_array("main")
            image = Image.fromarray(frame, 'RGB')
            image = image.resize((width, height))  # make sure it's 135x240
            disp.image(image)
            
        else:
            disp.image(blank_image)

        time.sleep(0.03)  # ~30fps

# Start the preview loop in a thread
threading.Thread(target=update_display, daemon=True).start()

# === Button Capture Function ===
def capture_image():
    with camera_lock:
        print("Capturing hi-res...")
        picam2.stop()
        picam2.configure(capture_config)
        picam2.start()
        time.sleep(0.5)

        image = picam2.capture_array("main")
        Image.fromarray(image).save("/home/awdriggs/Pictures/capture.jpg")
        print("Saved!")

        picam2.stop()
        picam2.configure(preview_config)
        picam2.start()

def toggle_display():
    print("toggle display")
    global display_on_off
    display_on_off = not display_on_off
    backlight.value = display_on_off 


button.when_pressed = capture_image
toggle_button.when_pressed = toggle_display


pause()

