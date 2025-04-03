
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
from pathlib import Path

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
playback_button = Button(21, bounce_time=0.1)
forward_button = Button(20, bounce_time=0.1)

camera_lock = Lock()

# === Image Capture Function ===
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

# === Display Shit === 
display_mode = "off"
# Backlight control
backlight = digitalio.DigitalInOut(board.D18)
backlight.direction = digitalio.Direction.OUTPUT
backlight.value = False  # Backlight ON

# === Preview Loop in a Background Thread ===
def update_display():
    while True:
        if display_mode == "preview":
            with camera_lock:
                frame = picam2.capture_array("main")
            image = Image.fromarray(frame, 'RGB')
        elif display_mode == "playback":
            images = get_images()

            if get_images: #has at least one image
                image = Image.open(path / images[playback_index])
            else: 
                print("no images")
                image = blank_image

            # image = Image.open("blinka.jpg") 
        else:
            image = blank_image

        image = image.resize((width, height))  
        disp.image(image)
        time.sleep(0.03)  # ~30fps

# Start the preview loop in a thread
threading.Thread(target=update_display, daemon=True).start()

def update_backlight():
    backlight.value = (display_mode != "off")

def set_display_mode(mode):
    global display_mode
    if mode == display_mode:
        display_mode = "off"
    else:
        display_mode = mode
    update_backlight()
    print(f"Display mode: {display_mode}")

def handle_capture_button():
    global playback_on_off
    if playback_on_off:
       toggle_playback() 
    else:
        capture_image()

num_images = 0
playback_index = 0

# playback shit
path = Path("/home/awdriggs/Pictures")

def get_images():
    image_list = [f.name for f in path.iterdir() if f.is_file()]
    global num_images
    num_images = len(image_list)
    return image_list 

def navigate(direction):
    global playback_index
    if direction == "forward":
        playback_index += 1

        if playback_index > num_images - 1:
            playback_index = 0

        print(f"{playback_index + 1} / {num_images}")
        

def test_button():
    print("button working");

button.when_pressed = handle_capture_button 
toggle_button.when_pressed = lambda: set_display_mode("preview")
playback_button.when_pressed = lambda: set_display_mode("playback")
forward_button.when_pressed = lambda: navigate("forward")

pause()

