import time
from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QColor, QFont, QPolygon

class PixelCharacter:
    def __init__(self,name): self.name=name; self.frame=0
    def tick(self): self.frame=(self.frame+1)%60
    def paint(self,p,x,y,scale=2):
        x,y,s=int(x),int(y),int(scale); p.setPen(Qt.NoPen)
        if self.name=='현무': self._turtle(p,x,y,s)
        elif self.name=='김선달': self._crow(p,x,y,s)
        elif self.name=='이묵': self._snake(p,x,y,s)
        elif self.name=='너부리': self._raccoon(p,x,y,s)
        else: self._cat(p,x,y,s)
    def _px(self,p,x,y,w,h,c): p.setBrush(QColor(c)); p.drawRect(x,y,w,h)
    def _turtle(self,p,x,y,s):
        self._px(p,x+7*s,y+10*s,24*s,16*s,'#31513b'); self._px(p,x+10*s,y+7*s,18*s,4*s,'#58744a'); self._px(p,x+12*s,y+12*s,4*s,4*s,'#789560'); self._px(p,x+21*s,y+12*s,4*s,4*s,'#789560'); self._px(p,x+28*s,y+13*s,8*s,7*s,'#719261'); self._px(p,x+34*s,y+15*s,4*s,3*s,'#17201a')
        for rx,ry in ((5,10),(7,24),(26,24),(29,9)): self._px(p,x+rx*s,y+ry*s,6*s,6*s,'#64875a')
        self._px(p,x+12*s,y+26*s,16*s,5*s,'#243a2c'); self._px(p,x+36*s,y+14*s,2*s,2*s,'#eadb9a')
    def _crow(self,p,x,y,s):
        self._px(p,x+11*s,y+8*s,19*s,17*s,'#25272d'); self._px(p,x+15*s,y+4*s,12*s,10*s,'#17191f'); self._px(p,x+8*s,y+13*s,8*s,7*s,'#353941'); self._px(p,x+28*s,y+14*s,12*s,3*s,'#9a7745'); self._px(p,x+20*s,y+7*s,3*s,3*s,'#e2d79b'); self._px(p,x+14*s,y+20*s,12*s,8*s,'#121419'); self._px(p,x+15*s,y+27*s,3*s,8*s,'#b08a4e'); self._px(p,x+25*s,y+27*s,3*s,8*s,'#b08a4e'); self._px(p,x+12*s,y+33*s,7*s,2*s,'#b08a4e'); self._px(p,x+23*s,y+33*s,7*s,2*s,'#b08a4e')
    def _snake(self,p,x,y,s):
        self._px(p,x+8*s,y+25*s,24*s,6*s,'#456c3e'); self._px(p,x+25*s,y+18*s,7*s,10*s,'#567c43'); self._px(p,x+27*s,y+9*s,7*s,12*s,'#5f8748'); self._px(p,x+25*s,y+6*s,11*s,8*s,'#3d6338'); self._px(p,x+28*s,y+8*s,2*s,2*s,'#eee0a0'); self._px(p,x+34*s,y+8*s,2*s,2*s,'#eee0a0'); self._px(p,x+36*s,y+12*s,5*s,2*s,'#ad4d57'); self._px(p,x+11*s,y+29*s,7*s,4*s,'#6b8f50'); self._px(p,x+20*s,y+31*s,8*s,4*s,'#5b7f47')
    def _raccoon(self,p,x,y,s):
        self._px(p,x+9*s,y+10*s,20*s,17*s,'#8b8178'); self._px(p,x+12*s,y+5*s,6*s,7*s,'#9c9289'); self._px(p,x+23*s,y+5*s,6*s,7*s,'#9c9289'); self._px(p,x+8*s,y+13*s,22*s,6*s,'#4b4542'); self._px(p,x+13*s,y+14*s,3*s,3*s,'#e2d6a0'); self._px(p,x+22*s,y+14*s,3*s,3*s,'#e2d6a0'); self._px(p,x+28*s,y+22*s,13*s,6*s,'#6f665f'); self._px(p,x+36*s,y+22*s,5*s,3*s,'#3f3937'); self._px(p,x+31*s,y+28*s,5*s,3*s,'#3f3937'); self._px(p,x+12*s,y+27*s,5*s,6*s,'#5e5650'); self._px(p,x+23*s,y+27*s,5*s,6*s,'#5e5650')
    def _cat(self,p,x,y,s):
        self._px(p,x+10*s,y+9*s,20*s,18*s,'#25262b'); self._px(p,x+12*s,y+4*s,6*s,7*s,'#202126'); self._px(p,x+23*s,y+4*s,6*s,7*s,'#202126'); self._px(p,x+14*s,y+12*s,3*s,3*s,'#d9c66f'); self._px(p,x+23*s,y+12*s,3*s,3*s,'#d9c66f'); self._px(p,x+30*s,y+22*s,12*s,4*s,'#25262b'); self._px(p,x+38*s,y+18*s,5*s,5*s,'#25262b'); self._px(p,x+18*s,y+27*s,5*s,8*s,'#17181c'); self._px(p,x+22*s,y+27*s,2*s,8*s,'#b94e59')
        p.setPen(QColor('#d6bd74')); p.setBrush(Qt.NoBrush); p.drawRect(x+12*s,y+11*s,6*s,4*s); p.drawRect(x+22*s,y+11*s,6*s,4*s); p.drawLine(x+18*s,y+13*s,x+22*s,y+13*s); p.setPen(Qt.NoPen)

class CharacterLayer:
    DESKS={'현무':(55,245,145),'김선달':(335,245,145),'이묵':(615,245,145),'너부리':(895,245,145),'알프레도':(1175,245,145)}
    POSITIONS={n:(x+w//2-42,300) for n,(x,y,w) in DESKS.items()}
    MEETING_POSITIONS={'현무':(430,345),'김선달':(555,345),'이묵':(680,345),'너부리':(805,345),'알프레도':(930,345)}
    DOOR=(55.0,470.0)
    def __init__(self):
        self.characters={n:PixelCharacter(n) for n in self.POSITIONS}; self.pos={n:(float(x),float(y)) for n,(x,y) in self.POSITIONS.items()}; self.active={n:True for n in self.POSITIONS}; self.mode='idle'; self.queue=[]; self.move_speed=42; self.bubbles={}; self.bubble_until={}; self.stage='idle'; self.office_open=9<=time.localtime().tm_hour<18
        if not self.office_open: self.reset_off_hours()
    def set_office_hours(self,hour,immediate=False):
        open_now=9<=hour<18
        if open_now==self.office_open:
            if immediate and self.mode not in ('meeting_arrival','meeting','verdict'): self.reset_office() if open_now else self.reset_off_hours()
            return
        self.office_open=open_now; self.reset_office() if open_now else self.reset_off_hours()
    def reset_office(self):
        self.mode='idle'; self.stage='idle'; self.queue=[]; self.clear_bubbles()
        for n,(x,y) in self.POSITIONS.items(): self.active[n]=True; self.pos[n]=(float(x),float(y))
    def reset_off_hours(self):
        self.mode='off_hours'; self.stage='idle'; self.queue=[]; self.clear_bubbles()
        for n in self.POSITIONS: self.active[n]=False; self.pos[n]=self.DOOR
    def summon_for_question(self,overtime=False):
        self.mode='meeting_arrival'; self.stage='summon'; self.queue=list(self.POSITIONS); self.clear_bubbles(); self.move_speed=42
        for n in self.POSITIONS: self.active[n]=True; self.pos[n]=self.DOOR
        self.set_bubble('알프레도','긴급 호출이다. 전원 회의실로!',4500)
    def set_meeting_stage(self,stage):
        if stage=='summon': self.summon_for_question()
        elif stage=='meeting':
            self.mode='meeting'; self.stage='meeting'; self.queue=[]
            for n,(x,y) in self.MEETING_POSITIONS.items(): self.active[n]=True; self.pos[n]=(float(x),float(y))
        elif stage=='verdict': self.show_final_verdict()
        elif stage=='return': self.reset_office() if self.office_open else self.reset_off_hours()
    def set_bubble(self,name,text,duration_ms=9000):
        if name not in self.POSITIONS: return
        text=' '.join(str(text).split()).strip()
        if text: self.bubbles[name]=text[:260]; self.bubble_until[name]=time.time()+duration_ms/1000
    def set_meeting_log(self,log):
        import re
        found=False
        for name in ('현무','김선달','이묵','너부리'):
            pats=[rf'{name}[^\n]*[:：]\s*(.+)',rf'###\s*.*{name}.*\n(.+?)(?=\n###|\Z)']
            for pat in pats:
                m=list(re.finditer(pat,str(log),re.S))
                if m:
                    text=m[-1].group(1).strip().split('\n')[0]; self.set_bubble(name,text,12000); found=True; break
        return found
    def show_final_verdict(self,error=False):
        self.mode='verdict'; self.stage='verdict'; self.clear_bubbles(); self.set_bubble('알프레도','분석완료! 회의완료! 최종 판단을 정리하겠습니다.',9000)
    def clear_bubbles(self): self.bubbles={}; self.bubble_until={}
    def tick(self):
        now=time.time()
        for c in self.characters.values(): c.tick()
        for n,t in list(self.bubble_until.items()):
            if now>t: self.bubble_until.pop(n,None); self.bubbles.pop(n,None)
        if self.mode=='meeting_arrival':
            remaining=[]
            for n in self.queue:
                tx,ty=self.MEETING_POSITIONS[n]; x,y=self.pos[n]; dx,dy=tx-x,ty-y; d=(dx*dx+dy*dy)**0.5
                if d<=self.move_speed: self.pos[n]=(float(tx),float(ty))
                else: self.pos[n]=(x+dx/d*self.move_speed,y+dy/d*self.move_speed); remaining.append(n)
            self.queue=remaining
            if not self.queue:
                self.mode='meeting'; self.stage='meeting'
                self.set_bubble('현무','시장부터 보겠습니다. 거시환경이 지금 어느 방향인지 확인해야 합니다.',9000)
                self.set_bubble('김선달','숫자만 보면 안 됩니다. 실적하고 최근 뉴스부터 짚고 가죠.',9000)
                self.set_bubble('이묵','잠깐. 차트는 다른 이야기를 하고 있습니다. 추세부터 보시죠.',9000)
                self.set_bubble('너부리','좋습니다. 그런데 이걸 지금 계좌 비중에 넣어도 되는지도 봐야 합니다.',9000)
    def paint(self,p):
        for n in self.POSITIONS:
            if self.active[n]: self.characters[n].paint(p,self.pos[n][0],self.pos[n][1],2)
        for n,text in list(self.bubbles.items()):
            if self.active.get(n,False): self._bubble(p,n,text,self.pos[n][0],self.pos[n][1])
    def _bubble(self,p,name,text,x,y):
        # Four lines maximum, with a generous reading time.
        chunks=[]; cur=''
        for ch in str(text).replace('\n',' '):
            cur+=ch
            if len(cur)>=18: chunks.append(cur); cur=''
        if cur: chunks.append(cur)
        lines=chunks[:5] or ['...']; bw=max(210,min(330,max(len(v) for v in lines)*9+34)); bh=20+len(lines)*20; bx=int(x+30); by=int(y-bh-22)
        if bx+bw>1490: bx=int(x-bw+10)
        if bx<10: bx=10
        if by<8: by=8
        p.setPen(QColor('#9b8968')); p.setBrush(QColor('#f4ecda')); p.drawRoundedRect(bx,by,bw,bh,8,8); p.setBrush(QColor('#f4ecda')); p.drawPolygon(QPolygon([QPoint(int(x+12),by+bh),QPoint(int(x+29),by+bh),QPoint(int(x+21),by+bh+11)])); p.setPen(QColor('#211f1c')); p.setFont(QFont('Malgun Gothic',8,QFont.Bold)); p.drawText(QRect(bx+10,by+5,bw-20,bh-8),Qt.AlignLeft|Qt.AlignVCenter,'\n'.join(lines))
