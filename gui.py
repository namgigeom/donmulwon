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
    """DONMULWON: high-resolution 2D pixel-art office, deliberately flat and side-on."""
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
        self.timer.start(280)
        self.draw_scene()

    def _tick(self):
        self.anim_tick = (self.anim_tick + 1) % 24
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
            sky, horizon, ground = "#829da8", "#c2b89d", "#4d5b59"
            label = "MORNING"
        elif 10 <= hour < 17:
            sky, horizon, ground = "#8eafb8", "#d2cbb5", "#56615d"
            label = "DAY"
        elif 17 <= hour < 20:
            sky, horizon, ground = "#8e716e", "#c49579", "#3e4748"
            label = "SUNSET"
        else:
            sky, horizon, ground = "#1c2947", "#273553", "#1d242d"
            label = "NIGHT"

        if self.weather == "cloud":
            sky, horizon = "#66757d", "#8b918d"
        elif self.weather == "rain":
            sky, horizon = "#455c6b", "#68767b"
        elif self.weather == "snow":
            sky, horizon = "#667780", "#939b9c"

        self.rect(wx, wy, ww, wh, sky, "#303a40", 3)
        self.rect(wx + 4, wy + 4, ww - 8, 90, horizon)
        self.text(wx + 15, wy + 11, label, 7, True, "#d8d1bb")

        night = hour >= 20 or hour < 6
        if night:
            for sx, sy in [(wx+70,wy+40),(wx+215,wy+25),(wx+360,wy+55),(wx+520,wy+31),
                           (wx+735,wy+51),(wx+900,wy+24),(wx+1010,wy+63)]:
                self.px(sx, sy, 3, 3, "#d8d5b9")
        else:
            for sx, sy in [(wx+80,wy+42),(wx+315,wy+30),(wx+640,wy+50),(wx+910,wy+32)]:
                self.px(sx, sy, 26, 4, "#d4d1c0")
                self.px(sx+7, sy-4, 12, 4, "#d4d1c0")

        buildings = [
            (wx+12, 166, 58, 98), (wx+78, 142, 72, 122), (wx+162, 188, 45, 76),
            (wx+220, 122, 78, 142), (wx+310, 154, 54, 110), (wx+378, 100, 82, 164),
            (wx+474, 145, 62, 119), (wx+552, 116, 86, 148), (wx+652, 175, 54, 89),
            (wx+720, 135, 80, 129), (wx+814, 98, 69, 166), (wx+900, 154, 59, 110),
            (wx+972, 126, 84, 138), (wx+1070, 169, 58, 95)
        ]
        for bx, by, bw, bh in buildings:
            self.rect(bx, by, bw, bh, "#2d353d")
            self.rect(bx + 5, by + 5, bw - 10, 5, "#20272d")
            for yy in range(by + 17, by + bh - 8, 13):
                for xx in range(bx + 8, bx + bw - 6, 12):
                    lit = ((xx * 3 + yy * 5 + hour) % 11) not in (0, 1, 2, 7)
                    if lit:
                        self.px(xx, yy, 4, 6, "#b4a66c")

        tx, ty = wx + 405, 76
        self.rect(tx, ty, 34, 188, "#232c34")
        self.rect(tx + 7, ty - 28, 20, 28, "#232c34")
        self.rect(tx + 12, ty - 43, 6, 15, "#4d565d")
        for yy in range(ty + 13, ty + 174, 13):
            self.px(tx + 6, yy, 5, 7, "#b6a56a")
            self.px(tx + 20, yy + 4, 5, 6, "#66737a")

        self.rect(wx + 3, 235, ww - 6, 29, ground)
        for i in range(1, 5):
            xx = wx + ww * i / 5
            self.line(xx, wy, xx, wy + wh, "#46535a", 3)
        self.line(wx, 235, wx + ww, 235, "#37454b", 2)

        if self.weather == "rain":
            for i in range(48):
                x = wx + 10 + ((i * 53 + self.anim_tick * 11) % int(ww - 20))
                y = wy + 8 + ((i * 37) % 214)
                self.line(x, y, x - 3, y + 11, "#9db4bd", 1)
        elif self.weather == "snow":
            for i in range(30):
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

        wx, wy, ww, wh = 198, 63, 1110, 242
        self.draw_sky(wx, wy, ww, wh)

        ex, ey = 42, 92
        self.rect(ex, ey, 124, 143, "#202528", "#69716d", 2)
        self.rect(ex + 11, ey + 11, 102, 85, "#29363a")
        self.rect(ex + 31, ey + 29, 62, 37, "#78957c")
        self.text(ex + 43, ey + 32, "EXIT", 12, True, "#f0e9d2")
        self.text(ex + 19, ey + 106, "STAFF DOOR", 7, True, "#c8bea4")
        self.text(ex + 19, ey + 120, "HYEONMU SIDE", 6, False, "#8b968e")

        px, py, pw, ph = 1324, 58, 228, 246
        self.rect(px, py, pw, ph, "#202528", "#857452", 2)
        self.text(px + 14, py + 12, "MARKET", 9, True, "#e1d5ba")
        self.text(px + 14, py + 31, "VOO", 8, True, "#aeb7a4")
        self.text(px + 51, py + 29, "$704.03", 10, True, "#91b69b")
        self.text(px + 144, py + 31, "+5.96%", 7, True, "#91b69b")
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
        xs = [35, 335, 635, 935, 1258]
        for i, data in enumerate(agents):
            self.draw_agent(xs[i], 365, 275 if i < 4 else 305, *data, lead=(i == 4))

        self.text(36, 742, "2D PIXEL OFFICE  •  SEPARATE DESKS  •  LIVE MARKET PANEL", 8, True, "#a49c88")
        self.text(1345, 742, datetime.now().strftime("%Y-%m-%d  %H:%M"), 8, True, "#a49c88")

    def draw_agent(self, x, y, w, name, role, accent, kind, lead=False):
        cx = x + w / 2
        self.draw_character(cx, y, kind, accent, lead=lead)
        self.rect(cx - 32, y + 128, 64, 60, "#2a2e31", "#151718", 2)
        self.rect(cx - 43, y + 178, 86, 9, "#141618")

        self.rect(x + 8, y + 103, w - 16, 16, "#ad8b59", "#4a3826", 2)
        self.rect(x + 17, y + 119, w - 34, 62, "#573f2b", "#30251d", 2)
        self.rect(x + 31, y + 128, w - 62, 43, "#192326", "#68736f", 2)
        self.rect(x + 42, y + 138, w - 84, 4, accent)
        self.rect(x + 42, y + 150, w - 84, 3, "#56605e")
        self.rect(x + 42, y + 161, w - 84, 3, "#56605e")
        self.rect(x + 22, y + 181, w - 44, 13, accent)
        self.rect(x + 31, y + 194, 10, 45, "#2b211a")
        self.rect(x + w - 41, y + 194, 10, 45, "#2b211a")
        self.rect(x + 5, y + 237, w - 10, 7, "#17191a")

        self.rect(x + 18, y + 251, w - 36, 42, "#242a2d", "#665c4c", 1)
        self.text(x + 30, y + 254, name, 11, True, "#f0e5ce" if lead else "#eee5cf")
        self.text(x + 30, y + 270, role, 6, True, "#aaa18c" if lead else "#a39a86", w - 110 if lead else w - 60)
        if lead:
            self.rect(x + w - 76, y + 255, 52, 16, "#a8794b")
            self.text(x + w - 71, y + 256, "LEAD", 6, True, "#fff0d2")

    def draw_character(self, cx, y, kind, accent, lead=False):
        # Larger sprite made from small blocks: readable at normal window size, but still true pixel art.
        d = "#15181a"
        white = "#eee7d4"
        shirt = "#ded8c8"
        suit = accent

        # Legs / shoes.
        self.px(cx - 16, y + 82, 12, 22, suit)
        self.px(cx + 4, y + 82, 12, 22, suit)
        self.px(cx - 18, y + 101, 15, 7, d)
        self.px(cx + 3, y + 101, 15, 7, d)

        # Body / jacket.
        self.px(cx - 24, y + 52, 48, 38, suit)
        self.px(cx - 28, y + 60, 7, 22, suit)
        self.px(cx + 21, y + 60, 7, 22, suit)
        self.px(cx - 14, y + 50, 10, 10, shirt)
        self.px(cx + 4, y + 50, 10, 10, shirt)
        self.px(cx - 4, y + 54, 8, 28, d)
        self.px(cx - 7, y + 55, 5, 10, "#b99b61")
        self.px(cx + 3, y + 55, 5, 10, "#b99b61")
        self.px(cx - 29, y + 68, 7, 15, "#d8d0bd")
        self.px(cx + 22, y + 68, 7, 15, "#d8d0bd")
        self.px(cx - 34, y + 79, 9, 6, d)
        self.px(cx + 25, y + 79, 9, 6, d)

        if kind == "turtle":
            shell, skin = "#355c50", "#7e9f85"
            self.px(cx - 24, y + 17, 48, 37, shell)
            self.px(cx - 29, y + 27, 7, 15, shell)
            self.px(cx + 22, y + 27, 7, 15, shell)
            self.px(cx - 19, y + 10, 38, 10, shell)
            self.px(cx - 16, y + 19, 32, 27, skin)
            self.px(cx - 12, y + 23, 9, 7, white)
            self.px(cx + 3, y + 23, 9, 7, white)
            self.px(cx - 9, y + 25, 5, 5, d)
            self.px(cx + 5, y + 25, 5, 5, d)
            self.px(cx - 8, y + 35, 16, 5, "#466f5d")
            self.px(cx - 17, y + 6, 34, 5, "#244139")
            self.px(cx - 9, y + 2, 18, 4, "#244139")
        elif kind == "bird":
            feather, beak = "#3b4145", "#b88d4d"
            self.px(cx - 22, y + 18, 44, 35, feather)
            self.px(cx - 16, y + 9, 32, 13, feather)
            self.px(cx - 8, y + 3, 16, 8, feather)
            self.px(cx + 20, y + 27, 14, 7, beak)
            self.px(cx - 12, y + 22, 9, 7, white)
            self.px(cx + 4, y + 22, 9, 7, white)
            self.px(cx - 9, y + 24, 5, 5, d)
            self.px(cx + 7, y + 24, 5, 5, d)
            self.px(cx - 8, y + 35, 16, 5, "#596062")
            self.px(cx - 23, y + 43, 10, 9, feather)
            self.px(cx + 13, y + 43, 10, 9, feather)
        elif kind == "snake":
            green, light = "#557663", "#8aa27f"
            self.px(cx - 18, y + 8, 36, 10, green)
            self.px(cx - 25, y + 17, 50, 30, green)
            self.px(cx - 18, y + 43, 36, 9, light)
            self.px(cx - 15, y + 21, 10, 7, "#d2d9bd")
            self.px(cx + 5, y + 21, 10, 7, "#d2d9bd")
            self.px(cx - 12, y + 23, 5, 5, d)
            self.px(cx + 8, y + 23, 5, 5, d)
            self.px(cx - 24, y + 30, 8, 7, light)
            self.px(cx + 16, y + 30, 8, 7, light)
            self.px(cx + 14, y + 46, 18, 5, "#7f5044")
        elif kind == "raccoon":
            fur, mask, light = "#74675e", "#292b2d", "#aea38f"
            self.px(cx - 24, y + 17, 48, 35, fur)
            self.px(cx - 16, y + 8, 32, 12, fur)
            self.px(cx - 20, y + 3, 10, 10, fur)
            self.px(cx + 10, y + 3, 10, 10, fur)
            self.px(cx - 19, y + 20, 38, 14, mask)
            self.px(cx - 13, y + 22, 10, 7, white)
            self.px(cx + 4, y + 22, 10, 7, white)
            self.px(cx - 10, y + 24, 5, 5, d)
            self.px(cx + 7, y + 24, 5, 5, d)
            self.px(cx - 8, y + 36, 16, 6, light)
            self.px(cx - 27, y + 44, 9, 8, fur)
            self.px(cx + 18, y + 44, 9, 8, fur)
        else:
            fur, light = "#8b6d59", "#c9aa87"
            self.px(cx - 23, y + 16, 46, 37, fur)
            self.px(cx - 16, y + 8, 32, 12, fur)
            self.px(cx - 20, y + 2, 11, 11, fur)
            self.px(cx + 9, y + 2, 11, 11, fur)
            self.px(cx - 15, y + 20, 10, 8, "#f0e6d1")
            self.px(cx + 5, y + 20, 10, 8, "#f0e6d1")
            self.px(cx - 11, y + 22, 5, 5, d)
            self.px(cx + 8, y + 22, 5, 5, d)
            self.px(cx - 6, y + 33, 12, 6, "#3b2d28")
            self.px(cx - 8, y + 41, 16, 5, light)

        self.px(cx - 15, y + 50, 9, 5, shirt)
        self.px(cx + 6, y + 50, 9, 5, shirt)
        self.px(cx - 4, y + 52, 8, 16, d)
        if lead:
            self.px(cx - 27, y + 58, 5, 12, "#d4ae68")
            self.px(cx + 22, y + 58, 5, 12, "#d4ae68")


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
