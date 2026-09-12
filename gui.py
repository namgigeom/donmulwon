import os
import sys
import io
import contextlib
import traceback
from datetime import datetime

from PySide6.QtCore import QObject, QThread, Signal, Slot, Qt, QTimer
from PySide6.QtGui import QFont, QPainter, QPen, QBrush, QColor
from PySide6.QtWidgets import (
    QApplication, QFrame, QGraphicsScene, QGraphicsView, QHBoxLayout,
    QLabel, QLineEdit, QMainWindow, QPushButton, QPlainTextEdit,
    QProgressBar, QVBoxLayout, QWidget, QComboBox
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


class AnalysisWorker(QObject):
    status = Signal(str)
    output = Signal(str)
    finished = Signal()
    failed = Signal(str)

    def __init__(self, question):
        super().__init__()
        self.question = question

    @Slot()
    def run(self):
        try:
            import main as backend
            self.status.emit("AI 팀을 준비하는 중...")
            modules = backend.load_ai_modules()
            parsed = backend.parse_question(self.question)
            self.status.emit("토스증권 계좌정보를 확인하는 중...")
            account_data = backend.get_account_data()
            backend.save_json(backend.AI_PORTFOLIO_FILE, account_data)
            self.status.emit("🐢 🐦 🐍 🦝 4인 분석 → 토론 → 🐱 알프레도 검증 중...")
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                result = backend.run_meeting(parsed, modules, account_data)
            text = buffer.getvalue()
            if isinstance(result, dict) and result.get("alfredo"):
                text += "\n\n===== 🐱 알프레도 최종 판단 =====\n" + str(result["alfredo"])
            self.output.emit(text)
            self.finished.emit()
        except Exception:
            self.failed.emit(traceback.format_exc())


class PixelOfficeView(QGraphicsView):
    """Flat 2D pixel-art office. Characters use small pixel blocks and a larger sprite footprint."""
    WEATHER = {"맑음": "clear", "비": "rain", "눈": "snow", "흐림": "cloud"}

    def __init__(self):
        super().__init__()
        self.setScene(QGraphicsScene(self))
        self.setRenderHint(QPainter.Antialiasing, False)
        self.setRenderHint(QPainter.SmoothPixmapTransform, False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.NoFrame)
        self.weather = "clear"
        self.anim_tick = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(260)
        self.draw_scene()

    def _tick(self):
        self.anim_tick = (self.anim_tick + 1) % 48
        if self.weather in ("rain", "snow"):
            self.draw_scene()

    def set_weather(self, value):
        self.weather = self.WEATHER.get(value, "clear")
        self.draw_scene()

    def rect(self, x, y, w, h, fill, stroke=None, width=1):
        pen = QPen(QColor(stroke or fill))
        pen.setWidth(width)
        return self.scene().addRect(x, y, w, h, pen, QBrush(QColor(fill)))

    def line(self, x1, y1, x2, y2, color, width=1):
        pen = QPen(QColor(color))
        pen.setWidth(width)
        return self.scene().addLine(x1, y1, x2, y2, pen)

    def text(self, x, y, value, size=10, bold=False, color="#29271f", width=0):
        font = QFont("Malgun Gothic", size, QFont.Bold if bold else QFont.Normal)
        item = self.scene().addText(value, font)
        item.setDefaultTextColor(QColor(color))
        item.setPos(x, y)
        if width:
            item.setTextWidth(width)
        return item

    def px(self, x, y, w, h, color):
        return self.rect(x, y, w, h, color)

    def draw_sky(self, wx, wy, ww, wh):
        hour = datetime.now().hour
        if 6 <= hour < 10:
            sky, horizon, ground, label = "#7896a4", "#c4b99e", "#4d5a58", "MORNING"
        elif 10 <= hour < 17:
            sky, horizon, ground, label = "#8caeb8", "#d2ccb7", "#56615d", "DAY"
        elif 17 <= hour < 20:
            sky, horizon, ground, label = "#8e716c", "#c49378", "#3e4748", "SUNSET"
        else:
            sky, horizon, ground, label = "#1a2745", "#273550", "#1b222c", "NIGHT"

        if self.weather == "cloud":
            sky, horizon = "#65747c", "#8a918f"
        elif self.weather == "rain":
            sky, horizon = "#435968", "#69777c"
        elif self.weather == "snow":
            sky, horizon = "#657681", "#929a9c"

        self.rect(wx, wy, ww, wh, sky, "#303a40", 3)
        self.rect(wx + 4, wy + 4, ww - 8, 92, horizon)
        self.text(wx + 14, wy + 10, label, 7, True, "#ded6c0")

        night = hour >= 20 or hour < 6
        if night:
            stars = [(70,40),(190,25),(320,54),(455,31),(590,48),(735,24),(875,55),(1010,36)]
            for sx, sy in stars:
                self.px(wx + sx, wy + sy, 3, 3, "#d8d4b9")
        else:
            for sx, sy in [(80,43),(330,29),(650,49),(910,33)]:
                self.px(wx + sx, wy + sy, 25, 4, "#d7d3c1")
                self.px(wx + sx + 7, wy + sy - 4, 11, 4, "#d7d3c1")

        buildings = [
            (12,166,58,98),(78,142,72,122),(162,188,45,76),(220,122,78,142),
            (310,154,54,110),(378,100,82,164),(474,145,62,119),(552,116,86,148),
            (652,175,54,89),(720,135,80,129),(814,98,69,166),(900,154,59,110),
            (972,126,84,138),(1070,169,58,95)
        ]
        for bx, by, bw, bh in buildings:
            bx += wx
            self.rect(bx, by, bw, bh, "#2b343c")
            self.rect(bx + 5, by + 5, bw - 10, 5, "#20272d")
            for yy in range(by + 17, by + bh - 8, 12):
                for xx in range(bx + 8, bx + bw - 6, 11):
                    lit = ((xx * 3 + yy * 5 + hour) % 13) not in (0,1,4,9)
                    if lit:
                        self.px(xx, yy, 3, 5, "#b9aa70")

        tx, ty = wx + 405, 76
        self.rect(tx, ty, 34, 188, "#232c34")
        self.rect(tx + 7, ty - 28, 20, 28, "#232c34")
        self.rect(tx + 12, ty - 43, 6, 15, "#4d565d")
        for yy in range(ty + 13, ty + 174, 12):
            self.px(tx + 6, yy, 5, 6, "#b6a56a")
            self.px(tx + 20, yy + 4, 5, 5, "#66737a")

        self.rect(wx + 3, wy + 235, ww - 6, 29, ground)
        for i in range(1, 5):
            xx = wx + ww * i / 5
            self.line(xx, wy, xx, wy + wh, "#46535a", 3)
        self.line(wx, wy + 235, wx + ww, wy + 235, "#37454b", 2)

        if self.weather == "rain":
            for i in range(52):
                x = wx + 10 + ((i * 53 + self.anim_tick * 11) % int(ww - 20))
                y = wy + 8 + ((i * 37) % 214)
                self.line(x, y, x - 3, y + 11, "#9db4bd", 1)
        elif self.weather == "snow":
            for i in range(34):
                x = wx + 10 + ((i * 47 + self.anim_tick * 4) % int(ww - 20))
                y = wy + 8 + ((i * 43 + self.anim_tick * 3) % 214)
                self.px(x, y, 3, 3, "#e2e1d8")

    def draw_scene(self):
        self.scene().clear()
        W, H = 1600, 820
        self.scene().setSceneRect(0, 0, W, H)
        self.rect(0, 0, W, H, "#141719")
        self.rect(18, 18, 1564, 315, "#353a3c", "#66675f", 2)
        self.text(38, 31, "DONMULWON  •  AI TRADING OFFICE", 10, True, "#dfd0ad")

        # Window is behind the agents. The doorway is deliberately outside the window area.
        wx, wy, ww, wh = 184, 63, 1090, 242
        self.draw_sky(wx, wy, ww, wh)

        # Door: immediately beside Hyeonmu, never on top of the window.
        ex, ey = 28, 100
        self.rect(ex, ey, 132, 160, "#202528", "#69716d", 2)
        self.rect(ex + 10, ey + 10, 112, 108, "#29363a")
        self.rect(ex + 22, ey + 22, 88, 84, "#3d4b4d")
        self.rect(ex + 83, ey + 53, 6, 6, "#c9ae6d")
        self.text(ex + 45, ey + 34, "EXIT", 13, True, "#f0e9d2")
        self.text(ex + 20, ey + 126, "STAFF DOOR", 7, True, "#c8bea4")
        self.text(ex + 20, ey + 140, "HYEONMU SIDE", 6, False, "#8b968e")

        # Market card sits on the far right, separate from the character row.
        px, py, pw, ph = 1300, 58, 270, 246
        self.rect(px, py, pw, ph, "#202528", "#857452", 2)
        self.text(px + 14, py + 12, "MARKET MONITOR", 9, True, "#e1d5ba")
        self.text(px + 14, py + 31, "VOO", 8, True, "#aeb7a4")
        self.text(px + 51, py + 29, "$704.03", 10, True, "#91b69b")
        self.text(px + 160, py + 31, "+5.96%", 7, True, "#91b69b")
        cx, cy, cw, ch = px + 14, py + 55, pw - 28, 112
        self.rect(cx, cy, cw, ch, "#171e20", "#435054", 1)
        for gy in (cy + 28, cy + 56, cy + 84):
            self.line(cx + 5, gy, cx + cw - 5, gy, "#2b3538", 1)
        vals = [57,52,64,60,70,67,80,76,91,84,97,91,104,101]
        pts = []
        for i, v in enumerate(vals):
            xx = cx + 7 + i * (cw - 14) / (len(vals) - 1)
            yy = cy + ch - 8 - v * .73
            pts.append((xx, yy))
        for a, b in zip(pts, pts[1:]):
            self.line(a[0], a[1], b[0], b[1], "#91b69b", 3)
        for xx, yy in pts:
            self.px(xx - 2, yy - 2, 4, 4, "#d6dfc6")
        self.text(px + 14, py + 180, "ACCOUNT", 7, True, "#929b91")
        self.text(px + 70, py + 177, "$1,124.19", 10, True, "#dfd3b7")
        self.text(px + 14, py + 200, "JEPQ  13.0%", 7, True, "#b5ad9b")
        self.text(px + 14, py + 218, "TTWO  24.2%", 7, True, "#b5ad9b")

        self.rect(20, 328, 1560, 16, "#171a1c")

        agents = [
            ("현무", "MACRO", "#5d8375", "turtle"),
            ("김선달", "FUNDAMENTAL + NEWS", "#a37c49", "bird"),
            ("이묵", "TECHNICAL", "#4f7890", "snake"),
            ("너부리", "PORTFOLIO + ACCOUNT", "#8b6a55", "raccoon"),
            ("알프레도", "TEAM LEAD / VERIFIER", "#a8794b", "cat"),
        ]
        # Horizontal straight-line desks. Hyeonmu is closest to the door.
        xs = [170, 420, 670, 920, 1235]
        for i, data in enumerate(agents):
            self.draw_agent(xs[i], 350, 225 if i < 4 else 330, *data, lead=(i == 4))

        self.text(36, 742, "2D PIXEL OFFICE  •  HIGH-RES SPRITES  •  LIVE MARKET PANEL", 8, True, "#a49c88")
        self.text(1345, 742, datetime.now().strftime("%Y-%m-%d  %H:%M"), 8, True, "#a49c88")

    def draw_agent(self, x, y, w, name, role, accent, kind, lead=False):
        cx = x + w / 2
        self.draw_character(cx, y, kind, accent, lead=lead)
        # monitor behind the desk
        self.rect(cx - 38, y + 126, 76, 58, "#2a2e31", "#151718", 2)
        self.rect(cx - 47, y + 177, 94, 9, "#141618")

        # desk
        self.rect(x + 7, y + 103, w - 14, 16, "#ad8b59", "#4a3826", 2)
        self.rect(x + 16, y + 119, w - 32, 62, "#573f2b", "#30251d", 2)
        self.rect(x + 30, y + 128, w - 60, 43, "#192326", "#68736f", 2)
        self.rect(x + 40, y + 138, w - 80, 4, accent)
        self.rect(x + 40, y + 150, w - 80, 3, "#56605e")
        self.rect(x + 40, y + 161, w - 80, 3, "#56605e")
        self.rect(x + 21, y + 181, w - 42, 13, accent)
        self.rect(x + 30, y + 194, 10, 45, "#2b211a")
        self.rect(x + w - 40, y + 194, 10, 45, "#2b211a")
        self.rect(x + 5, y + 237, w - 10, 7, "#17191a")

        self.rect(x + 16, y + 251, w - 32, 42, "#242a2d", "#665c4c", 1)
        self.text(x + 28, y + 254, name, 11, True, "#f0e5ce")
        self.text(x + 28, y + 270, role, 6, True, "#aaa18c", w - 105 if lead else w - 55)
        if lead:
            self.rect(x + w - 77, y + 255, 53, 16, "#a8794b")
            self.text(x + w - 72, y + 256, "LEAD", 6, True, "#fff0d2")

    def draw_character(self, cx, y, kind, accent, lead=False):
        """Large readable sprite built from 3-6px blocks; no giant primitive shapes."""
        dark = "#16181a"
        outline = "#252124"
        white = "#f0e7d3"
        shirt = "#e0d8c7"
        suit = accent
        shadow = "#342b28"

        # Legs, shoes, and lower silhouette.
        self.px(cx - 22, y + 103, 17, 31, suit)
        self.px(cx + 5, y + 103, 17, 31, suit)
        self.px(cx - 26, y + 129, 24, 8, outline)
        self.px(cx + 3, y + 129, 25, 8, outline)
        self.px(cx - 28, y + 136, 24, 7, dark)
        self.px(cx + 4, y + 136, 26, 7, dark)

        # Jacket and arms: many small stepped pixels for a less rigid silhouette.
        self.px(cx - 34, y + 61, 68, 47, suit)
        self.px(cx - 40, y + 70, 9, 31, suit)
        self.px(cx + 31, y + 70, 9, 31, suit)
        self.px(cx - 43, y + 91, 10, 9, shadow)
        self.px(cx + 33, y + 91, 10, 9, shadow)
        self.px(cx - 25, y + 56, 19, 16, shirt)
        self.px(cx + 6, y + 56, 19, 16, shirt)
        self.px(cx - 5, y + 61, 10, 37, dark)
        self.px(cx - 9, y + 62, 5, 14, "#b99b61")
        self.px(cx + 4, y + 62, 5, 14, "#b99b61")
        self.px(cx - 31, y + 96, 15, 8, "#c9c0af")
        self.px(cx + 16, y + 96, 15, 8, "#c9c0af")

        # Small shoulder highlights create a hand-drawn pixel-game silhouette.
        self.px(cx - 38, y + 67, 7, 13, "#eee4cf")
        self.px(cx + 31, y + 67, 7, 13, "#eee4cf")

        if kind == "turtle":
            shell, skin, shell_hi = "#315a4d", "#82a18a", "#4f7761"
            self.px(cx - 36, y + 18, 72, 48, outline)
            self.px(cx - 31, y + 13, 62, 49, shell)
            self.px(cx - 38, y + 29, 10, 24, shell)
            self.px(cx + 28, y + 29, 10, 24, shell)
            self.px(cx - 27, y + 8, 54, 11, shell)
            self.px(cx - 22, y + 18, 44, 34, skin)
            self.px(cx - 18, y + 22, 13, 10, white)
            self.px(cx + 5, y + 22, 13, 10, white)
            self.px(cx - 14, y + 24, 7, 7, dark)
            self.px(cx + 8, y + 24, 7, 7, dark)
            self.px(cx - 11, y + 38, 22, 6, shell_hi)
            self.px(cx - 20, y + 45, 40, 7, shell_hi)
            self.px(cx - 24, y + 3, 48, 6, "#234239")
            self.px(cx - 14, y - 1, 28, 5, "#234239")
        elif kind == "bird":
            feather, light, beak = "#394247", "#6d7477", "#bd8f4c"
            self.px(cx - 33, y + 17, 66, 48, outline)
            self.px(cx - 29, y + 13, 58, 48, feather)
            self.px(cx - 23, y + 5, 46, 12, feather)
            self.px(cx - 15, y, 30, 7, feather)
            self.px(cx + 28, y + 31, 18, 9, beak)
            self.px(cx - 19, y + 24, 14, 10, white)
            self.px(cx + 5, y + 24, 14, 10, white)
            self.px(cx - 14, y + 26, 7, 7, dark)
            self.px(cx + 9, y + 26, 7, 7, dark)
            self.px(cx - 12, y + 39, 24, 6, light)
            self.px(cx - 35, y + 45, 12, 14, feather)
            self.px(cx + 23, y + 45, 12, 14, feather)
            self.px(cx - 25, y + 59, 50, 6, "#242b2f")
        elif kind == "snake":
            green, light = "#4d715f", "#8ba783", "#bdcbaa"
            self.px(cx - 31, y + 11, 62, 9, green)
            self.px(cx - 36, y + 19, 72, 43, outline)
            self.px(cx - 31, y + 19, 62, 40, green)
            self.px(cx - 25, y + 49, 50, 12, light)
            self.px(cx - 22, y + 24, 17, 11, white)
            self.px(cx + 5, y + 24, 17, 11, white)
            self.px(cx - 17, y + 27, 7, 7, dark)
            self.px(cx + 10, y + 27, 7, 7, dark)
            self.px(cx - 32, y + 35, 9, 9, light)
            self.px(cx + 23, y + 35, 9, 9, light)
            self.px(cx + 12, y + 51, 23, 5, "#875347")
            self.px(cx + 30, y + 56, 11, 4, "#d0b36d")
        elif kind == "raccoon":
            fur, mask, light = "#72665e", "#292b2d", "#b2a58e"
            self.px(cx - 35, y + 17, 70, 48, outline)
            self.px(cx - 30, y + 13, 60, 48, fur)
            self.px(cx - 26, y + 5, 52, 12, fur)
            self.px(cx - 31, y, 13, 14, fur)
            self.px(cx + 18, y, 13, 14, fur)
            self.px(cx - 28, y + 22, 56, 18, mask)
            self.px(cx - 20, y + 25, 15, 10, white)
            self.px(cx + 5, y + 25, 15, 10, white)
            self.px(cx - 16, y + 28, 7, 7, dark)
            self.px(cx + 9, y + 28, 7, 7, dark)
            self.px(cx - 12, y + 41, 24, 7, light)
            self.px(cx - 39, y + 45, 12, 13, fur)
            self.px(cx + 27, y + 45, 12, 13, fur)
            self.px(cx + 27, y + 56, 22, 8, fur)
            self.px(cx + 42, y + 62, 10, 7, "#4d4542")
        else:
            fur, light = "#8b6d59", "#c9aa87"
            self.px(cx - 34, y + 16, 68, 49, outline)
            self.px(cx - 30, y + 13, 60, 49, fur)
            self.px(cx - 25, y + 5, 50, 12, fur)
            self.px(cx - 31, y, 14, 15, fur)
            self.px(cx + 17, y, 14, 15, fur)
            self.px(cx - 20, y + 23, 16, 11, "#f0e6d1")
            self.px(cx + 4, y + 23, 16, 11, "#f0e6d1")
            self.px(cx - 15, y + 26, 7, 7, dark)
            self.px(cx + 9, y + 26, 7, 7, dark)
            self.px(cx - 9, y + 39, 18, 7, "#3b2d28")
            self.px(cx - 12, y + 48, 24, 6, light)
            if lead:
                self.px(cx - 39, y + 52, 8, 17, "#d4ae68")
                self.px(cx + 31, y + 52, 8, 17, "#d4ae68")

        # Neck/tie layer keeps every character visibly suited.
        self.px(cx - 19, y + 59, 14, 8, shirt)
        self.px(cx + 5, y + 59, 14, 8, shirt)
        self.px(cx - 5, y + 65, 10, 20, dark)
        self.px(cx - 9, y + 66, 5, 9, "#b99b61")
        self.px(cx + 4, y + 66, 5, 9, "#b99b61")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("돈물원 — DONMULWON AI Trading Team")
        self.resize(1500, 980)
        self.setMinimumSize(1180, 800)
        self.worker_thread = None
        self.worker = None

        root = QWidget()
        self.setCentralWidget(root)
        root.setStyleSheet("QWidget{background:#141719;color:#e7dfcb;} QLabel{font-family:'Malgun Gothic';}")
        layout = QVBoxLayout(root)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        header = QHBoxLayout()
        title = QLabel("DONMULWON  /  돈물원")
        title.setStyleSheet("font-size:25px;font-weight:700;color:#dfcfaa;")
        header.addWidget(title)
        sub = QLabel("AI TRADING TEAM")
        sub.setStyleSheet("font-size:11px;color:#9d9a8b;")
        header.addWidget(sub)
        header.addStretch()

        self.weather = QComboBox()
        self.weather.addItems(["맑음", "흐림", "비", "눈"])
        self.weather.setStyleSheet(
            "QComboBox{background:#24292c;border:1px solid #615947;padding:6px;color:#e5dcc7;}"
            "QComboBox QAbstractItemView{background:#24292c;color:#e5dcc7;}"
        )
        self.weather.currentTextChanged.connect(self._weather_changed)
        header.addWidget(QLabel("날씨"))
        header.addWidget(self.weather)

        self.clock = QLabel()
        self.clock.setStyleSheet("font-size:11px;color:#aaa18c;padding-left:12px;")
        header.addWidget(self.clock)
        layout.addLayout(header)

        self.office = PixelOfficeView()
        layout.addWidget(self.office, 1)

        bottom = QFrame()
        bottom.setStyleSheet("QFrame{background:#24292c;border:1px solid #5c5445;border-radius:8px;}")
        bl = QHBoxLayout(bottom)
        bl.setContentsMargins(12, 10, 12, 10)
        self.input = QLineEdit()
        self.input.setPlaceholderText("무엇을 분석할까요?  예: VOO랑 JEPQ 추가매수했는데 어때?")
        self.input.setStyleSheet(
            "QLineEdit{background:#171a1d;border:1px solid #625945;border-radius:6px;"
            "padding:10px;color:#eee5d0;font-size:13px;}"
        )
        self.input.returnPressed.connect(self.start_analysis)
        bl.addWidget(self.input, 1)

        self.button = QPushButton("분석 시작")
        self.button.setStyleSheet(
            "QPushButton{background:#80653f;color:#fff0d3;border:0;border-radius:6px;"
            "padding:10px 20px;font-weight:700;}"
            "QPushButton:disabled{background:#49443b;color:#8c887d;}"
        )
        self.button.clicked.connect(self.start_analysis)
        bl.addWidget(self.button)
        layout.addWidget(bottom)

        self.status = QLabel("대기 중 · 사무실 운영 정상")
        self.status.setStyleSheet("color:#a9a28f;font-size:11px;padding:2px 4px;")
        layout.addWidget(self.status)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        self.progress.setStyleSheet(
            "QProgressBar{background:#202427;border:0;height:4px;}"
            "QProgressBar::chunk{background:#8b7350;}"
        )
        layout.addWidget(self.progress)

        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setPlaceholderText("분석 결과가 여기에 표시됩니다.")
        self.output.setStyleSheet(
            "QPlainTextEdit{background:#111416;border:1px solid #4b4539;color:#ded7c5;"
            "font-family:'Malgun Gothic';font-size:12px;padding:8px;}"
        )
        self.output.setMaximumHeight(235)
        layout.addWidget(self.output)

        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self._clock)
        self.clock_timer.start(1000)
        self._clock()

    def _clock(self):
        self.clock.setText(datetime.now().strftime("%Y-%m-%d  %H:%M:%S"))

    def _weather_changed(self, value):
        self.office.set_weather(value)
        self.status.setText(f"사무실 환경 · {value} · 2D PIXEL MODE")

    def start_analysis(self):
        question = self.input.text().strip()
        if not question:
            return
        self.button.setEnabled(False)
        self.input.setEnabled(False)
        self.progress.setVisible(True)
        self.status.setText("AI 팀 분석 진행 중...")
        self.output.clear()

        self.worker_thread = QThread(self)
        self.worker = AnalysisWorker(question)
        self.worker.moveToThread(self.worker_thread)
        self.worker.status.connect(self.status.setText)
        self.worker.output.connect(self.output.setPlainText)
        self.worker.finished.connect(self._analysis_finished)
        self.worker.failed.connect(self._analysis_failed)
        self.worker_thread.started.connect(self.worker.run)
        self.worker_thread.start()

    def _analysis_finished(self):
        self.progress.setVisible(False)
        self.button.setEnabled(True)
        self.input.setEnabled(True)
        self.status.setText("분석 완료 · 알프레도 최종 검증 완료")
        self._cleanup_thread()

    def _analysis_failed(self, error):
        self.progress.setVisible(False)
        self.button.setEnabled(True)
        self.input.setEnabled(True)
        self.status.setText("분석 실패 · 오류 내용을 결과창에서 확인")
        self.output.setPlainText(error)
        self._cleanup_thread()

    def _cleanup_thread(self):
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait(3000)
            self.worker_thread.deleteLater()
            self.worker_thread = None
            self.worker = None


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
