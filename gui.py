import os
import sys
import threading
import traceback
from datetime import datetime

from PySide6.QtCore import QObject, QThread, Signal, Slot, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QLabel, QLineEdit, QMainWindow,
    QMessageBox, QPushButton, QPlainTextEdit, QProgressBar, QVBoxLayout, QWidget
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
            self.status.emit("질문을 분석하는 중...")
            parsed = backend.parse_question(self.question)
            self.output.emit(
                f"질문: {self.question}\n"
                f"분석 유형: {parsed['intent']}\n"
                f"분석 종목: {', '.join(parsed['tickers']) if parsed['tickers'] else '전체 시장 / 포트폴리오'}\n\n"
            )
            self.status.emit("토스증권 계좌정보를 확인하는 중...")
            account_data = backend.get_account_data()
            backend.save_json(backend.AI_PORTFOLIO_FILE, account_data)
            self.status.emit("🐦 🐍 🦝 🐢 4인 AI 분석 + 토론 + 🐱 알프레도 검증 중...")

            # Keep the proven backend pipeline intact. Capture its terminal output
            # and stream it into the GUI instead of duplicating the investment logic.
            import io
            import contextlib
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                backend.run_meeting(parsed, modules, account_data)
            text = buffer.getvalue()
            self.output.emit(text)
            self.status.emit("분석 완료")
            self.finished.emit()
        except Exception:
            self.failed.emit(traceback.format_exc())


class TeamCard(QFrame):
    def __init__(self, emoji, name, role):
        super().__init__()
        self.setObjectName("teamCard")
        layout = QVBoxLayout(self)
        title = QLabel(f"{emoji}  {name}")
        title.setObjectName("teamTitle")
        role_label = QLabel(role)
        role_label.setObjectName("teamRole")
        self.state = QLabel("대기 중")
        self.state.setObjectName("teamState")
        layout.addWidget(title)
        layout.addWidget(role_label)
        layout.addWidget(self.state)

    def set_state(self, text):
        self.state.setText(text)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DONMULWON · AI TRADING TEAM")
        self.resize(1280, 820)
        self.worker_thread = None
        self.worker = None
        self.build_ui()

    def build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        main = QVBoxLayout(root)
        main.setContentsMargins(28, 24, 28, 24)
        main.setSpacing(16)

        header = QHBoxLayout()
        brand = QVBoxLayout()
        logo = QLabel("🏦  DONMULWON")
        logo.setObjectName("logo")
        subtitle = QLabel("AI TRADING TEAM  ·  통합 투자 분석 시스템")
        subtitle.setObjectName("subtitle")
        brand.addWidget(logo)
        brand.addWidget(subtitle)
        header.addLayout(brand)
        header.addStretch()
        self.connection = QLabel("● SYSTEM READY")
        self.connection.setObjectName("connection")
        header.addWidget(self.connection, alignment=Qt.AlignTop)
        main.addLayout(header)

        cards = QHBoxLayout()
        self.cards = [
            TeamCard("🐦", "김선달", "펀더멘털 · 뉴스"),
            TeamCard("🐍", "이묵", "기술적 분석"),
            TeamCard("🦝", "너부리", "포트폴리오 · 계좌"),
            TeamCard("🐢", "현무", "거시경제 · 시장환경"),
            TeamCard("🐱", "알프레도", "최종 검증 · 팀장"),
        ]
        for card in self.cards:
            cards.addWidget(card)
        main.addLayout(cards)

        input_frame = QFrame()
        input_frame.setObjectName("inputFrame")
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(14, 10, 14, 10)
        self.input = QLineEdit()
        self.input.setPlaceholderText("예: JOBY 지금 사도 괜찮아? / 내 계좌 전체적으로 봐줘")
        self.input.returnPressed.connect(self.start_analysis)
        self.button = QPushButton("분석 시작  ▶")
        self.button.setObjectName("analyzeButton")
        self.button.clicked.connect(self.start_analysis)
        input_layout.addWidget(self.input, 1)
        input_layout.addWidget(self.button)
        main.addWidget(input_frame)

        status_row = QHBoxLayout()
        self.status = QLabel("질문을 입력하고 분석을 시작하세요.")
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        status_row.addWidget(self.status, 1)
        status_row.addWidget(self.progress)
        main.addLayout(status_row)

        result_label = QLabel("FINAL ANALYSIS")
        result_label.setObjectName("sectionTitle")
        main.addWidget(result_label)
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setPlaceholderText("알프레도의 최종 판단과 AI 팀의 분석 결과가 여기에 표시됩니다.")
        main.addWidget(self.output, 1)

        self.setStyleSheet(self.styles())

    def styles(self):
        return """
        QWidget { background: #0b0f14; color: #e8edf3; font-family: 'Malgun Gothic'; }
        QMainWindow { background: #0b0f14; }
        QLabel#logo { font-size: 28px; font-weight: 800; }
        QLabel#subtitle { color: #7f8b99; font-size: 13px; }
        QLabel#connection { color: #65d98b; font-weight: 700; }
        QFrame#teamCard { background: #111720; border: 1px solid #202b38; border-radius: 12px; }
        QLabel#teamTitle { font-size: 15px; font-weight: 700; }
        QLabel#teamRole { color: #8e9baa; font-size: 11px; }
        QLabel#teamState { color: #657383; font-size: 11px; }
        QFrame#inputFrame { background: #111720; border: 1px solid #263342; border-radius: 12px; }
        QLineEdit { background: transparent; border: none; padding: 8px; font-size: 15px; color: #f2f5f8; }
        QPushButton#analyzeButton { background: #e9eef5; color: #0b0f14; border: none; border-radius: 9px; padding: 12px 20px; font-weight: 800; }
        QPushButton#analyzeButton:hover { background: #ffffff; }
        QPushButton#analyzeButton:disabled { color: #697583; background: #2a323c; }
        QLabel#sectionTitle { color: #aeb9c6; font-size: 12px; font-weight: 800; letter-spacing: 2px; }
        QPlainTextEdit { background: #080c11; border: 1px solid #202b38; border-radius: 12px; padding: 16px; font-size: 13px; line-height: 1.4; }
        QProgressBar { border: 0; background: #1b232d; border-radius: 3px; min-width: 120px; max-width: 180px; height: 5px; }
        QProgressBar::chunk { background: #8fa6bf; border-radius: 3px; }
        """

    def set_busy(self, busy):
        self.button.setDisabled(busy)
        self.input.setDisabled(busy)
        self.progress.setVisible(busy)
        self.connection.setText("● ANALYZING" if busy else "● SYSTEM READY")
        for card in self.cards:
            card.set_state("분석 중..." if busy else "대기 중")

    def start_analysis(self):
        question = self.input.text().strip()
        if not question:
            QMessageBox.information(self, "돈물원", "분석할 질문을 입력해주세요.")
            return
        self.output.clear()
        self.status.setText("분석을 시작했습니다...")
        self.set_busy(True)

        self.worker_thread = QThread()
        self.worker = AnalysisWorker(question)
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.status.connect(self.status.setText)
        self.worker.output.connect(self.output.insertPlainText)
        self.worker.finished.connect(self.analysis_finished)
        self.worker.failed.connect(self.analysis_failed)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.failed.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self.cleanup_worker)
        self.worker_thread.start()

    @Slot()
    def analysis_finished(self):
        self.set_busy(False)
        self.status.setText("분석 완료 · 알프레도 최종 판단까지 완료")
        for card in self.cards:
            card.set_state("완료")

    @Slot(str)
    def analysis_failed(self, error):
        self.set_busy(False)
        self.status.setText("분석 실패")
        self.output.appendPlainText("\n[ERROR]\n" + error)
        for card in self.cards:
            card.set_state("오류")

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
