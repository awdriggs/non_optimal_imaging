
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
dc_pin = digitalio.DigitalInOut(board.D20)
reset_pin = digitalio.DigitalInOut(board.D21)

disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    width=135,
    height=240,
    # width=240,
    # height=135,
    rotation=270,
    x_offset=53,
    y_offset=40,
    baudrate=24000000
)

width = disp.height
height = disp.width
# width = disp.width
# height = disp.height

blank_image = Image.new("RGB", (width, height), color=(0, 0, 0))

# === Camera Setup ===
picam2 = Picamera2()
preview_config = picam2.create_still_configuration(main={"size": (width, height)})
# preview_config = picam2.create_still_configuration(main={"size": (height, width)})
# preview_config = picam2.create_still_configuration(main={"size": (135, 240)})
capture_config = picam2.create_still_configuration(main={"size": (1024, 768)})  # or higher

picam2.configure(preview_config)
picam2.start()
time.sleep(1)

# === Button Setup ===
button = Button(4, bounce_time=0.1)
toggle_button = Button(12, bounce_time=0.1) #sw1
playback_button = Button(23, bounce_time=0.1) #center button on five d pad
forward_button = Button(18, bounce_time=0.1) #pin 5 of five d pad
back_button = Button(25, bounce_time=0.1) #pin 5 of five d pad

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
backlight = digitalio.DigitalInOut(board.D16)
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
    global display_mode
    if display_mode == "playback":
        display_mode = "preview"
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
    if display_mode == "playback":
        if direction == "forward":
            playback_index += 1

            if playback_index > num_images - 1:
                playback_index = 0

        if direction == "back":
            playback_index -= 1

            if playback_index < 0:
                playback_index = num_images - 1

        print(f"{playback_index + 1} / {num_images}")
        

def test_button():
    print("button working");

button.when_pressed = handle_capture_button 
toggle_button.when_pressed = lambda: set_display_mode("preview")
playback_button.when_pressed = lambda: set_display_mode("playback")
forward_button.when_pressed = lambda: navigate("forward")
back_button.when_pressed = lambda: navigate("back")

pause()

