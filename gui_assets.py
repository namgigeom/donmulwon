from __future__ import annotations

import io
import os
import threading
import urllib.request
import zipfile

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QImage


# CC0 Tiny Creatures pack by Clint Bellanger / Kenney, hosted by OpenGameArt.
# One consistent 16x16 pixel-art sheet contains all five animals used by DONMULWON.
TINY_CREATURES_URL = "https://opengameart.org/sites/default/files/tiny-creatures.zip"
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "tiny_creatures")
ZIP_PATH = os.path.join(CACHE_DIR, "tiny-creatures.zip")
TILEMAP_PATH = os.path.join(CACHE_DIR, "tilemap.png")

# tilemap.png is 10 sprites wide. The published tilemap order identifies these entries.
SPRITE_INDEX = {
    "snake": 40,     # asp
    "cat": 94,
    "crow": 126,     # crow/raven, wings up
    "turtle": 139,
    "raccoon": 168,
}


class TinyCreatureAssets:
    def __init__(self, on_ready=None):
        self.on_ready = on_ready
        self.images: dict[str, QImage] = {}
        self.ready = False
        self.loading = False

    def start(self):
        if self.ready or self.loading:
            return
        self.loading = True
        threading.Thread(target=self._load_worker, daemon=True).start()

    def _load_worker(self):
        try:
            os.makedirs(CACHE_DIR, exist_ok=True)
            if not os.path.exists(TILEMAP_PATH):
                request = urllib.request.Request(
                    TINY_CREATURES_URL,
                    headers={"User-Agent": "DONMULWON/1.0"},
                )
                with urllib.request.urlopen(request, timeout=12) as response:
                    data = response.read()
                with open(ZIP_PATH, "wb") as f:
                    f.write(data)
                with zipfile.ZipFile(io.BytesIO(data)) as zf:
                    tile_name = next(
                        (n for n in zf.namelist() if n.lower().endswith("tilemap.png")),
                        None,
                    )
                    if tile_name is None:
                        raise FileNotFoundError("tilemap.png not found in Tiny Creatures archive")
                    with zf.open(tile_name) as src, open(TILEMAP_PATH, "wb") as dst:
                        dst.write(src.read())

            sheet = QImage(TILEMAP_PATH)
            if sheet.isNull():
                raise RuntimeError("Tiny Creatures tilemap could not be loaded")

            for name, index in SPRITE_INDEX.items():
                col = index % 10
                row = index // 10
                frame = sheet.copy(QRect(col * 16, row * 16, 16, 16))
                # Nearest-neighbour scaling keeps the pixels crisp.
                self.images[name] = frame.scaled(64, 64, Qt.IgnoreAspectRatio, Qt.FastTransformation)
            self.ready = len(self.images) == len(SPRITE_INDEX)
        except Exception:
            self.images = {}
            self.ready = False
        finally:
            self.loading = False
            if self.on_ready:
                try:
                    self.on_ready()
                except Exception:
                    pass

    def get(self, name: str) -> QImage | None:
        return self.images.get(name)
