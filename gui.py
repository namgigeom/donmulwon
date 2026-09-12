# DONMULWON GUI — pixel office architecture v2
# 2D pixel-art office + sprite/state system. Backend/main.py remains unchanged.
import os
import sys
import io
import contextlib
import traceback
from datetime import datetime

from PySide6.QtCore import QObject, QThread, Signal, Slot, Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QPlainTextEdit, QProgressBar, QComboBox

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path: sys.path.insert(0,BASE_DIR)

class AnalysisWorker(QObject):
    status=Signal(str); output=Signal(str); finished=Signal(); failed=Signal(str)
    def __init__(self,q): super().__init__(); self.q=q
    @Slot()
    def run(self):
        try:
            import main
            buf=io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                result=main.run_analysis(self.q)
            text=buf.getvalue()
            if result is not None: text += "\n\n" + str(result)
            self.output.emit(text); self.finished.emit()
        except Exception:
            self.failed.emit(traceback.format_exc())

class PixelAgent:
    # name -> (sprite type, x, y, role)
    # NOTE: coordinates are integers. The previous version accidentally stored
    # (x, y) as one tuple, which caused: str + int TypeError during painting.
    DATA={
        '현무':('turtle',72,480,'slow'),
        '김선달':('bird',330,480,'read'),
        '이묵':('snake',588,480,'chart'),
        '너부리':('raccoon',846,480,'account'),
        '알프레도':('cat',1110,458,'lead')
    }
    def __init__(self,name): self.name=name; self.state='idle'; self.frame=0
    def tick(self): self.frame=(self.frame+1)%24
    def paint(self,p,x,y,scale=4):
        colors={'turtle':('#47745a','#294637','#d7c49c'),'bird':('#a75b3b','#e2c18b','#332d31'),
                'snake':('#536b49','#27352a','#c9ad72'),'raccoon':('#73706c','#39383a','#b99362'),
                'cat':('#b47a52','#4a3031','#d8c3a0')}
        typ=self.DATA[self.name][0]; c1,c2,c3=map(QColor,colors[typ]); ox=int(x); oy=int(y); scale=int(scale)
        p.setPen(Qt.NoPen); p.setBrush(QColor(25,23,22,100)); p.drawRect(ox+12*scale,oy+76*scale,30*scale,4*scale)
        p.setBrush(c2); p.drawRect(ox+18*scale,oy+57*scale,9*scale,22*scale); p.drawRect(ox+37*scale,oy+57*scale,9*scale,22*scale)
        p.setBrush(QColor('#1f2529')); p.drawRect(ox+12*scale,oy+32*scale,40*scale,29*scale)
        p.setBrush(c3); p.drawRect(ox+27*scale,oy+35*scale,10*scale,20*scale)
        p.setBrush(c2); p.drawRect(ox+31*scale,oy+37*scale,3*scale,12*scale)
        p.setBrush(c2); p.drawRect(ox+6*scale,oy+38*scale,8*scale,18*scale); p.drawRect(ox+50*scale,oy+38*scale,8*scale,18*scale)
        p.setBrush(c1); p.drawRect(ox+15*scale,oy+8*scale,35*scale,27*scale); p.drawRect(ox+21*scale,oy+3*scale,22*scale,7*scale)
        if typ=='turtle':
            p.setBrush(c1); p.drawRect(ox+8*scale,oy+25*scale,49*scale,20*scale); p.setBrush(c2); p.drawRect(ox+18*scale,oy+28*scale,29*scale,13*scale); p.setBrush(c3); p.drawRect(ox+28*scale,oy+31*scale,9*scale,7*scale)
        elif typ=='bird':
            p.setBrush(c3); p.drawRect(ox+47*scale,oy+21*scale,17*scale,7*scale); p.setBrush(c2); p.drawRect(ox+27*scale,oy+15*scale,5*scale,5*scale)
        elif typ=='snake':
            p.setBrush(c1); p.drawRect(ox+5*scale,oy+19*scale,14*scale,8*scale); p.drawRect(ox+2*scale,oy+24*scale,10*scale,7*scale)
        elif typ=='raccoon':
            p.setBrush(c2); p.drawRect(ox+14*scale,oy+14*scale,38*scale,10*scale); p.setBrush(c3); p.drawRect(ox+25*scale,oy+16*scale,6*scale,6*scale); p.drawRect(ox+38*scale,oy+16*scale,6*scale,6*scale)
        elif typ=='cat':
            p.setBrush(c1); p.drawRect(ox+12*scale,oy+1*scale,9*scale,12*scale); p.drawRect(ox+44*scale,oy+1*scale,9*scale,12*scale); p.setBrush(c3); p.drawRect(ox+25*scale,oy+16*scale,6*scale,6*scale); p.drawRect(ox+39*scale,oy+16*scale,6*scale,6*scale)
        p.setBrush(QColor('#161616')); p.drawRect(ox+25*scale,oy+19*scale,4*scale,4*scale); p.drawRect(ox+40*scale,oy+19*scale,4*scale,4*scale)
        p.setBrush(QColor('#7b3b35')); p.drawRect(ox+32*scale,oy+43*scale,4*scale,12*scale)

class PixelOffice(QWidget):
    def __init__(self):
        super().__init__(); self.weather='맑음'; self.time='밤'; self.agents={n:PixelAgent(n) for n in PixelAgent.DATA}; self.timer=QTimer(self); self.timer.timeout.connect(self.update_anim); self.timer.start(140)
    def update_anim(self):
        for a in self.agents.values(): a.tick()
        self.update()
    def set_weather(self,v): self.weather=v; self.update()
    def paintEvent(self,e):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing,False); w,h=self.width(),self.height(); p.fillRect(0,0,w,h,QColor('#171a20'))
        p.fillRect(18,18,w-36,310,QColor('#202d3c')); p.fillRect(18,328,w-36,h-346,QColor('#6e523b'))
        p.fillRect(38,42,w-76,250,QColor('#1b3150')); self.draw_city(p,38,42,w-76,250)
        p.setPen(QColor('#806747')); p.setBrush(Qt.NoBrush); p.drawRect(38,42,w-76,250)
        for xx in range(190,w-50,190): p.drawLine(xx,42,xx,292)
        p.setPen(Qt.NoPen); p.setBrush(QColor('#3c2a20')); p.drawRect(28,345,88,145); p.setBrush(QColor('#8d6a43')); p.drawRect(38,355,68,125); p.setBrush(QColor('#d7bd84')); p.drawRect(88,417,5,5)
        self.draw_desks(p)
        for n,a in self.agents.items():
            x,y,_=PixelAgent.DATA[n][1:]
            a.paint(p,x,y,4)
            p.setPen(QColor('#eee4d2')); p.setFont(QFont('Malgun Gothic',11,QFont.Bold)); p.drawText(x-5,y+325,130,24,n)
        if self.weather in ('비','눈'): self.draw_weather(p)
        p.setPen(QColor('#cbb98e')); p.setFont(QFont('Malgun Gothic',10)); p.drawText(40,h-22,f'2D PIXEL OFFICE · {self.time} · {self.weather}')
    def draw_city(self,p,x,y,w,h):
        p.setPen(Qt.NoPen); p.setBrush(QColor('#121b2c'))
        for i in range(24):
            bw=28+(i%4)*13; bh=55+(i*17)%125; bx=x+8+i*int((w-16)/24); p.drawRect(bx,y+h-bh,bw,bh); p.setBrush(QColor('#c6a85d'))
            for wy in range(y+h-bh+12,y+h-8,18):
                if (i+wy)%3: p.drawRect(bx+6,wy,5,5)
            p.setBrush(QColor('#121b2c'))
    def draw_desks(self,p):
        for x in (145,390,635,880):
            p.setPen(Qt.NoPen); p.setBrush(QColor('#4b3020')); p.drawRect(x,595,190,82); p.setBrush(QColor('#1b2024')); p.drawRect(x+58,548,74,48); p.setBrush(QColor('#705039')); p.drawRect(x+75,677,42,52)
        p.setBrush(QColor('#33231b')); p.drawRect(1070,575,300,110); p.setBrush(QColor('#1b2024')); p.drawRect(1135,512,160,63); p.setBrush(QColor('#705039')); p.drawRect(1190,685,55,55)
    def draw_weather(self,p):
        p.setPen(QColor('#a9c6d9')); p.setBrush(QColor('#a9c6d9')); step=18 if self.weather=='비' else 30
        for i in range(0,self.width(),step):
            yy=70+((i+self.agents['현무'].frame*8)%210)
            if self.weather=='비': p.drawRect(i,yy,2,12)
            else: p.drawRect(i,yy,4,4)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle('돈물원 · DONMULWON'); self.resize(1500,950); self.setStyleSheet("QMainWindow{background:#111416;color:#ded7c5;} QLabel{color:#ded7c5;}")
        root=QWidget(); lay=QVBoxLayout(root); lay.setContentsMargins(18,14,18,14)
        top=QHBoxLayout(); title=QLabel('🏦 DONMULWON  ·  AI TRADING TEAM'); title.setStyleSheet('font-size:22px;font-weight:700;'); top.addWidget(title); top.addStretch(); self.clock=QLabel(); top.addWidget(self.clock); lay.addLayout(top)
        self.office=PixelOffice(); lay.addWidget(self.office,1)
        bottom=QHBoxLayout(); self.input=QLineEdit(); self.input.setPlaceholderText('무엇을 분석할까요?'); self.button=QPushButton('분석 시작'); self.button.clicked.connect(self.start_analysis); self.input.returnPressed.connect(self.start_analysis); self.weather=QComboBox(); self.weather.addItems(['맑음','비','눈']); self.weather.currentTextChanged.connect(self.office.set_weather); bottom.addWidget(self.input,1); bottom.addWidget(self.weather); bottom.addWidget(self.button); lay.addLayout(bottom)
        self.status=QLabel('대기 중 · 2D PIXEL OFFICE'); lay.addWidget(self.status); self.progress=QProgressBar(); self.progress.setRange(0,0); self.progress.hide(); lay.addWidget(self.progress)
        self.output=QPlainTextEdit(); self.output.setReadOnly(True); self.output.setMaximumHeight(230); lay.addWidget(self.output); self.setCentralWidget(root)
        self.clock_timer=QTimer(self); self.clock_timer.timeout.connect(self.clock_update); self.clock_timer.start(1000); self.clock_update()
    def clock_update(self):
        now=datetime.now(); self.clock.setText(now.strftime('%Y-%m-%d  %H:%M:%S')); hr=now.hour; self.office.time='아침' if 6<=hr<11 else '낮' if 11<=hr<18 else '노을' if 18<=hr<20 else '밤'; self.office.update()
    def start_analysis(self):
        q=self.input.text().strip()
        if not q:return
        self.button.setEnabled(False); self.input.setEnabled(False); self.progress.show(); self.status.setText('AI 팀 분석 진행 중...'); self.output.clear()
        self.thread=QThread(self); self.worker=AnalysisWorker(q); self.worker.moveToThread(self.thread); self.worker.output.connect(self.output.setPlainText); self.worker.status.connect(self.status.setText); self.worker.finished.connect(self.done); self.worker.failed.connect(self.fail); self.thread.started.connect(self.worker.run); self.thread.start()
    def done(self): self.progress.hide(); self.button.setEnabled(True); self.input.setEnabled(True); self.status.setText('분석 완료 · 알프레도 최종 검증 완료'); self.thread.quit()
    def fail(self,e): self.progress.hide(); self.button.setEnabled(True); self.input.setEnabled(True); self.status.setText('분석 실패'); self.output.setPlainText(e); self.thread.quit()

def main():
    app=QApplication(sys.argv); app.setStyle('Fusion'); win=MainWindow(); win.show(); sys.exit(app.exec())
if __name__=='__main__': main()
