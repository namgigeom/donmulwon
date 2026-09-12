# DONMULWON - TOP DOWN PIXEL OFFICE
import os
import sys
import io
import contextlib
import traceback
from datetime import datetime

from PySide6.QtCore import QObject, QThread, Signal, Slot, Qt, QRect, QTimer
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QPlainTextEdit, QProgressBar, QComboBox
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from gui_background import PixelBackground
from gui_characters_v2 import CharacterLayer
from gui_motion import MotionController


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
                if not hasattr(main, "run_analysis"):
                    raise AttributeError("main.py에 run_analysis()가 없습니다.")
                result = main.run_analysis(self.question)

            # GUI에는 회의 전체 로그가 아니라 실제 최종 답변을 우선 표시한다.
            log = buf.getvalue().strip()
            answer = ""
            if isinstance(result, dict):
                answer = str(result.get("alfredo", "") or "").strip()
            elif result is not None:
                answer = str(result).strip()

            if not answer:
                answer = "❌ 알프레도의 최종 판단이 생성되지 않았습니다.\n\n" + (log[-5000:] if log else "로그가 없습니다.")

            # 디버깅이 필요할 때도 답변이 먼저 보이도록 한다.
            if log:
                answer += "\n\n────────────────────────\n[회의 로그]\n" + log[-5000:]

            self.output.emit(answer)
            self.finished.emit()
        except Exception:
            self.failed.emit(traceback.format_exc())


class PixelOffice(QWidget):
    # 각자 자기 책상. 회의 테이블보다 충분히 위쪽에 배치한다.
    DESK_LAYOUT = [
        ("현무", 55, 244, 175),
        ("김선달", 320, 244, 175),
        ("이묵", 585, 244, 175),
        ("너부리", 850, 244, 175),
        ("알프레도", 1115, 244, 175),
    ]

    def __init__(self):
        super().__init__()
        self.background = PixelBackground()
        self.characters = CharacterLayer()
        self.motion = MotionController(self)
        self.setMinimumHeight(620)

    def set_weather(self, value):
        self.background.set_weather(value)
        self.update()

    def auto_time(self):
        now = datetime.now()
        hour = now.hour
        self.background.set_clock(now)
        if 5 <= hour < 11:
            period = "아침"
        elif 11 <= hour < 17:
            period = "낮"
        elif 17 <= hour < 21:
            period = "저녁"
        else:
            period = "밤"
        self.background.set_time(period)
        return period

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, False)
        try:
            w, h = self.width(), self.height()
            self.background.paint(p, w, h)
            self.draw_desks(p)
            self.draw_conference_area(p, w, h)
            self.characters.paint(p)
            self.draw_character_labels(p)
            self.draw_side_monitor(p, w)
        finally:
            if p.isActive():
                p.end()

    @staticmethod
    def rect(p, x, y, w, h, color):
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(color))
        p.drawRect(int(x), int(y), int(w), int(h))

    @staticmethod
    def text(p, x, y, w, h, value, size=8, color="#eee4d2", align=Qt.AlignLeft | Qt.AlignVCenter):
        p.setPen(QColor(color))
        p.setFont(QFont("Malgun Gothic", size, QFont.Bold))
        p.drawText(QRect(int(x), int(y), int(w), int(h)), align, str(value))

    def draw_desks(self, p):
        for name, x, y, desk_w in self.DESK_LAYOUT:
            # 바닥 그림자
            self.rect(p, x + 12, y + 68, desk_w - 24, 7, "#30251e")

            # 의자
            chair_x = x + desk_w // 2 - 27
            self.rect(p, chair_x + 3, y + 72, 54, 32, "#17191d")
            self.rect(p, chair_x + 8, y + 77, 44, 20, "#36383c")
            self.rect(p, chair_x + 13, y + 81, 34, 12, "#4b4d50")
            self.rect(p, chair_x + 5, y + 101, 50, 5, "#17191d")

            # 책상 다리: 상판보다 먼저 그려서 실제로 받치는 구조
            for lx in (x + 10, x + desk_w - 20):
                self.rect(p, lx, y + 48, 10, 29, "#241a15")
                self.rect(p, lx + 3, y + 51, 4, 23, "#4d392a")

            # 책상 상판
            self.rect(p, x - 3, y - 3, desk_w + 6, 62, "#201713")
            self.rect(p, x, y, desk_w, 55, "#5c3e28")
            self.rect(p, x + 5, y + 5, desk_w - 10, 45, "#795337")
            self.rect(p, x + 9, y + 9, desk_w - 18, 37, "#68472f")

            # 나뭇결
            self.rect(p, x + 12, y + 13, 38, 2, "#916844")
            self.rect(p, x + 62, y + 28, 30, 2, "#8a5f3d")
            self.rect(p, x + desk_w - 55, y + 38, 38, 2, "#513621")

            # 모니터
            mx = x + desk_w // 2 - 39
            self.rect(p, mx + 29, y + 40, 20, 7, "#171b1f")
            self.rect(p, mx + 33, y + 37, 12, 6, "#555a5d")
            self.rect(p, mx, y + 6, 78, 35, "#171c20")
            self.rect(p, mx + 4, y + 10, 70, 27, "#15252b")
            self.rect(p, mx + 9, y + 14, 60, 1, "#2e4248")
            pts = [(mx + 11, y + 32), (mx + 20, y + 27), (mx + 29, y + 30),
                   (mx + 38, y + 21), (mx + 48, y + 25), (mx + 60, y + 16)]
            p.setPen(QColor("#c6aa6d"))
            for a, b in zip(pts, pts[1:]):
                p.drawLine(a[0], a[1], b[0], b[1])
            p.setPen(Qt.NoPen)

            # 키보드 / 마우스
            self.rect(p, x + desk_w // 2 - 43, y + 43, 66, 8, "#25282b")
            self.rect(p, x + desk_w // 2 - 37, y + 45, 54, 4, "#777b7b")
            self.rect(p, x + desk_w // 2 + 29, y + 43, 8, 9, "#292c2e")

            # 서랍
            self.rect(p, x + desk_w - 31, y + 34, 22, 18, "#4a3021")
            self.rect(p, x + desk_w - 28, y + 38, 16, 5, "#60432d")
            self.rect(p, x + desk_w - 28, y + 46, 16, 4, "#60432d")
            self.rect(p, x + desk_w - 21, y + 40, 3, 2, "#c0a06c")
            self.rect(p, x + desk_w - 21, y + 48, 3, 2, "#c0a06c")

            # 이름은 칠판/전광판 위가 아니라 자기 책상 상판에 표시한다.
            self.rect(p, x + 7, y + 48, 64, 9, "#2b211c")
            self.text(p, x + 8, y + 47, 62, 11, name, 6, "#e0c991", Qt.AlignCenter)

    def draw_conference_area(self, p, w, h):
        cx = w // 2

        # 대형 시장 전광판: 회의 테이블과 겹치지 않게 위쪽에 고정.
        board_w = min(560, max(480, w - 850))
        board_h = 102
        board_x = cx - board_w // 2
        board_y = 350

        # 벽 고정 브래킷
        self.rect(p, board_x + 25, board_y + board_h, 14, 38, "#29201b")
        self.rect(p, board_x + board_w - 39, board_y + board_h, 14, 38, "#29201b")
        self.rect(p, board_x + 18, board_y + board_h + 32, board_w - 36, 7, "#211916")

        # 프레임
        self.rect(p, board_x - 6, board_y - 6, board_w + 12, board_h + 12, "#211914")
        self.rect(p, board_x - 2, board_y - 2, board_w + 4, board_h + 4, "#6b5138")
        self.rect(p, board_x + 5, board_y + 5, board_w - 10, board_h - 10, "#11171a")
        self.rect(p, board_x + 10, board_y + 10, board_w - 20, board_h - 20, "#17252a")

        self.text(p, board_x + 16, board_y + 8, 220, 16, "DONMULWON · TEAM MARKET", 7, "#d8c48e")
        self.text(p, board_x + board_w - 75, board_y + 8, 55, 16, "LIVE", 7, "#b5c08e", Qt.AlignRight)

        grid_top = board_y + 32
        grid_bottom = board_y + board_h - 17
        p.setPen(QColor("#293d42"))
        for i in range(1, 4):
            yy = grid_top + i * (grid_bottom - grid_top) // 4
            p.drawLine(board_x + 17, yy, board_x + board_w - 17, yy)
        for i in range(1, 7):
            xx = board_x + 17 + i * (board_w - 34) // 7
            p.drawLine(xx, grid_top, xx, grid_bottom)

        values = [.44, .40, .48, .45, .55, .50, .63, .58, .70, .66, .79, .74, .86]
        pts = []
        plot_w = board_w - 42
        plot_h = grid_bottom - grid_top - 2
        for i, value in enumerate(values):
            px = board_x + 21 + int(i * plot_w / (len(values) - 1))
            py = grid_bottom - int(value * plot_h)
            pts.append((px, py))
        p.setPen(QColor("#d0b477"))
        for a, b in zip(pts, pts[1:]):
            p.drawLine(a[0], a[1], b[0], b[1])
        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#e1c681"))
        for px, py in pts:
            p.drawRect(px - 2, py - 2, 5, 5)

        self.rect(p, board_x + 17, board_y + board_h - 24, board_w - 34, 9, "#202f33")
        self.text(p, board_x + 22, board_y + board_h - 25, board_w - 44, 11,
                  "VOO +0.8%   JOBY +2.4%   SOFI +1.6%   KO +0.3%", 6, "#cdb985")

        # 회의 테이블: 가로폭을 확실히 줄이고 출입문과 겹치지 않도록 중앙 배치.
        table_w = min(390, max(340, w - 1000))
        table_h = 52
        table_x = cx - table_w // 2
        table_y = 500

        # 다리
        for lx in (table_x + 24, table_x + table_w - 38):
            self.rect(p, lx, table_y + 38, 14, 34, "#241a15")
            self.rect(p, lx + 3, table_y + 41, 7, 28, "#4e3829")
        self.rect(p, cx - 7, table_y + 38, 14, 34, "#241a15")
        self.rect(p, cx - 4, table_y + 41, 8, 28, "#4e3829")

        # 상판
        self.rect(p, table_x - 5, table_y - 5, table_w + 10, table_h + 10, "#211713")
        self.rect(p, table_x, table_y, table_w, table_h, "#4d3323")
        self.rect(p, table_x + 6, table_y + 6, table_w - 12, table_h - 12, "#725037")
        self.rect(p, table_x + 13, table_y + 13, table_w - 26, table_h - 26, "#825c3e")
        self.rect(p, table_x + 25, table_y + 25, table_w - 50, 2, "#5e402b")

        # 회의 의자: 테이블과 분리되어 보이게 한다.
        for sx in (table_x + 20, table_x + table_w - 60):
            self.rect(p, sx, table_y - 16, 40, 11, "#252326")
            self.rect(p, sx + 5, table_y - 13, 30, 6, "#4a4548")
            self.rect(p, sx, table_y + table_h + 5, 40, 11, "#252326")
            self.rect(p, sx + 5, table_y + table_h + 8, 30, 6, "#4a4548")

        # 회의용 문서
        self.rect(p, cx - 48, table_y + 17, 96, 19, "#33261e")
        self.rect(p, cx - 40, table_y + 20, 80, 12, "#b9a27a")
        self.rect(p, cx - 26, table_y + 23, 52, 2, "#806947")
        self.text(p, table_x, table_y + table_h + 18, table_w, 16,
                  "⚔ AI TRADING TEAM · CONFERENCE", 6, "#bca87e", Qt.AlignCenter)

    def draw_character_labels(self, p):
        # 별도 이름을 캐릭터 아래에 그리지 않는다. 이름은 각 책상 위 명패에만 있다.
        return

    def draw_side_monitor(self, p, w):
        x, y, ww, hh = w - 218, 112, 188, 108
        self.rect(p, x + 4, y + 5, ww, hh, "#17191b")
        self.rect(p, x, y, ww, hh, "#292d2e")
        self.rect(p, x + 5, y + 5, ww - 10, hh - 10, "#172125")
        self.text(p, x + 12, y + 9, 160, 16, "ACCOUNT MONITOR", 7, "#d8c48e")
        self.text(p, x + 12, y + 30, 160, 16, "PORTFOLIO", 6, "#8fa69a")
        self.text(p, x + 12, y + 48, 165, 16, "VOO     50%", 7)
        self.text(p, x + 12, y + 64, 165, 16, "KO      25%", 7)
        self.text(p, x + 12, y + 80, 165, 16, "SOFI    12.5%", 7)
        self.text(p, x + 92, y + 80, 80, 16, "JEPQ 6.25%", 6, "#bca87e", Qt.AlignRight)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("돈물원 · DONMULWON")
        self.resize(1500, 900)
        self.setStyleSheet(
            "QMainWindow{background:#111416;color:#ded7c5;}"
            "QLabel{color:#ded7c5;}"
            "QLineEdit,QPlainTextEdit,QComboBox{background:#202428;color:#eee4d2;border:1px solid #51483b;padding:7px;}"
            "QPushButton{background:#665039;color:#fff2d4;padding:8px 14px;border:1px solid #8a6c4c;}"
            "QProgressBar{border:1px solid #51483b;background:#202428;}"
            "QProgressBar::chunk{background:#806544;}"
        )

        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(18, 14, 18, 14)

        top = QHBoxLayout()
        title = QLabel("🏦 DONMULWON · AI TRADING TEAM")
        title.setStyleSheet("font-size:22px;font-weight:700;")
        top.addWidget(title)
        top.addStretch()
        self.clock = QLabel()
        top.addWidget(self.clock)
        layout.addLayout(top)

        self.office = PixelOffice()
        layout.addWidget(self.office, 1)

        controls = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("무엇을 분석할까요? (예: JOBY 지금 사도 괜찮아?)")
        self.button = QPushButton("분석 시작")
        self.button.clicked.connect(self.start_analysis)
        self.input.returnPressed.connect(self.start_analysis)
        self.weather = QComboBox()
        self.weather.addItems(["맑음", "비", "눈"])
        self.weather.currentTextChanged.connect(self.office.set_weather)
        controls.addWidget(self.input, 1)
        controls.addWidget(self.weather)
        controls.addWidget(self.button)
        layout.addLayout(controls)

        self.status = QLabel("대기 중 · TOP-DOWN PIXEL OFFICE")
        layout.addWidget(self.status)
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.hide()
        layout.addWidget(self.progress)
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setMaximumHeight(220)
        layout.addWidget(self.output)
        self.setCentralWidget(root)

        self.ui_timer = QTimer(self)
        self.ui_timer.timeout.connect(self.update_clock)
        self.ui_timer.start(1000)
        self.update_clock()
        self.thread = None
        self.worker = None

    def update_clock(self):
        now = datetime.now()
        period = self.office.auto_time()
        self.clock.setText(now.strftime("%Y-%m-%d  %H:%M:%S") + f"  ·  {period}")

    def start_analysis(self):
        q = self.input.text().strip()
        if not q or self.thread is not None:
            return

        behavior = self.office.motion.on_question()
        if behavior == "summoned":
            self.status.setText("🏃 퇴근 후 긴급 호출 · AI TRADING TEAM 복귀 중...")
        elif behavior == "overtime":
            self.status.setText("🌙 야근 모드 · AI TRADING TEAM 회의 시작")
        else:
            self.status.setText("⚔️ AI TRADING TEAM 회의 진행 중...")

        self.button.setEnabled(False)
        self.progress.show()
        self.output.clear()

        self.thread = QThread(self)
        self.worker = AnalysisWorker(q)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.output.connect(self.output.setPlainText)
        self.worker.failed.connect(self.on_failed)
        self.worker.finished.connect(self.on_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.failed.connect(self.thread.quit)
        self.thread.finished.connect(self.cleanup_thread)
        self.thread.start()

    def on_failed(self, text):
        self.output.setPlainText("❌ 분석 오류\n\n" + text)
        self.status.setText("오류 발생 · 로그를 확인하세요")

    def on_finished(self):
        self.progress.hide()
        self.button.setEnabled(True)
        self.status.setText("✅ 분석 완료")

    def cleanup_thread(self):
        if self.worker:
            self.worker.deleteLater()
        if self.thread:
            self.thread.deleteLater()
        self.worker = None
        self.thread = None


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
