# DONMULWON - TOP DOWN PIXEL OFFICE GUI
import os, sys, io, contextlib, traceback, re
from datetime import datetime

from PySide6.QtCore import QObject, QThread, Signal, Slot, Qt, QRect, QTimer
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QPlainTextEdit, QTextBrowser,
    QProgressBar, QComboBox
)

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
            import main
            buf=io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                if not hasattr(main,'run_analysis'): raise AttributeError('main.py에 run_analysis()가 없습니다.')
                result=main.run_analysis(self.question)
            log=buf.getvalue().strip()
            answer=''
            if isinstance(result,dict): answer=str(result.get('alfredo','') or '').strip()
            elif result is not None: answer=str(result).strip()
            if not answer: answer='알프레도의 최종 판단이 생성되지 않았습니다.'
            self.output.emit(answer+'\n\n[MEETING_LOG]\n'+log[-12000:])
            self.finished.emit()
        except Exception: self.failed.emit(traceback.format_exc())


class DialoguePanel(QTextBrowser):
    COLORS={'현무':'#527454','김선달':'#4d5059','이묵':'#667c4e','너부리':'#776e67','알프레도':'#68523b'}
    ICONS={'현무':'🐢','김선달':'🐦','이묵':'🐍','너부리':'🦝','알프레도':'🐱'}
    FLAVOR={'현무':'아... 천천히 보자.','김선달':'까악!','이묵':'쉬이익...','너부리':'구리!','알프레도':'냥.'}
    def __init__(self):
        super().__init__(); self.setReadOnly(True); self.setOpenExternalLinks(False); self.setMaximumHeight(300)
        self.setStyleSheet('QTextBrowser{background:#16191b;border:1px solid #4d4338;padding:8px;}')
    def _section(self,text,name):
        m=re.search(r'###\s*[^\n]*'+re.escape(name)+r'.*?(?=###\s|$)',text,re.S)
        if not m: return ''
        block=m.group(0)
        lines=[]
        for line in block.splitlines():
            s=line.strip().lstrip('*').strip()
            if s.startswith(('핵심 의견','근거','판단','**핵심 의견**','**근거**','**판단**')): lines.append(s.replace('**',''))
        if not lines:
            block=re.sub(r'#+.*\n','',block); block=re.sub(r'[*`_]','',block); return block[:520].strip()
        return ' '.join(lines)[:620]
    def set_meeting(self,text):
        cards=[]
        for name in ['현무','김선달','이묵','너부리']:
            body=self._section(text,name)
            if not body: continue
            flavor=self.FLAVOR[name]
            if name=='현무': body=flavor+' '+body.replace('다.','다...')
            elif name=='김선달': body=flavor+' '+body
            elif name=='이묵': body=flavor+' '+body
            elif name=='너부리': body=body+' '+flavor
            cards.append((name,body))
        final=''
        m=re.search(r'###\s*🐱\s*알프레도.*?(?=###\s*|\Z)',text,re.S)
        if m: final=re.sub(r'#+|\*|`','',m.group(0)).strip()[:900]
        if not cards and not final:
            final='회의 결과를 읽을 수 없습니다. 원본 회의 로그를 아래 분석창에서 확인하세요.'
        html='<div style="font-family:Malgun Gothic; font-size:11pt; color:#eee4d2;">'
        for name,body in cards:
            color=self.COLORS[name]
            html+=f'<div style="margin:5px 20px 5px 5px;padding:9px 12px;border:1px solid {color};background:#202427;border-radius:10px;"><b>{self.ICONS[name]} {name}</b><br>{body}</div>'
        if final:
            html+=f'<div style="margin:8px 5px 4px 70px;padding:10px 14px;border:2px solid #b99a63;background:#28231d;border-radius:10px;"><b>🐱 알프레도 · 최종 검증</b><br>{final}</div>'
        html+='</div>'
        self.setHtml(html); self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())


class PixelOffice(QWidget):
    DESKS=[('현무',55,244,175),('김선달',320,244,175),('이묵',585,244,175),('너부리',850,244,175),('알프레도',1115,244,175)]
    PORTFOLIO=[('VOO','51.91%','$702.56'),('JEPQ','13.04%','$59.78'),('TTWO','23.98%','$215.47'),('JOBY','5.57%','$6.39'),('ALAB','5.50%','$291.22'),('USD CASH','0.00%','$0.00')]
    def __init__(self):
        super().__init__(); self.background=PixelBackground(); self.characters=CharacterLayer(); self.setMinimumHeight(640)
    def set_weather(self,v): self.background.set_weather(v); self.update()
    def auto_time(self):
        now=datetime.now(); self.background.set_clock(now); h=now.hour
        period='아침' if 5<=h<11 else '낮' if 11<=h<17 else '저녁' if 17<=h<21 else '밤'; self.background.set_time(period); return period
    @staticmethod
    def rect(p,x,y,w,h,c): p.setPen(Qt.NoPen); p.setBrush(QColor(c)); p.drawRect(int(x),int(y),int(w),int(h))
    @staticmethod
    def text(p,x,y,w,h,v,size=8,c='#eee4d2',align=Qt.AlignLeft|Qt.AlignVCenter):
        p.setPen(QColor(c)); p.setFont(QFont('Malgun Gothic',size,QFont.Bold)); p.drawText(QRect(int(x),int(y),int(w),int(h)),align,str(v))
    def paintEvent(self,e):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing,False)
        try:
            w,h=self.width(),self.height(); self.background.paint(p,w,h); self.draw_desks(p); self.draw_exit(p); self.draw_market(p,w); self.draw_account(p,w); self.characters.paint(p)
        finally: p.end()
    def draw_desks(self,p):
        for name,x,y,dw in self.DESKS:
            self.rect(p,x+12,y+68,dw-24,7,'#30251e'); self.rect(p,x-3,y-3,dw+6,62,'#201713'); self.rect(p,x,y,dw,55,'#5c3e28'); self.rect(p,x+5,y+5,dw-10,45,'#795337')
            self.rect(p,x+12,y+13,38,2,'#916844'); self.rect(p,x+62,y+28,30,2,'#8a5f3d'); self.rect(p,x+dw-55,y+38,38,2,'#513621')
            mx=x+dw//2-39; self.rect(p,mx,y+6,78,35,'#171c20'); self.rect(p,mx+4,y+10,70,27,'#15252b'); self.rect(p,mx+29,y+40,20,7,'#171b1f')
            pts=[(mx+11,y+32),(mx+20,y+27),(mx+29,y+30),(mx+38,y+21),(mx+48,y+25),(mx+60,y+16)]; p.setPen(QColor('#c6aa6d'))
            for a,b in zip(pts,pts[1:]): p.drawLine(*a,*b)
            p.setPen(Qt.NoPen); self.rect(p,x+dw//2-43,y+43,66,8,'#25282b'); self.rect(p,x+dw//2-37,y+45,54,4,'#777b7b')
            self.rect(p,x+7,y+48,64,9,'#2b211c'); self.text(p,x+8,y+47,62,11,name,6,'#e0c991',Qt.AlignCenter)
    def draw_exit(self,p):
        # 출입문 대신 아래쪽 벽면의 독립된 비상구 표지. 현무 책상과 겹치지 않는다.
        x,y=42,430; self.rect(p,x,y,128,48,'#1c1f20'); self.rect(p,x+4,y+4,120,40,'#28312f'); self.rect(p,x+12,y+10,18,20,'#55705b'); self.text(p,x+38,y+8,76,17,'EXIT',9,'#d7e0c4'); self.text(p,x+38,y+25,76,12,'EMERGENCY',6,'#b9c3b0'); self.rect(p,x+12,y+32,98,3,'#55705b')
    def draw_market(self,p,w):
        cx=w//2; bw=min(690,max(560,w-760)); bh=142; x=cx-bw//2; y=345
        self.rect(p,x-6,y-6,bw+12,bh+12,'#211914'); self.rect(p,x-2,y-2,bw+4,bh+4,'#6b5138'); self.rect(p,x+5,y+5,bw-10,bh-10,'#11171a')
        self.text(p,x+16,y+8,300,18,'DONMULWON · MARKET MONITOR',9,'#d8c48e'); self.text(p,x+bw-90,y+8,70,18,'LIVE',8,'#b5c08e',Qt.AlignRight)
        top=y+36; bottom=y+bh-30; p.setPen(QColor('#293d42'))
        for i in range(1,5): p.drawLine(x+20,top+i*(bottom-top)//5,x+bw-20,top+i*(bottom-top)//5)
        for i in range(1,9): p.drawLine(x+20+i*(bw-40)//9,top,x+20+i*(bw-40)//9,bottom)
        vals=[.35,.31,.42,.39,.50,.46,.58,.55,.69,.62,.76,.71,.86,.81,.92]; pts=[]
        for i,v in enumerate(vals): pts.append((x+22+int(i*(bw-44)/(len(vals)-1)),bottom-int(v*(bottom-top))))
        p.setPen(QColor('#d0b477'))
        for a,b in zip(pts,pts[1:]): p.drawLine(*a,*b)
        p.setPen(Qt.NoPen); p.setBrush(QColor('#e1c681'))
        for px,py in pts: p.drawRect(px-2,py-2,5,5)
        self.text(p,x+20,y+bh-25,bw-40,15,'VOO   +5.74%     JEPQ   +0.00%     TTWO   -2.36%     JOBY   -9.23%     ALAB   -6.82%',6,'#cdb985',Qt.AlignCenter)
    def draw_account(self,p,w):
        x=w-325; y=40; ww=300; hh=190
        self.rect(p,x+5,y+5,ww,hh,'#17191b'); self.rect(p,x,y,ww,hh,'#292d2e'); self.rect(p,x+6,y+6,ww-12,hh-12,'#172125')
        self.text(p,x+14,y+10,190,18,'ACCOUNT MONITOR',9,'#d8c48e'); self.text(p,x+14,y+29,260,15,'PORTFOLIO · ALL HOLDINGS',6,'#8fa69a')
        yy=y+50
        for ticker,weight,price in self.PORTFOLIO:
            self.text(p,x+14,yy,88,17,ticker,7,'#eee4d2'); self.text(p,x+100,yy,72,17,weight,7,'#cdb985',Qt.AlignRight); self.text(p,x+180,yy,92,17,price,7,'#aebbb2',Qt.AlignRight); yy+=21


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle('돈물원 · DONMULWON'); self.resize(1540,1020)
        self.setStyleSheet('QMainWindow{background:#111416;color:#ded7c5;} QLabel{color:#ded7c5;} QLineEdit,QPlainTextEdit,QComboBox{background:#202428;color:#eee4d2;border:1px solid #51483b;padding:7px;} QPushButton{background:#665039;color:#fff2d4;padding:8px 14px;border:1px solid #8a6c4c;} QProgressBar{border:1px solid #51483b;background:#202428;} QProgressBar::chunk{background:#806544;}')
        root=QWidget(); layout=QVBoxLayout(root); layout.setContentsMargins(18,14,18,14)
        top=QHBoxLayout(); title=QLabel('🏦 DONMULWON · AI TRADING TEAM'); title.setStyleSheet('font-size:22px;font-weight:700;'); top.addWidget(title); top.addStretch(); self.clock=QLabel(); top.addWidget(self.clock); layout.addLayout(top)
        self.office=PixelOffice(); layout.addWidget(self.office,1)
        controls=QHBoxLayout(); self.input=QLineEdit(); self.input.setPlaceholderText('무엇을 분석할까요? (예: JOBY 지금 사도 괜찮아?)'); self.button=QPushButton('분석 시작'); self.button.clicked.connect(self.start_analysis); self.input.returnPressed.connect(self.start_analysis); self.weather=QComboBox(); self.weather.addItems(['맑음','비','눈']); self.weather.currentTextChanged.connect(self.office.set_weather); controls.addWidget(self.input,1); controls.addWidget(self.weather); controls.addWidget(self.button); layout.addLayout(controls)
        self.status=QLabel('대기 중 · TOP-DOWN PIXEL OFFICE'); layout.addWidget(self.status); self.progress=QProgressBar(); self.progress.setRange(0,0); self.progress.hide(); layout.addWidget(self.progress)
        self.dialogue=DialoguePanel(); self.dialogue.setPlaceholderText('분석이 끝나면 AI 팀의 실제 회의 내용이 말풍선으로 표시됩니다.'); layout.addWidget(self.dialogue)
        self.raw=QPlainTextEdit(); self.raw.setReadOnly(True); self.raw.setMaximumHeight(120); self.raw.hide(); layout.addWidget(self.raw)
        self.setCentralWidget(root); self.thread=None; self.worker=None
        self.timer=QTimer(self); self.timer.timeout.connect(self.update_clock); self.timer.timeout.connect(self.animate); self.timer.start(500); self.update_clock()
    def animate(self): self.office.characters.tick(); self.office.update()
    def update_clock(self):
        now=datetime.now(); self.clock.setText(now.strftime('%Y-%m-%d  %H:%M:%S')+'  ·  '+self.office.auto_time())
    def start_analysis(self):
        q=self.input.text().strip()
        if not q or self.thread is not None: return
        self.button.setEnabled(False); self.progress.show(); self.dialogue.setHtml('<div style="color:#bca87e;padding:20px;">⚔ AI TRADING TEAM 회의 시작...<br><br>각자 독립 분석 중입니다.</div>'); self.status.setText('⚔️ AI TRADING TEAM 회의 진행 중...')
        self.thread=QThread(self); self.worker=AnalysisWorker(q); self.worker.moveToThread(self.thread); self.thread.started.connect(self.worker.run); self.worker.output.connect(self.on_output); self.worker.failed.connect(self.on_failed); self.worker.finished.connect(self.on_finished); self.worker.finished.connect(self.thread.quit); self.worker.failed.connect(self.thread.quit); self.thread.finished.connect(self.cleanup_thread); self.thread.start()
    def on_output(self,text):
        self.raw.setPlainText(text); self.dialogue.set_meeting(text)
    def on_failed(self,text): self.dialogue.setHtml('<div style="color:#d58b82;padding:20px;"><b>❌ 분석 오류</b><br><br>'+text.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('\n','<br>')+'</div>'); self.status.setText('오류 발생 · 로그를 확인하세요')
    def on_finished(self): self.progress.hide(); self.button.setEnabled(True); self.status.setText('✅ 분석 완료 · AI 팀 회의록 표시 완료')
    def cleanup_thread(self):
        if self.worker: self.worker.deleteLater()
        if self.thread: self.thread.deleteLater()
        self.worker=None; self.thread=None


def main():
    app=QApplication(sys.argv); window=MainWindow(); window.show(); return app.exec()

if __name__=='__main__': sys.exit(main())
