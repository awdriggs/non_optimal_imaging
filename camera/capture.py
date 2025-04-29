# capture.py
from PIL import Image
import numpy as np
from pathlib import Path
from camera import CameraController
from gpiozero import PWMLED
from leds import status_led

# Setup paths
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"
CAPTURES_DIR = FRONTEND_DIR / "captures"

def capture_image(camera, camera_lock):
    """Capture a full-res image and save to Captures folder."""
    status_led.value = 0.2  # set brightness
    status_led.blink(on_time=0.2, off_time=0.2)

    with camera_lock:
        print("📸 Capturing full-res image...")
        filename = camera.generate_capture_filename()
        save_path = CAPTURES_DIR / filename

        # Get image from camera
        array = camera.capture_image_array()
        image = Image.fromarray(array)
        image.save(save_path)
        # camera.capture_and_save_image(save_path)
        print(f"✅ Saved: {save_path}")
        status_led.off()

