
# starts the pi camera 

from picamera2 import Picamera2, Preview 
from libcamera import Transform
import time
from datetime import datetime
from signal import pause
from  gpiozero import Button
import random

picam2 = Picamera2()
# picam2.start_preview(Preview.QTGL, x = 100, y =200, width=800, height=600, transform=Transform(hflip=1))
picam2.start_preview(Preview.QT, x = 100, y =200, width=800, height=600, transform=Transform(hflip=1))
picam2.start()

button = Button(14)


def capture_image():
    qt = random.randint(1, 95) 
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"/home/awdriggs/Pictures/image_{timestamp}_{qt}.jpg"

    picam2.options["quality"] = qt
    picam2.capture_file(filename)
    print("captured")

button.when_pressed = capture_image

pause()
