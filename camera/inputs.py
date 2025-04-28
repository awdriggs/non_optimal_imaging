from gpiozero import Button
from pathlib import Path

# === Button Pins ===
capture_button = Button(4, bounce_time=0.1)
preview_button = Button(12, bounce_time=0.1)    # SW1
playback_button = Button(23, bounce_time=0.1)   # Center on 5D pad
forward_button = Button(18, bounce_time=0.1)    # 5D pad - right
back_button = Button(25, bounce_time=0.1)       # 5D pad - left

# === Image Folder ===
image_dir = Path("/home/awdriggs/Pictures")
image_list = []
playback_index = 0

# === Helpers ===

def get_images():
    global image_list
    image_list = sorted([f.name for f in image_dir.iterdir() if f.is_file()])
    return image_list

def get_current_image():
    if not image_list:
        get_images()
    if image_list:
        return image_dir / image_list[playback_index]
    return None

def navigate_playback(direction):
    global playback_index
    if not image_list:
        get_images()
    if not image_list:
        return

    if direction == "forward":
        playback_index = (playback_index + 1) % len(image_list)
    elif direction == "back":
        playback_index = (playback_index - 1) % len(image_list)

    print(f"Playback {playback_index + 1}/{len(image_list)}")

def init_buttons(on_capture, set_display_mode, on_navigate, get_display_mode):
    def handle_capture():
        if get_display_mode() == "playback":
            set_display_mode("preview")
        else:
            on_capture()

    capture_button.when_pressed = handle_capture
    preview_button.when_pressed = lambda: set_display_mode("preview")
    playback_button.when_pressed = lambda: set_display_mode("playback")
    forward_button.when_pressed = lambda: on_navigate("forward")
    back_button.when_pressed = lambda: on_navigate("back")

