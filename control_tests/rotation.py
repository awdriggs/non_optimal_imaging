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
    rotation=270,
    x_offset=53,
    y_offset=40,
    baudrate=24000000
)

width = disp.height  # 240
height = disp.width  # 135

blank_image = Image.new("RGB", (width, height), color=(0, 0, 0))

# === Camera Setup ===
picam2 = Picamera2()
preview_config = picam2.create_still_configuration(
    main={"size": (height, width)}  # swap to match rotated camera
)
capture_config = picam2.create_still_configuration(
    main={"size": (1024, 768)}
)

picam2.configure(preview_config)
picam2.start()
time.sleep(1)

# === Button Setup ===
button = Button(4, bounce_time=0.1)
toggle_button = Button(12, bounce_time=0.1)  # sw1
playback_button = Button(23, bounce_time=0.1)  # center
forward_button = Button(18, bounce_time=0.1)  # dpad right
back_button = Button(25, bounce_time=0.1)  # dpad left

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
        image = Image.fromarray(image).transpose(Image.ROTATE_270)
        image.save("/home/awdriggs/Pictures/capture.jpg")
        print("Saved!")

        picam2.stop()
        picam2.configure(preview_config)
        picam2.start()

# === Display Control === 
display_mode = "off"
backlight = digitalio.DigitalInOut(board.D16)
backlight.direction = digitalio.Direction.OUTPUT
backlight.value = False

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

# === Preview Loop in a Background Thread ===
def update_display():
    while True:
        if display_mode == "preview":
            with camera_lock:
                frame = picam2.capture_array("main")
            image = Image.fromarray(frame, 'RGB')
        elif display_mode == "playback":
            images = get_images()
            if images:
                # image = Image.open(path / images[playback_index])
                image = Image.open(path / images[playback_index]).transpose(Image.ROTATE_270)
            else:
                print("no images")
                image = blank_image
        else:
            image = blank_image

        # Rotate to match camera orientation
        image = image.transpose(Image.ROTATE_270)

        # Resize to fit screen
        image = image.resize((width, height))
        disp.image(image)
        time.sleep(0.03)

# Start the display thread
threading.Thread(target=update_display, daemon=True).start()

# === Capture Button Behavior ===
def handle_capture_button():
    global display_mode
    if display_mode == "playback":
        display_mode = "preview"
    else:
        capture_image()

# === Playback Navigation ===
num_images = 0
playback_index = 0
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
            playback_index = (playback_index + 1) % num_images
        if direction == "back":
            playback_index = (playback_index - 1) % num_images
        print(f"{playback_index + 1} / {num_images}")

# === Button Assignments ===
button.when_pressed = handle_capture_button 
toggle_button.when_pressed = lambda: set_display_mode("preview")
playback_button.when_pressed = lambda: set_display_mode("playback")
forward_button.when_pressed = lambda: navigate("forward")
back_button.when_pressed = lambda: navigate("back")

pause()

