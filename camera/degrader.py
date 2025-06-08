# degrade.py
import os
import time
import random
import threading
from PIL import Image
import numpy as np
import tempfile

class Degrader:
    def __init__(self, directory: str,
                 image_timestamps: dict,
                 time_limit: float = 10.0,
                 pixels_per_drop: int = 1000,
                 interval: float = 1.0):
        self.dir = directory
        self.timestamps = image_timestamps
        self.time_limit = time_limit
        self.pixels_per_drop = pixels_per_drop
        self.interval = interval
        self._thread = None
        self._stop = threading.Event()

    def _drop_pixels(self, filepath: str):
        try:
            with Image.open(filepath) as im:
                px = im.load()
                for _ in range(self.pixels_per_drop):
                    x = random.randrange(im.width)
                    y = random.randrange(im.height)
                    px[x, y] = (
                        random.randrange(256),
                        random.randrange(256),
                        random.randrange(256)
                    )
                im.save(filepath)
        except Exception as e:
            print(f"[degrader] Failed to degrade {filepath}: {e}")

    def _degrade_loop(self):
        max_time = 200       # seconds to reach full degradation
        max_stddev = 255      # max noise stddev

        while not self._stop.is_set():
            now = time.time()
            for name, last_seen in list(self.timestamps.items()):
                path = os.path.join(self.dir, name)

                if not os.path.isfile(path):
                    self.timestamps.pop(name, None)
                    continue

                elapsed = now - last_seen
                if elapsed >= self.time_limit:
                    scale = min((elapsed / max_time) ** 2, 1.0)
                    stddev = scale * max_stddev

                    self._add_gaussian_noise(path, stddev)
                    #⬅️ bump timestamp forward
                    self.timestamps[name] = last_seen + self.time_limit

            time.sleep(self.interval)

    def start(self):
        if self._thread is None:
            self._thread = threading.Thread(
                target=self._degrade_loop,
                daemon=True
            )
            self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join()

    # def _add_gaussian_noise(self, filepath: str, stddev: float):
    #     try:
    #         im = Image.open(filepath).convert("RGB")
    #         arr = np.array(im).astype(np.int16)
    #         noise = np.random.normal(0, stddev, arr.shape)
    #         arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    #         Image.fromarray(arr).save(filepath)
    #     except Exception as e:
    #         print(f"[degrader] Failed to add noise to {filepath}: {e}")

    def _add_gaussian_noise(self, filepath: str, stddev: float):
        try:
            im = Image.open(filepath).convert("RGB")
            arr = np.array(im).astype(np.int16)
            noise = np.random.normal(0, stddev, arr.shape)
            arr = np.clip(arr + noise, 0, 255).astype(np.uint8)

            # save to temp file in same dir, then overwrite original
            # tmp_path = filepath + ".tmp"
            base, _ = os.path.splitext(filepath)
            tmp_path = base + ".tmp"

            # Image.fromarray(arr).save(tmp_path)
            Image.fromarray(arr).save(tmp_path, format="JPEG")
            os.replace(tmp_path, filepath)  # atomic move
            print(f"[degrader] added noise to {os.path.basename(filepath)} with stddev={stddev:.2f}")
        except Exception as e:
            print(f"[degrader] Failed to add noise to {filepath}: {e}")
    
