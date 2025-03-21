
# starts the pi camera 

from picamera2 import Picamera2, Preview 
from libcamera import Transform
import time
from datetime import datetime
from signal import pause
from  gpiozero import Button
import random
import subprocess #needed for the ffmeg bizness
import os

picam2 = Picamera2()
# picam2.start_preview(Preview.QTGL, x = 100, y =200, width=800, height=600, transform=Transform(hflip=1))
# picam2.start_preview(Preview.QT, x = 100, y =200, width=800, height=600, transform=Transform(hflip=1))

button = Button(14)

max_height = 3040

def set_size():
    apsectRatio = 1 #square for now
    # max resolutions 4056 × 3040 
    # width = random.randrange(2, 3041, 2)  # 3041 is exclusive, step of 2 gives only even numbers
    width = random.randrange(2, 10, 2)  # 3041 is exclusive, step of 2 gives only even numbers
    height = width

    picam2.stop() 
    # picam2.still_configuration.main.size = (4056, 3040) #full res hq camera
    picam2.still_configuration.main.size = (width, height)
    picam2.configure("still")

    picam2.start()
    return width

def scale_image(filepath, width, height):
    temp_path = filepath + ".tmp.jpg"
    
    cmd = [
        "ffmpeg",
        "-y",
        "-i", filepath,
        "-vf", f"scale={width}:{height}",
        temp_path
    ]
    
    subprocess.run(cmd, check=True)

    # Replace original with resized version
    os.replace(temp_path, filepath)

# # Example usage
# resize_image("image.jpg", "image_resized.jpg", 640, 480)

def capture_image():
    size = set_size() 
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"/home/awdriggs/Pictures/random_size_{timestamp}_{size}.jpg"

    # picam2.still_configuration.main.size = (width, height)
    # picam2.still_configuration.main.size = (4056, 3040)
    # picam2.configure("still")

    # picam2.options["quality"] = qt
    picam2.capture_file(filename)
    print("captured")
    scale_image(filename, max_height, max_height)
    print("resized")

button.when_pressed = capture_image

pause()
 
# psuedo code

# choose a random size
# always make it the same aspect ratio ? square to keep it easy?
# set the resolution of the image to a random amount, w and h
# capture the photo at that resoultion
# use ffmpeg to resize the image to the highest resolution

