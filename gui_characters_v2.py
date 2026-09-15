import time, re
from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QColor, QFont, QPolygon

class PixelCharacter:
    # Detailed vector silhouettes rendered with crisp edges. No sprite-sheet cropping.
    COLORS={
        '현무':('#17251d','#294b35','#4d7650','#829966','#b5bd82'),
        '김선달':('#11161a','#242c32','#3b474e','#69757a','#b2aa91'),
        '이묵':('#202d1e','#385832','#56783f','#83a255','#b6bd78'),
        '너부리':('#303130','#555552','#74736e','#a29e95','#d1c7b6'),
        '알프레도':('#504a47','#8b807a','#afa39b','#d3c7b9','#eee3d0')}
    def __init__(self,name): self.name=name; self.frame=0
    def tick(self): self.frame=(self.frame+1)%60
    def rect(self,p,x,y,w,h,c): p.setPen(Qt.NoPen); p.setBrush(QColor(c)); p.drawRect(int(x),int(y),int(w),int(h))
    def ell(self,p,x,y,w,h,c): p.setPen(Qt.NoPen); p.setBrush(QColor(c)); p.drawEllipse(int(x),int(y),int(w),int(h))
    def poly(self,p,pts,c): p.setPen(Qt.NoPen); p.setBrush(QColor(c)); p.drawPolygon(QPolygon([QPoint(int(x),int(y)) for x,y in pts]))
    def line(self,p,a,b,c,width=2): p.setPen(QColor(c)); p.setBrush(Qt.NoBrush); p.drawLine(QPoint(int(a[0]),int(a[1])),QPoint(int(b[0]),int(b[1]))); p.setPen(Qt.NoPen)
    def paint(self,p,x,y,scale=2.25):
        s=scale
        if self.name=='현무': self.turtle(p,x,y,s)
        elif self.name=='김선달': self.crow(p,x,y,s)
        elif self.name=='이묵': self.snake(p,x,y,s)
        elif self.name=='너부리': self.raccoon(p,x,y,s)
        else: self.cat(p,x,y,s)
    def turtle(self,p,x,y,s):
        a,b,c,d,e=self.COLORS['현무']
        self.poly(p,[(x+12*s,y+42*s),(x+2*s,y+36*s),(x+7*s,y+48*s)],b)
        for xx in (15,30,45,53): self.ell(p,x+xx*s,y+36*s,13*s,10*s,c)
        self.ell(p,x+7*s,y+8*s,55*s,39*s,e); self.ell(p,x+10*s,y+10*s,49*s,35*s,a); self.ell(p,x+14*s,y+12*s,41*s,31*s,b)
        self.ell(p,x+20*s,y+16*s,29*s,23*s,c)
        self.line(p,(x+34*s,y+13*s),(x+34*s,y+42*s),a,2); self.line(p,(x+15*s,y+27*s),(x+54*s,y+27*s),a,2)
        self.line(p,(x+23*s,y+15*s),(x+20*s,y+25*s),a,2); self.line(p,(x+45*s,y+15*s),(x+49*s,y+25*s),a,2)
        self.ell(p,x+54*s,y+15*s,20*s,19*s,c); self.ell(p,x+58*s,y+18*s,12*s,12*s,d); self.ell(p,x+65*s,y+20*s,3*s,3*s,e)
        self.rect(p,x+68*s,y+24*s,6*s,2*s,e)
        self.rect(p,x+17*s,y+43*s,10*s,4*s,d); self.rect(p,x+43*s,y+43*s,10*s,4*s,d)
    def crow(self,p,x,y,s):
        a,b,c,d,e=self.COLORS['김선달']
        self.poly(p,[(x+31*s,y+38*s),(x+8*s,y+58*s),(x+39*s,y+50*s),(x+54*s,y+43*s)],a)
        self.ell(p,x+14*s,y+17*s,45*s,39*s,e); self.ell(p,x+18*s,y+20*s,38*s,33*s,a)
        self.poly(p,[(x+25*s,y+23*s),(x+5*s,y+36*s),(x+13*s,y+51*s),(x+39*s,y+45*s)],b)
        for i in range(4): self.line(p,(x+(11+i*6)*s,y+(43-i*2)*s),(x+(29+i*4)*s,y+(28+i*2)*s),c,2)
        self.ell(p,x+25*s,y+3*s,31*s,29*s,a); self.ell(p,x+29*s,y+6*s,24*s,22*s,b)
        self.poly(p,[(x+49*s,y+12*s),(x+75*s,y+17*s),(x+49*s,y+21*s)],e)
        self.ell(p,x+45*s,y+10*s,6*s,6*s,d); self.ell(p,x+47*s,y+12*s,2*s,2*s,e)
        self.line(p,(x+28*s,y+51*s),(x+25*s,y+66*s),c,3); self.line(p,(x+45*s,y+50*s),(x+48*s,y+66*s),c,3)
        for xx in (25,48): self.line(p,(x+xx*s,y+66*s),(x+(xx-8)*s,y+69*s),c,2); self.line(p,(x+xx*s,y+66*s),(x+(xx+3)*s,y+69*s),c,2)
    def snake(self,p,x,y,s):
        a,b,c,d,e=self.COLORS['이묵']
        self.ell(p,x+3*s,y+31*s,61*s,27*s,e); self.ell(p,x+7*s,y+29*s,53*s,23*s,a)
        self.poly(p,[(x+8*s,y+42*s),(x+20*s,y+51*s),(x+46*s,y+49*s),(x+58*s,y+39*s),(x+52*s,y+51*s),(x+20*s,y+56*s)],b)
        for xx in (14,26,38,50): self.rect(p,x+xx*s,y+38*s,5*s,3*s,d)
        self.rect(p,x+43*s,y+10*s,13*s,31*s,a); self.rect(p,x+47*s,y+7*s,10*s,30*s,b)
        self.ell(p,x+43*s,y+2*s,24*s,18*s,b); self.ell(p,x+47*s,y+5*s,17*s,13*s,a)
        self.ell(p,x+52*s,y+7*s,4*s,4*s,d); self.ell(p,x+61*s,y+7*s,4*s,4*s,d); self.ell(p,x+53*s,y+8*s,2*s,2*s,e); self.ell(p,x+62*s,y+8*s,2*s,2*s,e)
        self.line(p,(x+58*s,y+14*s),(x+70*s,y+15*s),e,2); self.line(p,(x+69*s,y+15*s),(x+74*s,y+13*s),e,1)
        for yy in (24,29,34):
            for xx in (46,54): self.rect(p,x+xx*s,y+yy*s,4*s,2*s,c)
    def raccoon(self,p,x,y,s):
        a,b,c,d,e=self.COLORS['너부리']
        self.ell(p,x+42*s,y+31*s,34*s,17*s,a); self.rect(p,x+55*s,y+34*s,9*s,10*s,e); self.rect(p,x+66*s,y+36*s,7*s,8*s,c)
        self.ell(p,x+15*s,y+27*s,42*s,40*s,a); self.ell(p,x+20*s,y+31*s,32*s,33*s,b)
        self.poly(p,[(x+16*s,y+21*s),(x+18*s,y+3*s),(x+31*s,y+18*s)],a); self.poly(p,[(x+39*s,y+18*s),(x+52*s,y+3*s),(x+54*s,y+22*s)],a)
        self.poly(p,[(x+20*s,y+15*s),(x+22*s,y+9*s),(x+27*s,y+16*s)],d); self.poly(p,[(x+43*s,y+16*s),(x+50*s,y+9*s),(x+50*s,y+17*s)],d)
        self.ell(p,x+13*s,y+12*s,44*s,36*s,c)
        self.poly(p,[(x+14*s,y+24*s),(x+25*s,y+18*s),(x+35*s,y+22*s),(x+45*s,y+18*s),(x+57*s,y+24*s),(x+48*s,y+36*s),(x+35*s,y+32*s),(x+23*s,y+36*s)],e)
        self.ell(p,x+22*s,y+23*s,8*s,7*s,d); self.ell(p,x+41*s,y+23*s,8*s,7*s,d); self.ell(p,x+25*s,y+25*s,3*s,3*s,e); self.ell(p,x+44*s,y+25*s,3*s,3*s,e); self.ell(p,x+31*s,y+29*s,8*s,6*s,e)
        self.ell(p,x+17*s,y+57*s,12*s,9*s,c); self.ell(p,x+43*s,y+57*s,12*s,9*s,c)
    def cat(self,p,x,y,s):
        a,b,c,d,e=self.COLORS['알프레도']
        self.line(p,(x+48*s,y+45*s),(x+71*s,y+34*s),a,7); self.line(p,(x+69*s,y+34*s),(x+76*s,y+39*s),a,6)
        self.ell(p,x+17*s,y+27*s,41*s,41*s,a); self.ell(p,x+22*s,y+31*s,31*s,33*s,b)
        self.poly(p,[(x+17*s,y+21*s),(x+19*s,y+2*s),(x+31*s,y+17*s)],a); self.poly(p,[(x+39*s,y+17*s),(x+52*s,y+2*s),(x+54*s,y+22*s)],a)
        self.poly(p,[(x+21*s,y+15*s),(x+22*s,y+8*s),(x+28*s,y+15*s)],d); self.poly(p,[(x+42*s,y+15*s),(x+50*s,y+8*s),(x+50*s,y+16*s)],d)
        self.ell(p,x+14*s,y+11*s,43*s,36*s,b)
        self.ell(p,x+23*s,y+21*s,8*s,8*s,e); self.ell(p,x+42*s,y+21*s,8*s,8*s,e); self.ell(p,x+26*s,y+23*s,3*s,3*s,a); self.ell(p,x+45*s,y+23*s,3*s,3*s,a)
        self.ell(p,x+32*s,y+29*s,8*s,6*s,a); self.line(p,(x+36*s,y+34*s),(x+36*s,y+38*s),a,2)
        self.line(p,(x+35*s,y+37*s),(x+28*s,y+36*s),a,1); self.line(p,(x+37*s,y+37*s),(x+44*s,y+36*s),a,1)
        self.ell(p,x+27*s,y+42*s,19*s,24*s,c); self.ell(p,x+18*s,y+57*s,13*s,10*s,b); self.ell(p,x+44*s,y+57*s,13*s,10*s,b)
        # Alfredo only: subtle glasses + tie, keeping a cat body.
        self.line(p,(x+22*s,y+20*s),(x+32*s,y+20*s),d,2); self.line(p,(x+40*s,y+20*s),(x+50*s,y+20*s),d,2)
        self.poly(p,[(x+33*s,y+40*s),(x+39*s,y+40*s),(x+36*s,y+55*s)],e); self.rect(p,x+31*s,y+40*s,10*s,3*d if False else 3*s,d)

class CharacterLayer:
    # These are the original prototype station coordinates, retained exactly.
    DESKS={'현무':(55,244,145),'김선달':(335,244,145),'이묵':(615,244,145),'너부리':(895,244,145),'알프레도':(1175,244,145)}
    POSITIONS={n:(x+45,296) for n,(x,y,w) in DESKS.items()}
    MEETING_POSITIONS={'현무':(400,335),'김선달':(515,335),'이묵':(630,335),'너부리':(745,335),'알프레도':(860,335)}
    DOOR=(42.0,410.0)
    def __init__(self):
        self.characters={n:PixelCharacter(n) for n in self.POSITIONS}; self.pos={n:(float(x),float(y)) for n,(x,y) in self.POSITIONS.items()}; self.active={n:True for n in self.POSITIONS}; self.mode='idle'; self.stage='idle'; self.queue=[]; self.move_speed=180.0; self.bubbles={}; self.bubble_until={}; self.office_open=9<=time.localtime().tm_hour<18
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
    def start_arrival(self):
        self.mode='arrival';self.stage='arrival';self.queue=list(self.POSITIONS);self.clear_bubbles()
        for n in self.POSITIONS:self.active[n]=True;self.pos[n]=self.DOOR
    def start_departure(self): self.mode='leaving';self.stage='leaving';self.queue=list(self.POSITIONS)
    def summon_for_question(self,overtime=False):
        self.mode='meeting_arrival';self.stage='summon';self.queue=list(self.POSITIONS);self.clear_bubbles()
        for n in self.POSITIONS:self.active[n]=True;self.pos[n]=self.DOOR
    def begin_meeting(self):
        self.mode='meeting';self.stage='meeting';self.queue=[]
        for n,(x,y) in self.MEETING_POSITIONS.items():self.active[n]=True;self.pos[n]=(float(x),float(y))
    def set_meeting_stage(self,stage):
        if stage=='summon':self.summon_for_question()
        elif stage=='meeting':self.begin_meeting()
        elif stage=='verdict':self.show_final_verdict()
        elif stage=='return':self.reset_office() if self.office_open else self.reset_off_hours()
    def set_bubble(self,name,text,duration_ms=20000):
        text=' '.join(str(text).split()).strip()
        if name in self.POSITIONS and text:self.bubbles[name]=text[:420];self.bubble_until[name]=time.time()+duration_ms/1000.0
    def set_meeting_log(self,log):
        txt=str(log); found=False
        for name in ('현무','김선달','이묵','너부리'):
            hits=[]
            for pat in [rf'###\s*\*?[^\n]*{re.escape(name)}[^\n]*\n(.+?)(?=\n###|\Z)',rf'{re.escape(name)}\s*[:：]\s*(.+)']:
                hits += list(re.finditer(pat,txt,re.S))
            if hits:
                block=hits[-1].group(1).strip(); lines=[v.strip(' -*') for v in block.splitlines() if v.strip()]
                line=next((v for v in lines if len(v)>12),lines[0] if lines else '')
                if line:self.set_bubble(name,line,24000);found=True
        return found
    def show_final_verdict(self,error=False):
        self.mode='verdict';self.stage='verdict';self.clear_bubbles();self.set_bubble('알프레도','분석완료! 회의완료! 최종 판단을 정리했습니다.',12000)
    def clear_bubbles(self):self.bubbles={};self.bubble_until={}
    def tick(self):
        now=time.time()
        for c in self.characters.values():c.tick()
        for n,t in list(self.bubble_until.items()):
            if now>t:self.bubble_until.pop(n,None);self.bubbles.pop(n,None)
        if self.mode in ('arrival','meeting_arrival'):
            remaining=[]
            for n in self.queue:
                tx,ty=self.MEETING_POSITIONS[n] if self.mode=='meeting_arrival' else self.POSITIONS[n];x,y=self.pos[n];dx,dy=tx-x,ty-y;d=(dx*dx+dy*dy)**0.5
                if d<=self.move_speed:self.pos[n]=(float(tx),float(ty))
                else:self.pos[n]=(x+dx/d*self.move_speed,y+dy/d*self.move_speed);remaining.append(n)
            self.queue=remaining
            if not remaining:
                if self.mode=='meeting_arrival':self.begin_meeting()
                else:self.mode='idle';self.stage='idle'
        elif self.mode=='leaving':
            remaining=[]
            for n in self.queue:
                tx,ty=self.DOOR;x,y=self.pos[n];dx,dy=tx-x,ty-y;d=(dx*dx+dy*dy)**0.5
                if d<=self.move_speed:self.pos[n]=(float(tx),float(ty));self.active[n]=False
                else:self.pos[n]=(x+dx/d*self.move_speed,y+dy/d*self.move_speed);remaining.append(n)
            self.queue=remaining
    def paint(self,p):
        for n in self.POSITIONS:
            if self.active[n]:self.characters[n].paint(p,self.pos[n][0],self.pos[n][1],2.25)
        for n,text in list(self.bubbles.items()):
            if self.active.get(n,False):self._bubble(p,n,text,self.pos[n][0],self.pos[n][1])
    def _bubble(self,p,name,text,x,y):
        words=str(text).replace('\n',' ').split();lines=[];cur=''
        for word in words:
            nxt=(cur+' '+word).strip()
            if len(nxt)>25 and cur:lines.append(cur);cur=word
            else:cur=nxt
        if cur:lines.append(cur)
        lines=lines[:8] or ['...']; bw=max(240,min(410,max(26,max(map(len,lines)))*8+32));bh=18+len(lines)*17;bx=int(x+45);by=int(y-bh-18)
        if bx+bw>1490:bx=int(x-bw+15)
        if bx<8:bx=8
        if by<8:by=8
        p.setPen(QColor('#8f7c5d'));p.setBrush(QColor('#f4ecda'));p.drawRoundedRect(bx,by,bw,bh,9,9);tailx=int(x+20 if bx>x else x+48);p.drawPolygon(QPolygon([QPoint(tailx,by+bh),QPoint(tailx+15,by+bh),QPoint(tailx+7,by+bh+10)]));p.setPen(QColor('#25221e'));p.setFont(QFont('Malgun Gothic',8,QFont.Bold));p.drawText(QRect(bx+10,by+5,bw-20,bh-8),Qt.AlignLeft|Qt.AlignVCenter,'\n'.join(lines))
