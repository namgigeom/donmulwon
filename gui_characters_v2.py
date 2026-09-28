import time, re
from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QColor, QFont, QPolygon

# Cute rounded pixel-mascot characters.
# Original character design: oversized heads, tiny bodies, simple faces, office suits.
# Intentionally avoids copying any existing character design.

class PixelCharacter:
    """Cute original chibi pixel mascots for DONMULWON.

    Design direction:
    - oversized soft head
    - tiny rounded body
    - very simple dot eyes / tiny mouth
    - small ears, horns, beak, shell and tail per role
    - no suits: characters are the visual identity of the office
    """

    PALETTE = {
        '현무':     {'body':'#7f9f78','dark':'#3e5140','light':'#c9d8b8','cheek':'#e8a6a0','accent':'#6e8d68'},
        '김선달':   {'body':'#3b4145','dark':'#202427','light':'#727b80','cheek':'#d9908c','accent':'#d2b36f'},
        '이묵':     {'body':'#76a45f','dark':'#30452a','light':'#b8d393','cheek':'#e8a29c','accent':'#dfc477'},
        '너부리':   {'body':'#9b8f84','dark':'#514940','light':'#d7cabb','cheek':'#e7a09a','accent':'#a97e59'},
        '알프레도': {'body':'#d0b9a7','dark':'#5a4d47','light':'#f2dfcf','cheek':'#e6a29c','accent':'#b78b62'},
    }

    def __init__(self, name):
        self.name = name
        self.frame = 0

    def tick(self):
        self.frame = (self.frame + 1) % 60

    def rect(self,p,x,y,w,h,c,r=0):
        p.setPen(Qt.NoPen); p.setBrush(QColor(c))
        if r: p.drawRoundedRect(int(x),int(y),int(w),int(h),r,r)
        else: p.drawRect(int(x),int(y),int(w),int(h))

    def ell(self,p,x,y,w,h,c):
        p.setPen(Qt.NoPen); p.setBrush(QColor(c))
        p.drawEllipse(int(x),int(y),int(w),int(h))

    def poly(self,p,pts,c):
        p.setPen(Qt.NoPen); p.setBrush(QColor(c))
        p.drawPolygon(QPolygon([QPoint(int(x),int(y)) for x,y in pts]))

    def line(self,p,a,b,c,width=1):
        p.setPen(QColor(c)); p.setBrush(Qt.NoBrush)
        p.drawLine(QPoint(int(a[0]),int(a[1])),QPoint(int(b[0]),int(b[1])))
        p.setPen(Qt.NoPen)

    def face(self,p,x,y,s,q):
        dark=q['dark']; cheek=q['cheek']
        # tiny bean-like eyes
        self.ell(p,x+18*s,y+31*s,5*s,7*s,dark)
        self.ell(p,x+45*s,y+31*s,5*s,7*s,dark)
        # soft cheeks
        self.ell(p,x+10*s,y+43*s,9*s,5*s,cheek)
        self.ell(p,x+49*s,y+43*s,9*s,5*s,cheek)
        # tiny happy mouth
        self.line(p,(x+30*s,y+43*s),(x+33*s,y+45*s),dark,1)
        self.line(p,(x+33*s,y+45*s),(x+36*s,y+43*s),dark,1)

    def body(self,p,x,y,s,q):
        body,dark,light,accent=q['body'],q['dark'],q['light'],q['accent']
        # tiny bean body
        self.ell(p,x+17*s,y+65*s,39*s,31*s,dark)
        self.ell(p,x+20*s,y+63*s,33*s,29*s,body)
        # belly patch
        self.ell(p,x+27*s,y+72*s,19*s,14*s,light)
        # little arms
        self.ell(p,x+8*s,y+72*s,14*s,10*s,body)
        self.ell(p,x+53*s,y+72*s,14*s,10*s,body)
        # tiny feet
        self.ell(p,x+19*s,y+88*s,15*s,8*s,dark)
        self.ell(p,x+40*s,y+88*s,15*s,8*s,dark)

    def paint(self,p,x,y,scale=2.15):
        s=scale
        q=self.PALETTE[self.name]
        if self.name=='현무': self.turtle(p,x,y,s,q)
        elif self.name=='김선달': self.crow(p,x,y,s,q)
        elif self.name=='이묵': self.snake(p,x,y,s,q)
        elif self.name=='너부리': self.raccoon(p,x,y,s,q)
        else: self.cat(p,x,y,s,q)

    def turtle(self,p,x,y,s,q):
        body,dark,light=q['body'],q['dark'],q['light']
        # round shell behind head
        self.ell(p,x+5*s,y+38*s,60*s,42*s,dark)
        self.ell(p,x+9*s,y+39*s,52*s,34*s,body)
        self.ell(p,x+17*s,y+44*s,36*s,25*s,light)
        self.line(p,(x+35*s,y+44*s),(x+35*s,y+67*s),dark,1)
        self.line(p,(x+19*s,y+56*s),(x+51*s,y+56*s),dark,1)
        # huge soft head
        self.ell(p,x+8*s,y+10*s,62*s,58*s,dark)
        self.ell(p,x+12*s,y+13*s,54*s,52*s,body)
        self.ell(p,x+17*s,y+19*s,44*s,40*s,light)
        self.face(p,x+14*s,y+12*s,s,q)
        self.body(p,x+3*s,y+0,s,q)

    def crow(self,p,x,y,s,q):
        body,dark,light,accent=q['body'],q['dark'],q['light'],q['accent']
        # tiny feather tuft
        self.poly(p,[(x+28*s,y+13*s),(x+34*s,y+2*s),(x+39*s,y+14*s)],dark)
        # round head
        self.ell(p,x+5*s,y+11*s,62*s,57*s,dark)
        self.ell(p,x+10*s,y+15*s,52*s,48*s,body)
        self.ell(p,x+16*s,y+21*s,40*s,35*s,light)
        self.face(p,x+13*s,y+14*s,s,q)
        # tiny beak
        self.poly(p,[(x+58*s,y+36*s),(x+74*s,y+40*s),(x+58*s,y+44*s)],accent)
        self.body(p,x+2*s,y,s,q)

    def snake(self,p,x,y,s,q):
        body,dark,light,accent=q['body'],q['dark'],q['light'],q['accent']
        # curled little body
        self.ell(p,x+3*s,y+48*s,61*s,27*s,dark)
        self.ell(p,x+8*s,y+50*s,51*s,18*s,body)
        # upright round head
        self.ell(p,x+20*s,y+10*s,47*s,52*s,dark)
        self.ell(p,x+24*s,y+14*s,39*s,44*s,body)
        self.ell(p,x+29*s,y+20*s,29*s,31*s,light)
        self.face(p,x+26*s,y+13*s,s,q)
        # tiny tongue
        self.line(p,(x+62*s,y+40*s),(x+72*s,y+40*s),accent,1)
        self.line(p,(x+72*s,y+40*s),(x+76*s,y+37*s),accent,1)
        self.line(p,(x+72*s,y+40*s),(x+76*s,y+43*s),accent,1)
        self.body(p,x+1*s,y+4*s,s,q)

    def raccoon(self,p,x,y,s,q):
        body,dark,light=q['body'],q['dark'],q['light']
        # soft triangular ears
        self.poly(p,[(x+12*s,y+23*s),(x+13*s,y+4*s),(x+29*s,y+18*s)],dark)
        self.poly(p,[(x+42*s,y+18*s),(x+58*s,y+4*s),(x+59*s,y+23*s)],dark)
        self.poly(p,[(x+16*s,y+19*s),(x+16*s,y+10*s),(x+25*s,y+19*s)],light)
        self.poly(p,[(x+46*s,y+19*s),(x+56*s,y+10*s),(x+55*s,y+20*s)],light)
        # round head
        self.ell(p,x+7*s,y+12*s,61*s,57*s,dark)
        self.ell(p,x+12*s,y+17*s,51*s,48*s,body)
        self.ell(p,x+17*s,y+23*s,41*s,36*s,light)
        # simple mask
        self.ell(p,x+15*s,y+27*s,20*s,13*s,dark)
        self.ell(p,x+43*s,y+27*s,20*s,13*s,dark)
        self.ell(p,x+20*s,y+29*s,8*s,7*s,light)
        self.ell(p,x+48*s,y+29*s,8*s,7*s,light)
        self.face(p,x+13*s,y+14*s,s,q)
        self.body(p,x+2*s,y,s,q)
        # fluffy tail
        self.ell(p,x+58*s,y+67*s,27*s,19*s,dark)
        self.ell(p,x+64*s,y+66*s,23*s,14*s,body)

    def cat(self,p,x,y,s,q):
        body,dark,light=q['body'],q['dark'],q['light']
        # soft cat ears
        self.poly(p,[(x+11*s,y+24*s),(x+14*s,y+4*s),(x+30*s,y+19*s)],dark)
        self.poly(p,[(x+42*s,y+19*s),(x+58*s,y+4*s),(x+61*s,y+24*s)],dark)
        self.poly(p,[(x+15*s,y+20*s),(x+16*s,y+10*s),(x+25*s,y+20*s)],light)
        self.poly(p,[(x+47*s,y+20*s),(x+57*s,y+10*s),(x+57*s,y+20*s)],light)
        # huge fluffy head
        self.ell(p,x+7*s,y+12*s,61*s,57*s,dark)
        self.ell(p,x+12*s,y+17*s,51*s,48*s,body)
        self.ell(p,x+17*s,y+22*s,41*s,36*s,light)
        self.face(p,x+13*s,y+14*s,s,q)
        # tiny glasses, kept extremely simple
        self.line(p,(x+17*s,y+32*s),(x+30*s,y+32*s),dark,1)
        self.line(p,(x+42*s,y+32*s),(x+55*s,y+32*s),dark,1)
        self.line(p,(x+30*s,y+32*s),(x+42*s,y+32*s),dark,1)
        self.body(p,x+2*s,y,s,q)
        # little tail
        self.ell(p,x+59*s,y+72*s,26*s,13*s,dark)
        self.ell(p,x+64*s,y+68*s,23*s,11*s,body)



class CharacterLayer:
    DESKS={'현무':(55,244,145),'김선달':(335,244,145),'이묵':(615,244,145),'너부리':(895,244,145),'알프레도':(1175,244,145)}
    POSITIONS={n:(x+42,288) for n,(x,y,w) in DESKS.items()}
    MEETING_POSITIONS={'현무':(400,335),'김선달':(515,335),'이묵':(630,335),'너부리':(745,335),'알프레도':(860,335)}
    DOOR=(42.0,410.0)

    def __init__(self):
        self.characters={n:PixelCharacter(n) for n in self.POSITIONS}
        self.pos={n:(float(x),float(y)) for n,(x,y) in self.POSITIONS.items()}
        self.active={n:True for n in self.POSITIONS}
        self.mode='idle'; self.stage='idle'; self.queue=[]
        self.move_speed=180.0; self.bubbles={}; self.bubble_until={}
        self.office_open=9<=time.localtime().tm_hour<18
        if not self.office_open:self.reset_off_hours()

    def set_office_hours(self,hour,immediate=False):
        open_now=9<=hour<18
        if open_now==self.office_open:return
        self.office_open=open_now
        self.reset_office() if open_now else self.reset_off_hours()

    def reset_office(self):
        self.mode='idle';self.stage='idle';self.queue=[];self.clear_bubbles()
        for n,(x,y) in self.POSITIONS.items():self.active[n]=True;self.pos[n]=(float(x),float(y))

    def reset_off_hours(self):
        self.mode='off_hours';self.stage='idle';self.queue=[];self.clear_bubbles()
        for n in self.POSITIONS:self.active[n]=False;self.pos[n]=self.DOOR

    def start_arrival(self):
        self.mode='arrival';self.stage='arrival';self.queue=list(self.POSITIONS);self.clear_bubbles()
        for n in self.POSITIONS:self.active[n]=True;self.pos[n]=self.DOOR

    def start_departure(self):
        self.mode='leaving';self.stage='leaving';self.queue=list(self.POSITIONS)

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
        if name in self.POSITIONS and text:
            self.bubbles[name]=text[:420];self.bubble_until[name]=time.time()+duration_ms/1000.0

    def set_meeting_log(self,log):
        txt=str(log); found=False
        for name in ('현무','김선달','이묵','너부리'):
            hits=[]
            for pat in [rf'###\s*\*?[^\n]*{re.escape(name)}[^\n]*\n(.+?)(?=\n###|\Z)',rf'{re.escape(name)}\s*[:：]\s*(.+)']:
                hits += list(re.finditer(pat,txt,re.S))
            if hits:
                block=hits[-1].group(1).strip()
                lines=[v.strip(' -*') for v in block.splitlines() if v.strip()]
                line=next((v for v in lines if len(v)>12),lines[0] if lines else '')
                if line:self.set_bubble(name,line,24000);found=True
        return found

    def show_final_verdict(self,error=False):
        self.mode='verdict';self.stage='verdict';self.clear_bubbles()
        self.set_bubble('알프레도','분석완료! 회의완료! 최종 판단을 정리했습니다.',12000)

    def clear_bubbles(self):self.bubbles={};self.bubble_until={}

    def tick(self):
        now=time.time()
        for c in self.characters.values():c.tick()
        for n,t in list(self.bubble_until.items()):
            if now>t:self.bubble_until.pop(n,None);self.bubbles.pop(n,None)
        if self.mode in ('arrival','meeting_arrival'):
            remaining=[]
            for n in self.queue:
                tx,ty=self.MEETING_POSITIONS[n] if self.mode=='meeting_arrival' else self.POSITIONS[n]
                x,y=self.pos[n];dx,dy=tx-x,ty-y;d=(dx*dx+dy*dy)**0.5
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
            if self.active[n]:self.characters[n].paint(p,self.pos[n][0],self.pos[n][1],2.15)
        for n,text in list(self.bubbles.items()):
            if self.active.get(n,False):self._bubble(p,n,text,self.pos[n][0],self.pos[n][1])

    def _bubble(self,p,name,text,x,y):
        words=str(text).replace('\n',' ').split();lines=[];cur=''
        for word in words:
            nxt=(cur+' '+word).strip()
            if len(nxt)>25 and cur:lines.append(cur);cur=word
            else:cur=nxt
        if cur:lines.append(cur)
        lines=lines[:8] or ['...']
        bw=max(240,min(410,max(26,max(map(len,lines)))*8+32))
        bh=18+len(lines)*17;bx=int(x+45);by=int(y-bh-18)
        if bx+bw>1490:bx=int(x-bw+15)
        if bx<8:bx=8
        if by<8:by=8
        p.setPen(QColor('#8f7c5d'));p.setBrush(QColor('#f4ecda'))
        p.drawRoundedRect(bx,by,bw,bh,9,9)
        tailx=int(x+20 if bx>x else x+48)
        p.drawPolygon(QPolygon([QPoint(tailx,by+bh),QPoint(tailx+15,by+bh),QPoint(tailx+7,by+bh+10)]))
        p.setPen(QColor('#25221e'));p.setFont(QFont('Malgun Gothic',8,QFont.Bold))
        p.drawText(QRect(bx+10,by+5,bw-20,bh-8),Qt.AlignLeft|Qt.AlignVCenter,'\n'.join(lines))
