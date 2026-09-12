# DONMULWON - TOP DOWN PIXEL OFFICE
import os, sys, io, contextlib, traceback
from datetime import datetime
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
                if hasattr(main, 'run_analysis'): result = main.run_analysis(self.question)
                elif hasattr(main, 'main'): result = main.main(self.question)
                else: raise AttributeError('main.py에 분석 실행 함수가 없습니다.')
            text = buf.getvalue()
            if result is not None: text += '\n\n' + str(result)
            self.output.emit(text); self.finished.emit()
        except Exception: self.failed.emit(traceback.format_exc())

class PixelOffice(QWidget):
    def __init__(self):
        super().__init__(); self.background=PixelBackground(); self.characters=CharacterLayer(); self.motion=MotionController(self); self.setMinimumHeight(620)
    def set_weather(self,value): self.background.set_weather(value); self.update()
    def set_time(self,value): self.background.set_time(value); self.update()
    def auto_time(self):
        now=datetime.now(); hour=now.hour
        self.background.set_clock(now)
        if 5 <= hour < 11: period='아침'
        elif 11 <= hour < 17: period='낮'
        elif 17 <= hour < 21: period='저녁'
        else: period='밤'
        self.background.set_time(period); self.update(); return period
    def paintEvent(self,event):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing,False)
        try:
            w,h=self.width(),self.height(); self.background.paint(p,w,h); self.draw_desks(p,w); self.draw_conference_area(p,w,h); self.characters.paint(p)
            p.setFont(QFont('Malgun Gothic',9,QFont.Bold)); p.setPen(QColor('#eee4d2'))
            for name,(x,y,_) in self.characters.POSITIONS.items(): p.drawText(QRect(int(x-35),int(y+70),140,22),Qt.AlignCenter,str(name))
            self.draw_side_monitor(p,w)
        finally:
            if p.isActive(): p.end()
    def draw_desks(self,p,w):
        stations=[(65,235),(330,235),(595,235),(860,235)]
        for x,y in stations:
            p.setPen(QColor('#241b16')); p.setBrush(QColor('#34251d')); p.drawRect(x,y,175,70); p.setBrush(QColor('#705039')); p.drawRect(x+6,y+6,163,58); p.setBrush(QColor('#20272c')); p.drawRect(x+49,y+9,77,35); p.setBrush(QColor('#3c4649')); p.drawRect(x+56,y+15,63,23); p.setBrush(QColor('#4a3023')); p.drawRect(x+71,y+46,34,18)
        x,y=min(1160,w-270),225; p.setPen(QColor('#241b16')); p.setBrush(QColor('#2e211a')); p.drawRect(x,y,220,98); p.setBrush(QColor('#795638')); p.drawRect(x+7,y+7,206,84); p.setBrush(QColor('#20272c')); p.drawRect(x+40,y+11,140,43); p.setBrush(QColor('#3c4649')); p.drawRect(x+49,y+18,122,30); p.setBrush(QColor('#4a3023')); p.drawRect(x+89,y+62,42,27)
    def draw_conference_area(self,p,w,h):
        cx=w//2; table_w=min(600,max(520,w-700)); table_x=cx-table_w//2; table_y=360; table_h=68
        p.setPen(Qt.NoPen); p.setBrush(QColor('#493827')); p.drawRect(table_x-20,table_y-20,table_w+40,table_h+40); p.setBrush(QColor('#5b4430')); p.drawRect(table_x-14,table_y-14,table_w+28,table_h+28); p.setPen(QColor('#251b16')); p.setBrush(QColor('#241914')); p.drawRect(table_x,table_y,table_w,table_h); p.setBrush(QColor('#725238')); p.drawRect(table_x+7,table_y+7,table_w-14,table_h-14); p.setBrush(QColor('#876445')); p.drawRect(table_x+15,table_y+15,table_w-30,table_h-30)
        p.setPen(QColor('#5b402d')); p.drawLine(table_x+18,table_y+table_h//2,table_x+table_w-18,table_y+table_h//2); p.setPen(Qt.NoPen); p.setBrush(QColor('#30251e')); p.drawRect(cx-75,table_y+22,150,24); p.setBrush(QColor('#c7ad7b')); p.drawRect(cx-62,table_y+26,124,3); p.drawRect(cx-40,table_y+35,80,3)
        p.setBrush(QColor('#292421'))
        for sx in [table_x+45,table_x+150,table_x+table_w-195,table_x+table_w-90]: p.drawRect(sx,table_y-10,42,10); p.drawRect(sx,table_y+table_h,42,10)
        p.drawRect(cx-21,table_y-10,42,10); p.drawRect(cx-21,table_y+table_h,42,10)
        chart_w=min(500,w-800); chart_x=cx-chart_w//2; chart_y=455; chart_h=max(82,min(105,h-chart_y-8)); p.setPen(QColor('#241b16')); p.setBrush(QColor('#211d1a')); p.drawRect(chart_x,chart_y,chart_w,chart_h); p.setBrush(QColor('#302b26')); p.drawRect(chart_x+5,chart_y+5,chart_w-10,chart_h-10); p.setPen(QColor('#cdbb99')); p.setFont(QFont('Malgun Gothic',8,QFont.Bold)); p.drawText(QRect(chart_x+12,chart_y+7,170,18),Qt.AlignLeft,'TEAM MARKET CHART')
        p.setPen(QColor('#6f604c')); grid_top,grid_bottom=chart_y+27,chart_y+chart_h-13
        for i in range(1,4): yy=grid_top+i*(grid_bottom-grid_top)//4; p.drawLine(chart_x+12,yy,chart_x+chart_w-12,yy)
        for i in range(1,6): xx=chart_x+12+i*(chart_w-24)//6; p.drawLine(xx,grid_top,xx,grid_bottom)
        values=[.48,.43,.52,.49,.58,.55,.66,.61,.72,.68,.79,.75,.86]; points=[]; plot_w=chart_w-40; plot_h=grid_bottom-grid_top-6
        for i,v in enumerate(values): px=chart_x+20+int(i*plot_w/(len(values)-1)); py=grid_bottom-int(v*plot_h); points.append((px,py))
        p.setPen(QColor('#b9a16d'))
        for a,b in zip(points,points[1:]): p.drawLine(a[0],a[1],b[0],b[1])
        p.setPen(Qt.NoPen); p.setBrush(QColor('#d6bd7e'))
        for px,py in points: p.drawRect(px-2,py-2,5,5)
    def draw_side_monitor(self,p,w):
        x,y,ww,hh=w-225,225,195,118; p.setPen(QColor('#241b16')); p.setBrush(QColor('#292d2c')); p.drawRect(x,y,ww,hh); p.setPen(QColor('#e4d6b9')); p.setFont(QFont('Malgun Gothic',8,QFont.Bold)); p.drawText(QRect(x+12,y+10,165,18),Qt.AlignLeft,'MARKET MONITOR'); p.setPen(QColor('#8b9c82')); pts=[(x+15,y+92),(x+35,y+84),(x+56,y+87),(x+78,y+67),(x+100,y+75),(x+122,y+48),(x+145,y+60),(x+174,y+33)]
        for a,b in zip(pts,pts[1:]): p.drawLine(a[0],a[1],b[0],b[1])
        p.setPen(QColor('#bda977')); p.drawText(QRect(x+12,y+98,170,16),Qt.AlignLeft,'VOO +0.8% | JOBY +2.4%')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle('돈물원 · DONMULWON'); self.resize(1500,900); self.setStyleSheet("QMainWindow{background:#111416;color:#ded7c5;} QLabel{color:#ded7c5;} QLineEdit,QPlainTextEdit,QComboBox{background:#202428;color:#eee4d2;border:1px solid #51483b;padding:7px;} QPushButton{background:#665039;color:#fff2d4;padding:8px 14px;border:1px solid #8a6c4c;} QProgressBar{border:1px solid #51483b;background:#202428;} QProgressBar::chunk{background:#806544;}")
        root=QWidget(); layout=QVBoxLayout(root); layout.setContentsMargins(18,14,18,14); top=QHBoxLayout(); title=QLabel('🏦 DONMULWON  ·  AI TRADING TEAM'); title.setStyleSheet('font-size:22px;font-weight:700;'); top.addWidget(title); top.addStretch(); self.clock=QLabel(); top.addWidget(self.clock); layout.addLayout(top); self.office=PixelOffice(); layout.addWidget(self.office,1)
        controls=QHBoxLayout(); self.input=QLineEdit(); self.input.setPlaceholderText('무엇을 분석할까요? (예: JOBY 지금 사도 괜찮아?)'); self.button=QPushButton('분석 시작'); self.button.clicked.connect(self.start_analysis); self.input.returnPressed.connect(self.start_analysis); self.weather=QComboBox(); self.weather.addItems(['맑음','비','눈']); self.weather.currentTextChanged.connect(self.office.set_weather); controls.addWidget(self.input,1); controls.addWidget(self.weather); controls.addWidget(self.button); layout.addLayout(controls); self.status=QLabel('대기 중 · TOP-DOWN PIXEL OFFICE'); layout.addWidget(self.status); self.progress=QProgressBar(); self.progress.setRange(0,0); self.progress.hide(); layout.addWidget(self.progress); self.output=QPlainTextEdit(); self.output.setReadOnly(True); self.output.setMaximumHeight(220); layout.addWidget(self.output); self.setCentralWidget(root); self.ui_timer=QTimer(self); self.ui_timer.timeout.connect(self.update_clock); self.ui_timer.start(1000); self.update_clock(); self.thread=None; self.worker=None
    def update_clock(self):
        now=datetime.now(); period=self.office.auto_time(); self.clock.setText(now.strftime('%Y-%m-%d  %H:%M:%S')+f'  ·  {period}')
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
