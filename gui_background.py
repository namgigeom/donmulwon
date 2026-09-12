from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


class PixelBackground:
    """2D side-view office background. Window is always behind desks; door is beside Hyeonmu."""
    def __init__(self):
        self.time = "밤"
        self.weather = "맑음"
        self.phase = 0

    def set_time(self, value): self.time = value
    def set_weather(self, value): self.weather = value
    def tick(self): self.phase = (self.phase + 1) % 120

    def paint(self, p, w, h):
        # warm old-office palette, not neon
        sky = {"아침":"#9bb7c0", "낮":"#9fc4d2", "저녁":"#756f7c", "밤":"#283446"}.get(self.time, "#283446")
        wall = "#b79b73"; floor = "#5a4939"
        p.fillRect(0, 0, w, h, QColor("#17181a"))
        p.fillRect(18, 18, w-36, h-105, QColor(wall))
        # one long window band
        wx, wy, ww, wh = 145, 35, w-190, 260
        p.setPen(Qt.NoPen); p.setBrush(QColor("#453b32")); p.drawRect(wx-9, wy-9, ww+18, wh+18)
        p.setBrush(QColor(sky)); p.drawRect(wx, wy, ww, wh)
        self._city(p, wx, wy, ww, wh)
        # window mullions
        p.setBrush(QColor("#8a7358"))
        for x in (wx+ww//3, wx+2*ww//3): p.drawRect(x, wy, 7, wh)
        p.setBrush(QColor("#8a7358")); p.drawRect(wx, wy+wh-8, ww, 8)
        # door on the left, next to Hyeonmu; never overlaps the window
        p.setBrush(QColor("#2d211b")); p.drawRect(32, 320, 92, 220)
        p.setBrush(QColor("#755136")); p.drawRect(42, 330, 72, 200)
        p.setBrush(QColor("#c6ad7b")); p.drawRect(93, 430, 6, 6)
        # wall trim and floor
        p.setBrush(QColor("#8b7356")); p.drawRect(18, h-105, w-36, 9)
        p.setBrush(QColor(floor)); p.drawRect(18, h-96, w-36, 78)
        # floor planks
        p.setPen(QColor("#6c5843"))
        for x in range(25, w-25, 115): p.drawLine(x, h-96, x, h-18)
        p.setPen(Qt.NoPen)
        if self.weather in ("비", "눈"): self._weather(p, w, wy, wh)

    def _city(self, p, x, y, w, h):
        base = y+h
        # pixel skyline with time-dependent building lights
        light = "#d8bf75" if self.time in ("저녁", "밤") else "#d9e0d7"
        for i in range(32):
            bw = 20 + (i % 4)*9
            bh = 45 + ((i*31) % 130)
            bx = x + 7 + int(i*(w-20)/32)
            p.setBrush(QColor("#27313c" if self.time != "낮" else "#536873"))
            p.drawRect(bx, base-bh, bw, bh)
            p.setBrush(QColor(light))
            for yy in range(base-bh+12, base-9, 18):
                if (i+yy//18) % 3: p.drawRect(bx+5, yy, 5, 5)
        # distant rooftop silhouettes
        p.setBrush(QColor("#344550")); p.drawRect(x, base-22, w, 22)

    def _weather(self, p, w, y, h):
        p.setPen(Qt.NoPen); p.setBrush(QColor("#b7cbd5"))
        if self.weather == "비":
            for i in range(70):
                x = (i*97) % w
                yy = y + ((i*43 + self.phase*4) % max(1,h-15))
                p.drawRect(x, yy, 2, 11)
        else:
            for i in range(45):
                x = (i*83) % w
                yy = y + ((i*47 + self.phase*2) % max(1,h-8))
                p.drawRect(x, yy, 4, 4)
