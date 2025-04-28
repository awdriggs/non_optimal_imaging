import threading
import time
from threading import Lock
from signal import pause
from gpiozero import Button
from PIL import Image
import camera
import display

camera_lock = Lock()
display_on_off = False

button = Button(14, bounce_time=0.1)
toggle_button = Button(16, bounce_time=0.1)

def update_display_loop():
    while True:
        if display_on_off:
            with camera_lock:
                frame = camera.get_preview_frame()
            image = Image.fromarray(frame, 'RGB')
            display.show_image(image)
        else:
            display.clear_display()

        time.sleep(0.03)

def capture_image():
    with camera_lock:
        print("Capturing...")
        camera.capture_average_color_image()

def toggle_display():
    global display_on_off
    display_on_off = not display_on_off
    display.set_backlight(display_on_off)
    print("Display is", "ON" if display_on_off else "OFF")

# Start everything
camera.start_preview()
threading.Thread(target=update_display_loop, daemon=True).start()

button.when_pressed = capture_image
toggle_button.when_pressed = toggle_display

print("🟢 Ready. Display off by default.")
pause()

