# camera.py, handle
# full resoltion could be 4608 x 2592, but this slows down on the pi and makes user experience crap

from PIL import Image
from picamera2 import Picamera2
import time

class CameraController:
    def __init__(self, preview_size=(640, 360), capture_size=(1920, 1080)):
        self.picam2 = Picamera2()

        # print(self.picam2.sensor_modes)

        self.preview_config = self.picam2.create_still_configuration(main={"size": preview_size}, sensor={"output_size": (2304, 1296)}) #ouput size needs to match caputre size otherwise we get weird zooms
        self.capture_config = self.picam2.create_still_configuration(main={"size": capture_size})
        self.current_config = "preview"
        self.preview_size = preview_size
        self.capture_size = capture_size

        self.picam2.configure(self.preview_config)
        self.picam2.start()
        # print("📷 Preview config:", self.picam2.camera_config)
        time.sleep(1)

    def start_preview(self):
        if self.current_config != "preview":
            self.picam2.stop()
            self.picam2.configure(self.preview_config)
            self.picam2.start()
            self.current_config = "preview"

    def stop(self):
        self.picam2.stop()

    def capture_image_array(self):
        """Capture a full-res image and return as array (without saving)."""
        if self.current_config != "capture":
            self.picam2.stop()
            self.picam2.configure(self.capture_config)
            self.picam2.start()
            self.current_config = "capture"
            # print("📷 Capture config:", self.picam2.camera_config)

        # time.sleep(0.5)
        for _ in range(1): #flush stale frames
            self.picam2.capture_array("main")


        image_array = self.picam2.capture_array("main")
        # time.sleep(3)

        self.start_preview()
        return image_array

    def get_frame(self):
        """Get current preview frame."""
        return self.picam2.capture_array("main")

