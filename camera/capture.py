# capture.py
from PIL import Image
import numpy as np
from pathlib import Path
import time
from camera import CameraController
from gpiozero import PWMLED
from leds import status_led

#camera specific libs
import random
import copy

# Setup paths
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"
CAPTURES_DIR = FRONTEND_DIR / "captures"

SAVE_FULLRES = True  # Only saves fullres image if True

CAMERA_NAME = "no03"

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

def capture_image(camera, camera_lock):
    print("📸 Capturing Fullres and Average Color...")

    with camera_lock:
        status_led.value = 0.2  # set brightness
        status_led.blink(on_time=0.2, off_time=0.2)

        # === Prepare save folders
        base_dir = Path(__file__).resolve().parent
        frontend_dir = base_dir / "frontend"
        fullres_dir = frontend_dir / "fullres"
        captures_dir = frontend_dir / "captures"

        fullres_dir.mkdir(parents=True, exist_ok=True)
        captures_dir.mkdir(parents=True, exist_ok=True)

        # === Get base filename
        filename = generate_capture_filename(CAMERA_NAME)

        fullres_filename = f"fullres-{filename}"

        fullres_path = fullres_dir / fullres_filename
        save_path = captures_dir / filename 


        UPSCALED_SIZE = camera.capture_config["main"]["size"]
        # === Always capture ONE fullres frame
        camera.picam2.stop()
        camera.picam2.configure(camera.capture_config)
        camera.picam2.start()
        time.sleep(0.5)

        # Get image from camera
        array = camera.capture_image_array()

        # === Save Fullres if enabled
        if SAVE_FULLRES:
            Image.fromarray(array).save(fullres_path)
            print(f"✅ Fullres saved to {fullres_path}")
        else:
            print("⚡ Fullres saving skipped (SAVE_FULLRES=False)")

        # rescale code goes here...
        image = Image.fromarray(array)

        # downscaled = image.resize((6, 2), Image.BOX)
        # downscaled = image.resize((6, 2), Image.NEAREST)
        downscaled = image.resize((6, 2), Image.LANCZOS)

        # upscaled = image.resize(UPSCALED_SIZE, resample=Image.NEAREST)
        # upscaled = image.resize(UPSCALED_SIZE, resample=Image.BILINEAR)
        upscaled = downscaled.resize(UPSCALED_SIZE, resample=Image.BICUBIC)
        upscaled.save(save_path)
        print(f"✅ Low-res upscaled saved to {save_path}")

        status_led.off()
