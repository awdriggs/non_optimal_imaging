# capture.py

from pathlib import Path
from camera import CameraController

# Setup paths
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"
CAPTURES_DIR = FRONTEND_DIR / "captures"

# Use the shared CameraController instance (already started in main)
# (We won't create a second camera here)

def capture_image(camera, camera_lock):
    """Capture a full-res image and save to Captures folder."""
    with camera_lock:
        print("📸 Capturing full-res image...")
        filename = camera.generate_capture_filename()
        save_path = CAPTURES_DIR / filename
        camera.capture_and_save_image(save_path)
        print(f"✅ Saved: {save_path}")

