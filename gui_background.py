from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

class PixelBackground:
    def __init__(self): self.time='밤'; self.weather='맑음'; self.phase=0
    def set_time(self,v): self.time=v
    def set_weather(self,v): self.weather=v
    def tick(self): self.phase=(self.phase+1)%120
    def paint(self,p,w,h):
        p.setPen(Qt.NoPen); p.fillRect(0,0,w,h,QColor('#17181a'))
        p.setBrush(QColor('#806a50')); p.drawRect(18,18,w-36,205)
        wx,wy,ww,wh=112,34,w-150,166
        sky={'아침':'#aac5c5','낮':'#a8ccd3','저녁':'#746d7b','밤':'#273548'}.get(self.time,'#273548')
        p.setBrush(QColor('#3a342e')); p.drawRect(wx-7,wy-7,ww+14,wh+14)
        p.setBrush(QColor(sky)); p.drawRect(wx,wy,ww,wh)
        base=wy+wh
        for i in range(30):
            bw=18+(i%3)*7; bh=28+((i*37)%82); bx=wx+5+int(i*(ww-20)/30)
            p.setBrush(QColor('#27323d' if self.time!='낮' else '#60747c')); p.drawRect(bx,base-bh,bw,bh)
            if self.time in ('저녁','밤'):
                p.setBrush(QColor('#d7c27c'))
                for yy in range(base-bh+9,base-5,14):
                    if (i+yy//14)%3: p.drawRect(bx+4,yy,4,4)
        p.setBrush(QColor('#8a7358'))
        for x in (wx+ww//4,wx+ww//2,wx+3*ww//4): p.drawRect(x,wy,5,wh)
        p.drawRect(wx,wy+wh-6,ww,6)
        p.setBrush(QColor('#5c4a39')); p.drawRect(18,223,w-36,h-241)
        p.setPen(QColor('#6d5742'))
        for x in range(28,w-20,72): p.drawLine(x,223,x,h-18)
        for y in range(255,h-10,52): p.drawLine(18,y,w-18,y)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor('#251c17')); p.drawRect(27,274,72,148)
        p.setBrush(QColor('#765237')); p.drawRect(35,282,56,132)
        p.setBrush(QColor('#c8ae73')); p.drawRect(78,345,6,7)
        if self.weather=='비':
            p.setBrush(QColor('#bdcdd2'))
            for i in range(75): p.drawRect(wx+(i*67%ww),wy+(i*41+self.phase*4)%max(1,wh-8),2,8)
        elif self.weather=='눈':
            p.setBrush(QColor('#e1e4e2'))
            for i in range(48): p.drawRect(wx+(i*71%ww),wy+(i*47+self.phase*2)%max(1,wh-5),4,4)
