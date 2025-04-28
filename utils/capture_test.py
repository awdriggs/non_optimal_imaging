# capture_test.py
from picamera2 import Picamera2
from PIL import Image
from pathlib import Path
import time
from datetime import datetime

# === Setup Paths ===
BASE_DIR = Path(__file__).resolve().parent
TESTS_DIR = BASE_DIR / "capture_tests"
TESTS_DIR.mkdir(parents=True, exist_ok=True)  # Create folder if needed

# === Start Camera ===
picam2 = Picamera2()
preview_config = picam2.create_still_configuration(main={"size": (640, 480)})
picam2.configure(preview_config)
picam2.start()

print("📸 Camera warming up...")
time.sleep(1)  # Let it warm up a bit

# === Capture Image ===
frame = picam2.capture_array("main")
image = Image.fromarray(frame, "RGB")

# === Create Timestamped Filename ===
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"test_image_{timestamp}.jpg"
save_path = TESTS_DIR / filename

# === Save Image ===
image.save(save_path)

print(f"✅ Test image saved to {save_path}")

# === Stop Camera ===
picam2.stop()

