import threading
import time
import digitalio
import board
from threading import Lock, Timer #needed for no04
from signal import pause
from pathlib import Path
from PIL import Image
from gpiozero import Button, LED
from camera import CameraController
from display import DisplayController
from share import start_server, stop_server
import pathlib
from capture import capture_image
from leds import status_led, share_led

# === Base Paths ===
BASE_DIR = pathlib.Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"
CAPTURES_DIR = FRONTEND_DIR / "captures"
SCREENS_DIR = FRONTEND_DIR / "screens"

NO_IMAGES_FILE = SCREENS_DIR / "no-images.jpg"
DELETE_SCREEN_FILE = SCREENS_DIR / "delete.jpg"

# === Image Folder ===
image_dir = CAPTURES_DIR

# === Global State ===
camera_lock = Lock()
display_mode = "off"
previous_display_mode = "off"
playback_index = 0
image_list = []
camera_ready = threading.Event()
sharing_active = False
confirm_delete = False

# no04 specific
led_timeout = 0.8
shake_window = 0.2
led_timer = None
shake_active = False
shake_timer = None
button_ready = True

# === Yellow LED Setup ===
status_led.blink(on_time=0.25, off_time=0.25)  # Start blinking immediately

# === Green LED Setup (Sharing Indicator) ===
share_led.off()  # Make sure it's OFF initially

# === Initialize components ===
camera = CameraController()
display = DisplayController()

# === Button Setup ===
capture_button = Button(4, bounce_time=0.1)
preview_button = Button(12, bounce_time=0.1)
playback_button = Button(23, bounce_time=0.1)
forward_button = Button(18, bounce_time=0.1)
back_button = Button(25, bounce_time=0.1)
share_button = Button(26, bounce_time=0.1)
up_button = Button(1, bounce_time=0.1)
down_button = Button(24, bounce_time=0.1)

# no04 specific
shake_one = Button(27)
shake_two = Button(22)

# === Helper Functions ===
def get_images():
    global image_list, playback_index
    image_list = sorted([f.name for f in image_dir.iterdir() if f.is_file()])
    
    if image_list:
        playback_index = len(image_list) - 1
    else:
        playback_index = 0

    return image_list

def get_current_image():
    if not image_list:
        get_images()
    if image_list:
        return image_dir / image_list[playback_index]
    return None

def navigate_playback(direction):
    global playback_index

    if display_mode != "playback":
        set_display_mode("playback") 
        return

    if not image_list:
        get_images()
    if not image_list:
        return

    if direction == "forward":
        playback_index = (playback_index + 1) % len(image_list)
    elif direction == "back":
        playback_index = (playback_index - 1) % len(image_list)

    print(f"Playback {playback_index + 1}/{len(image_list)}")

# === Actions ===
# def capture_image():
#     with camera_lock:
#         print("Capturing...")
#         camera.capture_image()
#     get_images()

def set_display_mode(mode):
    global display_mode, previous_display_mode, confirm_delete
    if mode == "playback":
        previous_display_mode = display_mode

    if mode == display_mode:
        display_mode = "off"
    else:
        display_mode = mode

    #If leaving playback mode, clear any delete confirmation
    if display_mode != "playback":
        confirm_delete = False

    display.set_backlight(display_mode != "off")
    print(f"Display mode: {display_mode}")

def get_display_mode():
    return display_mode

def get_previous_display_mode():
    return previous_display_mode

def delete_current_image():
    global playback_index

    image_path = get_current_image()
    if image_path and image_path.exists():
        print(f"🗑 Deleting {image_path}")
        image_path.unlink()  # delete file

        # Capture current index before refreshing list
        old_index = playback_index

        get_images()  # refresh image list

        # Now carefully update playback_index:
        if len(image_list) == 0:
            playback_index = 0
        elif old_index >= len(image_list):
            playback_index = len(image_list) - 1
        else:
            playback_index = old_index

# === Button Handlers ===
def handle_share():
    global sharing_active

    if sharing_active:
        print("Stopping Share Server...")
        stop_server()
        share_led.off()
        sharing_active = False
    else:
        print("Starting Share Server...")
        threading.Thread(target=start_server, daemon=True).start()
        share_led.on()
        sharing_active = True

def handle_up():
    global confirm_delete

    if display_mode != "playback":
        set_display_mode("playback") 
        return

    # Don't allow delete if no real images
    if not image_list:
        return

    if not confirm_delete:
        # First press: show confirmation
        confirm_delete = True
        print("🟠 Delete confirmation ON")
    else:
        # Second press: delete image
        delete_current_image()
        confirm_delete = False

def handle_down():
    global confirm_delete

    if display_mode != "playback":
        set_display_mode("playback") 
        return

    if confirm_delete:
        # Cancel delete
        confirm_delete = False
        print("🟡 Delete cancelled")

def handle_capture():
    global button_ready #no04 necessary
    if get_display_mode() == "playback":
        set_display_mode(get_previous_display_mode())
    else:
        if button_ready and shake_active:
            # no04 triggers when shaked and button pressed 
            button_ready = False
            capture_image(camera, camera_lock)
            get_images()

# n004 specific
def handle_shake():
    global shake_active, shake_timer
    shake_active = True

    print("shake")

    status_led.on() #indicates a shake to the user
    if shake_timer:
        shake_timer.cancel() #this cancels a shake_timer if one is already running
    shake_timer = Timer(shake_window, reset_shake) #shakes are fleeting, this makes them linger some
    shake_timer.start() #start the shake timer

    global led_timer
    if led_timer:
        led_timer.cancel() #this cancles a led timer if one is already running
    # led_timer = Timer(led_timeout, turn_off_led) 
    led_timer = Timer(led_timeout, lambda: (status_led.off())) #setup a new timer, kill the light when done
    led_timer.start() #start the led timer

def reset_shake(): #gets called when shake_timer expires
    global shake_active
    shake_active = False

def reset_button():
    global button_ready
    button_ready = True

# button handler assignments

capture_button.when_pressed = handle_capture
preview_button.when_pressed = lambda: set_display_mode("preview")
playback_button.when_pressed = lambda: set_display_mode("playback")
forward_button.when_pressed = lambda: navigate_playback("forward")
back_button.when_pressed = lambda: navigate_playback("back")
share_button.when_pressed = handle_share
up_button.when_pressed = handle_up
down_button.when_pressed = handle_down

# no04 extras
shake_one.when_pressed = handle_shake
shake_two.when_pressed = handle_shake 
capture_button.when_released = reset_button

# === Display Update Loop ===
def update_display_loop():
    while True:
        if display_mode == "preview":
            with camera_lock:
                frame = camera.get_frame()
            image = Image.fromarray(frame, 'RGB')
            display.show_image(image)

        elif display_mode == "playback":
            if confirm_delete:
                image = Image.open(DELETE_SCREEN_FILE)     
            else:
                image_path = get_current_image()
                if image_path:
                    image = Image.open(image_path)
                else:
                    image = Image.open(NO_IMAGES_FILE)     

            display.show_image(image)

            # saving this for now as an example of how to use the overlays. 
            # if confirm_delete:
            #     display.show_image(image, overlay_text="Delete? UP=Yes DOWN=No")
            # else:

        else:
            display.clear()

        time.sleep(0.03)

# === Start Everything ===
camera.start_preview()
status_led.off()

threading.Thread(target=update_display_loop, daemon=True).start()

print("Camera Ready")
set_display_mode("preview")
pause()

