import os, sys, io, contextlib, traceback, re
from datetime import datetime
from PySide6.QtCore import QObject, QThread, Signal, Slot, Qt, QRect, QTimer
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QPlainTextEdit, QTextBrowser, QProgressBar, QComboBox
BASE_DIR=os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path: sys.path.insert(0,BASE_DIR)
from gui_background import PixelBackground
from gui_characters_v2 import CharacterLayer
class AnalysisWorker(QObject):
    output=Signal(str); finished=Signal(); failed=Signal(str)
    def __init__(self,question): super().__init__(); self.question=question
    @Slot()
    def run(self):
        try:
            import main; buf=io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf): result=main.run_analysis(self.question)
            log=buf.getvalue().strip(); answer=str(result.get('alfredo','') if isinstance(result,dict) else result or '').strip()
            if not answer: answer='알프레도의 최종 판단이 생성되지 않았습니다.'
            self.output.emit(answer+'\n\n[MEETING_LOG]\n'+log[-12000:]); self.finished.emit()
        except Exception: self.failed.emit(traceback.format_exc())
class DialoguePanel(QTextBrowser):
    COLORS={'현무':'#668a62','김선달':'#666b78','이묵':'#829b5e','너부리':'#8d8178','알프레도':'#c09a5b'}; ICONS={'현무':'🐢','김선달':'🐦','이묵':'🐍','너부리':'🦝','알프레도':'🐱'}
    def __init__(self): super().__init__(); self.setReadOnly(True); self.setMaximumHeight(250); self.setStyleSheet('QTextBrowser{background:#141719;border:1px solid #4b4034;padding:8px;}')
    def _section(self,text,name):
        m=re.search(r'###\s*[^\n]*'+re.escape(name)+r'.*?(?=###\s|$)',text,re.S)
        if not m:return ''
        block=m.group(0); lines=[]
        for line in block.splitlines():
            s=line.strip().replace('**','').lstrip('*').strip()
            if s.startswith(('핵심 의견','근거','판단')): lines.append(s)
        return (' '.join(lines) if lines else re.sub(r'#+|[*`_]','',block))[:600].strip()
    def set_meeting(self,text):
        html='<div style="font-family:Malgun Gothic;color:#eee4d2;font-size:10pt">'; count=0
        for n in ['현무','김선달','이묵','너부리']:
            b=self._section(text,n)
            if b: html+=f'<div style="margin:4px;padding:8px;border:1px solid {self.COLORS[n]};background:#202427;border-radius:7px"><b>{self.ICONS[n]} {n}</b><br>{b}</div>'; count+=1
        m=re.search(r'###\s*🐱\s*알프레도.*?(?=###\s*|\Z)',text,re.S)
        if m: html+=f'<div style="margin:7px 4px;padding:10px;border:2px solid #b99a63;background:#29231b;border-radius:7px"><b>🐱 알프레도 · FINAL VERDICT</b><br>{re.sub(r"#+|[*`]","",m.group(0)).strip()[:900]}</div>'; count+=1
        if not count: html+='<div style="padding:18px;color:#9f9687">회의 결과가 아직 없습니다.</div>'
        self.setHtml(html+'</div>')
class PixelOffice(QWidget):
    DESKS=[('현무',55,244,175),('김선달',320,244,175),('이묵',585,244,175),('너부리',850,244,175),('알프레도',1115,244,175)]
    ROLE={'김선달':'FUNDAMENTALS + NEWS','이묵':'TECHNICAL','너부리':'PORTFOLIO','현무':'MACRO','알프레도':'FINAL VERIFIER'}
    PORTFOLIO=[('VOO','51.9%','$702.56'),('JEPQ','13.0%','$59.78'),('TTWO','24.0%','$215.47'),('JOBY','5.6%','$6.39'),('ALAB','5.5%','$291.22')]
    def __init__(self): super().__init__(); self.background=PixelBackground(); self.characters=CharacterLayer(); self.setMinimumHeight(560); self.active_ticker='MARKET'
    def set_weather(self,v): self.background.set_weather(v); self.update()
    def auto_time(self):
        now=datetime.now(); self.background.set_clock(now); h=self.background.hour
        self.characters.set_office_hours(h)
        return '아침' if 5<=h<11 else '낮' if 11<=h<17 else '저녁' if 17<=h<21 else '밤'
    @staticmethod
    def rect(p,x,y,w,h,c): p.setPen(Qt.NoPen); p.setBrush(QColor(c)); p.drawRect(int(x),int(y),int(w),int(h))
    @staticmethod
    def text(p,x,y,w,h,v,size=8,c='#eee4d2',align=Qt.AlignLeft|Qt.AlignVCenter): p.setPen(QColor(c)); p.setFont(QFont('Malgun Gothic',size,QFont.Bold)); p.drawText(QRect(int(x),int(y),int(w),int(h)),align,str(v))
    def paintEvent(self,e):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing,False); w,h=self.width(),self.height(); self.background.paint(p,w,h); self.draw_room(p,w,h); self.draw_window(p,w); self.draw_furniture(p,w,h); self.draw_desks(p); self.draw_market(p,w); self.draw_account(p,w); self.characters.paint(p); p.end()
    def draw_room(self,p,w,h):
        self.rect(p,18,18,w-36,28,'#3b2b22'); self.rect(p,18,46,w-36,6,'#80664c'); self.rect(p,18,52,w-36,172,'#765d46'); self.rect(p,18,224,w-36,h-242,'#55483d'); p.setPen(QColor('#655448'))
        for x in range(28,w-20,54): p.drawLine(x,224,x,h-18)
        for y in range(254,h-12,44): p.drawLine(18,y,w-18,y)
        p.setPen(Qt.NoPen); self.rect(p,34,58,82,120,'#3b2e27'); self.rect(p,40,64,70,108,'#514036'); self.text(p,44,68,62,16,'NOTICE',7,'#d0bb83',Qt.AlignCenter)
        for i,t in enumerate(['AI TEAM','MARKET','RULES','MEETING']): self.text(p,46,92+i*19,58,15,t,6,'#9e9481',Qt.AlignCenter)
        self.rect(p,32,h-116,88,84,'#241c19'); self.rect(p,38,h-109,76,77,'#60432f'); self.rect(p,45,h-102,62,68,'#2b2b2c'); self.rect(p,98,h-67,5,5,'#d0ae65'); self.rect(p,42,h-126,68,16,'#28362d'); self.text(p,45,h-125,62,15,'EXIT',8,'#c9d2b4',Qt.AlignCenter)
        self.rect(p,w-100,202,8,35,'#4b3525'); self.rect(p,w-120,228,48,11,'#61432e'); self.rect(p,w-122,194,48,10,'#496a4c'); self.rect(p,w-112,183,28,20,'#557850')
    def tree(self,p,x,base,s):
        self.rect(p,x-3*s,base-28*s,6*s,28*s,'#3c2b20')
        for dx,dy,ww,hh in [(-17,-40,34,15),(-24,-31,48,17),(-12,-51,28,16),(3,-35,26,14)]: self.rect(p,x+dx*s,base+dy*s,ww*s,hh*s,'#46684b')
        self.rect(p,x-8*s,base-45*s,13*s,8*s,'#5b8054')
    def draw_window(self,p,w):
        x,y,ww,wh=145,60,max(540,w-620),125; self.rect(p,x-8,y-8,ww+16,wh+16,'#2b211c'); self.rect(p,x,y,ww,wh,'#78989e'); self.rect(p,x+5,y+5,ww-10,wh-10,'#91b0ae'); self.text(p,x+16,y+8,250,18,'OUTSIDE VIEW · PIXEL CITY',7,'#e6d39d'); base=y+wh-12
        for i in range(18):
            bw=22+(i%4)*8; bh=25+((i*17)%55); bx=x+10+i*int((ww-20)/18); self.rect(p,bx,base-bh,bw,bh,'#596d72' if self.background.hour<17.5 else '#34434b')
            if self.background.hour>=18.5 or self.background.hour<6.5:
                for yy in range(base-bh+10,base-5,16): self.rect(p,bx+5,yy,4,4,'#d4bc76')
        for tx,sc in [(x+90,1),(x+ww//2,2),(x+ww-90,1)]: self.tree(p,tx,base+2,sc)
        p.setPen(QColor('#4b4034')); p.setBrush(Qt.NoBrush); p.drawRect(x,y,ww,wh)
        for xx in [x+ww//3,x+2*ww//3]: p.drawRect(xx,y,5,wh)
    def draw_furniture(self,p,w,h):
        x=w//2-150; y=h-175; self.rect(p,x-8,y-8,316,96,'#34271f'); self.rect(p,x,y,300,80,'#7a5337'); self.rect(p,x+8,y+8,284,64,'#63442f'); self.text(p,x+20,y+8,260,18,'AI TRADING TEAM · MEETING TABLE',8,'#e0c98e',Qt.AlignCenter); self.text(p,x+25,y+34,250,22,'DISCUSS · DISAGREE · VERIFY',7,'#a99d8c',Qt.AlignCenter)
        for cx,cy in [(x-32,y+25),(x+306,y+25),(x+55,y+88),(x+215,y+88)]: self.rect(p,cx,cy,32,25,'#382a23'); self.rect(p,cx+4,cy+4,24,17,'#67472f')
        sx=w-230; sy=h-155; self.rect(p,sx,sy,150,105,'#34261f'); self.rect(p,sx+8,sy+8,134,89,'#65462f')
        for i,t in enumerate(['RESEARCH','REPORTS','HISTORY']): self.rect(p,sx+16,sy+18+i*23,116,16,'#3a2b24'); self.text(p,sx+20,sy+18+i*23,108,16,t,6,'#c7b27d',Qt.AlignCenter)
    def draw_desks(self,p):
        for name,x,y,dw in self.DESKS:
            self.rect(p,x+10,y+65,dw-20,12,'#30241e'); self.rect(p,x-4,y-4,dw+8,65,'#34261f'); self.rect(p,x,y,dw,56,'#775236'); self.rect(p,x+5,y+5,dw-10,46,'#89603e'); mx=x+dw//2-43; self.rect(p,mx,y+7,86,35,'#171b1e'); self.rect(p,mx+5,y+11,76,26,'#182b30'); self.rect(p,mx+32,y+42,22,7,'#1a1c1f'); self.rect(p,mx+20,y+49,46,4,'#302b27'); pts=[(mx+9,y+32),(mx+18,y+28),(mx+27,y+30),(mx+37,y+21),(mx+49,y+26),(mx+60,y+16),(mx+72,y+21)]; p.setPen(QColor('#d4bb76'))
            for a,b in zip(pts,pts[1:]): p.drawLine(*a,*b)
            p.setPen(Qt.NoPen); self.rect(p,x+12,y+13,24,3,'#a0744d'); self.rect(p,x+dw-42,y+13,28,3,'#5e3f2c'); self.rect(p,x+dw//2-34,y+47,68,6,'#303033'); self.rect(p,x+dw-29,y+43,12,9,'#4e6652'); self.rect(p,x+8,y+43,62,10,'#3a2b23'); self.text(p,x+10,y+47,60,12,name,6,'#e1cb91',Qt.AlignCenter); self.text(p,x,y+78,dw,18,self.ROLE[name],5,'#9f927d',Qt.AlignCenter)
    def draw_market(self,p,w):
        x=150; y=205; ww=min(610,w-670); self.rect(p,x-4,y-4,ww+8,44,'#30241e'); self.rect(p,x,y,ww,36,'#171d20'); self.text(p,x+12,y+5,190,15,'MARKET BOARD',7,'#d8c48e'); self.text(p,x+205,y+5,ww-220,15,self.active_ticker,7,'#9ab0a8',Qt.AlignRight); self.text(p,x+12,y+20,ww-24,13,'VOO +5.74%   JEPQ +0.00%   TTWO -2.36%   JOBY -9.23%   ALAB -6.82%',5,'#cdb985')
    def draw_account(self,p,w):
        x=w-205; y=55; ww=175; hh=140; self.rect(p,x,y,ww,hh,'#252a2c'); self.rect(p,x+5,y+5,ww-10,hh-10,'#172024'); self.text(p,x+12,y+10,150,18,'ACCOUNT',8,'#d8c48e'); self.text(p,x+12,y+28,150,14,'LIVE HOLDINGS',5,'#8fa69a'); yy=y+48
        for t,wt,val in self.PORTFOLIO: self.text(p,x+10,yy,45,14,t,5,'#eee4d2'); self.text(p,x+57,yy,42,14,wt,5,'#cdb985',Qt.AlignRight); self.text(p,x+101,yy,62,14,val,5,'#aebbb2',Qt.AlignRight); yy+=18
    def set_ticker(self,t): self.active_ticker=t or 'MARKET'; self.update()
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle('돈물원 · DONMULWON'); self.resize(1500,980); self.setMinimumSize(1180,820); self.setStyleSheet('QMainWindow{background:#101315;color:#ded7c5;} QLabel{color:#ded7c5;} QLineEdit,QPlainTextEdit,QComboBox{background:#1d2225;color:#eee4d2;border:1px solid #51483b;padding:7px;} QPushButton{background:#665039;color:#fff2d4;padding:8px 16px;border:1px solid #8a6c4c;} QProgressBar{border:1px solid #51483b;background:#202428;} QProgressBar::chunk{background:#806544;}')
        root=QWidget(); layout=QVBoxLayout(root); layout.setContentsMargins(14,10,14,10); layout.setSpacing(8); top=QHBoxLayout(); title=QLabel('🏦 DONMULWON · PIXEL TRADING OFFICE'); title.setStyleSheet('font-size:21px;font-weight:700;'); top.addWidget(title); top.addStretch(); self.clock=QLabel(); top.addWidget(self.clock); layout.addLayout(top); self.office=PixelOffice(); layout.addWidget(self.office,1)
        controls=QHBoxLayout(); self.input=QLineEdit(); self.input.setPlaceholderText('예: JOBY 지금 사도 괜찮아? / 내 계좌 전체적으로 봐줘'); self.button=QPushButton('분석 시작'); self.button.clicked.connect(self.start_analysis); self.input.returnPressed.connect(self.start_analysis); self.weather=QComboBox(); self.weather.addItems(['맑음','비','눈']); self.weather.currentTextChanged.connect(self.office.set_weather); controls.addWidget(self.input,1); controls.addWidget(self.weather); controls.addWidget(self.button); layout.addLayout(controls); self.status=QLabel('대기 중 · 실제 시각 기준 출근/퇴근 시스템'); layout.addWidget(self.status); self.progress=QProgressBar(); self.progress.setRange(0,0); self.progress.hide(); layout.addWidget(self.progress); self.dialogue=DialoguePanel(); layout.addWidget(self.dialogue); self.raw=QPlainTextEdit(); self.raw.setReadOnly(True); self.raw.hide(); self.raw.setMaximumHeight(120); layout.addWidget(self.raw); self.setCentralWidget(root); self.thread=None; self.worker=None; self.timer=QTimer(self); self.timer.timeout.connect(self.update_clock); self.timer.timeout.connect(self.animate); self.timer.start(500); self.update_clock()
    def animate(self): self.office.characters.tick(); self.office.update()
    def update_clock(self):
        now=datetime.now(); period=self.office.auto_time(); self.clock.setText(now.strftime('%Y-%m-%d  %H:%M:%S')+' · '+period); self.office.update()
    def start_analysis(self):
        q=self.input.text().strip()
        if not q or self.thread is not None:return
        self.button.setEnabled(False); self.progress.show(); self.dialogue.setHtml('<div style="color:#bca87e;padding:20px;">⚔ AI TRADING TEAM 회의 시작...<br><br>각자 독립 분석 중입니다.</div>'); self.status.setText('⚔️ AI TRADING TEAM 회의 진행 중...')
        self.thread=QThread(self); self.worker=AnalysisWorker(q); self.worker.moveToThread(self.thread); self.thread.started.connect(self.worker.run); self.worker.output.connect(self.on_output); self.worker.failed.connect(self.on_failed); self.worker.finished.connect(self.thread.quit); self.worker.finished.connect(self.worker.deleteLater); self.thread.finished.connect(self.thread.deleteLater); self.thread.finished.connect(self.analysis_done); self.thread.start()
    def on_output(self,text): self.raw.setPlainText(text); self.dialogue.set_meeting(text)
    def on_failed(self,err): self.raw.setPlainText(err); self.dialogue.setHtml('<div style="color:#e29a8d;padding:18px;">분석 실패<br><br>'+err.replace('&','&amp;').replace('<','&lt;')+'</div>')
    def analysis_done(self): self.thread=None; self.worker=None; self.button.setEnabled(True); self.progress.hide(); self.status.setText('분석 완료 · 현재 시각 기준 사무실 상태 유지')
if __name__=='__main__':
    app=QApplication(sys.argv); win=MainWindow(); win.show(); sys.exit(app.exec())
