import numpy as np
from datetime import datetime
from PIL import Image
from picamera2 import Picamera2
import time
import colorsys

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

def average_rgb():
    # Switch to high-res
    picam2.stop()
    picam2.configure(capture_config)
    picam2.start()
    time.sleep(0.5)

    # Get frame and convert to PIL Image
    array = picam2.capture_array("main")
    image = Image.fromarray(array)

    # Convert to NumPy array
    np_image = np.array(image)

    # Compute average color
    avg_color = np_image.reshape(-1, 3).mean(axis=0)
    avg_r, avg_g, avg_b = [int(c) for c in avg_color]

    print(f"Average color: ({avg_r}, {avg_g}, {avg_b})")

    # Create solid color image
    width, height = image.size
    solid = Image.new("RGB", (width, height), (avg_r, avg_g, avg_b))

    # Save with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    solid.save(f"/home/awdriggs/Pictures/average_{timestamp}.jpg")
    print("Saved average color image.")

    # Return to preview
    picam2.stop()
    picam2.configure(preview_config)
    picam2.start()

def capture_average_color_image():
    # Switch to high-res mode
    picam2.stop()
    picam2.configure(capture_config)
    picam2.start()
    time.sleep(0.5)

    array = picam2.capture_array("main")
    image = Image.fromarray(array)
    np_image = np.array(image)

    # # Normalize RGB to 0–1 and flatten to (N, 3)
    # pixels = np_image.reshape(-1, 3) / 255.0

    # # Convert all pixels to HSV
    # hsv_pixels = np.array([colorsys.rgb_to_hsv(*pixel) for pixel in pixels])



    # Average each HSV channel
    # avg_h = np.mean(hsv_pixels[:, 0])
    # avg_s = np.mean(hsv_pixels[:, 1])
    # avg_v = np.mean(hsv_pixels[:, 2])

    pixels = np_image.reshape(-1, 3) / 255.0
    hsv_pixels = rgb_to_hsv_np(pixels)

    avg_h, avg_s, avg_v = np.mean(hsv_pixels, axis=0)


    # Convert back to RGB
    avg_rgb = colorsys.hsv_to_rgb(avg_h, avg_s, avg_v)
    avg_r, avg_g, avg_b = [int(c * 255) for c in avg_rgb]

    print(f"Average HSV: ({round(avg_h, 2)}, {round(avg_s, 2)}, {round(avg_v, 2)})")
    print(f"Converted RGB: ({avg_r}, {avg_g}, {avg_b})")

    # Create a solid color image
    solid = Image.new("RGB", image.size, (avg_r, avg_g, avg_b))

    # Save with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    solid.save(f"/home/awdriggs/Pictures/average_{timestamp}.jpg")
    print("✅ Saved average color image.")

    # Return to preview mode
    picam2.stop()
    picam2.configure(preview_config)
    picam2.start()

def rgb_to_hsv_np(pixels):
    # Input shape: (N, 3), values 0-1
    r, g, b = pixels[:, 0], pixels[:, 1], pixels[:, 2]
    cmax = np.max(pixels, axis=1)
    cmin = np.min(pixels, axis=1)
    delta = cmax - cmin + 1e-10  # avoid divide by zero

    # Hue calculation
    h = np.zeros_like(cmax)
    mask = (cmax == r)
    h[mask] = ((g - b)[mask] / delta[mask]) % 6
    mask = (cmax == g)
    h[mask] = ((b - r)[mask] / delta[mask]) + 2
    mask = (cmax == b)
    h[mask] = ((r - g)[mask] / delta[mask]) + 4
    h = h / 6  # normalize to 0-1
    h = np.mod(h, 1.0)

    # Saturation
    s = delta / (cmax + 1e-10)

    # Brightness
    v = cmax

    return np.stack([h, s, v], axis=1)

