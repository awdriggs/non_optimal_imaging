from PIL import Image
from picamera2 import Picamera2
import time
from pathlib import Path
import re

IMAGE_DIR = Path("/home/awdriggs/frontend/captures")

class CameraController:
    def __init__(self, camera_name="no00", preview_size=(240, 135), capture_size=(1024, 768)):
        self.picam2 = Picamera2()
        self.preview_config = self.picam2.create_still_configuration(main={"size": preview_size})
        self.capture_config = self.picam2.create_still_configuration(main={"size": capture_size})
        self.current_config = "preview"
        self.preview_size = preview_size
        self.capture_size = capture_size
        self.camera_name = camera_name

        self.picam2.configure(self.preview_config)
        self.picam2.start()
        time.sleep(1)

    def start_preview(self):
        if self.current_config != "preview":
            self.picam2.stop()
            self.picam2.configure(self.preview_config)
            self.picam2.start()
            self.current_config = "preview"

    def capture_image(self):
        if self.current_config != "capture":
            self.picam2.stop()
            self.picam2.configure(self.capture_config)
            self.picam2.start()
            self.current_config = "capture"

        time.sleep(0.5)
        image_array = self.picam2.capture_array("main")
        image = Image.fromarray(image_array)

        # Ensure the directory exists
        IMAGE_DIR.mkdir(parents=True, exist_ok=True)

        # Find the next available filename
        existing_files = list(IMAGE_DIR.glob(f"{self.camera_name}-*.jpg"))
        numbers = [
            int(re.search(rf"{self.camera_name}-(\d+).jpg", f.name).group(1))
            for f in existing_files
            if re.search(rf"{self.camera_name}-(\d+).jpg", f.name)
        ]
        next_num = max(numbers) + 1 if numbers else 1
        filename = f"{self.camera_name}-{next_num:03}.jpg"
        path = IMAGE_DIR / filename

        image.save(path)
        print(f"Saved: {path}")

        self.start_preview()

    def get_frame(self):
        return self.picam2.capture_array("main")

    def stop(self):
        self.picam2.stop()

