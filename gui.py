import os, sys, io, contextlib, traceback, html, time, re, json
from datetime import datetime
from math import sin
from PySide6.QtCore import QObject, QThread, Signal, Slot, Qt, QRect, QTimer
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextBrowser, QProgressBar, QComboBox

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path: sys.path.insert(0,BASE_DIR)
from gui_background import PixelBackground
from gui_characters_v2 import CharacterLayer

class AnalysisWorker(QObject):
    output=Signal(str); failed=Signal(str); finished=Signal()
    def __init__(self,question): super().__init__(); self.question=question
    @Slot()
    def run(self):
        try:
            import main
            class LiveStream(io.StringIO):
                def __init__(self, emit):
                    super().__init__()
                    self.emit = emit
                def write(self, s):
                    if s:
                        super().write(s)
                        self.emit(s.rstrip())
                    return len(s)
                def flush(self):
                    pass

            live = LiveStream(self.output.emit)
            with contextlib.redirect_stdout(live), contextlib.redirect_stderr(live):
                result=main.run_analysis(self.question)
            log=live.getvalue().strip()
            answer=''
            if isinstance(result,dict): answer=str(result.get('alfredo','') or result.get('final','') or '').strip()
            else: answer=str(result or '').strip()
            if not answer: answer='알프레도의 최종 판단이 생성되지 않았습니다.'
            self.output.emit('[FINAL_RESULT]\n'+answer+'\n\n[MEETING_LOG]\n'+log[-16000:])
        except Exception:
            self.failed.emit(traceback.format_exc())
        finally:
            self.finished.emit()

class ResultPanel(QTextBrowser):
    def __init__(self):
        super().__init__(); self.setReadOnly(True); self.setMinimumHeight(190)
        self.setStyleSheet('QTextBrowser{background:#141719;border:1px solid #65543e;padding:10px;color:#eee4d2;}')
    def show_result(self,text):
        raw=text.split('[MEETING_LOG]')[0].strip() or '최종 분석 결과가 없습니다.'
        safe=html.escape(raw).replace('\n','<br>')
        self.setHtml('<div style="font-family:Malgun Gothic;color:#eee4d2;font-size:10pt"><div style="color:#c8a866;font-size:12pt;font-weight:700;margin-bottom:8px">🐱 알프레도 · ANALYSIS RESULT</div><div style="background:#29231b;border:1px solid #9b7c4c;padding:12px;border-radius:7px">'+safe+'</div></div>')
    def show_waiting(self): self.setHtml('<div style="color:#8f877b;padding:18px">회의가 끝나면 알프레도의 최종 검증 결과가 이곳에 정리됩니다.</div>')

class MeetingLogPanel(QTextBrowser):
    def __init__(self):
        super().__init__(); self.setReadOnly(True); self.setFixedHeight(82)
        self.setStyleSheet('QTextBrowser{background:#111517;border:1px solid #3f3930;padding:8px;color:#bfb6a6;}')
    def set_status(self,title,detail):
        self.setHtml(f'<div style="font-family:Malgun Gothic;color:#eee4d2"><b>{html.escape(title)}</b><br><span style="color:#a49a8b">{html.escape(detail)}</span></div>')

class PixelOffice(QWidget):
    # Five compact stations. The old 175px desks made the office look like one long counter.
    DESKS=[('현무',55,244,145),('김선달',335,244,145),('이묵',615,244,145),('너부리',895,244,145),('알프레도',1175,244,145)]
    ROLE={'김선달':'FUNDAMENTALS + NEWS','이묵':'TECHNICAL','너부리':'PORTFOLIO','현무':'MACRO','알프레도':'FINAL VERIFIER'}
    PORTFOLIO=[]
    def __init__(self): super().__init__(); self.background=PixelBackground(); self.characters=CharacterLayer(); self.setMinimumHeight(560); self.active_ticker='MARKET'; self.market_rows=[]; self.refresh_portfolio()
    def refresh_portfolio(self):
        path=os.path.join(BASE_DIR,"ai_portfolio.json")
        try:
            with open(path,"r",encoding="utf-8") as f:
                data=json.load(f)
            stocks=data.get("stocks",[])
            portfolio=[]
            for stock in stocks:
                symbol=str(stock.get("symbol","?"))
                weight=float(stock.get("portfolio_weight",0) or 0)*100
                value=float(stock.get("market_value",0) or 0)
                portfolio.append((symbol,f"{weight:.1f}%",f"${value:,.2f}"))
            self.PORTFOLIO=portfolio[:10]
            self.market_rows=[(str(s.get('symbol','?')), str(s.get('change_percent',s.get('change','-')))) for s in stocks[:10]]
        except Exception:
            self.PORTFOLIO=[]
        self.update()
    def set_weather(self,v): self.background.set_weather(v); self.update()
    def auto_time(self):
        now=datetime.now(); self.background.set_clock(now); h=self.background.hour; self.characters.set_office_hours(h,immediate=True)
        return '아침' if 5<=h<11 else '낮' if 11<=h<17 else '저녁' if 17<=h<21 else '밤'
    @staticmethod
    def rect(p,x,y,w,h,c): p.setPen(Qt.NoPen); p.setBrush(QColor(c)); p.drawRect(int(x),int(y),int(w),int(h))
    @staticmethod
    def text(p,x,y,w,h,v,size=8,c='#eee4d2',align=Qt.AlignLeft|Qt.AlignVCenter): p.setPen(QColor(c)); p.setFont(QFont('Malgun Gothic',size,QFont.Bold)); p.drawText(QRect(int(x),int(y),int(w),int(h)),align,str(v))
    def paintEvent(self,e):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing,False)
        try:
            w,h=self.width(),self.height(); self.background.paint(p,w,h); self.draw_room(p,w,h); self.draw_window(p,w); self.draw_furniture(p,w,h); self.draw_desks(p); self.draw_market(p,w); self.draw_account(p,w); self.characters.paint(p)
        finally:
            if p.isActive(): p.end()
    def draw_room(self,p,w,h):
        self.rect(p,18,18,w-36,28,'#3b2b22'); self.rect(p,18,46,w-36,6,'#80664c'); self.rect(p,18,52,w-36,172,'#765d46'); self.rect(p,18,224,w-36,h-242,'#55483d'); p.setPen(QColor('#655448'))
        for x in range(28,w-20,54): p.drawLine(x,224,x,h-18)
        for y in range(254,h-12,44): p.drawLine(18,y,w-18,y)
        self.rect(p,34,58,82,120,'#3b2e27'); self.rect(p,40,64,70,108,'#514036'); self.text(p,44,68,62,16,'NOTICE',7,'#d0bb83',Qt.AlignCenter)
        for i,t in enumerate(['AI TEAM','MARKET','RULES','MEETING']): self.text(p,46,92+i*19,58,15,t,6,'#9e9481',Qt.AlignCenter)
        self.rect(p,32,h-116,88,84,'#241c19'); self.rect(p,38,h-109,76,77,'#60432f'); self.rect(p,45,h-102,62,68,'#2b2b2c'); self.rect(p,98,h-67,5,5,'#d0ae65'); self.rect(p,42,h-126,68,16,'#28362d'); self.text(p,45,h-125,62,15,'EXIT',8,'#c9d2b4',Qt.AlignCenter)
    def tree(self,p,x,base,s,phase):
        leaf={'아침':'#587b55','낮':'#466f4a','저녁':'#4b5541','밤':'#26382d'}[phase]; leaf2={'아침':'#73956a','낮':'#5b8054','저녁':'#60664b','밤':'#304a38'}[phase]; self.rect(p,x-3*s,base-28*s,6*s,28*s,'#3c2b20')
        for dx,dy,ww,hh in [(-17,-40,34,15),(-24,-31,48,17),(-12,-51,28,16),(3,-35,26,14)]: self.rect(p,x+dx*s,base+dy*s,ww*s,hh*s,leaf)
        self.rect(p,x-8*s,base-45*s,13*s,8*s,leaf2)
    def draw_window(self,p,w):
        x,y,ww,wh=145,60,max(540,w-620),125; hour=self.background.hour; phase='아침' if 5<=hour<8 else '낮' if 8<=hour<17 else '저녁' if 17<=hour<21 else '밤'; sky={'아침':'#b97972','낮':'#a8ced8','저녁':'#c67869','밤':'#101a2d'}[phase]; horizon={'아침':'#d6a36f','낮':'#c5c9a4','저녁':'#80566a','밤':'#252c42'}[phase]
        self.rect(p,x-8,y-8,ww+16,wh+16,'#2b211c'); self.rect(p,x,y,ww,wh,sky); self.rect(p,x+5,y+5,ww-10,wh-10,horizon); self.text(p,x+16,y+8,250,18,'OUTSIDE VIEW · '+phase,7,'#e6d39d')
        if phase!='밤':
            start,end=(5,8) if phase=='아침' else ((8,17) if phase=='낮' else (17,21)); t=max(0,min(1,(hour-start)/(end-start))); sx=x+int(t*ww); sy=y+25+int((1-sin(3.14159*t))*42); self.rect(p,sx-7,sy-7,14,14,'#ffe0a0' if phase!='저녁' else '#ff9f68')
        else:
            t=(hour-21)/8 if hour>=21 else (hour+3)/8; mx=x+int(max(0,min(1,t))*ww); my=y+30; self.rect(p,mx-7,my-7,14,14,'#e7e2c9'); self.rect(p,mx+1,my-6,6,12,sky)
            for i in range(16): self.rect(p,x+15+(i*83%max(20,ww-30)),y+15+(i*37%65),2,2,'#ddd8b5')
        base=y+wh-12
        for i in range(18):
            bw=22+(i%4)*8; bh=25+((i*17)%55); bx=x+10+i*int((ww-20)/18); building={'아침':'#596d72','낮':'#708287','저녁':'#46505b','밤':'#252f3c'}[phase]; self.rect(p,bx,base-bh,bw,bh,building)
            if phase in ('저녁','밤'):
                light='#d2b36f' if phase=='저녁' else '#e0c47c'
                for yy in range(base-bh+10,base-5,16):
                    if (i+yy//16)%3:self.rect(p,bx+5,yy,4,4,light)
        for tx,sc in [(x+90,1),(x+ww//2,2),(x+ww-90,1)]: self.tree(p,tx,base+2,sc,phase)
        self.rect(p,x,base-4,ww,4,{'아침':'#61704e','낮':'#6e8b62','저녁':'#4b4d3b','밤':'#263a2b'}[phase]); p.setPen(QColor('#4b4034')); p.setBrush(Qt.NoBrush); p.drawRect(x,y,ww,wh)
        for xx in [x+ww//3,x+2*ww//3]: p.drawRect(xx,y,5,wh)
    def draw_furniture(self,p,w,h):
        x=w//2-125; y=h-175; self.rect(p,x-8,y-8,266,86,'#34271f'); self.rect(p,x,y,250,70,'#7a5337'); self.rect(p,x+8,y+8,234,54,'#63442f'); self.text(p,x+12,y+7,226,17,'AI TEAM · MEETING TABLE',7,'#e0c98e',Qt.AlignCenter); self.text(p,x+15,y+30,220,20,'DISCUSS · DISAGREE · VERIFY',6,'#a99d8c',Qt.AlignCenter)
        for cx,cy in [(x-28,y+22),(x+246,y+22),(x+42,y+77),(x+176,y+77)]: self.rect(p,cx,cy,28,22,'#382a23'); self.rect(p,cx+4,cy+4,20,14,'#67472f')
        sx=w-210; sy=h-145; self.rect(p,sx,sy,145,100,'#34261f'); self.rect(p,sx+8,sy+8,129,84,'#65462f')
        for i,t in enumerate(['RESEARCH','REPORTS','HISTORY']): self.rect(p,sx+15,sy+16+i*22,114,15,'#3a2b24'); self.text(p,sx+19,sy+16+i*22,106,15,t,6,'#c7b27d',Qt.AlignCenter)
    def draw_desks(self,p):
        for name,x,y,dw in self.DESKS:
            self.rect(p,x+8,y+61,dw-16,10,'#30241e'); self.rect(p,x-4,y-4,dw+8,61,'#34261f'); self.rect(p,x,y,dw,52,'#775236'); self.rect(p,x+5,y+5,dw-10,42,'#89603e')
            mx=x+dw//2-35; self.rect(p,mx,y+7,70,30,'#171b1e'); self.rect(p,mx+4,y+10,62,22,'#182b30'); self.rect(p,mx+26,y+37,18,6,'#1a1c1f'); self.rect(p,mx+16,y+43,38,4,'#302b27')
            pts=[(mx+7,y+27),(mx+16,y+23),(mx+25,y+25),(mx+34,y+18),(mx+45,y+22),(mx+54,y+13),(mx+63,y+19)]; p.setPen(QColor('#d4bb76'))
            for a,b in zip(pts,pts[1:]): p.drawLine(*a,*b)
            p.setPen(Qt.NoPen); self.rect(p,x+10,y+12,20,3,'#a0744d'); self.rect(p,x+dw-34,y+12,24,3,'#5e3f2c'); self.rect(p,x+dw//2-28,y+43,56,5,'#303033'); self.rect(p,x+dw-25,y+40,10,8,'#4e6652'); self.rect(p,x+8,y+40,54,9,'#3a2b23'); self.text(p,x+9,y+43,58,11,name,6,'#e1cb91',Qt.AlignCenter); self.text(p,x,y+72,dw,17,self.ROLE[name],5,'#9f927d',Qt.AlignCenter)
    def draw_account(self,p,w):
        x=w-205; y=55; ww=175; hh=175
        self.rect(p,x,y,ww,hh,'#252a2c'); self.rect(p,x+5,y+5,ww-10,hh-10,'#172024')
        self.text(p,x+10,y+7,155,16,'ACCOUNT',7,'#d8c48e')
        self.text(p,x+10,y+23,155,12,'LIVE HOLDINGS · WEIGHT',4,'#8fa69a')
        yy=y+40
        for t,wt,val in self.PORTFOLIO[:10]:
            self.text(p,x+8,yy,42,12,t,4,'#eee4d2')
            self.text(p,x+52,yy,42,12,wt,4,'#cdb985',Qt.AlignRight)
            self.text(p,x+96,yy,70,12,val,4,'#aebbb2',Qt.AlignRight)
            yy+=13

    def draw_market(self,p,w):
        # 10종목까지 표시하되 책상 영역(y=244)과 겹치지 않는 높이로 고정
        y=55; ww=175; hh=175; account_x=w-205; x=account_x-10-ww
        self.rect(p,x,y,ww,hh,'#252a2c'); self.rect(p,x+5,y+5,ww-10,hh-10,'#172024')
        self.text(p,x+10,y+7,155,16,'MARKET BOARD',7,'#d8c48e')
        self.text(p,x+10,y+23,155,12,'LIVE MARKET',4,'#8fa69a')
        rows=self.market_rows[:10] if hasattr(self,'market_rows') else []
        yy=y+40
        for ticker,change in rows:
            self.text(p,x+8,yy,70,12,ticker,4,'#eee4d2')
            self.text(p,x+80,yy,82,12,change,4,'#cdb985',Qt.AlignRight)
            yy+=13

    def set_ticker(self,t): self.active_ticker=t or 'MARKET'; self.update()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle('돈물원 · DONMULWON'); self.resize(1500,980); self.setMinimumSize(1180,820)
        self.setStyleSheet('QMainWindow{background:#101315;color:#ded7c5;} QLabel{color:#ded7c5;} QLineEdit,QTextBrowser,QComboBox{background:#1d2225;color:#eee4d2;border:1px solid #51483b;padding:7px;} QPushButton{background:#665039;color:#fff2d4;padding:8px 16px;border:1px solid #8a6c4c;} QProgressBar{border:1px solid #51483b;background:#202428;} QProgressBar::chunk{background:#806544;}')
        root=QWidget(); layout=QVBoxLayout(root); layout.setContentsMargins(14,10,14,10); layout.setSpacing(8)
        top=QHBoxLayout(); title=QLabel('🏦 DONMULWON · PIXEL TRADING OFFICE'); title.setStyleSheet('font-size:21px;font-weight:700;'); top.addWidget(title); top.addStretch(); self.clock=QLabel(); top.addWidget(self.clock); layout.addLayout(top)
        self.office=PixelOffice(); layout.addWidget(self.office,1)
        controls=QHBoxLayout(); self.input=QLineEdit(); self.input.setPlaceholderText('예: JOBY 지금 사도 괜찮아? / 내 계좌 전체적으로 봐줘'); self.button=QPushButton('분석 시작'); self.button.clicked.connect(self.start_analysis); self.input.returnPressed.connect(self.start_analysis); self.weather=QComboBox(); self.weather.addItems(['맑음','비','눈']); self.weather.currentTextChanged.connect(self.office.set_weather); controls.addWidget(self.input,1); controls.addWidget(self.weather); controls.addWidget(self.button); layout.addLayout(controls)
        self.status=QLabel('대기 중 · 실제 시각 기준 사무실 상태 유지'); layout.addWidget(self.status)
        self.progress=QProgressBar(); self.progress.setRange(0,100); self.progress.setValue(0); self.progress.hide(); layout.addWidget(self.progress)
        self.meeting=MeetingLogPanel(); self.meeting.set_status('대기 중','분석을 시작하면 전원이 출입문에서 회의실로 이동합니다.'); layout.addWidget(self.meeting)
        self.team_status=QTextBrowser(); self.team_status.setReadOnly(True); self.team_status.setFixedHeight(64); self.team_status.setStyleSheet('QTextBrowser{background:#111517;border:1px solid #3f3930;padding:7px;color:#bfb6a6;}'); layout.addWidget(self.team_status)
        self._reset_team_status()
        self.result=ResultPanel(); self.result.show_waiting(); layout.addWidget(self.result)
        self.setCentralWidget(root); self.thread=None; self.worker=None; self.meeting_started_at=0.0
        self.timer=QTimer(self); self.timer.timeout.connect(self.update_clock); self.timer.timeout.connect(self.animate); self.timer.start(250); self.update_clock()

    def _reset_team_status(self):
        self.team_states={'현무':'대기중','김선달':'대기중','이묵':'대기중','너부리':'대기중','알프레도':'대기중'}
        self._render_team_status()

    def _render_team_status(self):
        icons={'현무':'🐢','김선달':'🐦','이묵':'🐍','너부리':'🦝','알프레도':'🐱'}
        roles=['현무','김선달','이묵','너부리','알프레도']
        cells=[]
        for name in roles:
            cells.append(
                f'<td style="width:20%;text-align:center;padding:7px 3px;'
                f'border-right:1px solid #3f3930"><b>{icons[name]} {name}</b>'
                f'<br><span style="color:#c8a866;font-size:10pt">{html.escape(self.team_states[name])}</span></td>'
            )
        self.team_status.setHtml(
            '<table width="100%" cellspacing="0" cellpadding="0" style="font-family:Malgun Gothic;">'
            '<tr>'+''.join(cells)+'</tr></table>'
        )

    def _set_team_state(self,name,state):
        if name in self.team_states:
            self.team_states[name]=state
            self._render_team_status()

    def animate(self): self.office.characters.tick(); self.office.update()
    def update_clock(self):
        now=datetime.now(); period=self.office.auto_time(); self.clock.setText(now.strftime('%Y-%m-%d  %H:%M:%S')+' · '+period); self.office.update()
        if self.thread is not None:
            elapsed=int(time.time()-self.meeting_started_at); self.status.setText(f'⚔️ AI TRADING TEAM 회의 진행 중 · {elapsed}초 경과')

    def start_analysis(self):
        q=self.input.text().strip()
        if not q or self.thread is not None: return
        self.meeting_started_at=time.time(); self.office.characters.summon_for_question(overtime=True); self.office.update()
        self.button.setEnabled(False); self.progress.show(); self.progress.setRange(0,100); self.progress.setValue(5)
        self._reset_team_status(); self.meeting.set_status('⚔ AI TRADING TEAM 회의 시작','긴급 호출 · 전원이 출입문으로 출근하는 중...')
        self.result.show_waiting(); self.status.setText('⚔️ AI TRADING TEAM 회의 진행 중...')
        self.thread=QThread(self); self.worker=AnalysisWorker(q); self.worker.moveToThread(self.thread); self.thread.started.connect(self.worker.run); self.worker.output.connect(self.on_output); self.worker.failed.connect(self.on_failed); self.worker.finished.connect(self.thread.quit); self.worker.finished.connect(self.worker.deleteLater); self.thread.finished.connect(self.thread.deleteLater); self.thread.finished.connect(self.analysis_done); self.thread.start()

    def on_output(self,text):
        self.office.refresh_portfolio()
        if '[FINAL_RESULT]' in text:
            final=text.split('[FINAL_RESULT]',1)[1]
            answer=final.split('[MEETING_LOG]',1)[0].strip()
            log=final.split('[MEETING_LOG]',1)[1] if '[MEETING_LOG]' in final else ''
            self.progress.setValue(100)
            for name in ['현무','김선달','이묵','너부리','알프레도']: self._set_team_state(name,'회의중')
            self._set_team_state('알프레도','회의중')
            self.meeting.set_status('🐱 알프레도 · 분석완료! 회의완료!','최종 검증이 끝났습니다. 아래에 최종 판단을 정리했습니다.')
            self.office.characters.set_meeting_log(log[-16000:])
            self.office.characters.set_meeting_stage('verdict')
            self._show_result_after_verdict(answer)
        else:
            clean=text.strip()
            if clean:
                line=clean.splitlines()[-1].strip()
                stage='회의 진행 중'
                detail=line
                role_map={'🐦 김선달':'🐦 김선달','🐍 이묵':'🐍 이묵','🦝 너부리':'🦝 너부리','🐢 현무':'🐢 현무'}
                for key,label in role_map.items():
                    if key in line:
                        if '데이터 수집 시작' in line: stage=f'{label} · 데이터 수집 중'
                        elif '데이터 수집 완료' in line: stage=f'{label} · AI 분석 준비'
                        elif 'AI 분석 요청 시작' in line: stage=f'{label} · AI 분석 중...'
                        elif 'AI 분석 응답 수신' in line: stage=f'{label} · 분석 정리 중'
                        elif '통합 분석 완료' in line: stage=f'{label} · 통합 분석 완료'
                        else: stage=f'{label} · 작업 중...'
                        break
                if 'OpenRouter' in line: stage='🌐 OpenRouter · 응답 대기 중'
                elif 'Gemini' in line: stage='🤖 Gemini · 응답 대기 중'
                elif '알프레도' in line: stage='🐱 알프레도 · 최종 검증 중'
                self.status.setText(f'⚔️ {stage}')
                self.meeting.set_status(f'⚔️ AI TRADING TEAM · {stage}',detail[-220:])
                for role,label in role_map.items():
                    if role in line:
                        name=label.split(' ',1)[1]
                        if '통합 분석 완료' in line: self._set_team_state(name,'분석완료')
                        elif '데이터 수집' in line: self._set_team_state(name,'자료조사중')
                        elif 'AI 분석' in line: self._set_team_state(name,'분석중')
                        else: self._set_team_state(name,'작업중')
                self.progress.setValue(min(95, max(8, self.progress.value()+1)))
        self.office.update()

    def _show_result_after_verdict(self,text):
        self.progress.setValue(100); self.result.show_result(text); self.meeting.set_status('🐱 알프레도 · 분석완료! 회의완료!','최종 검증이 끝났습니다. 아래에 최종 판단을 정리했습니다.'); self.office.characters.show_final_verdict(); self.office.update()

    def on_failed(self,err):
        self.progress.setValue(100); self.meeting.set_status('❌ 분석 실패','오류가 발생했습니다. 상세 내용은 아래 최종 결과 영역에서 확인할 수 있습니다.'); self.result.show_result('분석 실패\n\n'+err); self.office.characters.show_final_verdict(error=True); self.office.update()

    def analysis_done(self):
        self.thread=None; self.worker=None; self.button.setEnabled(True); self.progress.hide(); self.status.setText('분석 완료 · 현재 시각 기준 사무실 상태 유지')

if __name__=='__main__':
    app=QApplication(sys.argv); win=MainWindow(); win.show(); sys.exit(app.exec())
