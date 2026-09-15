import os
import time
import zipfile
import urllib.request
from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QColor, QFont, QPolygon, QImage, QPainter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, 'assets', 'tiny_creatures')
ZIP_URL = 'https://opengameart.org/sites/default/files/tiny-creatures.zip'
TILEMAP = os.path.join(ASSET_DIR, 'tilemap.png')

# Tiny Creatures by Clint Bellanger / Kenney collaboration, CC0.
# The published tilemap is 10 columns x 18 rows, 16x16 pixels per cell.
# IMPORTANT: these are zero-based (column, row) coordinates in tilemap.png.
# Source order is documented on the OpenGameArt page.
SPRITE_CELL = {
    '현무': (9, 14),       # turtle
    '김선달': (6, 13),     # crow/raven, wings up
    '이묵': (1, 4),        # adder
    '너부리': (8, 17),     # raccoon
    '알프레도': (4, 9),    # cat
}


def _download_assets():
    os.makedirs(ASSET_DIR, exist_ok=True)
    if os.path.exists(TILEMAP):
        return True
    try:
        zip_path = os.path.join(ASSET_DIR, 'tiny-creatures.zip')
        urllib.request.urlretrieve(ZIP_URL, zip_path)
        with zipfile.ZipFile(zip_path, 'r') as zf:
            member = next((n for n in zf.namelist() if n.lower().endswith('/tilemap.png') or n.lower() == 'tilemap.png'), None)
            if not member:
                raise FileNotFoundError('tilemap.png not found in Tiny Creatures archive')
            with zf.open(member) as src, open(TILEMAP, 'wb') as dst:
                dst.write(src.read())
        try:
            os.remove(zip_path)
        except OSError:
            pass
        return True
    except Exception:
        return False


class PixelCharacter:
    def __init__(self, name):
        self.name = name
        self.frame = 0
        self.sprite = None
        self._load_sprite()

    def _load_sprite(self):
        if not os.path.exists(TILEMAP):
            _download_assets()
        if not os.path.exists(TILEMAP):
            return
        sheet = QImage(TILEMAP)
        if sheet.isNull():
            return

        # Do not guess the sheet layout. Validate that the downloaded image is
        # actually the expected 160x288 tilemap before cropping it.
        if sheet.width() < 160 or sheet.height() < 288:
            return

        col, row = SPRITE_CELL.get(self.name, (0, 0))
        src = sheet.copy(col * 16, row * 16, 16, 16)
        if src.isNull() or src.width() != 16 or src.height() != 16:
            return
        self.sprite = src.convertToFormat(QImage.Format_ARGB32)

    def tick(self):
        self.frame = (self.frame + 1) % 60

    def paint(self, p, x, y, scale=5):
        x, y, s = int(x), int(y), int(scale)
        if self.sprite is not None and not self.sprite.isNull():
            # Keep the original hard pixel edges. Never bilinear-filter a
            # 16x16 sprite while enlarging it.
            old_hint = p.renderHints()
            p.setRenderHint(QPainter.SmoothPixmapTransform, False)
            target = QRect(x, y, 16 * s, 16 * s)
            p.drawImage(target, self.sprite)
            p.setRenderHints(old_hint)
            return
        self._fallback(p, x, y, s)

    def _px(self, p, x, y, w, h, c):
        p.setBrush(QColor(c)); p.setPen(Qt.NoPen); p.drawRect(x, y, w, h)

    def _fallback(self, p, x, y, s):
        # Emergency fallback only when the CC0 package cannot be downloaded.
        if self.name == '현무':
            self._px(p,x+7*s,y+8*s,24*s,16*s,'#31513b'); self._px(p,x+11*s,y+5*s,16*s,5*s,'#58744a'); self._px(p,x+29*s,y+11*s,9*s,7*s,'#719261')
            for rx,ry in ((5,9),(7,22),(25,22),(29,8)): self._px(p,x+rx*s,y+ry*s,6*s,6*s,'#64875a')
            self._px(p,x+36*s,y+13*s,3*s,3*s,'#eadb9a')
        elif self.name == '김선달':
            self._px(p,x+8*s,y+8*s,23*s,18*s,'#25272d'); self._px(p,x+13*s,y+4*s,13*s,9*s,'#17191f'); self._px(p,x+28*s,y+14*s,12*s,3*s,'#9a7745'); self._px(p,x+20*s,y+7*s,3*s,3*s,'#e2d79b')
        elif self.name == '이묵':
            self._px(p,x+7*s,y+23*s,27*s,7*s,'#456c3e'); self._px(p,x+26*s,y+7*s,9*s,17*s,'#5f8748'); self._px(p,x+25*s,y+5*s,12*s,8*s,'#3d6338'); self._px(p,x+29*s,y+8*s,2*s,2*s,'#eee0a0'); self._px(p,x+35*s,y+8*s,2*s,2*s,'#eee0a0')
        elif self.name == '너부리':
            self._px(p,x+8*s,y+9*s,22*s,18*s,'#8b8178'); self._px(p,x+11*s,y+4*s,7*s,8*s,'#9c9289'); self._px(p,x+23*s,y+4*s,7*s,8*s,'#9c9289'); self._px(p,x+8*s,y+13*s,22*s,6*s,'#4b4542'); self._px(p,x+13*s,y+14*s,3*s,3*s,'#e2d6a0'); self._px(p,x+22*s,y+14*s,3*s,3*s,'#e2d6a0'); self._px(p,x+29*s,y+23*s,13*s,6*s,'#6f665f')
        else:
            self._px(p,x+10*s,y+8*s,20*s,19*s,'#25262b'); self._px(p,x+12*s,y+3*s,6*s,8*s,'#202126'); self._px(p,x+23*s,y+3*s,6*s,8*s,'#202126'); self._px(p,x+14*s,y+12*s,3*s,3*s,'#d9c66f'); self._px(p,x+23*s,y+12*s,3*s,3*s,'#d9c66f')


class CharacterLayer:
    DESKS={'현무':(55,245,145),'김선달':(335,245,145),'이묵':(615,245,145),'너부리':(895,245,145),'알프레도':(1175,245,145)}
    POSITIONS={n:(x+w//2-40,300) for n,(x,y,w) in DESKS.items()}
    MEETING_POSITIONS={'현무':(425,355),'김선달':(555,355),'이묵':(685,355),'너부리':(815,355),'알프레도':(945,355)}
    DOOR=(55.0,470.0)

    def __init__(self):
        _download_assets()
        self.characters={n:PixelCharacter(n) for n in self.POSITIONS}
        self.pos={n:(float(x),float(y)) for n,(x,y) in self.POSITIONS.items()}
        self.active={n:True for n in self.POSITIONS}
        self.mode='idle'; self.queue=[]; self.move_speed=42; self.bubbles={}; self.bubble_until={}; self.stage='idle'; self.office_open=9<=time.localtime().tm_hour<18
        if not self.office_open: self.reset_off_hours()

    def set_office_hours(self,hour,immediate=False):
        open_now=9<=hour<18
        if open_now==self.office_open:
            if immediate and self.mode not in ('meeting_arrival','meeting','verdict'):
                self.reset_office() if open_now else self.reset_off_hours()
            return
        self.office_open=open_now
        self.reset_office() if open_now else self.reset_off_hours()

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
            if self.active[n]: self.characters[n].paint(p,self.pos[n][0],self.pos[n][1],5)
        for n,text in list(self.bubbles.items()):
            if self.active.get(n,False): self._bubble(p,n,text,self.pos[n][0],self.pos[n][1])

    def _bubble(self,p,name,text,x,y):
        chunks=[]; cur=''
        for ch in str(text).replace('\n',' '):
            cur+=ch
            if len(cur)>=18: chunks.append(cur); cur=''
        if cur: chunks.append(cur)
        lines=chunks[:5] or ['...']; bw=max(210,min(330,max(len(v) for v in lines)*9+34)); bh=20+len(lines)*20; bx=int(x+40); by=int(y-bh-22)
        if bx+bw>1490: bx=int(x-bw+10)
        if bx<10: bx=10
        if by<8: by=8
        p.setPen(QColor('#9b8968')); p.setBrush(QColor('#f4ecda')); p.drawRoundedRect(bx,by,bw,bh,8,8); p.setBrush(QColor('#f4ecda')); p.drawPolygon(QPolygon([QPoint(int(x+12),by+bh),QPoint(int(x+29),by+bh),QPoint(int(x+21),by+bh+11)])); p.setPen(QColor('#211f1c')); p.setFont(QFont('Malgun Gothic',8,QFont.Bold)); p.drawText(QRect(bx+10,by+5,bw-20,bh-8),Qt.AlignLeft|Qt.AlignVCenter,'\n'.join(lines))
