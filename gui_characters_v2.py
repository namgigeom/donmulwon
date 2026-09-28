import os, time, re
from PySide6.QtCore import Qt, QRect, QPoint, QRectF, QByteArray
from PySide6.QtGui import QColor, QFont
from PySide6.QtSvg import QSvgRenderer


class ChibiCharacter:
    """Cute animal mascot renderer using bundled Twemoji SVG artwork."""

    ASSETS = {
        '현무': 'twemoji_turtle.svg',
        '김선달': 'twemoji_black_bird.svg',
        '이묵': 'twemoji_snake.svg',
        '너부리': 'twemoji_raccoon.svg',
        '알프레도': 'twemoji_cat.svg',
    }

    ROLE_COLORS = {
        '현무': '#78a96b',
        '김선달': '#66717a',
        '이묵': '#86b85b',
        '너부리': '#a88a73',
        '알프레도': '#e2a96f',
    }

    def __init__(self, name):
        self.name = name
        self.frame = 0
        self.renderer = None
        filename = self.ASSETS.get(name)
        if filename:
            path = os.path.join(os.path.dirname(__file__), 'assets', 'office_animals', filename)
            try:
                self.renderer = QSvgRenderer(path)
            except Exception:
                self.renderer = None

    def tick(self):
        self.frame = (self.frame + 1) % 60

    def paint(self, painter, x, y, scale=2.15):
        # Keep the characters visually consistent: same SVG source, same box,
        # only their role badge/accent differs.
        size = int(86 * scale / 2.15)
        box = QRectF(float(x), float(y), float(size), float(size))
        if self.renderer and self.renderer.isValid():
            self.renderer.render(painter, box)

        # Small role badge under the mascot so the five agents remain distinct
        # even when the window is resized.
        painter.save()
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(self.ROLE_COLORS.get(self.name, '#888888')))
        painter.drawEllipse(QRectF(x + size * 0.39, y + size * 0.88, size * 0.22, size * 0.08))
        painter.restore()


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
