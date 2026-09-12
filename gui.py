# DONMULWON GUI
# Layers: gui_background.py / gui_characters.py / gui_motion.py

import os, sys, io, contextlib, traceback
from PySide6.QtCore import QObject, QThread, Signal, Slot, Qt, QRect, QTimer
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QPlainTextEdit, QProgressBar, QComboBox

from gui_background import PixelBackground
from gui_characters import CharacterLayer
from gui_motion import MotionController

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path: sys.path.insert(0, BASE_DIR)


class AnalysisWorker(QObject):
    output = Signal(str); finished = Signal(); failed = Signal(str)
    def __init__(self, question): super().__init__(); self.question = question
    @Slot()
    def run(self):
        try:
            import main
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                result = main.run_analysis(self.question)
            text = buf.getvalue()
            if result is not None: text += "\n\n" + str(result)
            self.output.emit(text); self.finished.emit()
        except Exception: self.failed.emit(traceback.format_exc())


class PixelOffice(QWidget):
    def __init__(self):
        super().__init__()
        self.background = PixelBackground()
        self.characters = CharacterLayer()
        self.motion = MotionController(self)
        self.setMinimumHeight(650)

    def set_weather(self, value): self.background.set_weather(value); self.update()
    def set_time(self, value): self.background.set_time(value); self.update()

    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing, False)
        try:
            w, h = self.width(), self.height()
            self.background.paint(p, w, h)
            self.draw_desks(p, h)
            self.characters.paint(p)
            for name, (x, y) in self.characters.POSITIONS.items():
                p.setPen(QColor('#eee4d2')); p.setFont(QFont('Malgun Gothic', 11, QFont.Bold))
                p.drawText(QRect(int(x-25), int(y+295), 150, 28), Qt.AlignCenter, str(name))
        finally:
            if p.isActive(): p.end()

    def draw_desks(self, p, h):
        p.setPen(Qt.NoPen)
        for x in (120, 395, 670, 945):
            p.setBrush(QColor('#4b3020')); p.drawRect(x, 535, 205, 82)
            p.setBrush(QColor('#20272c')); p.drawRect(x+57, 490, 90, 45)
            p.setBrush(QColor('#705039')); p.drawRect(x+82, 617, 40, 45)
        p.setBrush(QColor('#33231b')); p.drawRect(1135, 520, 300, 97)
        p.setBrush(QColor('#20272c')); p.drawRect(1195, 465, 180, 55)
        p.setBrush(QColor('#705039')); p.drawRect(1260, 617, 45, 45)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle('돈물원 · DONMULWON'); self.resize(1500, 950)
        self.setStyleSheet("QMainWindow{background:#111416;color:#ded7c5;} QLabel{color:#ded7c5;} QLineEdit,QPlainTextEdit,QComboBox{background:#202428;color:#eee4d2;border:1px solid #51483b;padding:7px;} QPushButton{background:#665039;color:#fff2d4;padding:8px 14px;border:1px solid #8a6c4c;} QProgressBar{border:1px solid #51483b;background:#202428;} QProgressBar::chunk{background:#806544;}")
        root = QWidget(); layout = QVBoxLayout(root); layout.setContentsMargins(18,14,18,14)
        top = QHBoxLayout(); title = QLabel('🏦 DONMULWON  ·  AI TRADING TEAM'); title.setStyleSheet('font-size:22px;font-weight:700;'); top.addWidget(title); top.addStretch(); self.clock = QLabel(); top.addWidget(self.clock); layout.addLayout(top)
        self.office = PixelOffice(); layout.addWidget(self.office, 1)
        controls = QHBoxLayout(); self.input = QLineEdit(); self.input.setPlaceholderText('무엇을 분석할까요? (예: JOBY 지금 사도 괜찮아?)')
        self.button = QPushButton('분석 시작'); self.button.clicked.connect(self.start_analysis); self.input.returnPressed.connect(self.start_analysis)
        self.time = QComboBox(); self.time.addItems(['아침','낮','저녁','밤']); self.time.setCurrentText('밤'); self.time.currentTextChanged.connect(self.office.set_time)
        self.weather = QComboBox(); self.weather.addItems(['맑음','비','눈']); self.weather.currentTextChanged.connect(self.office.set_weather)
        controls.addWidget(self.input,1); controls.addWidget(self.time); controls.addWidget(self.weather); controls.addWidget(self.button); layout.addLayout(controls)
        self.status = QLabel('대기 중 · 캐릭터 / 배경 / 모션 분리 완료'); layout.addWidget(self.status)
        self.progress = QProgressBar(); self.progress.setRange(0,0); self.progress.hide(); layout.addWidget(self.progress)
        self.output = QPlainTextEdit(); self.output.setReadOnly(True); self.output.setMaximumHeight(230); layout.addWidget(self.output); self.setCentralWidget(root)
        self.ui_timer = QTimer(self); self.ui_timer.timeout.connect(self.update_clock); self.ui_timer.start(1000); self.update_clock(); self.thread = None; self.worker = None

    def update_clock(self):
        from datetime import datetime; self.clock.setText(datetime.now().strftime('%Y-%m-%d  %H:%M:%S'))
    def start_analysis(self):
        question = self.input.text().strip()
        if not question or self.thread is not None: return
        self.button.setEnabled(False); self.progress.show(); self.status.setText('⚔️ AI TRADING TEAM 회의 진행 중...'); self.output.clear()
        self.thread = QThread(self); self.worker = AnalysisWorker(question); self.worker.moveToThread(self.thread); self.thread.started.connect(self.worker.run)
        self.worker.output.connect(lambda t: self.output.setPlainText(t)); self.worker.failed.connect(self.on_failed); self.worker.finished.connect(self.on_finished); self.worker.finished.connect(self.thread.quit); self.thread.finished.connect(self.cleanup_thread); self.thread.start()
    def on_failed(self, text): self.output.setPlainText('❌ 분석 오류\n\n'+text); self.status.setText('오류 발생 · 로그를 확인하세요')
    def on_finished(self): self.progress.hide(); self.button.setEnabled(True); self.status.setText('✅ 분석 완료')
    def cleanup_thread(self):
        if self.worker: self.worker.deleteLater()
        if self.thread: self.thread.deleteLater()
        self.worker = None; self.thread = None


def main():
    app = QApplication(sys.argv); window = MainWindow(); window.show(); return app.exec()

if __name__ == '__main__': sys.exit(main())
