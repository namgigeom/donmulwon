import os, sys, io, contextlib, traceback
from datetime import datetime
from PySide6.QtCore import QObject, QThread, Signal, Slot, Qt, QTimer, QRect
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QPlainTextEdit, QProgressBar, QComboBox)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

class AnalysisWorker(QObject):
    output = Signal(str)
    finished = Signal()
    failed = Signal(str)
    def __init__(self, question):
        super().__init__()
        self.question = question
    @Slot()
    def run(self):
        try:
            import main
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                result = main.run_analysis(self.question)
            text = buf.getvalue()
            if result is not None:
                text += "\n\n" + str(result)
            self.output.emit(text)
            self.finished.emit()
        except Exception:
            self.failed.emit(traceback.format_exc())

class PixelAgent:
    DATA = {
        "현무": ("turtle", 92, 408),
        "김선달": ("bird", 352, 408),
        "이묵": ("snake", 612, 408),
        "너부리": ("raccoon", 872, 408),
        "알프레도": ("cat", 1170, 392),
    }
    def __init__(self, name):
        self.name = name
        self.frame = 0
    def tick(self):
        self.frame = (self.frame + 1) % 32
    def paint(self, painter, x, y, scale=3):
        s = int(scale)
        ox, oy = int(x), int(y)
        kind = self.DATA[self.name][0]
        palette = {
            "turtle": ("#5d8f6a", "#263d31", "#d2bd8b", "#18221d"),
            "bird": ("#a95f42", "#493033", "#ead0a1", "#1b2025"),
            "snake": ("#71845a", "#2a382d", "#d8bd79", "#171b18"),
            "raccoon": ("#918b83", "#36383b", "#c9b090", "#1b1d20"),
            "cat": ("#17191c", "#08090b", "#d0b994", "#101114"),
        }
        fur, suit, skin, ink = [QColor(v) for v in palette[kind]]
        painter.setPen(Qt.NoPen)
        def px(x0, y0, w, h, color):
            painter.setBrush(color)
            painter.drawRect(ox + x0*s, oy + y0*s, w*s, h*s)
        px(7, 58, 34, 3, QColor(12, 13, 14, 115))
        px(13, 48, 7, 12, suit); px(29, 48, 7, 12, suit)
        px(11, 59, 11, 3, ink); px(27, 59, 11, 3, ink)
        px(9, 26, 31, 24, suit); px(12, 27, 25, 21, suit); px(15, 28, 19, 19, suit)
        px(19, 28, 7, 18, QColor("#e7dfcf")); px(22, 29, 2, 14, QColor("#8d4d47")); px(21, 42, 4, 5, QColor("#6d3938"))
        px(4, 29, 7, 19, suit); px(38, 29, 7, 19, suit)
        px(3, 45, 8, 5, skin); px(38, 45, 8, 5, skin)
        px(18, 22, 9, 7, skin); px(11, 5, 26, 20, fur); px(14, 3, 20, 4, fur); px(14, 20, 20, 5, skin)
        if kind == "cat":
            px(10, 0, 9, 9, fur); px(30, 0, 9, 9, fur)
            px(12, 2, 5, 5, QColor("#51424a")); px(32, 2, 5, 5, QColor("#51424a"))
            frame = QColor("#d7c9aa")
            px(14, 8, 11, 2, frame); px(27, 8, 11, 2, frame)
            px(14, 8, 2, 8, frame); px(23, 8, 2, 8, frame); px(27, 8, 2, 8, frame); px(36, 8, 2, 8, frame); px(23, 10, 6, 2, frame)
            px(18, 10, 3, 3, QColor("#e6d27e")); px(30, 10, 3, 3, QColor("#e6d27e"))
            px(19, 10, 1, 3, ink); px(31, 10, 1, 3, ink)
            px(24, 14, 3, 2, QColor("#d08d98")); px(21, 16, 3, 1, QColor("#c9b7a0")); px(27, 16, 3, 1, QColor("#c9b7a0"))
            px(12, 16, 8, 1, QColor("#b6a995")); px(31, 16, 8, 1, QColor("#b6a995"))
        elif kind == "turtle":
            shell = QColor("#355f49"); shell_hi = QColor("#709273")
            px(4, 23, 39, 23, fur); px(8, 24, 31, 20, shell); px(12, 27, 23, 15, shell_hi)
            px(18, 10, 10, 14, skin); px(26, 12, 8, 9, skin); px(29, 14, 2, 2, ink)
            px(19, 28, 3, 8, QColor("#466f55")); px(28, 27, 3, 9, QColor("#466f55")); px(12, 34, 25, 3, QColor("#466f55"))
            px(5, 39, 8, 6, skin); px(36, 39, 8, 6, skin)
        elif kind == "bird":
            px(13, 2, 18, 5, fur); px(8, 7, 27, 17, fur); px(4, 16, 10, 12, fur); px(34, 15, 10, 11, fur)
            px(40, 14, 8, 4, QColor("#d59a45")); px(17, 9, 5, 5, QColor("#eee0a9")); px(29, 9, 5, 5, QColor("#eee0a9"))
            px(18, 10, 2, 3, ink); px(30, 10, 2, 3, ink); px(15, 18, 18, 5, QColor("#874936"))
        elif kind == "snake":
            px(10, 2, 25, 6, fur); px(8, 7, 29, 17, fur); px(12, 10, 21, 11, QColor("#536a45"))
            px(17, 9, 5, 5, QColor("#d8c47f")); px(28, 9, 5, 5, QColor("#d8c47f")); px(18, 10, 2, 3, ink); px(29, 10, 2, 3, ink)
            px(4, 18, 10, 6, fur); px(0, 22, 10, 6, fur); px(31, 18, 9, 6, fur)
        elif kind == "raccoon":
            px(9, 2, 11, 8, fur); px(29, 2, 11, 8, fur); px(9, 7, 31, 18, fur)
            px(12, 9, 11, 8, QColor("#4b4d50")); px(27, 9, 11, 8, QColor("#4b4d50"))
            px(15, 11, 5, 5, QColor("#d7c4ab")); px(30, 11, 5, 5, QColor("#d7c4ab")); px(16, 12, 2, 3, ink); px(31, 12, 2, 3, ink)
            px(21, 16, 10, 6, QColor("#c8b7a0")); px(24, 18, 4, 3, QColor("#8d5b55")); px(7, 20, 8, 8, fur); px(34, 20, 8, 8, fur)
        px(15, 31, 2, 2, QColor("#b9a06f")); px(15, 38, 2, 2, QColor("#b9a06f")); px(31, 31, 2, 2, QColor("#b9a06f")); px(31, 38, 2, 2, QColor("#b9a06f"))

class PixelOffice(QWidget):
    def __init__(self):
        super().__init__(); self.weather = "맑음"; self.time = "밤"
        self.agents = {name: PixelAgent(name) for name in PixelAgent.DATA}
        self.timer = QTimer(self); self.timer.timeout.connect(self.update_animation); self.timer.start(140); self.setMinimumHeight(650)
    def update_animation(self):
        for agent in self.agents.values(): agent.tick()
        self.update()
    def set_weather(self, value): self.weather = value; self.update()
    def paintEvent(self, event):
        painter = QPainter(self); painter.setRenderHint(QPainter.Antialiasing, False)
        try:
            w, h = self.width(), self.height()
            painter.fillRect(0, 0, w, h, QColor("#17191d")); painter.fillRect(18, 18, w - 36, 330, QColor("#b99b72")); painter.fillRect(38, 42, w - 76, 270, QColor("#27394b"))
            self.draw_city(painter, 38, 42, w - 76, 270)
            painter.setPen(QColor("#8b765b")); painter.setBrush(Qt.NoBrush); painter.drawRect(38, 42, w - 76, 270)
            for xx in range(200, w - 50, 190): painter.drawLine(xx, 42, xx, 312)
            # Entrance is beside Hyeonmu, never inside the window area.
            painter.setPen(Qt.NoPen); painter.setBrush(QColor("#33251e")); painter.drawRect(28, 350, 94, 170); painter.setBrush(QColor("#805a39")); painter.drawRect(38, 360, 74, 150); painter.setBrush(QColor("#d8bf88")); painter.drawRect(94, 425, 5, 5)
            self.draw_desks(painter)
            for name, agent in self.agents.items():
                x, y = PixelAgent.DATA[name][1:]; agent.paint(painter, x, y, 3)
                painter.setPen(QColor("#eee4d2")); painter.setFont(QFont("Malgun Gothic", 11, QFont.Bold)); painter.drawText(QRect(x - 18, y + 184, 165, 26), Qt.AlignCenter, name)
            if self.weather in ("비", "눈"): self.draw_weather(painter)
            painter.setPen(QColor("#cbb98e")); painter.setFont(QFont("Malgun Gothic", 10)); painter.drawText(40, h - 22, f"2D PIXEL OFFICE  ·  {self.time}  ·  {self.weather}")
        finally:
            if painter.isActive(): painter.end()
    def draw_city(self, painter, x, y, width, height):
        painter.setPen(Qt.NoPen)
        for i in range(24):
            bw = 28 + (i % 4) * 13; bh = 55 + (i * 17) % 125; bx = x + 8 + i * int((width - 16) / 24)
            painter.setBrush(QColor("#152235")); painter.drawRect(bx, y + height - bh, bw, bh); painter.setBrush(QColor("#d1b76a"))
            for wy in range(y + height - bh + 12, y + height - 8, 18):
                if (i + wy) % 3: painter.drawRect(bx + 6, wy, 5, 5)
    def draw_desks(self, painter):
        for x in (145, 405, 665, 925):
            painter.setPen(Qt.NoPen); painter.setBrush(QColor("#4b3020")); painter.drawRect(x, 565, 190, 76); painter.setBrush(QColor("#20272c")); painter.drawRect(x + 52, 525, 86, 40); painter.setBrush(QColor("#705039")); painter.drawRect(x + 76, 641, 38, 48)
        painter.setBrush(QColor("#33231b")); painter.drawRect(1110, 545, 300, 96); painter.setBrush(QColor("#20272c")); painter.drawRect(1170, 490, 180, 55); painter.setBrush(QColor("#705039")); painter.drawRect(1240, 641, 42, 50)
    def draw_weather(self, painter):
        painter.setPen(QColor("#a9c6d9")); painter.setBrush(QColor("#a9c6d9")); step = 18 if self.weather == "비" else 30
        for i in range(0, self.width(), step):
            yy = 70 + ((i + self.agents["현무"].frame * 8) % 220); painter.drawRect(i, yy, 2, 12) if self.weather == "비" else painter.drawRect(i, yy, 4, 4)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle("돈물원 · DONMULWON"); self.resize(1500, 950); self.setStyleSheet("QMainWindow{background:#111416;color:#ded7c5;} QLabel{color:#ded7c5;}")
        root = QWidget(); layout = QVBoxLayout(root); layout.setContentsMargins(18, 14, 18, 14)
        top = QHBoxLayout(); title = QLabel("🏦 DONMULWON  ·  AI TRADING TEAM"); title.setStyleSheet("font-size:22px;font-weight:700;"); top.addWidget(title); top.addStretch(); self.clock = QLabel(); top.addWidget(self.clock); layout.addLayout(top)
        self.office = PixelOffice(); layout.addWidget(self.office, 1)
        bottom = QHBoxLayout(); self.input = QLineEdit(); self.input.setPlaceholderText("무엇을 분석할까요?"); self.button = QPushButton("분석 시작"); self.button.clicked.connect(self.start_analysis); self.input.returnPressed.connect(self.start_analysis); self.weather = QComboBox(); self.weather.addItems(["맑음", "비", "눈"]); self.weather.currentTextChanged.connect(self.office.set_weather); bottom.addWidget(self.input, 1); bottom.addWidget(self.weather); bottom.addWidget(self.button); layout.addLayout(bottom)
        self.status = QLabel("대기 중 · 2D PIXEL OFFICE"); layout.addWidget(self.status); self.progress = QProgressBar(); self.progress.setRange(0, 0); self.progress.hide(); layout.addWidget(self.progress); self.output = QPlainTextEdit(); self.output.setReadOnly(True); self.output.setMaximumHeight(230); layout.addWidget(self.output); self.setCentralWidget(root)
        self.clock_timer = QTimer(self); self.clock_timer.timeout.connect(self.update_clock); self.clock_timer.start(1000); self.update_clock()
    def update_clock(self):
        now = datetime.now(); self.clock.setText(now.strftime("%Y-%m-%d  %H:%M:%S")); hour = now.hour; self.office.time = "아침" if 6 <= hour < 11 else "낮" if 11 <= hour < 18 else "노을" if 18 <= hour < 20 else "밤"; self.office.update()
    def start_analysis(self):
        question = self.input.text().strip()
        if not question: return
        self.button.setEnabled(False); self.input.setEnabled(False); self.progress.show(); self.status.setText("AI 팀 분석 진행 중..."); self.output.clear(); self.thread = QThread(self); self.worker = AnalysisWorker(question); self.worker.moveToThread(self.thread); self.worker.output.connect(self.output.setPlainText); self.worker.finished.connect(self.analysis_done); self.worker.failed.connect(self.analysis_failed); self.thread.started.connect(self.worker.run); self.thread.start()
    def analysis_done(self):
        self.progress.hide(); self.button.setEnabled(True); self.input.setEnabled(True); self.status.setText("분석 완료 · 알프레도 최종 검증 완료"); self.thread.quit()
    def analysis_failed(self, error):
        self.progress.hide(); self.button.setEnabled(True); self.input.setEnabled(True); self.status.setText("분석 실패"); self.output.setPlainText(error); self.thread.quit()

def main():
    app = QApplication(sys.argv); window = MainWindow(); window.show(); return app.exec()

if __name__ == "__main__": sys.exit(main())
