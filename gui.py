# DONMULWON - TOP DOWN PIXEL OFFICE
import os,sys,io,contextlib,traceback
from PySide6.QtCore import QObject,QThread,Signal,Slot,Qt,QRect,QTimer
from PySide6.QtGui import QPainter,QColor,QFont
from PySide6.QtWidgets import QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QLabel,QLineEdit,QPushButton,QPlainTextEdit,QProgressBar,QComboBox
from gui_background import PixelBackground
from gui_characters import CharacterLayer
from gui_motion import MotionController

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path: sys.path.insert(0,BASE_DIR)

class AnalysisWorker(QObject):
    output=Signal(str); finished=Signal(); failed=Signal(str)
    def __init__(self,question): super().__init__(); self.question=question
    @Slot()
    def run(self):
        try:
            import main
            buf=io.StringIO()
            with contextlib.redirect_stdout(buf),contextlib.redirect_stderr(buf):
                if hasattr(main,'run_analysis'): result=main.run_analysis(self.question)
                elif hasattr(main,'main'): result=main.main(self.question)
                else: raise AttributeError('main.py에 분석 실행 함수가 없습니다.')
            text=buf.getvalue()
            if result is not None: text+='\n\n'+str(result)
            self.output.emit(text); self.finished.emit()
        except Exception: self.failed.emit(traceback.format_exc())

class PixelOffice(QWidget):
    def __init__(self):
        super().__init__(); self.background=PixelBackground(); self.characters=CharacterLayer(); self.motion=MotionController(self); self.setMinimumHeight(650)
    def set_weather(self,v): self.background.set_weather(v); self.update()
    def set_time(self,v): self.background.set_time(v); self.update()
    def paintEvent(self,event):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing,False)
        try:
            w,h=self.width(),self.height(); self.background.paint(p,w,h); self.draw_desks(p); self.characters.paint(p)
            p.setFont(QFont('Malgun Gothic',10,QFont.Bold)); p.setPen(QColor('#eee4d2'))
            for name,(x,y,_) in self.characters.POSITIONS.items(): p.drawText(QRect(x-45,y+82,170,25),Qt.AlignCenter,str(name))
            # small right-side market monitor
            p.setBrush(QColor('#292d2c')); p.setPen(QColor('#806a50')); p.drawRect(w-250,245,210,145)
            p.setPen(QColor('#e4d6b9')); p.setFont(QFont('Malgun Gothic',9,QFont.Bold)); p.drawText(w-235,265,180,20,'MARKET MONITOR')
            p.setPen(QColor('#879f86'))
            pts=[(w-230,350),(w-210,338),(w-188,342),(w-165,315),(w-140,326),(w-115,292),(w-85,304),(w-55,278)]
            for a,b in zip(pts,pts[1:]): p.drawLine(a[0],a[1],b[0],b[1])
        finally:
            if p.isActive(): p.end()
    def draw_desks(self,p):
        # Top-down desks: characters sit below each desk facing the monitor.
        stations=[(95,300),(365,300),(635,300),(905,300)]
        for x,y in stations:
            p.setPen(QColor('#241b16')); p.setBrush(QColor('#34251d')); p.drawRect(x,y,190,82)
            p.setBrush(QColor('#705039')); p.drawRect(x+6,y+6,178,70)
            p.setBrush(QColor('#20272c')); p.drawRect(x+53,y+10,84,42)
            p.setBrush(QColor('#3c4649')); p.drawRect(x+61,y+17,68,27)
            p.setBrush(QColor('#4a3023')); p.drawRect(x+77,y+52,36,24)
        # Alfredo's larger isolated team-lead desk
        x,y=1190,285
        p.setPen(QColor('#241b16')); p.setBrush(QColor('#2e211a')); p.drawRect(x,y,255,112)
        p.setBrush(QColor('#795638')); p.drawRect(x+7,y+7,241,98)
        p.setBrush(QColor('#20272c')); p.drawRect(x+48,y+12,150,50)
        p.setBrush(QColor('#3c4649')); p.drawRect(x+57,y+19,132,35)
        p.setBrush(QColor('#4a3023')); p.drawRect(x+105,y+68,45,30)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle('돈물원 · DONMULWON'); self.resize(1500,950)
        self.setStyleSheet("QMainWindow{background:#111416;color:#ded7c5;} QLabel{color:#ded7c5;} QLineEdit,QPlainTextEdit,QComboBox{background:#202428;color:#eee4d2;border:1px solid #51483b;padding:7px;} QPushButton{background:#665039;color:#fff2d4;padding:8px 14px;border:1px solid #8a6c4c;} QProgressBar{border:1px solid #51483b;background:#202428;} QProgressBar::chunk{background:#806544;}")
        root=QWidget(); layout=QVBoxLayout(root); layout.setContentsMargins(18,14,18,14)
        top=QHBoxLayout(); title=QLabel('🏦 DONMULWON  ·  AI TRADING TEAM'); title.setStyleSheet('font-size:22px;font-weight:700;'); top.addWidget(title); top.addStretch(); self.clock=QLabel(); top.addWidget(self.clock); layout.addLayout(top)
        self.office=PixelOffice(); layout.addWidget(self.office,1)
        controls=QHBoxLayout(); self.input=QLineEdit(); self.input.setPlaceholderText('무엇을 분석할까요? (예: JOBY 지금 사도 괜찮아?)'); self.button=QPushButton('분석 시작'); self.button.clicked.connect(self.start_analysis); self.input.returnPressed.connect(self.start_analysis)
        self.time=QComboBox(); self.time.addItems(['아침','낮','저녁','밤']); self.time.setCurrentText('밤'); self.time.currentTextChanged.connect(self.office.set_time)
        self.weather=QComboBox(); self.weather.addItems(['맑음','비','눈']); self.weather.currentTextChanged.connect(self.office.set_weather)
        controls.addWidget(self.input,1); controls.addWidget(self.time); controls.addWidget(self.weather); controls.addWidget(self.button); layout.addLayout(controls)
        self.status=QLabel('대기 중 · TOP-DOWN PIXEL OFFICE'); layout.addWidget(self.status); self.progress=QProgressBar(); self.progress.setRange(0,0); self.progress.hide(); layout.addWidget(self.progress); self.output=QPlainTextEdit(); self.output.setReadOnly(True); self.output.setMaximumHeight(230); layout.addWidget(self.output); self.setCentralWidget(root)
        self.ui_timer=QTimer(self); self.ui_timer.timeout.connect(self.update_clock); self.ui_timer.start(1000); self.update_clock(); self.thread=None; self.worker=None
    def update_clock(self):
        from datetime import datetime; self.clock.setText(datetime.now().strftime('%Y-%m-%d  %H:%M:%S'))
    def start_analysis(self):
        q=self.input.text().strip()
        if not q or self.thread is not None:return
        self.button.setEnabled(False); self.progress.show(); self.status.setText('⚔️ AI TRADING TEAM 회의 진행 중...'); self.output.clear(); self.thread=QThread(self); self.worker=AnalysisWorker(q); self.worker.moveToThread(self.thread); self.thread.started.connect(self.worker.run); self.worker.output.connect(lambda t:self.output.setPlainText(t)); self.worker.failed.connect(self.on_failed); self.worker.finished.connect(self.on_finished); self.worker.finished.connect(self.thread.quit); self.thread.finished.connect(self.cleanup_thread); self.thread.start()
    def on_failed(self,t): self.output.setPlainText('❌ 분석 오류\n\n'+t); self.status.setText('오류 발생 · 로그를 확인하세요')
    def on_finished(self): self.progress.hide(); self.button.setEnabled(True); self.status.setText('✅ 분석 완료')
    def cleanup_thread(self):
        if self.worker:self.worker.deleteLater()
        if self.thread:self.thread.deleteLater()
        self.worker=None; self.thread=None

def main():
    app=QApplication(sys.argv); window=MainWindow(); window.show(); return app.exec()
if __name__=='__main__': sys.exit(main())
