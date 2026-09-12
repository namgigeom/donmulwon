import os
import sys
import io
import contextlib
import traceback
import re
from datetime import datetime

from PySide6.QtCore import QObject, QThread, Signal, Slot, Qt, QTimer
from PySide6.QtGui import QFont, QPainter, QPen, QBrush, QColor
from PySide6.QtWidgets import (
    QApplication, QFrame, QGraphicsScene, QGraphicsView, QHBoxLayout,
    QLabel, QLineEdit, QMainWindow, QMessageBox, QPushButton, QPlainTextEdit,
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
    """Wide 2D pixel-art office scene. No 3D/isometric perspective."""
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
        self.timer.start(350)
        self.draw_scene()

    def _tick(self):
        self.anim_tick = (self.anim_tick + 1) % 12
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
            sky, sky2, ground = "#9fb9c0", "#c7c7ad", "#5b6865"
            label = "MORNING"
        elif 10 <= hour < 17:
            sky, sky2, ground = "#9fc1c9", "#d2d2bd", "#66706a"
            label = "DAY"
        elif 17 <= hour < 20:
            sky, sky2, ground = "#9a8277", "#d1a77e", "#4f5350"
            label = "SUNSET"
        else:
            sky, sky2, ground = "#202d4d", "#2d3a58", "#20252d"
            label = "NIGHT"
        if self.weather == "cloud":
            sky, sky2 = "#6f7d82", "#929b96"
        if self.weather in ("rain", "snow"):
            sky, sky2 = ("#526576", "#6c7880") if self.weather == "rain" else ("#78848b", "#9ca5a7")

        self.rect(wx, wy, ww, wh, sky, "#39464d", 3)
        self.rect(wx + 3, wy + 3, ww - 6, 95, sky2)
        self.text(wx + 16, wy + 12, label, 7, True, "#d7d0bc")

        # Pixel clouds / stars.
        if datetime.now().hour >= 20 or datetime.now().hour < 6:
            for sx, sy in [(wx+90,wy+38),(wx+260,wy+24),(wx+590,wy+54),(wx+820,wy+29),(wx+980,wy+65)]:
                self.px(sx, sy, 3, 3, "#d7d7c2")
        else:
            for sx, sy in [(wx+105,wy+42),(wx+430,wy+30),(wx+760,wy+48)]:
                self.px(sx, sy, 22, 4, "#d8d5c3")
                self.px(sx+7, sy-4, 10, 4, "#d8d5c3")

        buildings = [
            (wx+15, 172, 55, 92), (wx+82, 148, 70, 116), (wx+170, 188, 48, 76),
            (wx+232, 126, 74, 138), (wx+324, 164, 57, 100), (wx+395, 105, 78, 159),
            (wx+492, 151, 61, 113), (wx+568, 121, 82, 143), (wx+668, 173, 56, 91),
            (wx+740, 139, 76, 125), (wx+834, 102, 68, 162), (wx+920, 158, 58, 106),
            (wx+992, 132, 82, 132)
        ]
        for bx, by, bw, bh in buildings:
            self.rect(bx, by, bw, bh, "#333b42")
            self.rect(bx+5, by+5, bw-10, 5, "#22292f")
            for yy in range(by+18, by+bh-8, 17):
                for xx in range(bx+9, bx+bw-6, 16):
                    lit = ((xx+yy)//7 + datetime.now().hour) % 4 != 0
                    if lit:
                        self.px(xx, yy, 5, 7, "#b9a86d")
        # One tall pixel-art tower to echo the supplied reference without copying it.
        tx, ty = wx + 410, 84
        self.rect(tx, ty, 30, 180, "#252d35")
        self.rect(tx+8, ty-30, 14, 30, "#252d35")
        self.rect(tx+12, ty-42, 6, 12, "#4b5359")
        for yy in range(ty+12, ty+168, 17):
            self.px(tx+6, yy, 5, 7, "#b7a76c")
            self.px(tx+18, yy+5, 5, 7, "#68747a")

        self.rect(wx+3, 235, ww-6, 29, ground)
        for i in range(1, 5):
            xx = wx + ww*i/5
            self.line(xx, wy, xx, wy+wh, "#46565d", 3)
        self.line(wx, 235, wx+ww, 235, "#3c4b50", 2)

        if self.weather == "rain":
            for i in range(34):
                x = wx + 15 + ((i*73 + self.anim_tick*13) % int(ww-30))
                y = wy + 12 + ((i*41) % 205)
                self.line(x, y, x-4, y+12, "#9eb6bf", 1)
        elif self.weather == "snow":
            for i in range(24):
                x = wx + 12 + ((i*61 + self.anim_tick*5) % int(ww-24))
                y = wy + 10 + ((i*47 + self.anim_tick*4) % 215)
                self.px(x, y, 3, 3, "#e6e4d8")

    def draw_scene(self):
        self.scene().clear()
        W, H = 1600, 820
        self.scene().setSceneRect(0, 0, W, H)
        self.rect(0, 0, W, H, "#171a1d")
        # Wall / floor are deliberately flat 2D blocks.
        self.rect(18, 18, 1564, 315, "#34393b", "#6a6b62", 2)
        self.text(38, 31, "DONMULWON  •  AI TRADING OFFICE", 10, True, "#e1d4b7")

        wx, wy, ww, wh = 205, 63, 1090, 242
        self.draw_sky(wx, wy, ww, wh)

        # Door at far left; window is never attached to the door.
        ex, ey = 45, 93
        self.rect(ex, ey, 122, 142, "#202629", "#65706d", 2)
        self.rect(ex+12, ey+12, 98, 82, "#2b393c")
        self.rect(ex+31, ey+28, 58, 34, "#708f76")
        self.text(ex+42, ey+31, "EXIT", 12, True, "#f1ecd6")
        self.text(ex+19, ey+105, "STAFF DOOR", 7, True, "#c9c0a5")
        self.text(ex+19, ey+119, "HYEONMU SIDE", 6, False, "#8d9991")

        # Market side monitor: intentionally compact so the office scene remains dominant.
        px, py, pw, ph = 1310, 58, 240, 246
        self.rect(px, py, pw, ph, "#202629", "#8e7b58", 2)
        self.text(px+14, py+12, "MARKET", 9, True, "#e4d8bd")
        self.text(px+14, py+31, "VOO", 8, True, "#a9b09e")
        self.text(px+50, py+29, "$704.03", 10, True, "#91b69b")
        self.text(px+145, py+31, "+5.96%", 7, True, "#91b69b")
        cx, cy, cw, ch = px+14, py+55, pw-28, 112
        self.rect(cx, cy, cw, ch, "#182022", "#435154", 1)
        for gy in (cy+28, cy+56, cy+84): self.line(cx+5, gy, cx+cw-5, gy, "#2d383a", 1)
        vals = [57, 52, 64, 60, 70, 67, 80, 76, 91, 84, 97, 91, 104, 101]
        pts=[]
        for i,v in enumerate(vals):
            xx=cx+7+i*(cw-14)/(len(vals)-1); yy=cy+ch-8-v*.73; pts.append((xx,yy))
        for a,b in zip(pts,pts[1:]): self.line(a[0],a[1],b[0],b[1],"#91b69b",3)
        for xx,yy in pts: self.px(xx-2,yy-2,4,4,"#d6dfc6")
        self.text(px+14, py+180, "ACCOUNT", 7, True, "#929b91")
        self.text(px+72, py+177, "$1,124.19", 10, True, "#e0d5bb")
        self.text(px+14, py+200, "JEPQ  13.0%", 7, True, "#b6ae9c")
        self.text(px+14, py+218, "TTWO  24.2%", 7, True, "#b6ae9c")

        self.rect(20, 328, 1560, 16, "#181b1d")

        agents = [
            ("현무", "MACRO", "#5f8073", "turtle"),
            ("김선달", "FUNDAMENTAL + NEWS", "#9b7b4a", "bird"),
            ("이묵", "TECHNICAL", "#4f7488", "snake"),
            ("너부리", "PORTFOLIO + ACCOUNT", "#836653", "raccoon"),
            ("알프레도", "TEAM LEAD / VERIFIER", "#a97447", "cat"),
        ]
        # Wide straight row. Alfredo is separate but aligned on the same floor line.
        xs = [35, 335, 635, 935, 1265]
        for i, data in enumerate(agents):
            self.draw_agent(xs[i], 370, 275 if i<4 else 300, *data, lead=(i==4))

        self.text(36, 742, "PIXEL OFFICE  •  EACH AGENT HAS A SEPARATE DESK  •  LIVE MARKET PANEL", 8, True, "#a49b85")
        self.text(1350, 742, datetime.now().strftime("%Y-%m-%d  %H:%M"), 8, True, "#a49b85")

    def draw_agent(self, x, y, w, name, role, accent, kind, lead=False):
        # Back chair.
        self.rect(x+w/2-29, y+115, 58, 65, "#292d30", "#151719", 2)
        self.rect(x+w/2-39, y+169, 78, 9, "#141719")
        self.draw_character(x+w/2, y+8, kind, accent)

        # Desk: one horizontal plane, no perspective.
        self.rect(x+10, y+92, w-20, 15, "#aa8a5b", "#4b3926", 2)
        self.rect(x+18, y+107, w-36, 56, "#553d2b", "#30251d", 2)
        self.rect(x+31, y+116, w-62, 41, "#1c272a", "#64706b", 2)
        self.rect(x+42, y+126, w-84, 4, accent)
        self.rect(x+42, y+137, w-84, 3, "#56605e")
        self.rect(x+42, y+147, w-84, 3, "#56605e")
        self.rect(x+23, y+163, w-46, 13, accent)
        self.rect(x+32, y+176, 10, 48, "#2b211a")
        self.rect(x+w-42, y+176, 10, 48, "#2b211a")
        self.rect(x+6, y+221, w-12, 7, "#17191a")
        self.rect(x+20, y+238, w-40, 30, "#202529", "#665c4c", 1)
        self.text(x+30, y+241, name, 10, True, "#eee6d2")
        self.text(x+30, y+255, role, 6, True, "#a39a86", w-60)
        if lead:
            self.rect(x+w-82, y+240, 54, 15, "#a97447")
            self.text(x+w-77, y+241, "LEAD", 6, True, "#fff0d2")

    def draw_character(self, cx, y, kind, accent):
        # Detailed 2D pixel sprite. Suits are mandatory; silhouette is built from small blocks.
        dark="#181b1d"; outline="#24282a"; skin="#e8e1ce"; shirt="#ddd8c9"
        suit=accent
        # legs / suit jacket
        self.px(cx-18,y+61,36,30,suit); self.px(cx-16,y+87,12,12,dark); self.px(cx+4,y+87,12,12,dark)
        self.px(cx-12,y+48,24,13,shirt); self.px(cx-3,y+49,6,34,dark); self.px(cx-18,y+56,6,26,suit); self.px(cx+12,y+56,6,26,suit)
        self.px(cx-7,y+57,4,8,"#bda66c"); self.px(cx+3,y+57,4,8,"#bda66c")
        # head varies by mascot
        if kind=="turtle":
            shell="#34594e"; mid="#6f947f"; skin2="#88aa8e"
            self.px(cx-19,y+15,38,36,shell); self.px(cx-24,y+23,5,15,mid); self.px(cx+19,y+23,5,15,mid)
            self.px(cx-14,y+10,28,9,shell); self.px(cx-13,y+17,26,28,skin2)
            self.px(cx-9,y+21,7,6,"#d1d9bd"); self.px(cx+3,y+21,7,6,"#d1d9bd")
            self.px(cx-7,y+23,4,4,dark); self.px(cx+4,y+23,4,4,dark); self.px(cx-5,y+34,10,4,"#4c735f")
            self.px(cx-15,y+5,30,5,"#243f38"); self.px(cx-8,y+1,16,4,"#243f38")
        elif kind=="bird":
            feather="#3b3f42"; beak="#b7904f"
            self.px(cx-17,y+17,34,32,feather); self.px(cx-12,y+9,24,12,feather); self.px(cx-6,y+4,12,7,feather)
            self.px(cx+16,y+24,10,6,beak); self.px(cx-10,y+20,6,6,"#d8d0b8"); self.px(cx+4,y+20,6,6,"#d8d0b8")
            self.px(cx-8,y+22,4,4,dark); self.px(cx+6,y+22,4,4,dark); self.px(cx-4,y+32,8,5,"#555b5c")
        elif kind=="snake":
            green="#567763"; light="#88a07c"
            self.px(cx-14,y+9,28,8,green); self.px(cx-20,y+17,40,27,green); self.px(cx-13,y+43,26,8,light)
            self.px(cx-10,y+20,7,6,"#cbd2b8"); self.px(cx+3,y+20,7,6,"#cbd2b8"); self.px(cx-8,y+22,4,4,dark); self.px(cx+5,y+22,4,4,dark)
            self.px(cx-18,y+29,6,6,light); self.px(cx+12,y+29,6,6,light); self.px(cx+12,y+45,14,4,"#7c4e42")
        elif kind=="raccoon":
            fur="#6e625a"; mask="#292a2b"; lightfur="#aaa08f"
            self.px(cx-19,y+16,38,31,fur); self.px(cx-13,y+8,26,11,fur); self.px(cx-15,y+4,7,7,fur); self.px(cx+8,y+4,7,7,fur)
            self.px(cx-15,y+19,30,12,mask); self.px(cx-11,y+21,7,6,"#d9d3c2"); self.px(cx+4,y+21,7,6,"#d9d3c2")
            self.px(cx-9,y+23,4,4,dark); self.px(cx+5,y+23,4,4,dark); self.px(cx-5,y+33,10,5,lightfur)
        else:
            fur="#8b6c58"; lightfur="#c6a98a"
            self.px(cx-18,y+15,36,34,fur); self.px(cx-13,y+7,26,12,fur); self.px(cx-16,y+3,8,9,fur); self.px(cx+8,y+3,8,9,fur)
            self.px(cx-11,y+19,7,7,"#eee4cd"); self.px(cx+4,y+19,7,7,"#eee4cd"); self.px(cx-8,y+21,4,4,dark); self.px(cx+5,y+21,4,4,dark)
            self.px(cx-4,y+31,8,5,"#392b26"); self.px(cx-6,y+38,12,4,lightfur)
        # suit collar / tie pixels over mascot body
        self.px(cx-13,y+49,7,4,shirt); self.px(cx+6,y+49,7,4,shirt); self.px(cx-3,y+51,6,13,"#25282a")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("돈물원 — DONMULWON AI Trading Team")
        self.resize(1500, 980)
        self.setMinimumSize(1180, 800)
        self.worker_thread = None
        self.worker = None

        root = QWidget(); self.setCentralWidget(root)
        root.setStyleSheet("QWidget{background:#171a1d;color:#e7dfcb;} QLabel{font-family:'Malgun Gothic';}")
        layout = QVBoxLayout(root); layout.setContentsMargins(10,10,10,10); layout.setSpacing(8)

        header = QHBoxLayout()
        title = QLabel("DONMULWON  /  돈물원")
        title.setStyleSheet("font-size:25px;font-weight:700;color:#dfcfaa;")
        header.addWidget(title)
        sub = QLabel("AI TRADING TEAM")
        sub.setStyleSheet("font-size:11px;color:#9d9a8b;")
        header.addWidget(sub); header.addStretch()
        self.weather = QComboBox(); self.weather.addItems(["맑음","흐림","비","눈"])
        self.weather.setStyleSheet("QComboBox{background:#24292c;border:1px solid #615947;padding:6px;color:#e5dcc7;} QComboBox QAbstractItemView{background:#24292c;color:#e5dcc7;}")
        self.weather.currentTextChanged.connect(self._weather_changed)
        header.addWidget(QLabel("날씨")); header.addWidget(self.weather)
        self.clock = QLabel(); self.clock.setStyleSheet("font-size:11px;color:#aaa18c;padding-left:12px;"); header.addWidget(self.clock)
        layout.addLayout(header)

        self.office = PixelOfficeView()
        layout.addWidget(self.office, 1)

        bottom = QFrame(); bottom.setStyleSheet("QFrame{background:#24292c;border:1px solid #5c5445;border-radius:8px;}")
        bl = QHBoxLayout(bottom); bl.setContentsMargins(12,10,12,10)
        self.input = QLineEdit(); self.input.setPlaceholderText("무엇을 분석할까요?  예: VOO랑 JEPQ 추가매수했는데 어때?")
        self.input.setStyleSheet("QLineEdit{background:#171a1d;border:1px solid #625945;border-radius:6px;padding:10px;color:#eee5d0;font-size:13px;}" )
        self.input.returnPressed.connect(self.start_analysis)
        bl.addWidget(self.input, 1)
        self.button = QPushButton("분석 시작")
        self.button.setStyleSheet("QPushButton{background:#80653f;color:#fff0d3;border:0;border-radius:6px;padding:10px 20px;font-weight:700;} QPushButton:disabled{background:#49443b;color:#8c887d;}")
        self.button.clicked.connect(self.start_analysis); bl.addWidget(self.button)
        layout.addWidget(bottom)

        self.status = QLabel("대기 중 · 사무실 운영 정상")
        self.status.setStyleSheet("color:#a9a28f;font-size:11px;padding:2px 4px;")
        layout.addWidget(self.status)
        self.progress = QProgressBar(); self.progress.setRange(0,0); self.progress.setVisible(False)
        self.progress.setStyleSheet("QProgressBar{background:#202427;border:0;height:4px;} QProgressBar::chunk{background:#8b7350;}")
        layout.addWidget(self.progress)

        self.output = QPlainTextEdit(); self.output.setReadOnly(True); self.output.setPlaceholderText("분석 결과가 여기에 표시됩니다.")
        self.output.setStyleSheet("QPlainTextEdit{background:#111416;border:1px solid #4b4539;color:#ded7c5;font-family:'Malgun Gothic';font-size:12px;padding:8px;}")
        self.output.setMaximumHeight(235)
        layout.addWidget(self.output)

        self.clock_timer = QTimer(self); self.clock_timer.timeout.connect(self._clock); self.clock_timer.start(1000); self._clock()

    def _clock(self):
        self.clock.setText(datetime.now().strftime("%Y-%m-%d  %H:%M:%S"))

    def _weather_changed(self, value):
        self.office.set_weather(value)
        self.status.setText(f"사무실 환경 · {value} · 2D PIXEL MODE")

    def start_analysis(self):
        question = self.input.text().strip()
        if not question: return
        self.button.setEnabled(False); self.input.setEnabled(False); self.progress.setVisible(True)
        self.status.setText("AI 팀 분석 진행 중...")
        self.output.clear()
        self.worker_thread = QThread(self); self.worker = AnalysisWorker(question); self.worker.moveToThread(self.worker_thread)
        self.worker.status.connect(self.status.setText); self.worker.output.connect(self.output.setPlainText)
        self.worker.finished.connect(self._analysis_finished); self.worker.failed.connect(self._analysis_failed)
        self.worker_thread.started.connect(self.worker.run); self.worker_thread.start()

    def _analysis_finished(self):
        self.progress.setVisible(False); self.button.setEnabled(True); self.input.setEnabled(True); self.status.setText("분석 완료 · 알프레도 최종 검증 완료")
        self._cleanup_thread()

    def _analysis_failed(self, error):
        self.progress.setVisible(False); self.button.setEnabled(True); self.input.setEnabled(True); self.status.setText("분석 실패 · 오류 내용을 결과창에서 확인")
        self.output.setPlainText(error); self._cleanup_thread()

    def _cleanup_thread(self):
        if self.worker_thread:
            self.worker_thread.quit(); self.worker_thread.wait(3000); self.worker_thread.deleteLater(); self.worker_thread=None; self.worker=None


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MainWindow(); win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
