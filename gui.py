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
    def __init__(self):
        super().__init__()
        self.setScene(QGraphicsScene(self))
        self.setRenderHint(QPainter.Antialiasing)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.NoFrame)
        self.setBackgroundBrush(QBrush("#e7dfc9"))
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

    def draw_office(self):
        s = self.scene()
        s.clear()
        s.setSceneRect(0, 0, 1500, 760)

        # ------------------------------------------------------------
        # 1. BACK WALL: window only. The door is NOT part of the window.
        # ------------------------------------------------------------
        self.rect(20, 20, 1460, 330, "#dbe6d8", "#557565", 2)
        self.text(38, 35, "DONMULWON OFFICE  •  WINDOW VIEW", 9, True)

        # Large rear window.
        wx, wy, ww, wh = 170, 65, 1090, 235
        self.rect(wx, wy, ww, wh, "#cfe0d7", "#6b8675", 2)
        for i in range(1, 6):
            x = wx + ww * i / 6
            s.addLine(x, wy, x, wy + wh, QPen("#718b7a", 2))
        # Outside skyline / landscape.
        self.rect(wx, 255, ww, 45, "#c6d1bf")
        buildings = [(215, 210, 48, 45), (305, 190, 55, 65), (405, 205, 45, 50),
                     (505, 180, 60, 75), (625, 205, 48, 50), (730, 170, 62, 85),
                     (855, 198, 52, 57), (965, 185, 58, 70), (1080, 205, 45, 50),
                     (1160, 175, 50, 80)]
        for x, y, w, h in buildings:
            self.rect(x, y, w, h, "#77746b")
        s.addLine(wx, 255, wx + ww, 255, QPen("#6d806e", 2))

        # ------------------------------------------------------------
        # 2. ENTRANCE: independent wall-mounted door, far left.
        # ------------------------------------------------------------
        self.rect(38, 72, 108, 230, "#f5eddb", "#806648", 2)
        self.rect(48, 82, 88, 210, "#292d27", "#806648", 3)
        s.addLine(62, 125, 122, 125, QPen("#a1afa4", 2))
        self.rect(121, 145, 5, 25, "#b37835")
        self.text(45, 308, "ENTRANCE", 8, True)

        # ------------------------------------------------------------
        # 3. MARKET MONITOR: detached UI panel in front of the room.
        #    It does not touch or sit on the window.
        # ------------------------------------------------------------
        px, py, pw, ph = 1290, 82, 170, 205
        self.rect(px, py, pw, ph, "#f7f0df", "#806a4c", 2)
        self.text(px+14, py+12, "MARKET MONITOR", 11, True)
        self.text(px+14, py+36, "VOO  $612.40  +1.84%", 8, True, "#557d67")
        base = py + 150
        vals = [20, 35, 27, 48, 39, 62, 45, 70, 54]
        for i, v in enumerate(vals):
            self.rect(px+14+i*16, base-v, 9, v, "#557d67")
        s.addLine(px+12, base, px+pw-12, base, QPen("#9a8d77", 1))
        self.text(px+14, base+8, "1D PERFORMANCE", 7, False, "#817967")
        self.text(px+14, base+27, "ACCOUNT  $1,124.19", 8, True)

        # Floor line.
        self.rect(30, 330, 1440, 14, "#5d5140")

        # ------------------------------------------------------------
        # 4. FIVE INDIVIDUAL DESKS. Each agent has a separate station.
        # ------------------------------------------------------------
        agents = [
            ("🐢", "현무", "MACRO", "#617e74"),
            ("🐦", "김선달", "FUNDAMENTAL + NEWS", "#7b704f"),
            ("🐍", "이묵", "TECHNICAL", "#456b82"),
            ("🦝", "너부리", "PORTFOLIO + ACCOUNT", "#6e594c"),
            ("🐱", "알프레도", "TEAM LEAD / VERIFIER", "#8a6248"),
        ]
        start_x, y, desk_w, gap = 45, 400, 270, 18
        for i, (emoji, name, role, accent) in enumerate(agents):
            x = start_x + i * (desk_w + gap)
            self.draw_desk(x, y, desk_w, emoji, name, role, accent, i == 4)

        self.text(35, 705, "5 AI AGENTS  •  INDIVIDUAL DESKS  •  FRONT OFFICE VIEW", 8, True, "#817967")

    def draw_desk(self, x, y, w, emoji, name, role, accent, lead=False):
        # Monitor/nameplate.
        self.rect(x+12, y, w-24, 78, "#f7f0df", "#2f2b22", 3)
        self.text(x+25, y+13, f"{emoji}  {name}", 12, True)
        self.text(x+25, y+39, role, 7, True, "#817967", w-50)

        # Desktop + front panel.
        self.rect(x+12, y+86, w-24, 18, accent)
        self.rect(x+12, y+104, w-24, 48, "#725333", "#513b28", 1)
        # Two legs = physical desk, clearly separated from the next desk.
        self.rect(x+30, y+152, 8, 55, "#4b3929")
        self.rect(x+w-38, y+152, 8, 55, "#4b3929")

        # Chair behind the desk.
        self.rect(x+w/2-24, y+154, 48, 25, accent)
        self.rect(x+w/2-20, y+179, 40, 7, "#4b3929")
        if lead:
            self.text(x+92, y+112, "FINAL VERIFIER", 7, True, "#f7f0df")


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
        subtitle = QLabel("AI TRADING TEAM  •  LIVE")
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
        QWidget { background:#e7dfc9; color:#29271f; font-family:'Malgun Gothic'; }
        QMainWindow { background:#e7dfc9; }
        QLabel#logo { font-size:22px; font-weight:800; }
        QLabel#subtitle { color:#657462; font-size:10px; font-weight:700; }
        QLabel#status { color:#557d67; font-size:10px; font-weight:800; }
        QFrame#command { background:#302c24; border-radius:9px; }
        QLineEdit { background:transparent; border:0; color:#f7f0df; padding:7px; font-size:12px; }
        QLineEdit::placeholder { color:#aaa28f; }
        QPushButton { background:#a86f31; color:white; border:0; border-radius:7px; padding:10px 20px; font-weight:800; }
        QPushButton:disabled { background:#6b604e; }
        QProgressBar { background:#c8bea8; border:0; border-radius:2px; }
        QProgressBar::chunk { background:#557d67; border-radius:2px; }
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
        dialog = QFrame()
        # Keep the main scene clean; result is a dedicated floating panel.
        self.result_window = QMainWindow(self)
        self.result_window.setWindowTitle("🐱 알프레도 · 최종 판단")
        self.result_window.resize(820, 650)
        editor = QPlainTextEdit()
        editor.setReadOnly(True)
        editor.setPlainText(text)
        editor.setStyleSheet("background:#f7f0df; color:#29271f; padding:16px; font-size:12px;")
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
