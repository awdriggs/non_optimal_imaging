from PIL import Image
from picamera2 import Picamera2
import time

picam2 = Picamera2()

preview_config = picam2.create_still_configuration(main={"size": (240, 135)})
capture_config = picam2.create_still_configuration(main={"size": (1024, 768)})

def start_preview():
    picam2.configure(preview_config)
    picam2.start()
    time.sleep(1)

def capture_fullres_image(path="/home/awdriggs/Pictures/capture.jpg"):
    picam2.stop()
    picam2.configure(capture_config)
    picam2.start()
    time.sleep(0.5)

    image_array = picam2.capture_array("main")
    image = Image.fromarray(image_array)
    image.save(path)

    print(f"Saved: {path}")

    picam2.stop()
    picam2.configure(preview_config)
    picam2.start()

def get_preview_frame():
    return picam2.capture_array("main")

def get_camera():
    return picam2

