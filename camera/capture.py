# capture.py
from PIL import Image
import numpy as np
from pathlib import Path
from camera import CameraController
from gpiozero import PWMLED
from leds import status_led

from push import send_image_to_server  # <--- for the exhibition, push to pi server 
PUSH_TO_SERVER = False # toggle on/off for the display

import time

# Setup paths
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"
CAPTURES_DIR = FRONTEND_DIR / "captures"

CAMERA_NAME = "no06" 

def generate_capture_filename(camera_name):
    """Generate a sequential filename like 'no00-0001.jpg'."""
    captures_dir = Path(__file__).resolve().parent / "frontend" / "captures"
    captures_dir.mkdir(parents=True, exist_ok=True)  # Ensure folder exists

    existing_files = list(captures_dir.glob(f"{camera_name}-*.jpg"))

    if not existing_files:
        next_num = 1
    else:
        numbers = [
            int(f.stem.split("-")[-1])
            for f in existing_files if f.stem.startswith(camera_name)
        ]
        next_num = max(numbers) + 1

    filename = f"{camera_name}-{next_num:04d}.jpg"
    return filename

def capture_image(camera, camera_lock, display):
    """Capture a full-res image and save to Captures folder."""
    status_led.value = 0.2  # set brightness
    status_led.blink(on_time=0.2, off_time=0.2)

    with camera_lock:
        print("📸 Capturing full-res image...")
        filename = generate_capture_filename(CAMERA_NAME)
        save_path = CAPTURES_DIR / filename

        try:
            # Get image from camera
            array = camera.capture_image_array()
            image = Image.fromarray(array)
            image.save(save_path)
             
            if save_path.stat().st_size == 0:
                print("zero byte")
                save_path.unlink(missing_ok=True)
                status_led.off()
                return None

          
            print(f"✅ Saved: {save_path}")
            # display whatever was saved...
            flash_capture = Image.open(save_path)
            display.show_image(flash_capture)
            time.sleep(2)

        except Exception as e:
            print(f"Capture failed: {e}")
            satus_led.off()
            return None
   
        status_led.off()
  
         # --- Conditionally push the image to the server ---
        if PUSH_TO_SERVER:
            send_image_to_server(save_path, CAMERA_NAME)
        else:
            print("   (Push to server is disabled)")
 
