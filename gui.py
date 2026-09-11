import os
import sys
import io
import contextlib
import traceback

from PySide6.QtCore import QObject, QThread, Signal, Slot, Qt
from PySide6.QtGui import QFont, QPainter, QPen, QBrush, QColor
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
            self.finished.emit()
        except Exception:
            self.failed.emit(traceback.format_exc())


class OfficeView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setScene(QGraphicsScene(self))
        self.setRenderHint(QPainter.Antialiasing, False)
        self.setRenderHint(QPainter.SmoothPixmapTransform, False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.NoFrame)
        self.setBackgroundBrush(QBrush(QColor("#17191d")))
        self.draw_office()

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

    def draw_office(self):
        self.scene().clear()
        self.scene().setSceneRect(0, 0, 1500, 760)

        # Back wall.
        self.rect(20, 20, 1460, 330, "#252a2d", "#596269", 2)
        self.text(38, 35, "DONMULWON OFFICE  •  PIXEL OPERATIONS ROOM", 9, True, "#d9d1b8")

        # Large window: deliberately isolated from the exit area.
        wx, wy, ww, wh = 195, 65, 1010, 235
        self.rect(wx, wy, ww, wh, "#9bb4bc", "#52636a", 3)
        self.rect(wx + 3, wy + 3, ww - 6, 78, "#a9c7cf")
        self.rect(wx + 3, wy + 81, ww - 6, 76, "#8fb0b8")
        self.rect(wx + 3, wy + 157, ww - 6, 40, "#718b8f")
        buildings = [
            (225, 207, 44, 48), (290, 184, 54, 71), (368, 214, 42, 41),
            (440, 179, 60, 76), (530, 202, 46, 53), (606, 167, 58, 88),
            (690, 197, 53, 58), (772, 178, 63, 77), (870, 205, 45, 50),
            (944, 184, 57, 71), (1032, 170, 55, 85), (1110, 204, 43, 51)
        ]
        for bx, by, bw, bh in buildings:
            self.rect(bx, by, bw, bh, "#59666a")
            for yy in range(by + 10, by + bh - 5, 16):
                for xx in range(bx + 8, bx + bw - 5, 15):
                    self.rect(xx, yy, 5, 7, "#c9b77e")
        self.rect(wx + 3, 255, ww - 6, 42, "#536966")
        for i in range(1, 5):
            xx = wx + ww * i / 5
            self.line(xx, wy, xx, wy + wh, "#52636a", 3)
        self.line(wx, 255, wx + ww, 255, "#465b5f", 2)

        # Exit is a wall sign, not a giant door beside the window.
        ex, ey = 48, 90
        self.rect(ex, ey, 118, 135, "#1c2528", "#53615f", 2)
        self.rect(ex + 12, ey + 12, 94, 72, "#263538")
        self.rect(ex + 31, ey + 28, 56, 32, "#6c9b76")
        self.text(ex + 43, ey + 31, "EXIT", 13, True, "#edf2d8")
        self.line(ex + 59, ey + 63, ex + 59, ey + 49, "#edf2d8", 3)
        self.line(ex + 45, ey + 57, ex + 59, ey + 44, "#edf2d8", 3)
        self.line(ex + 73, ey + 57, ex + 59, ey + 44, "#edf2d8", 3)
        self.text(ex + 19, ey + 96, "EMERGENCY EXIT", 7, True, "#d9d1b8")
        self.text(ex + 25, ey + 111, "→ STAFF AREA", 6, False, "#8e9b91")

        # Large market monitor, with generous chart bounds so nothing is clipped.
        px, py, pw, ph = 1230, 55, 235, 245
        self.rect(px, py, pw, ph, "#20252a", "#a58b5b", 2)
        self.text(px + 15, py + 12, "MARKET MONITOR", 11, True, "#e1d5b5")
        self.text(px + 15, py + 35, "VOO", 8, True, "#b6b09f")
        self.text(px + 51, py + 34, "$612.40", 10, True, "#8cc39e")
        self.text(px + 142, py + 36, "+1.84%", 8, True, "#8cc39e")

        cx, cy, cw, ch = px + 16, py + 63, pw - 32, 105
        self.rect(cx, cy, cw, ch, "#182023", "#46575a", 1)
        for gy in (cy + 26, cy + 52, cy + 78):
            self.line(cx + 5, gy, cx + cw - 5, gy, "#303c3e", 1)
        values = [56, 51, 63, 59, 70, 65, 82, 76, 91, 84, 98, 90, 105, 99]
        pts = []
        for i, value in enumerate(values):
            xx = cx + 8 + i * ((cw - 16) / (len(values) - 1))
            yy = cy + ch - 8 - value * 0.72
            pts.append((xx, yy))
        for a, b in zip(pts, pts[1:]):
            self.line(a[0], a[1], b[0], b[1], "#8cc39e", 3)
        for xx, yy in pts:
            self.rect(xx - 2, yy - 2, 4, 4, "#d7e3bd")
        self.text(px + 16, py + 176, "1D PERFORMANCE", 7, True, "#8e9b91")
        self.text(px + 16, py + 194, "ACCOUNT", 7, True, "#8e9b91")
        self.text(px + 70, py + 191, "$1,124.19", 10, True, "#e1d5b5")
        self.text(px + 16, py + 216, "VOL  1.24M   •   TREND  UP", 7, True, "#9e957f")

        self.rect(30, 330, 1440, 14, "#16191b")

        agents = [
            ("현무", "MACRO", "#56766d", "turtle"),
            ("김선달", "FUNDAMENTAL + NEWS", "#9a7947", "crow"),
            ("이묵", "TECHNICAL", "#426c83", "snake"),
            ("너부리", "PORTFOLIO + ACCOUNT", "#80634e", "raccoon"),
            ("알프레도", "TEAM LEAD / VERIFIER", "#a26d42", "cat"),
        ]
        start_x, y, desk_w, gap = 45, 395, 270, 18
        for i, data in enumerate(agents):
            self.draw_desk(start_x + i * (desk_w + gap), y, desk_w, *data, lead=(i == 4))

        self.text(35, 705, "5 AI AGENTS  •  PIXEL SUITS  •  INDIVIDUAL DESKS  •  LIVE ANALYSIS ROOM", 8, True, "#9e957f")

    def draw_desk(self, x, y, w, name, role, accent, kind, lead=False):
        # Chair behind the character.
        self.rect(x + w / 2 - 27, y + 124, 54, 65, "#292b2e", "#111315", 2)
        self.rect(x + w / 2 - 36, y + 177, 72, 9, "#111315")
        self.draw_character(x + w / 2, y + 5, kind, accent)

        # Desk + monitor.
        self.rect(x + 10, y + 98, w - 20, 72, "#15191b", "#a58b5b", 2)
        self.rect(x + 28, y + 109, w - 56, 48, "#29383c", "#53686b", 2)
        self.rect(x + 39, y + 119, w - 78, 3, accent)
        self.rect(x + 39, y + 129, w - 78, 3, "#52615e")
        self.rect(x + 39, y + 139, w - 78, 3, "#52615e")
        self.rect(x + 10, y + 172, w - 20, 18, accent)
        self.rect(x + 10, y + 190, w - 20, 43, "#5a3f2c", "#33251c", 1)
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
        # Small-pixel sprite: 3-5 px blocks, many individual marks.
        dark = "#1a1d20"
        light = "#e7e0cf"
        shirt = "#ded8c8"
        suit = accent
        # Body / suit silhouette.
        self.px(cx - 18, y + 48, 36, 30, suit)
        self.px(cx - 13, y + 43, 26, 8, shirt)
        self.px(cx - 3, y + 45, 6, 30, dark)
        self.px(cx - 17, y + 54, 6, 21, suit)
        self.px(cx + 11, y + 54, 6, 21, suit)
        self.px(cx - 2, y + 49, 4, 10, "#25282b")
        self.px(cx - 7, y + 75, 6, 5, dark)
        self.px(cx + 1, y + 75, 6, 5, dark)

        if kind == "turtle":
            skin, shell, shade = "#78a087", "#36594f", "#507965"
            self.px(cx - 17, y + 13, 34, 34, skin)
            self.px(cx - 21, y + 20, 5, 17, shade)
            self.px(cx + 16, y + 20, 5, 17, shade)
            self.px(cx - 16, y + 7, 32, 8, shell)
            self.px(cx - 11, y + 3, 22, 5, shell)
            self.px(cx - 12, y + 17, 7, 5, "#b5c7a5")
            self.px(cx + 5, y + 17, 7, 5, "#b5c7a5")
            self.px(cx - 10, y + 23, 5, 5, dark)
            self.px(cx + 5, y + 23, 5, 5, dark)
            self.px(cx - 4, y + 31, 8, 4, shade)
            self.px(cx - 7, y + 36, 14, 3, "#557a67")

        elif kind == "crow":
            feather, black = "#3a3e43", "#202326"
            self.px(cx - 17, y + 13, 34, 34, feather)
            self.px(cx - 13, y + 5, 7, 11, black)
            self.px(cx - 3, y + 1, 7, 15, black)
            self.px(cx + 7, y + 6, 7, 10, black)
            self.px(cx - 10, y + 19, 7, 5, "#d8cfb2")
            self.px(cx + 4, y + 19, 7, 5, "#d8cfb2")
            self.px(cx - 8, y + 21, 4, 5, dark)
            self.px(cx + 5, y + 21, 4, 5, dark)
            self.px(cx + 16, y + 25, 13, 5, "#c18a45")
            self.px(cx - 5, y + 31, 10, 3, "#b47448")
            self.px(cx - 15, y + 39, 7, 5, black)
            self.px(cx + 8, y + 39, 7, 5, black)

        elif kind == "snake":
            green, shade = "#527d5d", "#31553d"
            self.px(cx - 17, y + 12, 34, 35, green)
            self.px(cx - 12, y + 6, 9, 10, shade)
            self.px(cx + 4, y + 5, 9, 11, shade)
            self.px(cx - 11, y + 20, 7, 6, "#e4d49f")
            self.px(cx + 4, y + 20, 7, 6, "#e4d49f")
            self.px(cx - 9, y + 21, 4, 4, dark)
            self.px(cx + 6, y + 21, 4, 4, dark)
            self.px(cx - 3, y + 30, 6, 6, "#d76d70")
            self.px(cx - 8, y + 36, 6, 3, "#d76d70")
            self.px(cx + 2, y + 36, 6, 3, "#d76d70")
            self.px(cx - 15, y + 41, 6, 4, shade)
            self.px(cx + 9, y + 41, 6, 4, shade)

        elif kind == "raccoon":
            fur, mask = "#8b8077", "#454747"
            self.px(cx - 17, y + 12, 34, 35, fur)
            self.px(cx - 16, y + 5, 9, 10, mask)
            self.px(cx + 7, y + 5, 9, 10, mask)
            self.px(cx - 17, y + 21, 34, 12, mask)
            self.px(cx - 10, y + 22, 7, 6, "#e2d5b5")
            self.px(cx + 3, y + 22, 7, 6, "#e2d5b5")
            self.px(cx - 8, y + 23, 4, 4, dark)
            self.px(cx + 4, y + 23, 4, 4, dark)
            self.px(cx - 4, y + 31, 8, 5, dark)
            self.px(cx - 18, y + 38, 5, 8, mask)
            self.px(cx + 13, y + 38, 5, 8, mask)

        else:
            # Alfredo: cat + small glasses + neat team-lead suit.
            fur, ear = "#c79770", "#6e493c"
            self.px(cx - 18, y + 12, 36, 34, fur)
            self.px(cx - 17, y + 4, 11, 12, ear)
            self.px(cx + 6, y + 4, 11, 12, ear)
            self.px(cx - 14, y + 7, 7, 7, fur)
            self.px(cx + 7, y + 7, 7, 7, fur)
            # glasses frames are intentionally pixel-thin.
            self.px(cx - 13, y + 20, 11, 7, "#d6ddd7")
            self.px(cx + 2, y + 20, 11, 7, "#d6ddd7")
            self.px(cx - 2, y + 22, 4, 3, dark)
            self.px(cx - 10, y + 22, 4, 4, dark)
            self.px(cx + 6, y + 22, 4, 4, dark)
            self.px(cx - 4, y + 31, 8, 4, "#58372d")
            self.px(cx - 11, y + 38, 8, 4, fur)
            self.px(cx + 3, y + 38, 8, 4, fur)
            # Bow tie.
            self.px(cx - 7, y + 46, 6, 5, "#2a2020")
            self.px(cx + 1, y + 46, 6, 5, "#2a2020")
            self.px(cx - 2, y + 47, 4, 4, "#d0a45d")

        self.px(cx - 10, y + 48, 5, 5, light)
        self.px(cx + 5, y + 48, 5, 5, light)


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
