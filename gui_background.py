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
    def _lerp(self,a,b,t):
        return tuple(int(a[i]*(1-t)+b[i]*t) for i in range(3))
    def _sky_color(self):
        h=self.hour
        stops=[(0.0,(20,28,48)),(4.0,(27,34,55)),(5.0,(62,48,67)),(6.0,(224,145,91)),(7.0,(155,191,202)),(9.0,(177,211,218)),(12.0,(181,218,225)),(16.0,(168,204,214)),(17.0,(231,161,96)),(18.5,(224,119,86)),(20.0,(103,70,91)),(21.0,(42,49,72)),(24.0,(20,28,48))]
        for i in range(len(stops)-1):
            a,ca=stops[i]; b,cb=stops[i+1]
            if a<=h<=b:
                return self._lerp(ca,cb,(h-a)/(b-a))
        return stops[-1][1]
    def _tree(self,p,x,base,scale=1,night=False,evening=False):
        s=int(scale); trunk='#3b2a20' if not night else '#241d1b'
        leaf='#45684b' if not night else ('#304535' if evening else '#263d31')
        leaf2='#5b8054' if not night else ('#405a3e' if evening else '#304a38')
        p.setBrush(QColor(trunk)); p.drawRect(x-3*s,base-28*s,6*s,28*s)
        p.setBrush(QColor(leaf))
        for dx,dy,w,h in [(-15,-40,30,14),(-22,-31,44,16),(-12,-51,25,15),(4,-35,25,13)]: p.drawRect(x+dx*s,base+dy*s,w*s,h*s)
        p.setBrush(QColor(leaf2))
        for dx,dy,w,h in [(-9,-46,12,8),(8,-30,13,8),(-20,-34,11,7)]: p.drawRect(x+dx*s,base+dy*s,w*s,h*s)
    def _phase(self):
        h=self.hour
        if 5<=h<8: return '아침'
        if 8<=h<17: return '낮'
        if 17<=h<21: return '저녁'
        return '밤'
    def paint(self,p,w,h):
        p.setPen(Qt.NoPen); p.fillRect(0,0,w,h,QColor('#17181a'))
        p.setBrush(QColor('#806a50')); p.drawRect(18,18,w-36,205)
        wx,wy,ww,wh=112,34,w-150,166; sky=self._sky_color(); phase=self._phase()
        # 유리창 안쪽 하늘: 실제 PC 시간에 맞춰 아침/낮/저녁/밤이 연속적으로 변한다.
        p.setBrush(QColor(*sky)); p.drawRect(wx,wy,ww,wh)
        p.setBrush(QColor('#3a342e')); p.drawRect(wx-7,wy-7,ww+14,wh+14)
        p.setBrush(QColor(*sky)); p.drawRect(wx,wy,ww,wh)
        hnow=self.hour
        if phase in ('아침','낮','저녁'):
            start,end=(5,17) if phase=='아침' else ((8,17) if phase=='낮' else (17,21))
            t=max(0,min(1,(hnow-start)/(end-start)))
            sx=wx+int(t*ww); sy=wy+wh-20-int(sin(pi*max(0,min(1,t)))*105)
            r=9 if phase=='낮' else 7
            p.setBrush(QColor('#ffe0a0' if phase!='저녁' else '#ffb36b')); p.drawRect(sx-r,sy-r,2*r,2*r)
        if phase=='밤' or phase=='아침':
            # 새벽/밤에는 달이 남아 있고, 아침으로 넘어가며 희미해진다.
            if phase=='밤': t=((hnow-20)%24)/12.0
            else: t=(hnow-5)/3.0
            mx=wx+int(max(0,min(1,t))*ww); my=wy+wh-18-int(sin(pi*max(0,min(1,t)))*108)
            p.setBrush(QColor('#e7e2c9')); p.drawRect(mx-7,my-7,14,14); p.setBrush(QColor(*sky)); p.drawRect(mx+1,my-6,6,12)
        base=wy+wh
        nightish=phase=='밤'; evening=phase=='저녁'
        # 도시 실루엣과 창문 불빛도 시간대별로 바뀐다.
        for i in range(30):
            bw=18+(i%3)*7; bh=28+((i*37)%82); bx=wx+5+int(i*(ww-20)/30)
            if phase=='낮': building='#60747c'
            elif phase=='아침': building='#667a80'
            elif phase=='저녁': building='#46545e'
            else: building='#27323d'
            p.setBrush(QColor(building)); p.drawRect(bx,base-bh,bw,bh)
            if phase in ('저녁','밤'):
                p.setBrush(QColor('#d7c27c' if phase=='밤' else '#cfae68'))
                density=2 if phase=='저녁' else 1
                for yy in range(base-bh+9,base-5,14):
                    if (i+yy//14)%3 < density: p.drawRect(bx+4,yy,4,4)
        # 아침/낮에는 녹색, 저녁/밤에는 어두운 실루엣으로 나무가 변한다.
        self._tree(p,wx+75,base-8,1,nightish,evening)
        self._tree(p,wx+ww//2-35,base-6,2,nightish,evening)
        self._tree(p,wx+ww-105,base-7,1,nightish,evening)
        self._tree(p,wx+ww-25,base-4,2,nightish,evening)
        p.setBrush(QColor('#273a2b' if nightish else ('#4e5f45' if evening else '#6e8b62'))); p.drawRect(wx,base-4,ww,4)
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
