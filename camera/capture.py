from PIL import Image
import numpy as np
from pathlib import Path
from camera import CameraController
from gpiozero import PWMLED
from leds import status_led
from push import send_image_to_server
import time
import random

PUSH_TO_SERVER = False

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"
CAPTURES_DIR = FRONTEND_DIR / "captures"
CAMERA_NAME = "no06"

def generate_capture_filename(camera_name):
    captures_dir = CAPTURES_DIR
    captures_dir.mkdir(parents=True, exist_ok=True)
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

def brownian_walk_effect(array, hit_ratio=0.3):
    arr = array.copy()
    height, width, _ = arr.shape
    total_pixels = height * width
    visited = set()
    x, y = width // 2, height // 2
    while len(visited) < hit_ratio * total_pixels:
        for dx in range(-5, 5):
            for dy in range(-5, 5):
                nx, ny = np.clip(x + dx, 0, width - 1), np.clip(y + dy, 0, height - 1)
                visited.add((nx, ny))
                arr[ny, nx] = [random.randint(0, 255) for _ in range(3)]
        dx, dy = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
        x = np.clip(x + dx, 0, width - 1)
        y = np.clip(y + dy, 0, height - 1)
    return arr

def capture_image(camera, camera_lock, display):
    status_led.value = 0.2
    status_led.blink(on_time=0.2, off_time=0.2)

    with camera_lock:
        print("\U0001f4f8 Capturing full-res image...")
        filename = generate_capture_filename(CAMERA_NAME)
        save_path = CAPTURES_DIR / filename

        try:
            array = camera.capture_image_array()
            array = brownian_walk_effect(array)
            image = Image.fromarray(array)
            image.save(save_path)

            if save_path.stat().st_size == 0:
                print("zero byte")
                save_path.unlink(missing_ok=True)
                status_led.off()
                return None

            print(f"✅ Saved: {save_path}")

            flash_capture = Image.open(save_path)
            display.show_image(flash_capture)
            time.sleep(2)

        except Exception as e:
            print(f"Capture failed: {e}")
            status_led.off()
            return None

        status_led.off()

        if PUSH_TO_SERVER:
            send_image_to_server(save_path, CAMERA_NAME)
        else:
            print("   (Push to server is disabled)")

