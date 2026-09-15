import os, time, re
from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QColor, QFont, QPolygon, QImage

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
ASSET_DIR=os.path.join(BASE_DIR,'assets','office_animals')
os.makedirs(ASSET_DIR,exist_ok=True)

# Character art is deliberately drawn as complete pixel silhouettes instead of
# cropping arbitrary sprite-sheet tiles. This prevents heads/bodies being cut.
class PixelCharacter:
    def __init__(self,name): self.name=name; self.frame=0
    def tick(self): self.frame=(self.frame+1)%60
    def r(self,p,x,y,w,h,c): p.setPen(Qt.NoPen); p.setBrush(QColor(c)); p.drawRect(int(x),int(y),int(w),int(h))
    def paint(self,p,x,y,scale=3):
        s=scale; x=int(x); y=int(y)
        if self.name=='현무': self.turtle(p,x,y,s)
        elif self.name=='김선달': self.crow(p,x,y,s)
        elif self.name=='이묵': self.snake(p,x,y,s)
        elif self.name=='너부리': self.raccoon(p,x,y,s)
        else: self.cat(p,x,y,s)
    def turtle(self,p,x,y,s):
        # complete turtle: shell, head, four feet and tail
        self.r(p,x+14*s,y+7*s,34*s,20*s,'#31533c'); self.r(p,x+10*s,y+12*s,42*s,13*s,'#466d4d')
        self.r(p,x+17*s,y+5*s,8*s,5*s,'#587f58'); self.r(p,x+28*s,y+8*s,9*s,5*s,'#284534'); self.r(p,x+18*s,y+15*s,9*s,4*s,'#284534'); self.r(p,x+31*s,y+15*s,9*s,4*s,'#284534')
        self.r(p,x+45*s,y+10*s,11*s,12*s,'#6d8758'); self.r(p,x+53*s,y+12*s,5*s,5*s,'#8da06c'); self.r(p,x+56*s,y+11*s,2*s,2*s,'#171b18')
        self.r(p,x+12*s,y+25*s,9*s,6*s,'#5e7d56'); self.r(p,x+39*s,y+25*s,9*s,6*s,'#5e7d56'); self.r(p,x+24*s,y+27*s,7*s,6*s,'#5e7d56'); self.r(p,x+46*s,y+27*s,7*s,6*s,'#5e7d56')
        self.r(p,x+7*s,y+18*s,6*s,4*s,'#5e7d56'); self.r(p,x+5*s,y+20*s,4*s,3*s,'#5e7d56')
    def crow(self,p,x,y,s):
        # complete crow silhouette with head, beak, wings, legs and tail
        c='#252a30'; hi='#3c454c';
        self.r(p,x+18*s,y+5*s,18*s,14*s,c); self.r(p,x+12*s,y+11*s,31*s,25*s,c); self.r(p,x+8*s,y+22*s,39*s,15*s,c)
        self.r(p,x+2*s,y+20*s,12*s,5*s,c); self.r(p,x+0*s,y+21*s,8*s,3*s,'#15181b')
        self.r(p,x+27*s,y+2*s,5*s,5*s,hi); self.r(p,x+35*s,y+12*s,9*s,3*s,'#111416'); self.r(p,x+42*s,y+14*s,10*s,3*s,'#171a1d')
        self.r(p,x+16*s,y+27*s,17*s,5*s,hi); self.r(p,x+19*s,y+36*s,3*s,13*s,'#1a1d20'); self.r(p,x+32*s,y+35*s,3*s,14*s,'#1a1d20'); self.r(p,x+17*s,y+48*s,9*s,2*s,'#17191b'); self.r(p,x+30*s,y+48*s,9*s,2*s,'#17191b')
        self.r(p,x+8*s,y+36*s,9*s,13*s,c); self.r(p,x+39*s,y+34*s,12*s,14*s,c)
    def snake(self,p,x,y,s):
        c='#526f3e'; hi='#7f9950'; dark='#30462d'
        # full coiled body plus raised head
        self.r(p,x+8*s,y+28*s,42*s,8*s,c); self.r(p,x+15*s,y+35*s,34*s,8*s,c); self.r(p,x+8*s,y+40*s,39*s,7*s,c)
        self.r(p,x+37*s,y+8*s,11*s,29*s,c); self.r(p,x+42*s,y+4*s,13*s,13*s,c); self.r(p,x+52*s,y+9*s,8*s,5*s,dark); self.r(p,x+55*s,y+7*s,3*s,3*s,'#d4c77a'); self.r(p,x+57*s,y+8*s,2*s,2*s,'#171a16')
        for dx,dy in [(14,31),(26,37),(36,31),(20,42)]: self.r(p,x+dx*s,y+dy*s,5*s,3*s,hi)
        self.r(p,x+4*s,y+46*s,22*s,3*s,dark)
    def raccoon(self,p,x,y,s):
        c='#6b6a68'; dark='#35383a'; light='#aaa69b'
        self.r(p,x+12*s,y+9*s,34*s,27*s,c); self.r(p,x+17*s,y+4*s,9*s,8*s,c); self.r(p,x+35*s,y+4*s,9*s,8*s,c); self.r(p,x+5*s,y+17*s,13*s,18*s,c); self.r(p,x+43*s,y+17*s,13*s,18*s,c)
        self.r(p,x+14*s,y+14*s,31*s,13*s,dark); self.r(p,x+19*s,y+16*s,7*s,6*s,light); self.r(p,x+34*s,y+16*s,7*s,6*s,light); self.r(p,x+22*s,y+18*s,4*s,4*s,'#171819'); self.r(p,x+35*s,y+18*s,4*s,4*s,'#171819'); self.r(p,x+28*s,y+24*s,7*s,4*s,'#222324')
        self.r(p,x+12*s,y+31*s,34*s,14*s,c); self.r(p,x+17*s,y+42*s,7*s,8*s,dark); self.r(p,x+36*s,y+42*s,7*s,8*s,dark); self.r(p,x+48*s,y+37*s,19*s,7*s,c); self.r(p,x+59*s,y+38*s,10*s,4*s,dark); self.r(p,x+64*s,y+42*s,7*s,3*s,light)
    def cat(self,p,x,y,s):
        c='#b0a39a'; dark='#5d5753'; light='#d4c7b8'
        self.r(p,x+12*s,y+7*s,34*s,28*s,c); self.r(p,x+15*s,y+2*s,10*s,10*s,c); self.r(p,x+34*s,y+2*s,10*s,10*s,c); self.r(p,x+16*s,y+15*s,28*s,12*s,light); self.r(p,x+20*s,y+17*s,5*s,5*s,dark); self.r(p,x+35*s,y+17*s,5*s,5*s,dark); self.r(p,x+27*s,y+23*s,7*s,4*s,'#7e6962'); self.r(p,x+25*s,y+31*s,24*s,20*s,c); self.r(p,x+18*s,y+45*s,7*s,12*s,dark); self.r(p,x+41*s,y+45*s,7*s,12*s,dark); self.r(p,x+47*s,y+34*s,23*s,7*s,c); self.r(p,x+63*s,y+38*s,12*s,5*s,dark)
        # Alfredo only: simple pixel tie + glasses
        self.r(p,x+29*s,y+33*s,7*s,14*s,'#403a36'); self.r(p,x+28*s,y+34*s,9*s,3*s,'#d0b06b'); self.r(p,x+18*s,y+15*s,8*s,2*s,'#d0b06b'); self.r(p,x+35*s,y+15*s,8*s,2*s,'#d0b06b')

class CharacterLayer:
    DESKS={'현무':(70,245,130),'김선달':(335,245,130),'이묵':(600,245,130),'너부리':(865,245,130),'알프레도':(1130,245,130)}
    POSITIONS={n:(x+w//2-75,300) for n,(x,y,w) in DESKS.items()}
    MEETING_POSITIONS={'현무':(410,355),'김선달':(525,355),'이묵':(640,355),'너부리':(755,355),'알프레도':(870,355)}
    DOOR=(48.0,430.0)
    def __init__(self):
        self.characters={n:PixelCharacter(n) for n in self.POSITIONS}; self.pos={n:(float(x),float(y)) for n,(x,y) in self.POSITIONS.items()}; self.active={n:True for n in self.POSITIONS}; self.mode='idle'; self.queue=[]; self.move_speed=180; self.bubbles={}; self.bubble_until={}; self.stage='idle'; self.office_open=9<=time.localtime().tm_hour<18
        if not self.office_open:self.reset_off_hours()
    def set_office_hours(self,hour,immediate=False):
        open_now=9<=hour<18
        if open_now==self.office_open:return
        self.office_open=open_now; self.reset_office() if open_now else self.reset_off_hours()
    def reset_office(self):
        self.mode='idle';self.stage='idle';self.queue=[];self.clear_bubbles()
        for n,(x,y) in self.POSITIONS.items():self.active[n]=True;self.pos[n]=(float(x),float(y))
    def reset_off_hours(self):
        self.mode='off_hours';self.stage='idle';self.queue=[];self.clear_bubbles()
        for n in self.POSITIONS:self.active[n]=False;self.pos[n]=self.DOOR
    def summon_for_question(self,overtime=False):
        self.mode='meeting_arrival';self.stage='summon';self.queue=list(self.POSITIONS);self.clear_bubbles();self.move_speed=180
        for n in self.POSITIONS:self.active[n]=True;self.pos[n]=self.DOOR
    def set_meeting_stage(self,stage):
        if stage=='summon':self.summon_for_question()
        elif stage=='meeting':
            self.mode='meeting';self.stage='meeting';self.queue=[]
            for n,(x,y) in self.MEETING_POSITIONS.items():self.active[n]=True;self.pos[n]=(float(x),float(y))
        elif stage=='verdict':self.show_final_verdict()
        elif stage=='return':self.reset_office() if self.office_open else self.reset_off_hours()
    def set_bubble(self,name,text,duration_ms=12000):
        text=' '.join(str(text).split()).strip()
        if name in self.POSITIONS and text:self.bubbles[name]=text[:300];self.bubble_until[name]=time.time()+duration_ms/1000
    def set_meeting_log(self,log):
        found=False
        for name in ('현무','김선달','이묵','너부리'):
            for pat in [rf'{re.escape(name)}[^\n]*[:：]\s*(.+)',rf'###\s*.*{re.escape(name)}.*\n(.+?)(?=\n###|\Z)']:
                m=list(re.finditer(pat,str(log),re.S))
                if m:self.set_bubble(name,m[-1].group(1).strip().split('\n')[0],20000);found=True;break
        return found
    def show_final_verdict(self,error=False):self.mode='verdict';self.stage='verdict';self.clear_bubbles();self.set_bubble('알프레도','분석완료! 회의완료! 최종 판단을 정리하겠습니다.',10000)
    def clear_bubbles(self):self.bubbles={};self.bubble_until={}
    def tick(self):
        now=time.time()
        for c in self.characters.values():c.tick()
        for n,t in list(self.bubble_until.items()):
            if now>t:self.bubble_until.pop(n,None);self.bubbles.pop(n,None)
        if self.mode=='meeting_arrival':
            remaining=[]
            for n in self.queue:
                tx,ty=self.MEETING_POSITIONS[n];x,y=self.pos[n];dx,dy=tx-x,ty-y;d=(dx*dx+dy*dy)**0.5
                if d<=self.move_speed:self.pos[n]=(float(tx),float(ty))
                else:self.pos[n]=(x+dx/d*self.move_speed,y+dy/d*self.move_speed);remaining.append(n)
            self.queue=remaining
            if not self.queue:
                self.mode='meeting';self.stage='meeting'
                self.set_bubble('현무','시장부터 보겠습니다. 거시환경이 지금 어느 방향인지 확인해야 합니다.',20000)
                self.set_bubble('김선달','숫자만 보면 안 됩니다. 실적하고 최근 뉴스부터 짚고 가죠.',20000)
                self.set_bubble('이묵','잠깐. 차트는 다른 이야기를 하고 있습니다. 추세부터 보시죠.',20000)
                self.set_bubble('너부리','좋습니다. 그런데 이걸 지금 계좌 비중에 넣어도 되는지도 봐야 합니다.',20000)
    def paint(self,p):
        for n in self.POSITIONS:
            if self.active[n]:self.characters[n].paint(p,self.pos[n][0],self.pos[n][1],3)
        for n,text in list(self.bubbles.items()):
            if self.active.get(n,False):self._bubble(p,n,text,self.pos[n][0],self.pos[n][1])
    def _bubble(self,p,name,text,x,y):
        chunks=[];cur=''
        for ch in str(text).replace('\n',' '):
            cur+=ch
            if len(cur)>=18:chunks.append(cur);cur=''
        if cur:chunks.append(cur)
        lines=chunks[:7] or ['...'];bw=max(240,min(390,max(len(v) for v in lines)*9+34));bh=24+len(lines)*19;bx,by=int(x+30),int(y-bh-18)
        if bx+bw>1490:bx=int(x-bw+10)
        if bx<10:bx=10
        if by<8:by=8
        p.setPen(QColor('#9b8968'));p.setBrush(QColor('#f4ecda'));p.drawRoundedRect(bx,by,bw,bh,8,8);p.drawPolygon(QPolygon([QPoint(int(x+12),by+bh),QPoint(int(x+29),by+bh),QPoint(int(x+21),by+bh+11)]));p.setPen(QColor('#211f1c'));p.setFont(QFont('Malgun Gothic',8,QFont.Bold));p.drawText(QRect(bx+10,by+6,bw-20,bh-10),Qt.AlignLeft|Qt.AlignVCenter,'\n'.join(lines))