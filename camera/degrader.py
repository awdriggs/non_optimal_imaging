# degrade.py
import os
import time
import random
import threading
from PIL import Image

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
        while not self._stop.is_set():
            now = time.time()
            for name, last_seen in list(self.timestamps.items()):
                path = os.path.join(self.dir, name)
                if not os.path.isfile(path):
                    self.timestamps.pop(name, None)
                    continue
                if now - last_seen >= self.time_limit:
                    self._drop_pixels(path)
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

