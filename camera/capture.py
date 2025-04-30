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

SAVE_FULLRES = True  # Only saves fullres image if True

CAMERA_NAME = "no02"

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
        avgcolor_filename = filename

        fullres_path = fullres_dir / fullres_filename
        avgcolor_path = captures_dir / avgcolor_filename

        # === Always capture ONE fullres frame
        camera.picam2.stop()
        camera.picam2.configure(camera.capture_config)
        camera.picam2.start()
        time.sleep(0.5)

        frame_fullres = camera.picam2.capture_array("main")

        # === Save Fullres if enabled
        if SAVE_FULLRES:
            Image.fromarray(frame_fullres).save(fullres_path)
            print(f"✅ Fullres saved to {fullres_path}")
        else:
            print("⚡ Fullres saving skipped (SAVE_FULLRES=False)")

        # === Save Average Color (always fullres size)
        average_color = np.mean(frame_fullres, axis=(0, 1)).astype(int)
        r, g, b = average_color
        print(f"🎨 Average Color: R={r} G={g} B={b}")

        width, height = frame_fullres.shape[1], frame_fullres.shape[0]
        solid_color = Image.new("RGB", (width, height), color=(r, g, b))
        solid_color.save(avgcolor_path)

        print(f"✅ Average color saved to {avgcolor_path}")
        status_led.off()

        # === Restart Preview
        camera.start_preview()
