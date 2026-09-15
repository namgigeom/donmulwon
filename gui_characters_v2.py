import re
import time

from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QColor, QFont, QPolygon

from gui_characters import CharacterLayer as BaseCharacterLayer
from gui_assets import TinyCreatureAssets


class PixelCharacter:
    SPRITE_NAME = {'현무':'turtle','김선달':'crow','이묵':'snake','너부리':'raccoon','알프레도':'cat'}

    def __init__(self, name, assets):
        self.name = name
        self.assets = assets
        self.frame = 0

    def tick(self):
        self.frame = (self.frame + 1) % 60

    def paint(self, p, x, y):
        image = self.assets.get(self.SPRITE_NAME[self.name])
        if image is None:
            self._fallback(p, x, y)
            return
        p.setRenderHint(p.SmoothPixmapTransform, False)
        p.drawImage(int(x), int(y), image)
        # Alfredo alone gets a tiny office accessory layer.
        if self.name == '알프레도':
            s = 4
            ox, oy = int(x), int(y)
            p.setPen(QColor('#d8c178')); p.setBrush(Qt.NoBrush)
            p.drawRect(ox+12*s, oy+7*s, 4*s, 3*s)
            p.drawRect(ox+20*s, oy+7*s, 4*s, 3*s)
            p.drawLine(ox+16*s, oy+8*s, ox+20*s, oy+8*s)
            p.setPen(Qt.NoPen); p.setBrush(QColor('#b74452'))
            p.drawRect(ox+18*s, oy+14*s, 2*s, 7*s)

    def _fallback(self, p, x, y):
        # Only visible briefly while the CC0 pack downloads or if offline.
        s = 4; p.setPen(Qt.NoPen)
        colors = {'현무':('#355f42','#78975d'),'김선달':('#171a20','#b88e4d'),'이묵':('#507744','#b0c77a'),'너부리':('#777067','#d0bdab'),'알프레도':('#252730','#d7bd77')}
        dark, light = colors[self.name]
        p.setBrush(QColor(dark)); p.drawRect(int(x+8*s), int(y+12*s), 16*s, 12*s)
        p.setBrush(QColor(light)); p.drawRect(int(x+12*s), int(y+7*s), 8*s, 7*s)
        p.setBrush(QColor(dark)); p.drawRect(int(x+5*s), int(y+4*s), 6*s, 6*s); p.drawRect(int(x+21*s), int(y+4*s), 6*s, 6*s)


class CharacterLayer(BaseCharacterLayer):
    DESKS = {'현무':(55,244,175),'김선달':(320,244,175),'이묵':(585,244,175),'너부리':(850,244,175),'알프레도':(1115,244,175)}
    POSITIONS = {n:(x+w//2-32,166,0) for n,(x,y,w) in DESKS.items()}
    # 64x64 sprites. Previous y=500 put the meeting sprites below the 560px minimum viewport.
    MEETING_POSITIONS = {'현무':(455,392),'김선달':(595,392),'이묵':(735,392),'너부리':(875,392),'알프레도':(1015,392)}
    DOOR = (58.0,205.0)

    def __init__(self):
        super().__init__()
        self.assets = TinyCreatureAssets()
        self.assets.start()
        self.characters = {n:PixelCharacter(n,self.assets) for n in self.POSITIONS}
        self.pos = {n:(float(v[0]),float(v[1])) for n,v in self.POSITIONS.items()}
        self.active = {n:True for n in self.POSITIONS}
        self.mode='idle'; self.queue=[]; self.move_speed=28
        self.bubbles={}; self.bubble_until={}; self.stage='idle'
        self.office_open = 9 <= time.localtime().tm_hour < 18
        if not self.office_open: self.reset_off_hours()

    def set_office_hours(self,hour,immediate=False):
        open_now=9<=hour<18
        if open_now==self.office_open:
            if immediate and self.mode not in ('meeting_arrival','meeting','verdict'):
                self.reset_office() if open_now else self.reset_off_hours()
            return
        self.office_open=open_now; self.reset_office() if open_now else self.reset_off_hours()

    def reset_office(self):
        self.mode='idle'; self.stage='idle'; self.queue=[]; self.clear_bubbles()
        for n,(x,y,_) in self.POSITIONS.items(): self.active[n]=True; self.pos[n]=(float(x),float(y))

    def reset_off_hours(self):
        self.mode='off_hours'; self.stage='idle'; self.queue=[]; self.clear_bubbles()
        for n in self.POSITIONS: self.active[n]=False; self.pos[n]=self.DOOR

    def summon_for_question(self,overtime=False):
        self.mode='meeting_arrival'; self.stage='summon'; self.move_speed=28; self.queue=[]; self.clear_bubbles()
        for n in self.POSITIONS:
            self.active[n]=True; self.pos[n]=self.DOOR; self.queue.append(n)
        self.set_bubble('알프레도','긴급 호출이다. 전원 회의실로!',2400)

    def set_meeting_stage(self,stage):
        if stage=='summon': self.summon_for_question()
        elif stage=='meeting':
            self.mode='meeting'; self.stage='meeting'; self.queue=[]
            for n in self.POSITIONS: self.active[n]=True; self.pos[n]=tuple(map(float,self.MEETING_POSITIONS[n]))
        elif stage=='verdict': self.mode='verdict'; self.stage='verdict'; self.queue=[]
        elif stage=='return': self.reset_office() if self.office_open else self.reset_off_hours()

    def set_bubble(self,name,text,duration_ms=3600):
        if name not in self.POSITIONS: return
        text=re.sub(r'\s+',' ',str(text)).strip()
        if not text: return
        self.bubbles[name]=text[:220]; self.bubble_until[name]=time.time()+duration_ms/1000.0

    def set_meeting_log(self,log):
        patterns={'현무':r'(?:현무)[^\n:：]*[:：]\s*(.+)','김선달':r'(?:김선달)[^\n:：]*[:：]\s*(.+)','이묵':r'(?:이묵)[^\n:：]*[:：]\s*(.+)','너부리':r'(?:너부리)[^\n:：]*[:：]\s*(.+)'}
        for name,pattern in patterns.items():
            matches=list(re.finditer(pattern,str(log)))
            if matches: self.set_bubble(name,matches[-1].group(1),7000)

    def show_final_verdict(self,error=False):
        self.mode='verdict'; self.stage='verdict'; self.clear_bubbles()
        text='분석 실패! 회의는 중단되었습니다.' if error else '분석완료! 회의완료! 최종 판단을 정리하겠습니다.'
        self.set_bubble('알프레도',text,6000)

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
                self.set_bubble('현무','거시환경부터 보겠습니다. 시장 분위기부터 확인하죠.',5000)
                self.set_bubble('김선달','기업 실적과 최근 뉴스 흐름은 이렇습니다.',5000)
                self.set_bubble('이묵','차트상 가격과 추세는 조금 다르게 보입니다.',5000)
                self.set_bubble('너부리','현재 계좌 비중까지 같이 봐야 합니다.',5000)

    def paint(self,p):
        for n in self.POSITIONS:
            if self.active[n]: self.characters[n].paint(p,self.pos[n][0],self.pos[n][1])
        for n,text in list(self.bubbles.items()):
            if self.active.get(n,False): self._bubble(p,n,text,self.pos[n][0],self.pos[n][1])

    def _bubble(self,p,name,text,x,y):
        # Character-wrap Korean text so the bubble cannot render as an empty box.
        clean=str(text).replace('\n',' '); lines=[]; current=''
        for ch in clean:
            current+=ch
            if len(current)>=19: lines.append(current); current=''
        if current: lines.append(current)
        lines=lines[:5]
        bw=max(180,min(330,max(len(v) for v in lines)*9+30)); bh=18+len(lines)*18
        bx=int(x+18); by=int(y-bh-12)
        if bx+bw>1470: bx=int(x-bw+25)
        if bx<10: bx=10
        p.setPen(QColor('#b9a985')); p.setBrush(QColor('#f4ecda')); p.drawRoundedRect(bx,by,bw,bh,8,8)
        p.setBrush(QColor('#f4ecda')); p.drawPolygon(QPolygon([QPoint(int(x+10),by+bh),QPoint(int(x+27),by+bh),QPoint(int(x+18),by+bh+10)]))
        p.setPen(QColor('#25211d')); p.setFont(QFont('Malgun Gothic',8,QFont.Bold))
        p.drawText(QRect(bx+10,by+5,bw-20,bh-8),Qt.AlignLeft|Qt.AlignVCenter,'\n'.join(lines))
