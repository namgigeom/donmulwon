from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
SPECS={'현무':('#4f7657','#263f32','#a79570'),'김선달':('#a75d43','#5d352d','#d8b56f'),'이묵':('#60774f','#30432e','#c4ad79'),'너부리':('#777b7c','#3d4145','#c5b9a6'),'알프레도':('#17191d','#08090b','#d5bb6b')}
class PixelCharacter:
 def __init__(self,name): self.name=name; self.frame=0
 def tick(self): self.frame=(self.frame+1)%90
 def paint(self,p,x,y,scale=4):
  main,dark,accent=SPECS[self.name]; s=int(scale); x=int(x); y=int(y)
  def r(a,b,c,d,col): p.setBrush(QColor(col)); p.drawRect(x+a*s,y+b*s,c*s,d*s)
  p.setPen(Qt.NoPen); r(4,20,16,3,'#171719'); r(4,10,16,10,dark); r(2,12,4,6,dark); r(18,12,4,6,dark); r(8,11,8,7,'#eee6d4'); r(11,11,2,8,accent); r(6,3,12,9,main); r(8,1,8,3,main)
  if self.name=='알프레도':
   r(6,2,3,4,main); r(15,2,3,4,main); r(7,6,10,4,'#202228'); r(7,6,5,1,accent); r(12,6,5,1,accent); r(7,6,1,3,accent); r(11,6,1,3,accent); r(14,6,1,3,accent); r(17,6,1,3,accent); r(9,7,2,1,'#e1c965'); r(14,7,2,1,'#e1c965'); r(11,7,3,1,accent)
  elif self.name=='현무':
   r(5,6,14,9,dark); r(7,5,10,10,main); r(9,7,6,6,'#6f8d5c'); r(11,5,2,10,'#9aaa70'); r(2,9,5,5,main); r(17,9,5,5,main); r(18,5,4,5,'#b5a47d')
  elif self.name=='김선달':
   r(7,2,3,3,main); r(14,2,3,3,main); r(7,5,10,7,main); r(8,6,3,3,'#eee6d4'); r(13,6,3,3,'#eee6d4'); r(9,7,1,1,'#171719'); r(14,7,1,1,'#171719'); r(17,8,5,2,accent)
  elif self.name=='이묵':
   r(6,4,12,8,main); r(8,5,8,6,'#587047'); r(8,7,3,2,'#d0b27e'); r(13,7,3,2,'#d0b27e'); r(9,7,1,2,'#171719'); r(14,7,1,2,'#171719'); r(12,11,1,3,'#b76c70')
  else:
   r(6,2,3,4,main); r(15,2,3,4,main); r(7,5,10,7,main); r(7,7,4,3,dark); r(13,7,4,3,dark); r(8,7,2,2,'#d8c875'); r(14,7,2,2,'#d8c875'); r(9,8,1,1,'#171719'); r(15,8,1,1,'#171719')
class CharacterLayer:
 POSITIONS={'현무':(125,365,0),'김선달':(395,365,0),'이묵':(665,365,0),'너부리':(935,365,0),'알프레도':(1225,365,0)}
 IN_ORDER=['알프레도','김선달','이묵','너부리','현무']; OUT_ORDER=['김선달','이묵','너부리','현무','알프레도']; DOOR=(58.0,285.0)
 def __init__(self):
  self.characters={n:PixelCharacter(n) for n in self.POSITIONS}; self.pos={n:(float(v[0]),float(v[1])) for n,v in self.POSITIONS.items()}; self.active={n:True for n in self.POSITIONS}; self.mode='idle'; self.queue=[]; self.sequence=[]; self.index=0; self.ticks=0; self.move_speed=5
 def tick(self):
  for c in self.characters.values(): c.tick()
  for n in list(self.queue):
   tx,ty=self.DOOR if self.mode=='leaving' else self.POSITIONS[n][:2]; x,y=self.pos[n]; dx,dy=tx-x,ty-y; d=(dx*dx+dy*dy)**0.5
   speed=self.move_speed
   if self.mode=='summoned': speed=12
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
  self.mode='idle'; self.move_speed=5; self.queue=[]; self.sequence=[]; self.index=0; self.ticks=0
  for n,(x,y,_) in self.POSITIONS.items(): self.pos[n]=(float(x),float(y)); self.active[n]=True
 def summon_for_question(self, overtime=False):
  # After-hours questions summon everyone back through the door at a frantic pace.
  # Near closing time, cancel departure and keep everyone working as overtime.
  self.queue=[]; self.sequence=[]; self.index=0; self.ticks=0
  if overtime:
   self.mode='overtime'; self.move_speed=5
   for n,(x,y,_) in self.POSITIONS.items(): self.active[n]=True; self.pos[n]=(float(x),float(y))
   return
  self.mode='summoned'; self.move_speed=12
  for n in self.POSITIONS:
   if not self.active[n]:
    self.active[n]=True; self.pos[n]=self.DOOR
   self.queue.append(n)
 def paint(self,p):
  for n in self.POSITIONS:
   if self.active[n]: self.characters[n].paint(p,self.pos[n][0],self.pos[n][1],4)
