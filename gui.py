# DONMULWON GUI — detailed 2D pixel office
import os,sys,io,contextlib,traceback
from datetime import datetime
from PySide6.QtCore import QObject,QThread,Signal,Slot,Qt,QTimer,QRect
from PySide6.QtGui import QPainter,QColor,QFont
from PySide6.QtWidgets import QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QLabel,QLineEdit,QPushButton,QPlainTextEdit,QProgressBar,QComboBox
BASE_DIR=os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path: sys.path.insert(0,BASE_DIR)
class AnalysisWorker(QObject):
    output=Signal(str); finished=Signal(); failed=Signal(str)
    def __init__(self,q): super().__init__(); self.q=q
    @Slot()
    def run(self):
        try:
            import main; buf=io.StringIO()
            with contextlib.redirect_stdout(buf),contextlib.redirect_stderr(buf): result=main.run_analysis(self.q)
            text=buf.getvalue()
            if result is not None:text+='\n\n'+str(result)
            self.output.emit(text);self.finished.emit()
        except Exception:self.failed.emit(traceback.format_exc())
class PixelAgent:
    DATA={'현무':('turtle',90,430),'김선달':('bird',350,430),'이묵':('snake',610,430),'너부리':('raccoon',870,430),'알프레도':('cat',1160,405)}
    def __init__(self,name):self.name=name;self.frame=0
    def tick(self):self.frame=(self.frame+1)%24
    def paint(self,p,x,y,scale=4):
        s=int(scale);ox=int(x);oy=int(y);typ=self.DATA[self.name][0]
        pal={'turtle':('#4e8061','#244536','#cbb88d','#18211d'),'bird':('#a75c3d','#4a2c2a','#e5c58d','#1c2025'),'snake':('#647a50','#27352b','#d2b775','#171b18'),'raccoon':('#85817b','#35383b','#c5a46e','#191b1d'),'cat':('#17191b','#08090a','#c9b9a2','#111214')}
        fur,suit,skin,ink=map(QColor,pal[typ])
        def r(a,b,w,h,c):p.setBrush(c);p.drawRect(ox+a*s,oy+b*s,w*s,h*s)
        p.setPen(Qt.NoPen);r(5,40,22,2,QColor(15,15,15,110));r(8,32,6,9,suit);r(19,32,6,9,suit);r(7,40,8,2,ink);r(18,40,8,2,ink)
        r(5,18,22,17,suit);r(8,19,16,14,suit);r(12,19,8,13,skin);r(15,20,2,9,QColor('#eee4d2'));r(15,23,2,7,QColor('#8a4a42'));r(2,20,5,12,suit);r(25,20,5,12,suit);r(2,31,5,3,skin);r(25,31,5,3,skin);r(13,15,6,5,skin);r(7,4,18,13,fur);r(9,2,14,3,fur)
        if typ=='cat':
            r(7,0,5,7,fur);r(20,0,5,7,fur);r(8,2,3,3,QColor('#51454a'));r(21,2,3,3,QColor('#51454a'));r(11,8,3,2,QColor('#d7c47c'));r(19,8,3,2,QColor('#d7c47c'));r(12,8,1,2,ink);r(20,8,1,2,ink);r(15,11,2,2,QColor('#c78b91'))
        elif typ=='turtle':
            r(2,15,28,13,fur);r(6,16,20,10,suit);r(9,18,14,6,QColor('#355d47'));r(15,19,3,4,QColor('#a8b88e'));r(13,9,7,7,skin);r(19,10,4,5,skin);r(20,11,1,1,ink)
        elif typ=='bird':
            r(6,5,20,13,fur);r(3,12,7,6,fur);r(25,11,6,4,QColor('#d59a45'));r(12,8,3,2,QColor('#eee0a9'));r(20,8,3,2,QColor('#eee0a9'));r(13,8,1,2,ink);r(21,8,1,2,ink)
        elif typ=='snake':
            r(8,4,18,14,fur);r(10,2,5,4,fur);r(20,3,5,4,fur);r(11,8,3,2,QColor('#d7c47c'));r(20,8,3,2,QColor('#d7c47c'));r(12,8,1,2,ink);r(21,8,1,2,ink);r(5,13,6,4,fur);r(2,15,6,4,fur)
        elif typ=='raccoon':
            r(6,3,20,15,fur);r(5,7,22,7,suit);r(10,8,5,4,QColor('#c7b9a2'));r(18,8,5,4,QColor('#c7b9a2'));r(12,9,2,2,ink);r(20,9,2,2,ink);r(15,12,3,2,QColor('#8b5a55'));r(7,2,5,5,fur);r(20,2,5,5,fur)
        r(8,19,3,10,QColor('#4d5960'));r(21,19,3,10,QColor('#4d5960'));r(14,27,1,1,QColor('#d6bd78'));r(14,30,1,1,QColor('#d6bd78'))
class PixelOffice(QWidget):
    def __init__(self):
        super().__init__();self.weather='맑음';self.time='밤';self.agents={n:PixelAgent(n) for n in PixelAgent.DATA};self.timer=QTimer(self);self.timer.timeout.connect(self.update_anim);self.timer.start(140)
    def update_anim(self):
        for a in self.agents.values():a.tick()
        self.update()
    def set_weather(self,v):self.weather=v;self.update()
    def paintEvent(self,e):
        p=QPainter(self);p.setRenderHint(QPainter.Antialiasing,False)
        try:
            w,h=self.width(),self.height();p.fillRect(0,0,w,h,QColor('#171a20'));p.fillRect(18,18,w-36,310,QColor('#b99b72'));p.fillRect(38,42,w-76,250,QColor('#23354a'));self.draw_city(p,38,42,w-76,250);p.setPen(QColor('#8b765b'));p.setBrush(Qt.NoBrush);p.drawRect(38,42,w-76,250)
            for xx in range(190,w-50,190):p.drawLine(xx,42,xx,292)
            p.setPen(Qt.NoPen);p.setBrush(QColor('#33251e'));p.drawRect(28,345,92,150);p.setBrush(QColor('#805a39'));p.drawRect(38,355,72,130);p.setBrush(QColor('#d8bf88'));p.drawRect(91,417,5,5)
            self.draw_desks(p)
            for n,a in self.agents.items():
                x,y=PixelAgent.DATA[n][1:];a.paint(p,x,y,4);p.setPen(QColor('#eee4d2'));p.setFont(QFont('Malgun Gothic',11,QFont.Bold));p.drawText(QRect(x-18,y+177,165,26),Qt.AlignCenter,n)
            if self.weather in ('비','눈'):self.draw_weather(p)
            p.setPen(QColor('#cbb98e'));p.setFont(QFont('Malgun Gothic',10));p.drawText(40,h-22,f'2D PIXEL OFFICE · {self.time} · {self.weather}')
        finally:
            if p.isActive():p.end()
    def draw_city(self,p,x,y,w,h):
        p.setPen(Qt.NoPen);p.setBrush(QColor('#152235'))
        for i in range(24):
            bw=28+(i%4)*13;bh=55+(i*17)%125;bx=x+8+i*int((w-16)/24);p.drawRect(bx,y+h-bh,bw,bh);p.setBrush(QColor('#d1b76a'))
            for wy in range(y+h-bh+12,y+h-8,18):
                if (i+wy)%3:p.drawRect(bx+6,wy,5,5)
            p.setBrush(QColor('#152235'))
    def draw_desks(self,p):
        for x in (145,405,665,925):
            p.setPen(Qt.NoPen);p.setBrush(QColor('#4b3020'));p.drawRect(x,575,190,76);p.setBrush(QColor('#20272c'));p.drawRect(x+52,535,86,40);p.setBrush(QColor('#705039'));p.drawRect(x+76,651,38,48)
        p.setBrush(QColor('#33231b'));p.drawRect(1110,555,300,96);p.setBrush(QColor('#20272c'));p.drawRect(1170,500,180,55);p.setBrush(QColor('#705039'));p.drawRect(1240,651,42,50)
    def draw_weather(self,p):
        p.setPen(QColor('#a9c6d9'));p.setBrush(QColor('#a9c6d9'));step=18 if self.weather=='비' else 30
        for i in range(0,self.width(),step):
            yy=70+((i+self.agents['현무'].frame*8)%210);p.drawRect(i,yy,2 if self.weather=='비' else 4,12 if self.weather=='비' else 4)
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__();self.setWindowTitle('돈물원 · DONMULWON');self.resize(1500,950);self.setStyleSheet("QMainWindow{background:#111416;color:#ded7c5;} QLabel{color:#ded7c5;}");root=QWidget();lay=QVBoxLayout(root);lay.setContentsMargins(18,14,18,14)
        top=QHBoxLayout();title=QLabel('🏦 DONMULWON  ·  AI TRADING TEAM');title.setStyleSheet('font-size:22px;font-weight:700;');top.addWidget(title);top.addStretch();self.clock=QLabel();top.addWidget(self.clock);lay.addLayout(top);self.office=PixelOffice();lay.addWidget(self.office,1)
        bottom=QHBoxLayout();self.input=QLineEdit();self.input.setPlaceholderText('무엇을 분석할까요?');self.button=QPushButton('분석 시작');self.button.clicked.connect(self.start_analysis);self.input.returnPressed.connect(self.start_analysis);self.weather=QComboBox();self.weather.addItems(['맑음','비','눈']);self.weather.currentTextChanged.connect(self.office.set_weather);bottom.addWidget(self.input,1);bottom.addWidget(self.weather);bottom.addWidget(self.button);lay.addLayout(bottom);self.status=QLabel('대기 중 · 2D PIXEL OFFICE');lay.addWidget(self.status);self.progress=QProgressBar();self.progress.setRange(0,0);self.progress.hide();lay.addWidget(self.progress);self.output=QPlainTextEdit();self.output.setReadOnly(True);self.output.setMaximumHeight(230);lay.addWidget(self.output);self.setCentralWidget(root);self.clock_timer=QTimer(self);self.clock_timer.timeout.connect(self.clock_update);self.clock_timer.start(1000);self.clock_update()
    def clock_update(self):
        now=datetime.now();self.clock.setText(now.strftime('%Y-%m-%d  %H:%M:%S'));hr=now.hour;self.office.time='아침' if 6<=hr<11 else '낮' if 11<=hr<18 else '노을' if 18<=hr<20 else '밤';self.office.update()
    def start_analysis(self):
        q=self.input.text().strip()
        if not q:return
        self.button.setEnabled(False);self.input.setEnabled(False);self.progress.show();self.status.setText('AI 팀 분석 진행 중...');self.output.clear();self.thread=QThread(self);self.worker=AnalysisWorker(q);self.worker.moveToThread(self.thread);self.worker.output.connect(self.output.setPlainText);self.worker.finished.connect(self.done);self.worker.failed.connect(self.fail);self.thread.started.connect(self.worker.run);self.thread.start()
    def done(self):self.progress.hide();self.button.setEnabled(True);self.input.setEnabled(True);self.status.setText('분석 완료 · 알프레도 최종 검증 완료');self.thread.quit()
    def fail(self,e):self.progress.hide();self.button.setEnabled(True);self.input.setEnabled(True);self.status.setText('분석 실패');self.output.setPlainText(e);self.thread.quit()
def main():
    app=QApplication(sys.argv);window=MainWindow();window.show();return app.exec()
if __name__=='__main__':sys.exit(main())
