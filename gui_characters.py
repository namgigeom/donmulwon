from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

SPECS = {
    '현무': ('#5f8a5b', '#274735', '#b99a63'),
    '김선달': ('#25272c', '#0b0d12', '#b59a68'),
    '이묵': ('#6c8552', '#263a29', '#c4a96f'),
    '너부리': ('#8b8178', '#4b413d', '#c6ad80'),
    '알프레도': ('#202126', '#08090d', '#d8bd72'),
}

class PixelCharacter:
    def __init__(self, name): self.name=name; self.frame=0
    def tick(self): self.frame=(self.frame+1)%90
    def paint(self,p,x,y,scale=2):
        s=max(1,int(scale)); x,y=int(x),int(y); main,dark,accent=SPECS[self.name]; p.setPen(Qt.NoPen)
        def R(px,py,w,h,color): p.setBrush(QColor(color)); p.drawRect(x+px*s,y+py*s,w*s,h*s)
        R(7,29,18,2,'#171719'); R(5,30,22,1,'#24211e'); R(8,16,16,12,'#191a1e'); R(6,19,3,7,dark); R(23,19,3,7,dark); R(10,17,12,9,'#353238'); R(12,18,8,8,'#25262b'); R(14,19,4,7,accent); R(15,20,2,6,'#16171a'); R(10,26,4,4,'#101116'); R(18,26,4,4,'#101116'); R(9,29,5,2,'#30252a'); R(18,29,5,2,'#30252a')
        if self.name=='알프레도': self._cat(R)
        elif self.name=='김선달': self._crow(R)
        elif self.name=='현무': self._turtle(R)
        elif self.name=='이묵': self._snake(R)
        else: self._raccoon(R)
    def _cat(self,R):
        for a in [(8,4,16,14,'#202126'),(7,6,18,10,'#202126'),(9,2,5,5,'#08090d'),(18,2,5,5,'#08090d'),(10,3,3,3,'#383941'),(19,3,3,3,'#383941'),(10,9,12,6,'#17181d'),(12,12,8,4,'#34353a'),(14,13,4,2,'#8d8580'),(10,9,4,3,'#d8bd72'),(18,9,4,3,'#d8bd72'),(12,9,1,3,'#08090d'),(19,9,1,3,'#08090d'),(15,14,2,1,'#08090d'),(11,15,4,1,'#aaa0a0'),(17,15,4,1,'#aaa0a0'),(9,8,7,1,'#d8bd72'),(17,8,7,1,'#d8bd72'),(9,9,1,4,'#d8bd72'),(23,9,1,4,'#d8bd72'),(15,9,2,1,'#d8bd72'),(10,12,5,1,'#d8bd72'),(19,12,4,1,'#d8bd72'),(14,17,4,2,'#7a1f2c'),(15,19,2,3,'#b34b52')]: R(*a)
    def _crow(self,R):
        for a in [(8,4,16,13,'#25272c'),(6,7,18,9,'#0b0d12'),(9,3,4,4,'#0b0d12'),(19,3,4,4,'#0b0d12'),(8,6,3,3,'#3d4048'),(20,6,4,3,'#343740'),(7,11,5,5,'#15171c'),(20,11,6,5,'#15171c'),(9,14,14,4,'#30333a'),(11,9,3,3,'#d7c58c'),(18,9,3,3,'#d7c58c'),(12,9,1,2,'#08090d'),(19,9,1,2,'#08090d'),(23,11,6,3,'#15171b'),(24,13,4,2,'#5a4a3d'),(14,16,4,2,'#8d2630'),(15,18,2,4,'#b14a50'),(7,15,3,6,'#454850'),(22,15,3,6,'#454850')]: R(*a)
    def _turtle(self,R):
        for a in [(7,5,18,16,'#274735'),(5,8,22,10,'#274735'),(9,4,14,18,'#5f8a5b'),(11,6,10,14,'#719d65'),(14,6,2,14,'#385b3e'),(9,11,14,2,'#385b3e'),(12,8,6,2,'#8cb276'),(12,16,6,2,'#8cb276'),(11,1,10,7,'#5f8a5b'),(9,3,14,6,'#5f8a5b'),(11,5,10,5,'#8eab75'),(12,6,2,2,'#151719'),(18,6,2,2,'#151719'),(5,10,5,5,'#5f8a5b'),(22,10,5,5,'#5f8a5b'),(7,18,5,6,'#5f8a5b'),(20,18,5,6,'#5f8a5b'),(13,20,6,2,'#25262b'),(14,21,4,4,'#b99a63')]: R(*a)
    def _snake(self,R):
        for a in [(9,4,14,11,'#263a29'),(7,7,18,8,'#6c8552'),(10,5,12,7,'#6c8552'),(12,7,3,3,'#b4c281'),(18,7,3,3,'#b4c281'),(13,8,1,2,'#101116'),(19,8,1,2,'#101116'),(9,11,3,2,'#3f5b3b'),(13,11,3,2,'#3f5b3b'),(17,11,3,2,'#3f5b3b'),(21,11,3,2,'#3f5b3b'),(23,13,5,1,'#a64b5b'),(27,12,2,1,'#a64b5b'),(27,14,2,1,'#a64b5b'),(11,15,12,10,'#25262b'),(14,16,6,7,'#31343a'),(15,16,4,2,'#c4a96f'),(16,18,2,5,'#16171a'),(10,24,5,5,'#15161a'),(19,24,5,5,'#15161a')]: R(*a)
    def _raccoon(self,R):
        for a in [(7,5,18,13,'#8b8178'),(5,8,22,8,'#8b8178'),(8,3,5,5,'#4b413d'),(19,3,5,5,'#4b413d'),(10,6,12,10,'#a99d90'),(8,9,16,5,'#4b413d'),(11,9,4,4,'#625850'),(17,9,4,4,'#625850'),(12,10,2,2,'#d8c875'),(18,10,2,2,'#d8c875'),(12,10,1,2,'#17181a'),(18,10,1,2,'#17181a'),(14,13,4,3,'#c9b9a8'),(15,13,2,1,'#201f20'),(22,17,6,5,'#8b8178'),(25,19,5,5,'#8b8178'),(27,22,3,4,'#4b413d'),(24,20,3,2,'#4b413d'),(14,17,4,2,'#31506b'),(15,19,2,4,'#4d789b')]: R(*a)

class CharacterLayer:
    POSITIONS={'현무':(110,304,0),'김선달':(375,304,0),'이묵':(640,304,0),'너부리':(905,304,0),'알프레도':(1229,304,0)}
    IN_ORDER=['알프레도','김선달','이묵','너부리','현무']; OUT_ORDER=['김선달','이묵','너부리','현무','알프레도']; DOOR=(58.0,285.0)
    def __init__(self):
        self.characters={n:PixelCharacter(n) for n in self.POSITIONS}; self.pos={n:(float(v[0]),float(v[1])) for n,v in self.POSITIONS.items()}; self.active={n:True for n in self.POSITIONS}; self.mode='idle'; self.queue=[]; self.sequence=[]; self.index=0; self.ticks=0; self.move_speed=5; self.office_open=True
    def set_office_hours(self, hour):
        open_now=9.0 <= hour < 18.0
        if open_now==self.office_open: return
        self.office_open=open_now
        if open_now:
            self.start_arrival()
        else:
            self.start_departure()
    def tick(self):
        for c in self.characters.values(): c.tick()
        for n in list(self.queue):
            tx,ty=self.DOOR if self.mode=='leaving' else self.POSITIONS[n][:2]; x,y=self.pos[n]; dx,dy=tx-x,ty-y; d=(dx*dx+dy*dy)**0.5; speed=12 if self.mode=='summoned' else self.move_speed
            if d<=speed: self.pos[n]=(float(tx),float(ty)); self.queue.remove(n); self.active[n]=self.mode!='leaving'
            else: self.pos[n]=(x+dx/d*speed,y+dy/d*speed)
        self.ticks+=1
        if self.mode in ('arriving','leaving') and self.index<len(self.sequence) and (self.ticks==1 or self.ticks>=60):
            self.ticks=0; n=self.sequence[self.index]; self.index+=1; self.active[n]=True; self.pos[n]=self.DOOR if self.mode=='arriving' else tuple(map(float,self.POSITIONS[n][:2])); self.queue.append(n)
    def start_arrival(self):
        self.mode='arriving'; self.move_speed=5; self.sequence=self.IN_ORDER; self.index=0; self.ticks=0; self.queue=[]
        for n in self.POSITIONS: self.active[n]=False; self.pos[n]=self.DOOR
    def start_departure(self):
        self.mode='leaving'; self.move_speed=5; self.sequence=self.OUT_ORDER; self.index=0; self.ticks=0; self.queue=[]
    def reset_office(self):
        self.mode='idle'; self.queue=[]; self.sequence=[]; self.index=0; self.ticks=0
        for n,(x,y,_) in self.POSITIONS.items(): self.pos[n]=(float(x),float(y)); self.active[n]=True
    def summon_for_question(self,overtime=False):
        self.queue=[]; self.sequence=[]; self.index=0; self.ticks=0
        if overtime:
            self.mode='overtime'; self.move_speed=5
            for n,(x,y,_) in self.POSITIONS.items(): self.active[n]=True; self.pos[n]=(float(x),float(y))
            return
        self.mode='summoned'; self.move_speed=12
        for n in self.POSITIONS:
            if not self.active[n]: self.active[n]=True; self.pos[n]=self.DOOR
            self.queue.append(n)
    def paint(self,p):
        for n in self.POSITIONS:
            if self.active[n]: self.characters[n].paint(p,self.pos[n][0],self.pos[n][1],2)
