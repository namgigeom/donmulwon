import time, re
from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QColor, QFont, QPolygon

# Cute rounded pixel-mascot characters.
# Original character design: oversized heads, tiny bodies, simple faces, office suits.
# Intentionally avoids copying any existing character design.

class PixelCharacter:
    PALETTE = {
        '현무':    {'body':'#78966f','dark':'#3e5540','light':'#b9c9a1','accent':'#c7a86b'},
        '김선달':  {'body':'#31363a','dark':'#15191c','light':'#68757a','accent':'#c7a86b'},
        '이묵':    {'body':'#5f874d','dark':'#273b25','light':'#9fbd82','accent':'#c7a86b'},
        '너부리':  {'body':'#8a8177','dark':'#37332f','light':'#c2b6a7','accent':'#c7a86b'},
        '알프레도':{'body':'#b6aaa0','dark':'#514a46','light':'#eee3d2','accent':'#c7a86b'},
    }

    def __init__(self, name):
        self.name = name
        self.frame = 0

    def tick(self):
        self.frame = (self.frame + 1) % 60

    def rect(self,p,x,y,w,h,c,r=0):
        p.setPen(Qt.NoPen); p.setBrush(QColor(c))
        if r: p.drawRoundedRect(int(x),int(y),int(w),int(h),r,r))
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

    def face(self,p,x,y,s,body,dark,light):
        # Tiny dot eyes + soft blush. The face is deliberately simple and mascot-like.
        self.ell(p,x+20*s,y+25*s,5*s,7*s,dark)
        self.ell(p,x+47*s,y+25*s,5*s,7*s,dark)
        self.ell(p,x+17*s,y+36*s,7*s,4*s,'#d68d87')
        self.ell(p,x+48*s,y+36*s,7*s,4*s,'#d68d87')
        self.line(p,(x+33*s,y+35*s),(x+36*s,y+35*s),dark,1)
        self.line(p,(x+34*s,y+36*s),(x+36*s,y+38*s),dark,1)

    def suit(self,p,x,y,s,body,dark,light,accent):
        # Small navy/brown office suit silhouette.
        self.rect(p,x+16*s,y+60*s,42*s,30*s,dark,5)
        self.rect(p,x+11*s,y+66*s,14*s,25*s,dark,5)
        self.rect(p,x+49*s,y+66*s,14*s,25*s,dark,5)
        self.rect(p,x+23*s,y+61*s,28*s,25*s,'#24282b',4)
        self.poly(p,[(x+30*s,y+62*s),(x+39*s,y+62*s),(x+36*s,y+78*s)],light)
        self.poly(p,[(x+35*s,y+77*s),(x+40*s,y+77*s),(x+37*s,y+87*s)],accent)
        self.rect(p,x+20*s,y+87*s,14*s,9*s,'#15181a',3)
        self.rect(p,x+41*s,y+87*s,14*s,9*s,'#15181a',3)
        self.ell(p,x+5*s,y+70*s,12*s,15*s,body)
        self.ell(p,x+57*s,y+70*s,12*s,15*s,body)

    def paint(self,p,x,y,scale=2.15):
        s=scale
        pal=self.PALETTE[self.name]
        if self.name=='현무': self.turtle(p,x,y,s,pal)
        elif self.name=='김선달': self.crow(p,x,y,s,pal)
        elif self.name=='이묵': self.snake(p,x,y,s,pal)
        elif self.name=='너부리': self.raccoon(p,x,y,s,pal)
        else: self.cat(p,x,y,s,pal)

    def turtle(self,p,x,y,s,q):
        body,dark,light,accent=q['body'],q['dark'],q['light'],q['accent']
        # shell/back
        self.ell(p,x+8*s,y+30*s,54*s,38*s,dark)
        self.ell(p,x+12*s,y+31*s,46*s,32*s,body)
        self.ell(p,x+18*s,y+35*s,34*s,24*s,light)
        for a,b in [((x+35*s,y+35*s),(x+35*s,y+58*s)),((x+19*s,y+47*s),(x+51*s,y+47*s))]:
            self.line(p,a,b,dark,1)
        # head
        self.ell(p,x+37*s,y+13*s,36*s,34*s,body)
        self.ell(p,x+41*s,y+16*s,29*s,28*s,light)
        self.face(p,x+39*s,y+13*s,s,body,dark,light)
        self.suit(p,x+4*s,y+49*s,s,body,dark,light,accent)

    def crow(self,p,x,y,s,q):
        body,dark,light,accent=q['body'],q['dark'],q['light'],q['accent']
        # round crow head, little beak and feather tuft
        self.poly(p,[(x+21*s,y+12*s),(x+28*s,y+2*s),(x+34*s,y+13*s)],dark)
        self.ell(p,x+7*s,y+12*s,62*s,54*s,dark)
        self.ell(p,x+12*s,y+17*s,52*s,45*s,body)
        self.ell(p,x+18*s,y+22*s,40*s,34*s,light)
        self.face(p,x+15*s,y+17*s,s,body,dark,light)
        self.poly(p,[(x+59*s,y+30*s),(x+78*s,y+36*s),(x+59*s,y+41*s)],accent)
        self.suit(p,x+2*s,y+50*s,s,body,dark,light,accent)

    def snake(self,p,x,y,s,q):
        body,dark,light,accent=q['body'],q['dark'],q['light'],q['accent']
        # curled body
        self.ell(p,x+3*s,y+38*s,63*s,32*s,dark)
        self.ell(p,x+8*s,y+41*s,53*s,22*s,body)
        self.ell(p,x+39*s,y+10*s,30*s,40*s,dark)
        self.ell(p,x+43*s,y+13*s,24*s,33*s,light)
        self.face(p,x+41*s,y+11*s,s,body,dark,light)
        self.line(p,(x+66*s,y+31*s),(x+79*s,y+31*s),accent,2)
        self.suit(p,x+1*s,y+50*s,s,body,dark,light,accent)

    def raccoon(self,p,x,y,s,q):
        body,dark,light,accent=q['body'],q['dark'],q['light'],q['accent']
        self.poly(p,[(x+13*s,y+22*s),(x+12*s,y+4*s),(x+27*s,y+17*s)],dark)
        self.poly(p,[(x+43*s,y+17*s),(x+58*s,y+4*s),(x+57*s,y+23*s)],dark)
        self.ell(p,x+8*s,y+11*s,58*s,55*s,dark)
        self.ell(p,x+13*s,y+16*s,48*s,45*s,body)
        self.ell(p,x+17*s,y+21*s,40*s,34*s,light)
        # mask
        self.poly(p,[(x+15*s,y+29*s),(x+28*s,y+24*s),(x+35*s,y+29*s),(x+42*s,y+24*s),(x+57*s,y+29*s),(x+50*s,y+42*s),(x+22*s,y+42*s)],dark)
        self.ell(p,x+22*s,y+27*s,8*s,7*s,'#f2eadc')
        self.ell(p,x+43*s,y+27*s,8*s,7*s,'#f2eadc')
        self.ell(p,x+25*s,y+29*s,3*s,3*s,dark)
        self.ell(p,x+46*s,y+29*s,3*s,3*s,dark)
        self.ell(p,x+31*s,y+39*s,8*s,5*s,light)
        self.suit(p,x+2*s,y+50*s,s,body,dark,light,accent)
        self.ell(p,x+61*s,y+65*s,22*s,10*s,dark)
        self.ell(p,x+67*s,y+60*s,18*s,10*s,body)

    def cat(self,p,x,y,s,q):
        body,dark,light,accent=q['body'],q['dark'],q['light'],q['accent']
        # ears + giant soft head
        self.poly(p,[(x+13*s,y+21*s),(x+15*s,y+3*s),(x+29*s,y+17*s)],dark)
        self.poly(p,[(x+41*s,y+17*s),(x+56*s,y+3*s),(x+58*s,y+22*s)],dark)
        self.ell(p,x+8*s,y+12*s,60*s,55*s,dark)
        self.ell(p,x+13*s,y+17*s,50*s,45*s,body)
        self.ell(p,x+17*s,y+21*s,42*s,36*s,light)
        self.face(p,x+14*s,y+17*s,s,body,dark,light)
        # glasses + tiny tie for Alfredo
        self.line(p,(x+18*s,y+28*s),(x+32*s,y+28*s),dark,1)
        self.line(p,(x+41*s,y+28*s),(x+55*s,y+28*s),dark,1)
        self.line(p,(x+33*s,y+28*s),(x+40*s,y+28*s),dark,1)
        self.suit(p,x+2*s,y+50*s,s,body,dark,light,accent)
        self.ell(p,x+61*s,y+65*s,22*s,10*s,dark)
        self.ell(p,x+68*s,y+60*s,17*s,9*s,body)


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
