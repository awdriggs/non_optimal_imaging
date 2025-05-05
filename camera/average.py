# no05 specific function
# does pixel averaging using hsb color values
# called by capture.py and probably main.py

# from PIL import Image
import numpy as np

# fucntions
def initialize_composite_state(height, width):
    shape = (height, width)
    return {
        "hue_x": np.zeros(shape, dtype=np.float32),
        "hue_y": np.zeros(shape, dtype=np.float32),
        "sat":   np.zeros(shape, dtype=np.float32),
        "bri":   np.zeros(shape, dtype=np.float32),
        "weight": np.zeros(shape, dtype=np.float32),
    }
     
def update_composite_state(composite, rgb_frame, decay=0.995):
    from colorsys import rgb_to_hsv

    frame = rgb_frame.astype(np.float32) / 255.0
    r, g, b = frame[..., 0], frame[..., 1], frame[..., 2]

    hsv = np.vectorize(rgb_to_hsv)(r, g, b)
    h, s, v = hsv

    h_rad = h * 2 * np.pi  # hue as angle
    weight = s

    composite["hue_x"] = decay * composite["hue_x"] + np.cos(h_rad) * weight
    composite["hue_y"] = decay * composite["hue_y"] + np.sin(h_rad) * weight
    composite["sat"]   = decay * composite["sat"]   + s
    composite["bri"]   = decay * composite["bri"]   + v
    composite["weight"] = decay * composite["weight"] + weight
     
def composite_to_image(composite):
    from colorsys import hsv_to_rgb

    h = np.arctan2(composite["hue_y"], composite["hue_x"]) / (2 * np.pi)
    h[h < 0] += 1.0

    s = np.clip(composite["sat"] / (composite["weight"] + 1e-6), 0, 1)
    v = np.clip(composite["bri"] / (composite["weight"] + 1e-6), 0, 1)

    rgb = np.vectorize(hsv_to_rgb)(h, s, v)
    r, g, b = [np.clip(x * 255, 0, 255).astype(np.uint8) for x in rgb]
    return np.stack([r, g, b], axis=-1)
      
