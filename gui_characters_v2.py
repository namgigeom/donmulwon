import time, re
from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QColor, QFont, QPainterPath

class ChibiCharacter:
    """Original soft 2D chibi mascot renderer. No pixel-art styling."""
    PALETTE = {
        '현무': ('#7fa878','#4d6848','#dcebd2','#eea5a1'),
        '김선달': ('#50575c','#2b3034','#d9dee0','#e9a5a0'),
        '이묵': ('#8fbc67','#4f7139','#e4f1cf','#eeaaa4'),
        '너부리': ('#b39b87','#695747','#eadbce','#eda7a1'),
        '알프레도': ('#e0bfa7','#70584b','#fae8db','#eca7a1'),
    }

    def __init__(self, name):
        self.name = name
        self.frame = 0

    def tick(self):
        self.frame = (self.frame + 1) % 60

    def ellipse(self, p, x, y, w, h, color):
        p.setPen(Qt.NoPen); p.setBrush(QColor(color))
        p.drawEllipse(int(x), int(y), int(w), int(h))

    def path(self, p, points, color):
        q = QPainterPath()
        q.moveTo(points[0][0], points[0][1])
        for x, y in points[1:]:
            q.lineTo(x, y)
        q.closeSubpath()
        p.setPen(Qt.NoPen); p.setBrush(QColor(color)); p.drawPath(q)

    def line(self, p, a, b, color, width=2):
        pen = p.pen(); pen.setColor(QColor(color)); pen.setWidth(max(1, int(width)))
        p.setPen(pen); p.drawLine(QPoint(int(a[0]), int(a[1])), QPoint(int(b[0]), int(b[1])))
        p.setPen(Qt.NoPen)

    def face(self, p, x, y, s, dark, cheek):
        # simple sleepy bean eyes + tiny mouth
        self.ellipse(p, x+19*s, y+31*s, 5*s, 7*s, dark)
        self.ellipse(p, x+46*s, y+31*s, 5*s, 7*s, dark)
        self.ellipse(p, x+10*s, y+44*s, 10*s, 6*s, cheek)
        self.ellipse(p, x+50*s, y+44*s, 10*s, 6*s, cheek)
        self.line(p, (x+31*s,y+44*s), (x+34*s,y+46*s), dark, 1.5)
        self.line(p, (x+34*s,y+46*s), (x+37*s,y+44*s), dark, 1.5)

    def body(self, p, x, y, s, body, dark, light):
        self.ellipse(p,x+17*s,y+66*s,40*s,32*s,dark)
        self.ellipse(p,x+20*s,y+63*s,34*s,30*s,body)
        self.ellipse(p,x+28*s,y+73*s,18*s,13*s,light)
        self.ellipse(p,x+8*s,y+72*s,15*s,10*s,body)
        self.ellipse(p,x+52*s,y+72*s,15*s,10*s,body)
        self.ellipse(p,x+20*s,y+88*s,15*s,9*s,dark)
        self.ellipse(p,x+40*s,y+88*s,15*s,9*s,dark)

    def paint(self,p,x,y,scale=2.15):
        body,dark,light,cheek=self.PALETTE[self.name]
        s=scale
        if self.name == '현무': self.turtle(p,x,y,s,body,dark,light,cheek)
        elif self.name == '김선달': self.crow(p,x,y,s,body,dark,light,cheek)
        elif self.name == '이묵': self.snake(p,x,y,s,body,dark,light,cheek)
        elif self.name == '너부리': self.raccoon(p,x,y,s,body,dark,light,cheek)
        else: self.cat(p,x,y,s,body,dark,light,cheek)

    def base_head(self,p,x,y,s,body,dark,light,cheek):
        self.ellipse(p,x+6*s,y+10*s,63*s,58*s,dark)
        self.ellipse(p,x+10*s,y+14*s,55*s,50*s,body)
        self.ellipse(p,x+17*s,y+20*s,41*s,36*s,light)
        self.face(p,x+12*s,y+13*s,s,dark,cheek)
        self.body(p,x,y,s,body,dark,light)

    def turtle(self,p,x,y,s,body,dark,light,cheek):
        self.ellipse(p,x+4*s,y+48*s,66*s,43*s,dark)
        self.ellipse(p,x+9*s,y+50*s,56*s,34*s,body)
        self.ellipse(p,x+19*s,y+55*s,36*s,23*s,light)
        self.line(p,(x+37*s,y+55*s),(x+37*s,y+78*s),dark,1.5)
        self.line(p,(x+20*s,y+66*s),(x+54*s,y+66*s),dark,1.5)
        self.base_head(p,x,y,s,body,dark,light,cheek)

    def crow(self,p,x,y,s,body,dark,light,cheek):
        self.path(p,[(x+25*s,y+16*s),(x+33*s,y+1*s),(x+42*s,y+16*s)],dark)
        self.base_head(p,x,y,s,body,dark,light,cheek)
        self.path(p,[(x+61*s,y+36*s),(x+78*s,y+41*s),(x+61*s,y+46*s)],'#e0b35e')

    def snake(self,p,x,y,s,body,dark,light,cheek):
        self.ellipse(p,x+2*s,y+57*s,67*s,31*s,dark)
        self.ellipse(p,x+7*s,y+59*s,57*s,21*s,body)
        self.ellipse(p,x+19*s,y+9*s,49*s,56*s,dark)
        self.ellipse(p,x+23*s,y+13*s,41*s,48*s,body)
        self.ellipse(p,x+29*s,y+20*s,29*s,31*s,light)
        self.face(p,x+25*s,y+13*s,s,dark,cheek)
        self.line(p,(x+64*s,y+41*s),(x+77*s,y+41*s),'#d96e68',1.5)
        self.line(p,(x+77*s,y+41*s),(x+81*s,y+38*s),'#d96e68',1.5)
        self.line(p,(x+77*s,y+41*s),(x+81*s,y+44*s),'#d96e68',1.5)
        self.body(p,x,y+3*s,s,body,dark,light)

    def raccoon(self,p,x,y,s,body,dark,light,cheek):
        self.path(p,[(x+11*s,y+25*s),(x+13*s,y+3*s),(x+30*s,y+19*s)],dark)
        self.path(p,[(x+43*s,y+19*s),(x+60*s,y+3*s),(x+62*s,y+25*s)],dark)
        self.path(p,[(x+16*s,y+20*s),(x+17*s,y+10*s),(x+25*s,y+20*s)],light)
        self.path(p,[(x+48*s,y+20*s),(x+57*s,y+10*s),(x+57*s,y+20*s)],light)
        self.base_head(p,x,y,s,body,dark,light,cheek)
        self.ellipse(p,x+14*s,y+28*s,22*s,14*s,dark)
        self.ellipse(p,x+43*s,y+28*s,22*s,14*s,dark)
        self.ellipse(p,x+20*s,y+31*s,8*s,7*s,light)
        self.ellipse(p,x+49*s,y+31*s,8*s,7*s,light)
        self.ellipse(p,x+59*s,y+70*s,31*s,18*s,dark)
        self.ellipse(p,x+64*s,y+68*s,25*s,14*s,body)

    def cat(self,p,x,y,s,body,dark,light,cheek):
        self.path(p,[(x+11*s,y+25*s),(x+14*s,y+3*s),(x+31*s,y+19*s)],dark)
        self.path(p,[(x+42*s,y+19*s),(x+59*s,y+3*s),(x+62*s,y+25*s)],dark)
        self.path(p,[(x+16*s,y+20*s),(x+17*s,y+10*s),(x+25*s,y+20*s)],light)
        self.path(p,[(x+48*s,y+20*s),(x+57*s,y+10*s),(x+57*s,y+20*s)],light)
        self.base_head(p,x,y,s,body,dark,light,cheek)
        # Alfredo: tiny round glasses
        self.line(p,(x+17*s,y+33*s),(x+30*s,y+33*s),dark,1.5)
        self.line(p,(x+42*s,y+33*s),(x+55*s,y+33*s),dark,1.5)
        self.line(p,(x+30*s,y+33*s),(x+42*s,y+33*s),dark,1.5)
        self.ellipse(p,x+60*s,y+72*s,27*s,14*s,dark)
        self.ellipse(p,x+64*s,y+69*s,23*s,11*s,body)


class CharacterLayer:
    DESKS={'현무':(55,244,145),'김선달':(335,244,145),'이묵':(615,244,145),'너부리':(895,244,145),'알프레도':(1175,244,145)}
    POSITIONS={n:(x+42,288) for n,(x,y,w) in DESKS.items()}
    MEETING_POSITIONS={'현무':(400,335),'김선달':(515,335),'이묵':(630,335),'너부리':(745,335),'알프레도':(860,335)}
    DOOR=(42.0,410.0)

    def __init__(self):
        self.characters={n:ChibiCharacter(n) for n in self.POSITIONS}
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
        p.drawPolygon([QPoint(tailx,by+bh),QPoint(tailx+15,by+bh),QPoint(tailx+7,by+bh+10)])
        p.setPen(QColor('#25221e'));p.setFont(QFont('Malgun Gothic',8,QFont.Bold))
        p.drawText(QRect(bx+10,by+5,bw-20,bh-8),Qt.AlignLeft|Qt.AlignVCenter,'\n'.join(lines))
