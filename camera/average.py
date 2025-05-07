import numpy as np

def initialize_composite_state(h, w):
    return {
        "hue_x":  np.zeros((h, w), dtype=np.float32),
        "hue_y":  np.zeros((h, w), dtype=np.float32),
        "sat":    np.zeros((h, w), dtype=np.float32),
        "bri":    np.zeros((h, w), dtype=np.float32),
        "weight": np.zeros((h, w), dtype=np.float32),
    }

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

def update_composite_state(composite, rgb_frame, decay=0.995):
    f = rgb_frame.astype(np.float32) / 255.0
    h, s, v = rgb_to_hsv_np(f)
    w = v  # brightness as weight

    ang = h * 2 * np.pi
    composite["hue_x"]  = decay * composite["hue_x"] + np.cos(ang) * w
    composite["hue_y"]  = decay * composite["hue_y"] + np.sin(ang) * w
    composite["sat"]    = decay * composite["sat"]   + s * w
    composite["bri"]    = decay * composite["bri"]   + v * w
    composite["weight"] = decay * composite["weight"] + w

def composite_to_image(composite):
    h = np.arctan2(composite["hue_y"], composite["hue_x"]) / (2*np.pi)
    h %= 1.0

    w = composite["weight"] + 1e-6
    s = np.clip(composite["sat"] / w, 0, 1)
    v = np.clip(composite["bri"] / w, 0, 1)

    return hsv_to_rgb_np(h, s, v)

def hsv_to_rgb_np(h, s, v):
    i = (h*6).astype(int) % 6
    f = (h*6) - i
    p = v * (1 - s)
    q = v * (1 - f*s)
    t = v * (1 - (1-f)*s)

    r = np.select([i==0, i==1, i==2, i==3, i==4, i==5],
                  [v, q, p, p, t, v])
    g = np.select([i==0, i==1, i==2, i==3, i==4, i==5],
                  [t, v, v, q, p, p])
    b = np.select([i==0, i==1, i==2, i==3, i==4, i==5],
                  [p, p, t, v, v, q])

    return (np.dstack([r, g, b]) * 255).astype(np.uint8)

