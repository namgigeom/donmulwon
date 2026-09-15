import os, time, urllib.request, re
from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QColor, QFont, QPolygon, QImage

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, 'assets', 'office_animals')
os.makedirs(ASSET_DIR, exist_ok=True)

# Replaced the old Tiny Creatures atlas. These are separate/full-frame assets,
# so adjacent animals can never bleed into the character image.
ASSETS = {
    '현무': ('https://opengameart.org/sites/default/files/turtle_4.png', 'turtle.png'),
    '김선달': ('https://img.itch.zone/aW1nLzUyNTM3NjEuZ2lm/original/nH1Eed.gif', 'crow.gif'),
    '이묵': ('https://opengameart.org/sites/default/files/Snake%20sprite%20sheet.png', 'snake.png'),
    '너부리': ('https://img.itch.zone/aW1hZ2UvMjM0MTM1OS8xNDAxODQwOS5naWY%3D/original/0mMnE1.gif', 'raccoon.gif'),
    '알프레도': ('https://opengameart.org/sites/default/files/cat_run.png', 'cat.png'),
}

def _download(url, path):
    try:
        if os.path.exists(path) and os.path.getsize(path) > 100:
            return True
        req = urllib.request.Request(url, headers={'User-Agent': 'DONMULWON/1.0'})
        with urllib.request.urlopen(req, timeout=12) as r, open(path, 'wb') as f:
            f.write(r.read())
        return os.path.getsize(path) > 100
    except Exception:
        return False

def _load_image(path):
    img = QImage(path)
    return QImage() if img.isNull() else img.convertToFormat(QImage.Format_ARGB32)

class PixelCharacter:
    def __init__(self, name):
        self.name = name; self.sprite = QImage(); self.frame = 0; self._load()

    def _load(self):
        url, filename = ASSETS[self.name]
        path = os.path.join(ASSET_DIR, filename)
        _download(url, path)
        img = _load_image(path)
        if img.isNull(): return
        if self.name == '현무':
            self.sprite = img.copy(0, 0, min(16, img.width()), min(16, img.height()))
        elif self.name == '알프레도':
            self.sprite = img.copy(0, 0, min(66, img.width()), min(66, img.height()))
        elif self.name == '이묵':
            self.sprite = img.copy(0, 0, min(32, img.width()), min(32, img.height()))
        else:
            self.sprite = img

    def tick(self): self.frame = (self.frame + 1) % 60

    def paint(self, p, x, y, scale=3):
        x, y, s = int(x), int(y), int(scale)
        if self.sprite.isNull():
            self._fallback(p, x, y, s); return
        w, h = self.sprite.width() * s, self.sprite.height() * s
        p.drawImage(QRect(x, y, w, h), self.sprite)
        if self.name == '알프레도':
            p.setPen(QColor('#d8bd70')); p.setBrush(Qt.NoBrush)
            cx, cy = x + int(w*.43), y + int(h*.34)
            p.drawRect(cx, cy, max(3,s), max(3,s)); p.drawRect(cx+int(w*.16), cy, max(3,s), max(3,s))
            p.drawLine(cx+s, cy+s//2, cx+int(w*.16), cy+s//2)

    def _fallback(self, p, x, y, s):
        p.setPen(Qt.NoPen); p.setBrush(QColor('#394047')); p.drawRect(x,y,32*s,32*s)
        p.setBrush(QColor('#d8bd70')); p.drawRect(x+10*s,y+10*s,4*s,4*s); p.drawRect(x+18*s,y+10*s,4*s,4*s)

class CharacterLayer:
    DESKS={'현무':(55,245,145),'김선달':(335,245,145),'이묵':(615,245,145),'너부리':(895,245,145),'알프레도':(1175,245,145)}
    POSITIONS={n:(x+w//2-48,300) for n,(x,y,w) in DESKS.items()}
    MEETING_POSITIONS={'현무':(420,360),'김선달':(540,360),'이묵':(660,360),'너부리':(780,360),'알프레도':(900,360)}
    DOOR=(55.0,470.0)

    def __init__(self):
        self.characters={n:PixelCharacter(n) for n in self.POSITIONS}; self.pos={n:(float(x),float(y)) for n,(x,y) in self.POSITIONS.items()}
        self.active={n:True for n in self.POSITIONS}; self.mode='idle'; self.queue=[]; self.move_speed=75
        self.bubbles={}; self.bubble_until={}; self.stage='idle'; self.office_open=9<=time.localtime().tm_hour<18
        if not self.office_open: self.reset_off_hours()

    def set_office_hours(self,hour,immediate=False):
        open_now=9<=hour<18
        if open_now==self.office_open: return
        self.office_open=open_now; self.reset_office() if open_now else self.reset_off_hours()

    def reset_office(self):
        self.mode='idle'; self.stage='idle'; self.queue=[]; self.clear_bubbles()
        for n,(x,y) in self.POSITIONS.items(): self.active[n]=True; self.pos[n]=(float(x),float(y))

    def reset_off_hours(self):
        self.mode='off_hours'; self.stage='idle'; self.queue=[]; self.clear_bubbles()
        for n in self.POSITIONS: self.active[n]=False; self.pos[n]=self.DOOR

    def summon_for_question(self,overtime=False):
        self.mode='meeting_arrival'; self.stage='summon'; self.queue=list(self.POSITIONS); self.clear_bubbles(); self.move_speed=75
        for n in self.POSITIONS: self.active[n]=True; self.pos[n]=self.DOOR
        self.set_bubble('알프레도','긴급 호출이다. 전원 회의실로!',5500)

    def set_meeting_stage(self,stage):
        if stage=='summon': self.summon_for_question()
        elif stage=='meeting':
            self.mode='meeting'; self.stage='meeting'; self.queue=[]
            for n,(x,y) in self.MEETING_POSITIONS.items(): self.active[n]=True; self.pos[n]=(float(x),float(y))
        elif stage=='verdict': self.show_final_verdict()
        elif stage=='return': self.reset_office() if self.office_open else self.reset_off_hours()

    def set_bubble(self,name,text,duration_ms=12000):
        if name not in self.POSITIONS: return
        text=' '.join(str(text).split()).strip()
        if text: self.bubbles[name]=text[:300]; self.bubble_until[name]=time.time()+duration_ms/1000

    def set_meeting_log(self,log):
        found=False
        for name in ('현무','김선달','이묵','너부리'):
            pats=[rf'{re.escape(name)}[^\n]*[:：]\s*(.+)',rf'###\s*.*{re.escape(name)}.*\n(.+?)(?=\n###|\Z)']
            for pat in pats:
                m=list(re.finditer(pat,str(log),re.S))
                if m:
                    text=m[-1].group(1).strip().split('\n')[0]; self.set_bubble(name,text,15000); found=True; break
        return found

    def show_final_verdict(self,error=False):
        self.mode='verdict'; self.stage='verdict'; self.clear_bubbles(); self.set_bubble('알프레도','분석완료! 회의완료! 최종 판단을 정리하겠습니다.',10000)

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
                self.set_bubble('현무','시장부터 보겠습니다. 거시환경이 지금 어느 방향인지 확인해야 합니다.',15000)
                self.set_bubble('김선달','숫자만 보면 안 됩니다. 실적하고 최근 뉴스부터 짚고 가죠.',15000)
                self.set_bubble('이묵','잠깐. 차트는 다른 이야기를 하고 있습니다. 추세부터 보시죠.',15000)
                self.set_bubble('너부리','좋습니다. 그런데 이걸 지금 계좌 비중에 넣어도 되는지도 봐야 합니다.',15000)

    def paint(self,p):
        for n in self.POSITIONS:
            if self.active[n]: self.characters[n].paint(p,self.pos[n][0],self.pos[n][1],3)
        for n,text in list(self.bubbles.items()):
            if self.active.get(n,False): self._bubble(p,n,text,self.pos[n][0],self.pos[n][1])

    def _bubble(self,p,name,text,x,y):
        chunks=[]; cur=''
        for ch in str(text).replace('\n',' '):
            cur+=ch
            if len(cur)>=20: chunks.append(cur); cur=''
        if cur: chunks.append(cur)
        lines=chunks[:6] or ['...']; bw=max(230,min(380,max(len(v) for v in lines)*9+34)); bh=24+len(lines)*19
        bx,by=int(x+30),int(y-bh-18)
        if bx+bw>1490: bx=int(x-bw+10)
        if bx<10: bx=10
        if by<8: by=8
        p.setPen(QColor('#9b8968')); p.setBrush(QColor('#f4ecda')); p.drawRoundedRect(bx,by,bw,bh,8,8)
        p.drawPolygon(QPolygon([QPoint(int(x+12),by+bh),QPoint(int(x+29),by+bh),QPoint(int(x+21),by+bh+11)]))
        p.setPen(QColor('#211f1c')); p.setFont(QFont('Malgun Gothic',8,QFont.Bold)); p.drawText(QRect(bx+10,by+6,bw-20,bh-10),Qt.AlignLeft|Qt.AlignVCenter,'\n'.join(lines))
