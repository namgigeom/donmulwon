import os
import sys
import io
import contextlib
import traceback

from PySide6.QtCore import QObject, QThread, Signal, Slot, Qt
from PySide6.QtGui import QFont, QPainter, QPen, QBrush
from PySide6.QtWidgets import (
    QApplication, QFrame, QGraphicsScene, QGraphicsView, QHBoxLayout,
    QLabel, QLineEdit, QMainWindow, QMessageBox, QPushButton, QPlainTextEdit,
    QProgressBar, QVBoxLayout, QWidget
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
            self.status.emit("🐦 🐍 🦝 🐢 4인 분석 → 토론 → 🐱 알프레도 검증 중...")
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                result = backend.run_meeting(parsed, modules, account_data)
            text = buffer.getvalue()
            if isinstance(result, dict) and result.get("alfredo"):
                text += "\n\n===== 🐱 알프레도 최종 판단 =====\n" + str(result["alfredo"])
            self.output.emit(text)
            self.status.emit("분석 완료")
            self.finished.emit()
        except Exception:
            self.failed.emit(traceback.format_exc())


class OfficeView(QGraphicsView):
    PIXEL = 4

    def __init__(self):
        super().__init__()
        self.setScene(QGraphicsScene(self))
        self.setRenderHint(QPainter.Antialiasing, False)
        self.setRenderHint(QPainter.SmoothPixmapTransform, False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.NoFrame)
        self.setBackgroundBrush(QBrush("#17191d"))
        self.draw_office()

    def rect(self, x, y, w, h, fill, stroke=None, width=1):
        pen = QPen(stroke or fill)
        pen.setWidth(width)
        return self.scene().addRect(x, y, w, h, pen, QBrush(fill))

    def text(self, x, y, value, size=10, bold=False, color="#29271f", w=0, h=0):
        item = self.scene().addText(value, QFont("Malgun Gothic", size, QFont.Bold if bold else QFont.Normal))
        item.setDefaultTextColor(color)
        item.setPos(x, y)
        if w:
            item.setTextWidth(w)
        return item

    def pixel(self, x, y, w, h, color):
        return self.rect(x, y, w, h, color)

    def draw_office(self):
        s = self.scene()
        s.clear()
        s.setSceneRect(0, 0, 1500, 760)

        self.rect(20, 20, 1460, 330, "#252a2d", "#596269", 2)
        self.text(38, 35, "DONMULWON OFFICE  •  PIXEL OPERATIONS ROOM", 9, True, "#d9d1b8")

        wx, wy, ww, wh = 170, 65, 1090, 235
        self.rect(wx, wy, ww, wh, "#9bb4bc", "#52636a", 3)
        self.rect(wx + 3, wy + 3, ww - 6, 80, "#a9c7cf")
        self.rect(wx + 3, wy + 83, ww - 6, 75, "#8fb0b8")
        self.rect(wx + 3, wy + 158, ww - 6, 39, "#718b8f")
        buildings = [
            (210, 205, 48, 50), (285, 184, 55, 71), (375, 213, 44, 42),
            (455, 178, 64, 77), (560, 203, 48, 52), (640, 166, 62, 89),
            (750, 196, 55, 59), (845, 177, 65, 78), (955, 204, 46, 51),
            (1040, 185, 58, 70), (1135, 170, 57, 85), (1210, 203, 42, 52)
        ]
        for x, y, w, h in buildings:
            self.rect(x, y, w, h, "#59666a")
            for wy2 in range(y + 10, y + h - 5, 16):
                for wx2 in range(x + 8, x + w - 5, 15):
                    self.rect(wx2, wy2, 5, 7, "#c9b77e")
        self.rect(wx + 3, 255, ww - 6, 42, "#536966")
        for i in range(1, 6):
            x = wx + ww * i / 6
            s.addLine(x, wy, x, wy + wh, QPen("#52636a", 3))
        s.addLine(wx, 255, wx + ww, 255, QPen("#465b5f", 2))

        self.rect(38, 72, 108, 230, "#c9b99c", "#8c7a5e", 2)
        self.rect(48, 82, 88, 210, "#30383a", "#161a1c", 3)
        self.rect(57, 92, 70, 178, "#263033")
        self.rect(68, 118, 48, 6, "#667478")
        self.rect(121, 145, 6, 25, "#c49a54")
        self.text(47, 307, "ENTRANCE", 8, True, "#d9d1b8")

        px, py, pw, ph = 1290, 82, 170, 205
        self.rect(px, py, pw, ph, "#20252a", "#a58b5b", 2)
        self.text(px + 14, py + 12, "MARKET MONITOR", 10, True, "#e1d5b5")
        self.text(px + 14, py + 35, "VOO  $612.40", 8, True, "#8cc39e")
        self.text(px + 14, py + 50, "+1.84%", 8, True, "#8cc39e")
        base = py + 150
        vals = [20, 35, 27, 48, 39, 62, 45, 70, 54]
        for i, v in enumerate(vals):
            self.rect(px + 14 + i * 16, base - v, 9, v, "#668e78")
        s.addLine(px + 12, base, px + pw - 12, base, QPen("#6b6252", 1))
        self.text(px + 14, base + 8, "1D PERFORMANCE", 7, False, "#9e957f")
        self.text(px + 14, base + 27, "ACCOUNT  $1,124.19", 8, True, "#e1d5b5")

        self.rect(30, 330, 1440, 14, "#16191b")

        # 실제 AI 파일의 성격을 반영한 캐릭터 타입.
        agents = [
            ("현무", "MACRO", "#56766d", "turtle"),
            ("김선달", "FUNDAMENTAL + NEWS", "#9a7947", "crow"),
            ("이묵", "TECHNICAL", "#426c83", "snake"),
            ("너부리", "PORTFOLIO + ACCOUNT", "#80634e", "raccoon"),
            ("알프레도", "TEAM LEAD / VERIFIER", "#a26d42", "cat"),
        ]
        start_x, y, desk_w, gap = 45, 395, 270, 18
        for i, (name, role, accent, kind) in enumerate(agents):
            x = start_x + i * (desk_w + gap)
            self.draw_desk(x, y, desk_w, name, role, accent, kind, i == 4)

        self.text(35, 705, "5 AI AGENTS  •  PIXEL SUITS  •  INDIVIDUAL DESKS  •  LIVE ANALYSIS ROOM", 8, True, "#9e957f")

    def draw_desk(self, x, y, w, name, role, accent, kind, lead=False):
        self.rect(x + w / 2 - 25, y + 132, 50, 60, "#292b2e", "#111315", 2)
        self.rect(x + w / 2 - 34, y + 177, 68, 9, "#111315")
        self.draw_character(x + w / 2, y + 10, kind, accent)
        self.rect(x + 12, y + 98, w - 24, 72, "#15191b", "#a58b5b", 2)
        self.rect(x + 25, y + 110, w - 50, 45, "#29383c")
        self.rect(x + 35, y + 120, w - 70, 3, accent)
        self.rect(x + 12, y + 172, w - 24, 18, accent)
        self.rect(x + 12, y + 190, w - 24, 43, "#5a3f2c", "#33251c", 1)
        self.rect(x + 30, y + 233, 9, 50, "#29201a")
        self.rect(x + w - 39, y + 233, 9, 50, "#29201a")
        self.rect(x + 5, y + 283, w - 10, 8, "#191b1c")
        self.rect(x + 20, y + 298, w - 40, 29, "#20252a", "#695c48", 1)
        self.text(x + 31, y + 301, name, 10, True, "#eee5cc")
        self.text(x + 31, y + 315, role, 6, True, "#9e957f", w - 62)
        if lead:
            self.rect(x + w - 88, y + 304, 55, 15, "#a26d42")
            self.text(x + w - 83, y + 305, "LEAD", 6, True, "#fff1d0")

    def draw_character(self, cx, y, kind, accent):
        dark = "#1a1d20"
        white = "#e7e0cf"
        shirt = "#d8d2c2"
        suit = accent

        # 공통 양복 몸통.
        self.pixel(cx - 29, y + 46, 58, 42, suit)
        self.pixel(cx - 18, y + 42, 36, 10, shirt)
        self.pixel(cx - 4, y + 44, 8, 44, dark)
        self.pixel(cx - 25, y + 55, 10, 28, suit)
        self.pixel(cx + 15, y + 55, 10, 28, suit)
        self.pixel(cx - 4, y + 51, 8, 13, dark)
        self.pixel(cx - 6, y + 63, 12, 8, dark)

        if kind == "turtle":
            # 현무: 느긋하고 침착함. 무거운 등껍질과 처진 눈.
            skin = "#6d927d"
            self.pixel(cx - 27, y + 9, 54, 40, skin)
            self.pixel(cx - 32, y + 16, 9, 27, "#456b5e")
            self.pixel(cx + 23, y + 16, 9, 27, "#456b5e")
            self.pixel(cx - 27, y + 3, 54, 12, "#35544c")
            self.pixel(cx - 20, y - 1, 40, 7, "#35544c")
            self.pixel(cx - 17, y + 24, 9, 4, dark)
            self.pixel(cx + 8, y + 24, 9, 4, dark)
            self.pixel(cx - 7, y + 36, 14, 4, "#456b5e")
            # 작은 등껍질 무늬.
            self.pixel(cx - 13, y + 12, 8, 4, "#8eaa91")
            self.pixel(cx + 5, y + 12, 8, 4, "#8eaa91")

        elif kind == "crow":
            # 김선달: 말빨 좋고 자신감 넘치며 회의에 먼저 끼어드는 까마귀.
            feather = "#303438"
            self.pixel(cx - 28, y + 9, 56, 42, feather)
            self.pixel(cx - 21, y + 1, 10, 16, "#1e2225")
            self.pixel(cx - 8, y - 5, 9, 21, "#1e2225")
            self.pixel(cx + 5, y + 1, 10, 16, "#1e2225")
            # 자신만만하게 치켜뜬 눈썹.
            self.pixel(cx - 19, y + 21, 14, 4, "#c2b99d")
            self.pixel(cx + 5, y + 19, 14, 4, "#c2b99d")
            self.pixel(cx - 16, y + 27, 7, 7, "#e4dcc5")
            self.pixel(cx + 9, y + 27, 7, 7, "#e4dcc5")
            self.pixel(cx - 14, y + 29, 4, 4, dark)
            self.pixel(cx + 11, y + 29, 4, 4, dark)
            # 말 많은 느낌의 큰 부리.
            self.pixel(cx + 24, y + 28, 18, 8, "#c18a45")
            self.pixel(cx - 8, y + 39, 16, 4, "#a96e43")
            # 양복에 금빛 포인트.
            self.pixel(cx + 20, y + 48, 6, 14, "#c18a45")

        elif kind == "snake":
            # 이묵: 교활하고 빈틈을 노리는 이무기. 좁은 눈과 갈라진 혀.
            snake = "#4e7658"
            self.pixel(cx - 28, y + 8, 56, 43, snake)
            self.pixel(cx - 20, y + 1, 14, 13, "#385740")
            self.pixel(cx + 7, y + 1, 14, 13, "#385740")
            self.pixel(cx - 19, y + 22, 16, 4, dark)
            self.pixel(cx + 3, y + 22, 16, 4, dark)
            self.pixel(cx - 17, y + 26, 7, 6, "#e8d7a2")
            self.pixel(cx + 10, y + 26, 7, 6, "#e8d7a2")
            self.pixel(cx - 15, y + 27, 3, 4, dark)
            self.pixel(cx + 11, y + 27, 3, 4, dark)
            self.pixel(cx - 3, y + 37, 6, 9, "#d46d68")
            self.pixel(cx - 9, y + 44, 8, 3, "#d46d68")
            self.pixel(cx + 1, y + 44, 8, 3, "#d46d68")
            # 비늘 포인트.
            self.pixel(cx - 22, y + 15, 6, 5, "#779765")
            self.pixel(cx + 16, y + 15, 6, 5, "#779765")

        elif kind == "raccoon":
            # 너부리: 호전적이고 밀어붙이는 보노보노식 너부리. 마스크와 공격적인 눈.
            fur = "#81766e"
            self.pixel(cx - 27, y + 8, 54, 43, fur)
            self.pixel(cx - 27, y + 2, 15, 13, "#655b55")
            self.pixel(cx + 12, y + 2, 15, 13, "#655b55")
            self.pixel(cx - 24, y + 20, 48, 18, "#363a3a")
            self.pixel(cx - 18, y + 23, 10, 9, "#ddd0b0")
            self.pixel(cx + 8, y + 23, 10, 9, "#ddd0b0")
            self.pixel(cx - 15, y + 26, 5, 5, dark)
            self.pixel(cx + 10, y + 26, 5, 5, dark)
            # 화난 눈썹과 밀어붙이는 표정.
            self.pixel(cx - 20, y + 18, 14, 4, dark)
            self.pixel(cx + 6, y + 18, 14, 4, dark)
            self.pixel(cx - 7, y + 37, 14, 5, "#302827")
            # 꼬리/갈색 포인트.
            self.pixel(cx + 27, y + 35, 13, 7, "#5f4a3e")
            self.pixel(cx + 35, y + 42, 9, 7, "#2f2926")

        else:
            # 알프레도: Alfred 모티브. 냉철한 팀장 + 안경 + 정장/보타이.
            skin = "#c99770"
            self.pixel(cx - 29, y + 9, 58, 41, skin)
            self.pixel(cx - 27, y + 1, 16, 16, dark)
            self.pixel(cx + 11, y + 1, 16, 16, dark)
            self.pixel(cx - 21, y + 3, 42, 13, "#25282b")
            # 안경은 알프레도의 고정 시그니처.
            self.pixel(cx - 20, y + 21, 18, 13, "#c9d0ca")
            self.pixel(cx + 2, y + 21, 18, 13, "#c9d0ca")
            self.pixel(cx - 3, y + 25, 6, 4, "#25282b")
            self.pixel(cx - 13, y + 26, 5, 5, dark)
            self.pixel(cx + 8, y + 26, 5, 5, dark)
            self.pixel(cx - 7, y + 38, 14, 4, "#4d3025")
            # 팀장용 단정한 보타이.
            self.pixel(cx - 13, y + 49, 10, 8, suit)
            self.pixel(cx + 3, y + 49, 10, 8, suit)
            self.pixel(cx - 2, y + 50, 5, 6, "#d8b36a")
            self.pixel(cx - 22, y + 48, 6, 14, "#111315")
            self.pixel(cx + 16, y + 48, 6, 14, "#111315")

        # 공통 셔츠 칼라.
        self.pixel(cx - 13, y + 45, 8, 7, white)
        self.pixel(cx + 5, y + 45, 8, 7, white)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DONMULWON · AI TRADING TEAM")
        self.resize(1500, 900)
        self.worker_thread = None
        self.worker = None
        self.build_ui()

    def build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        main = QVBoxLayout(root)
        main.setContentsMargins(24, 20, 24, 20)
        main.setSpacing(10)

        header = QHBoxLayout()
        brand = QVBoxLayout()
        logo = QLabel("돈물원  DONMULWON")
        logo.setObjectName("logo")
        subtitle = QLabel("AI TRADING TEAM  •  PIXEL OPERATIONS ROOM")
        subtitle.setObjectName("subtitle")
        brand.addWidget(logo)
        brand.addWidget(subtitle)
        header.addLayout(brand)
        header.addStretch()
        self.status = QLabel("● SYSTEM READY")
        self.status.setObjectName("status")
        header.addWidget(self.status, alignment=Qt.AlignTop)
        main.addLayout(header)

        self.office = OfficeView()
        main.addWidget(self.office, 1)

        command = QFrame()
        command.setObjectName("command")
        row = QHBoxLayout(command)
        row.setContentsMargins(12, 8, 12, 8)
        self.input = QLineEdit()
        self.input.setPlaceholderText("무엇이든 물어보세요  ·  예: SOFI 지금 사도 괜찮아?")
        self.input.returnPressed.connect(self.start_analysis)
        self.button = QPushButton("분석 시작  ▶")
        self.button.clicked.connect(self.start_analysis)
        row.addWidget(self.input, 1)
        row.addWidget(self.button)
        main.addWidget(command)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        self.progress.setFixedHeight(5)
        main.addWidget(self.progress)
        self.setStyleSheet(self.styles())

    def styles(self):
        return """
        QWidget { background:#17191d; color:#e8dfc9; font-family:'Malgun Gothic'; }
        QMainWindow { background:#17191d; }
        QLabel#logo { font-size:22px; font-weight:800; color:#eee5cc; }
        QLabel#subtitle { color:#8e9b91; font-size:10px; font-weight:700; }
        QLabel#status { color:#7eb392; font-size:10px; font-weight:800; }
        QFrame#command { background:#22272b; border:1px solid #4b5356; border-radius:9px; }
        QLineEdit { background:transparent; border:0; color:#f4ead0; padding:7px; font-size:12px; }
        QLineEdit::placeholder { color:#777d7e; }
        QPushButton { background:#9b6838; color:white; border:0; border-radius:7px; padding:10px 20px; font-weight:800; }
        QPushButton:disabled { background:#4c4d49; }
        QProgressBar { background:#353b3e; border:0; border-radius:2px; }
        QProgressBar::chunk { background:#668e78; border-radius:2px; }
        """

    def start_analysis(self):
        question = self.input.text().strip()
        if not question:
            QMessageBox.information(self, "돈물원", "분석할 질문을 입력해주세요.")
            return
        self.set_busy(True)
        self.status.setText("● ANALYZING")
        self.worker_thread = QThread()
        self.worker = AnalysisWorker(question)
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.status.connect(self.status.setText)
        self.worker.output.connect(self.show_result)
        self.worker.finished.connect(self.analysis_finished)
        self.worker.failed.connect(self.analysis_failed)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.failed.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self.cleanup_worker)
        self.worker_thread.start()

    def set_busy(self, busy):
        self.input.setDisabled(busy)
        self.button.setDisabled(busy)
        self.progress.setVisible(busy)

    @Slot(str)
    def show_result(self, text):
        self.result_window = QMainWindow(self)
        self.result_window.setWindowTitle("🐱 알프레도 · 최종 판단")
        self.result_window.resize(820, 650)
        editor = QPlainTextEdit()
        editor.setReadOnly(True)
        editor.setPlainText(text)
        editor.setStyleSheet("background:#20252a; color:#eee5cc; padding:16px; font-size:12px;")
        self.result_window.setCentralWidget(editor)
        self.result_window.show()

    @Slot()
    def analysis_finished(self):
        self.set_busy(False)
        self.status.setText("● SYSTEM READY")

    @Slot(str)
    def analysis_failed(self, error):
        self.set_busy(False)
        self.status.setText("● ERROR")
        QMessageBox.critical(self, "분석 오류", error)

    def cleanup_worker(self):
        if self.worker:
            self.worker.deleteLater()
        if self.worker_thread:
            self.worker_thread.deleteLater()
        self.worker = None
        self.worker_thread = None


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("DONMULWON")
    app.setFont(QFont("Malgun Gothic", 10))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
