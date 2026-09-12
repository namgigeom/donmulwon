from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from math import sin, pi

class PixelBackground:
    def __init__(self):
        self.time='밤'; self.weather='맑음'; self.phase=0; self.hour=0.0
    def set_time(self,v): self.time=v
    def set_weather(self,v): self.weather=v
    def set_clock(self,dt):
        self.hour=dt.hour+dt.minute/60.0+dt.second/3600.0
        self.phase=int(dt.timestamp())%120
    def tick(self): self.phase=(self.phase+1)%120
    def _sky_color(self):
        h=self.hour
        stops=[(0.0,(24,38,58)),(5.0,(38,51,67)),(6.0,(224,155,105)),(7.0,(157,194,202)),(11.0,(168,204,211)),(16.0,(169,205,211)),(18.0,(229,145,91)),(19.5,(111,83,103)),(21.0,(39,53,72)),(24.0,(24,38,58))]
        for i in range(len(stops)-1):
            a,ca=stops[i]; b,cb=stops[i+1]
            if a<=h<=b:
                t=(h-a)/(b-a)
                return tuple(int(ca[k]*(1-t)+cb[k]*t) for k in range(3))
        return stops[-1][1]
    def _tree(self,p,x,base,scale=1,night=False):
        s=int(scale); trunk='#3b2a20' if not night else '#241d1b'; leaf='#45684b' if not night else '#263d31'; leaf2='#5b8054' if not night else '#304a38'
        p.setBrush(QColor(trunk)); p.drawRect(x-3*s,base-28*s,6*s,28*s)
        p.setBrush(QColor(leaf))
        for dx,dy,w,h in [(-15,-40,30,14),(-22,-31,44,16),(-12,-51,25,15),(4,-35,25,13)]: p.drawRect(x+dx*s,base+dy*s,w*s,h*s)
        p.setBrush(QColor(leaf2))
        for dx,dy,w,h in [(-9,-46,12,8),(8,-30,13,8),(-20,-34,11,7)]: p.drawRect(x+dx*s,base+dy*s,w*s,h*s)
    def paint(self,p,w,h):
        p.setPen(Qt.NoPen); p.fillRect(0,0,w,h,QColor('#17181a'))
        p.setBrush(QColor('#806a50')); p.drawRect(18,18,w-36,205)
        wx,wy,ww,wh=112,34,w-150,166; sky=self._sky_color()
        p.setBrush(QColor(*sky)); p.drawRect(wx,wy,ww,wh)
        p.setBrush(QColor('#3a342e')); p.drawRect(wx-7,wy-7,ww+14,wh+14)
        p.setBrush(QColor(*sky)); p.drawRect(wx,wy,ww,wh)
        hnow=self.hour
        if 5.5<=hnow<=19.5:
            t=(hnow-5.5)/14.0; sx=wx+int(t*ww); sy=wy+wh-20-int(sin(pi*t)*105); r=9 if 6.5<hnow<18.5 else 7
            p.setBrush(QColor('#ffe0a0')); p.drawRect(sx-r,sy-r,2*r,2*r)
        if hnow>=18.5 or hnow<6.5:
            t=((hnow-18.5)%24)/12.0
            if t<=1.0:
                mx=wx+int(t*ww); my=wy+wh-18-int(sin(pi*t)*108)
                p.setBrush(QColor('#e7e2c9')); p.drawRect(mx-7,my-7,14,14); p.setBrush(QColor('#273548')); p.drawRect(mx+1,my-6,6,12)
        base=wy+wh; nightish=hnow<6.5 or hnow>=17.5
        for i in range(30):
            bw=18+(i%3)*7; bh=28+((i*37)%82); bx=wx+5+int(i*(ww-20)/30)
            p.setBrush(QColor('#27323d' if nightish else '#60747c')); p.drawRect(bx,base-bh,bw,bh)
            if nightish:
                p.setBrush(QColor('#d7c27c'))
                for yy in range(base-bh+9,base-5,14):
                    if (i+yy//14)%3: p.drawRect(bx+4,yy,4,4)
        # 창문 너머에 픽셀 나무를 추가해 사무실 바깥 풍경을 만든다.
        self._tree(p,wx+75,base-8,1,nightish); self._tree(p,wx+ww//2-35,base-6,2,nightish); self._tree(p,wx+ww-105,base-7,1,nightish); self._tree(p,wx+ww-25,base-4,2,nightish)
        p.setBrush(QColor('#273a2b' if nightish else '#6e8b62')); p.drawRect(wx,base-4,ww,4)
        p.setBrush(QColor('#8a7358'))
        for x in (wx+ww//4,wx+ww//2,wx+3*ww//4): p.drawRect(x,wy,5,wh)
        p.drawRect(wx,wy+wh-6,ww,6)
        p.setBrush(QColor('#5c4a39')); p.drawRect(18,223,w-36,h-241); p.setPen(QColor('#6d5742'))
        for x in range(28,w-20,72): p.drawLine(x,223,x,h-18)
        for y in range(255,h-10,52): p.drawLine(18,y,w-18,y)
        p.setPen(Qt.NoPen); p.setBrush(QColor('#251c17')); p.drawRect(27,274,72,148); p.setBrush(QColor('#765237')); p.drawRect(35,282,56,132); p.setBrush(QColor('#c8ae73')); p.drawRect(78,345,6,7)
        if self.weather=='비':
            p.setBrush(QColor('#bdcdd2'))
            for i in range(75): p.drawRect(wx+(i*67%ww),wy+(i*41+self.phase*4)%max(1,wh-8),2,8)
        elif self.weather=='눈':
            p.setBrush(QColor('#e1e4e2'))
            for i in range(48): p.drawRect(wx+(i*71%ww),wy+(i*47+self.phase*2)%max(1,wh-5),4,4)
