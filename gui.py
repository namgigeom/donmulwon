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
        super().__init__()
        self.background=PixelBackground()
        self.characters=CharacterLayer()
        self.motion=MotionController(self)
        self.setMinimumHeight(650)

    def set_weather(self,v): self.background.set_weather(v); self.update()
    def set_time(self,v): self.background.set_time(v); self.update()

    def paintEvent(self,event):
        p=QPainter(self)
        p.setRenderHint(QPainter.Antialiasing,False)
        try:
            w,h=self.width(),self.height()
            self.background.paint(p,w,h)
            self.draw_desks(p)
            self.draw_conference_area(p,w,h)
            self.characters.paint(p)
            p.setFont(QFont('Malgun Gothic',10,QFont.Bold)); p.setPen(QColor('#eee4d2'))
            for name,(x,y,_) in self.characters.POSITIONS.items():
                p.drawText(QRect(int(x-45),int(y+82),170,25),Qt.AlignCenter,str(name))
            self.draw_side_monitor(p,w)
        finally:
            if p.isActive(): p.end()

    def draw_desks(self,p):
        # Individual top-down workstations. Door is kept on the far-left wall.
        stations=[(80,270),(350,270),(620,270),(890,270)]
        for x,y in stations:
            p.setPen(QColor('#241b16')); p.setBrush(QColor('#34251d')); p.drawRect(x,y,190,82)
            p.setBrush(QColor('#705039')); p.drawRect(x+6,y+6,178,70)
            p.setBrush(QColor('#20272c')); p.drawRect(x+53,y+10,84,42)
            p.setBrush(QColor('#3c4649')); p.drawRect(x+61,y+17,68,27)
            p.setBrush(QColor('#4a3023')); p.drawRect(x+77,y+52,36,24)
        # Alfredo's isolated team-lead station.
        x,y=1180,255
        p.setPen(QColor('#241b16')); p.setBrush(QColor('#2e211a')); p.drawRect(x,y,245,112)
        p.setBrush(QColor('#795638')); p.drawRect(x+7,y+7,231,98)
        p.setBrush(QColor('#20272c')); p.drawRect(x+45,y+12,150,50)
        p.setBrush(QColor('#3c4649')); p.drawRect(x+54,y+19,132,35)
        p.setBrush(QColor('#4a3023')); p.drawRect(x+100,y+68,45,30)

    def draw_conference_area(self,p,w,h):
        # Dedicated team meeting zone beneath the individual desks.
        # Everything is drawn as hard-edged pixel blocks to keep the top-down style.
        cx=w//2
        table_w=min(760,w-520)
        table_x=cx-table_w//2
        table_y=415
        table_h=92

        # Floor mat / meeting-zone boundary.
        p.setPen(Qt.NoPen)
        p.setBrush(QColor('#493827'))
        p.drawRect(table_x-28,table_y-26,table_w+56,table_h+52)
        p.setBrush(QColor('#5b4430'))
        p.drawRect(table_x-20,table_y-18,table_w+40,table_h+36)

        # Conference table: thick dark edge + wood surface.
        p.setPen(QColor('#251b16'))
        p.setBrush(QColor('#241914'))
        p.drawRect(table_x,table_y,table_w,table_h)
        p.setBrush(QColor('#725238'))
        p.drawRect(table_x+8,table_y+8,table_w-16,table_h-16)
        p.setBrush(QColor('#876445'))
        p.drawRect(table_x+18,table_y+18,table_w-36,table_h-36)

        # Pixel seam and central document/table detail.
        p.setPen(QColor('#5b402d'))
        p.drawLine(table_x+20,table_y+table_h//2,table_x+table_w-20,table_y+table_h//2)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor('#30251e'))
        p.drawRect(cx-95,table_y+29,190,34)
        p.setBrush(QColor('#c7ad7b'))
        p.drawRect(cx-78,table_y+35,156,4)
        p.drawRect(cx-50,table_y+45,100,4)

        # Five seats around the meeting table, top-down.
        seat_xs=[table_x+55,table_x+190,table_x+table_w//2-28,table_x+table_w-220,table_x+table_w-85]
        p.setBrush(QColor('#292421'))
        for sx in seat_xs[:2]+seat_xs[3:]:
            p.drawRect(sx,table_y-13,54,13)
            p.drawRect(sx,table_y+table_h,54,13)
        # central head seats
        p.drawRect(cx-27,table_y-13,54,13)
        p.drawRect(cx-27,table_y+table_h,54,13)

        # Chart in the foreground: the team's shared market screen.
        chart_w=min(650,w-650)
        chart_x=cx-chart_w//2
        chart_y=530
        chart_h=max(86,min(125,h-chart_y-12))
        p.setPen(QColor('#241b16')); p.setBrush(QColor('#211d1a'))
        p.drawRect(chart_x,chart_y,chart_w,chart_h)
        p.setBrush(QColor('#302b26'))
        p.drawRect(chart_x+6,chart_y+6,chart_w-12,chart_h-12)

        p.setPen(QColor('#cdbb99')); p.setFont(QFont('Malgun Gothic',9,QFont.Bold))
        p.drawText(chart_x+16,chart_y+8,130,20,'TEAM MARKET CHART')
        p.setPen(QColor('#8c7659'))
        grid_top=chart_y+30; grid_bottom=chart_y+chart_h-16
        for i in range(1,4):
            yy=grid_top+i*(grid_bottom-grid_top)//4
            p.drawLine(chart_x+14,yy,chart_x+chart_w-14,yy)
        for i in range(1,7):
            xx=chart_x+14+i*(chart_w-28)//7
            p.drawLine(xx,grid_top,xx,grid_bottom)

        # Pixel candlestick-style line, deliberately compact and readable.
        values=[0.48,0.43,0.52,0.49,0.58,0.55,0.66,0.61,0.72,0.68,0.79,0.75,0.86]
        points=[]
        plot_w=chart_w-50; plot_h=grid_bottom-grid_top-8
        for i,v in enumerate(values):
            px=chart_x+25+int(i*plot_w/(len(values)-1))
            py=grid_bottom-int(v*plot_h)
            points.append((px,py))
        p.setPen(QColor('#b9a16d'))
        for a,b in zip(points,points[1:]): p.drawLine(a[0],a[1],b[0],b[1])
        p.setPen(Qt.NoPen); p.setBrush(QColor('#d6bd7e'))
        for px,py in points: p.drawRect(px-2,py-2,5,5)

    def draw_side_monitor(self,p,w):
        # Compact ticker monitor on the right wall.
        x=w-255; y=250; ww=215; hh=140
        p.setPen(QColor('#241b16')); p.setBrush(QColor('#292d2c')); p.drawRect(x,y,ww,hh)
        p.setPen(QColor('#e4d6b9')); p.setFont(QFont('Malgun Gothic',9,QFont.Bold))
        p.drawText(x+14,y+14,180,20,'MARKET MONITOR')
        p.setPen(QColor('#8b9c82'))
        pts=[(x+18,y+108),(x+38,y+97),(x+62,y+101),(x+84,y+77),(x+108,y+87),(x+130,y+53),(x+157,y+67),(x+190,y+37)]
        for a,b in zip(pts,pts[1:]): p.drawLine(a[0],a[1],b[0],b[1])
        p.setPen(QColor('#bda977')); p.drawText(x+14,y+117,180,18,'VOO   +0.8%    |    JOBY   +2.4%')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('돈물원 · DONMULWON')
        self.resize(1500,950)
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
