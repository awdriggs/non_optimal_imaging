from PIL import Image
import numpy as np
from pathlib import Path
import time
from camera import CameraController
from gpiozero import PWMLED
from leds import status_led
#import colorsys # for hsv averaging

SAVE_FULLRES = True  # Only saves fullres image if True

CAMERA_NAME = "no01"
from push import send_image_to_server  # <--- for the exhibition, push to pi server 
PUSH_TO_SERVER = False # toggle on/off for the display

# Setup paths
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"
CAPTURES_DIR = FRONTEND_DIR / "captures"

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
        print(type(frame_fullres))
        print(frame_fullres.shape)

        small = np.array(Image.fromarray(frame_fullres).resize((160, 90)))

        # # convert form pil to np array
        # if not isinstance(frame_fullres, np.ndarray):
        #     frame_fullres = np.array(frame_fullres)

        # convert to hsv and comput average
        normed = small.astype(np.float32) / 255.0
        h, s, v = rgb_to_hsv_np(normed)
        print("converted to hsv")

        h = h * 2 * np.pi # maps hue to an angle
        print("unpacked hsv")
         
        #average hue as unit veoctrs
        x = np.cos(h)
        y = np.sin(h)
        avg_hue = np.arctan2(np.mean(y), np.mean(x)) / (2 * np.pi)
        avg_hue = avg_hue % 1.0 
        print("average the hue")

        #Average saturation and vlaue
        avg_sat = np.mean(s)
        avg_val = np.mean(v)
        print("average the sat and val")

        #Convert back to RGB
        # r, g, b = colorsys.hsv_to_rgb(avg_hue, avg_sat, avg_val)
        # r, g, b = int(r * 255), int(g * 255), int(b * 255)
        r, g, b = hsv_to_rgb_scalar(avg_hue, avg_sat, avg_val)
        print("convert back to rgb")

        print(f"🎨 Average Color: R={r} G={g} B={b}")

        width, height = frame_fullres.shape[1], frame_fullres.shape[0]
        solid_color = Image.new("RGB", (width, height), color=(r, g, b))
        solid_color.save(avgcolor_path)

        print(f"✅ Average color saved to {avgcolor_path}")
        status_led.off()

        # === Restart Preview
        camera.start_preview()
         
        if PUSH_TO_SERVER:
            send_image_to_server(avgcolor_path, CAMERA_NAME)
        else:
            print("push to server disabled")

def rgb_to_hsv_np(frame):
    """frame: H×W×3 float32 in [0,1]. Returns h,s,v each H×W in [0,1]."""
    r, g, b = frame[...,0], frame[...,1], frame[...,2]
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    d  = mx - mn

    # Hue
    h = np.zeros_like(mx)
    mask = d > 1e-6
    # red max
    idx = mask & (mx == r)
    h[idx] = ((g[idx] - b[idx]) / d[idx]) % 6
    # green max
    idx = mask & (mx == g)
    h[idx] = ((b[idx] - r[idx]) / d[idx]) + 2
    # blue max
    idx = mask & (mx == b)
    h[idx] = ((r[idx] - g[idx]) / d[idx]) + 4
    h /= 6.0

    # Saturation
    s = np.zeros_like(mx)
    s[mask] = d[mask] / mx[mask]

    # Value
    v = mx
    return h, s, v

def hsv_to_rgb_scalar(h, s, v):
    i = int(h * 6) % 6
    f = (h * 6) - i
    p = v * (1 - s)
    q = v * (1 -f * s)
    t = v * (1 - (1 - f) * s)

    #output depending on color region
    if i == 0:
        r, g, b = v, t, p
    elif i == 1:
        r, g, b = q, v, p
    elif i == 2:
        r, g, b = p, v, t
    elif i == 3:
        r, g, b = p, q, v
    elif i == 4:
        r, g, b = t, p, v
    else:
        r, g, b = v, p, q

    return int(r * 255), int(g * 255), int(b * 255)
