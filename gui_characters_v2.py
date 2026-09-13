import os, json, time
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPolygon
from gui_characters import CharacterLayer as BaseCharacterLayer

# Pixel-art palette. Every character is deliberately recognizable as an animal,
# while wearing a suit appropriate for the trading office.
PALETTE={
 '현무':{'skin':'#5d8b5b','light':'#91ad72','dark':'#294833','shell':'#345b40','shell2':'#73945c','suit':'#20252a','tie':'#b99a63'},
 '김선달':{'skin':'#20242b','light':'#59606a','dark':'#090b10','wing':'#303641','beak':'#c29a55','suit':'#1d2025','tie':'#9d3440'},
 '이묵':{'skin':'#66864e','light':'#b3c582','dark':'#253827','scale':'#3d5b3a','suit':'#20242a','tie':'#668db1'},
 '너부리':{'skin':'#93887e','light':'#c8b8a7','dark':'#4d4540','mask':'#403b3a','tail':'#756a63','suit':'#24272b','tie':'#557c9d'},
 '알프레도':{'skin':'#191b21','light':'#3d4049','dark':'#07080c','ear':'#613344','suit':'#17191e','tie':'#b63b49','glass':'#dfc476'}
}

class PixelCharacter:
 def __init__(self,name): self.name=name; self.frame=0
 def tick(self): self.frame=(self.frame+1)%60
 def paint(self,p,x,y,scale=2):
  s=max(1,int(scale)); x=int(x); y=int(y); c=PALETTE[self.name]; p.setPen(Qt.NoPen)
  def R(px,py,w,h,col): p.setBrush(QColor(col)); p.drawRect(x+px*s,y+py*s,w*s,h*s)
  if self.name=='현무': self.turtle(R,c)
  elif self.name=='김선달': self.crow(R,c)
  elif self.name=='이묵': self.snake(R,c)
  elif self.name=='너부리': self.raccoon(R,c)
  else: self.cat(R,c)
 def turtle(self,R,c):
  # Head, neck and four feet are intentionally visible around a large shell.
  R(11,2,14,8,c['skin']); R(8,6,20,7,c['skin']); R(13,7,4,4,c['dark']); R(22,7,4,4,c['dark'])
  R(14,8,3,2,c['light']); R(22,8,3,2,c['light']); R(8,11,23,18,c['shell']); R(5,15,29,10,c['shell'])
  R(11,11,17,18,c['shell2']); R(14,12,3,6,c['shell']); R(21,12,3,6,c['shell']); R(11,18,6,3,c['shell']); R(18,17,5,5,c['shell']); R(25,18,4,3,c['shell']); R(14,23,5,5,c['shell']); R(21,23,6,5,c['shell'])
  R(5,14,7,7,c['skin']); R(28,14,7,7,c['skin']); R(7,26,7,7,c['skin']); R(26,26,7,7,c['skin'])
  R(15,20,9,8,c['suit']); R(18,21,3,7,c['tie']); R(10,31,7,3,c['suit']); R(22,31,7,3,c['suit'])
 def crow(self,R,c):
  R(10,3,20,10,c['dark']); R(7,7,27,12,c['skin']); R(9,5,6,5,c['dark']); R(23,5,6,5,c['dark']); R(12,8,5,4,c['light']); R(22,8,5,4,c['light']); R(13,9,2,3,c['dark']); R(23,9,2,3,c['dark']); R(29,11,10,4,c['beak']); R(31,14,6,3,c['dark']); R(7,16,9,9,c['wing']); R(25,16,9,9,c['wing']); R(11,20,23,11,c['suit']); R(18,20,4,9,c['tie']); R(13,29,7,6,c['dark']); R(24,29,7,6,c['dark']); R(8,29,6,4,c['skin']); R(29,29,6,4,c['skin'])
 def snake(self,R,c):
  R(10,3,20,13,c['skin']); R(8,7,25,12,c['skin']); R(12,5,15,7,c['light']); R(14,8,3,3,c['dark']); R(23,8,3,3,c['dark']); R(28,12,9,2,c['light']); R(35,11,3,1,'#d05a69'); R(35,14,3,1,'#d05a69')
  for px,py in [(10,14),(14,15),(18,14),(22,15),(26,14),(30,15)]: R(px,py,2,2,c['scale'])
  R(10,19,24,12,c['suit']); R(17,19,6,4,c['light']); R(19,22,3,8,c['tie']); R(7,23,7,6,c['skin']); R(28,22,7,6,c['skin']); R(10,30,8,4,c['dark']); R(25,30,8,4,c['dark'])
 def raccoon(self,R,c):
  R(10,4,20,13,c['skin']); R(7,8,26,12,c['skin']); R(9,4,6,6,c['dark']); R(23,4,6,6,c['dark']); R(11,7,18,11,c['light']); R(8,10,25,7,c['mask']); R(12,10,6,5,c['dark']); R(22,10,6,5,c['dark']); R(14,11,3,3,'#dfcf7a'); R(23,11,3,3,'#dfcf7a'); R(15,12,1,3,c['dark']); R(23,12,1,3,c['dark']); R(17,16,6,4,c['light']); R(11,20,23,11,c['suit']); R(18,20,4,9,c['tie']); R(28,21,7,7,c['tail']); R(33,25,6,7,c['skin']); R(29,29,7,5,c['tail']); R(12,31,7,4,c['dark']); R(24,31,7,4,c['dark'])
 def cat(self,R,c):
  R(10,4,20,13,c['skin']); R(7,8,26,12,c['skin']); R(9,2,7,7,c['dark']); R(23,2,7,7,c['dark']); R(12,5,4,4,c['ear']); R(24,5,4,4,c['ear']); R(11,8,18,10,c['skin']); R(12,10,6,4,c['glass']); R(22,10,6,4,c['glass']); R(14,11,2,3,c['dark']); R(23,11,2,3,c['dark']); R(18,13,4,2,c['light']); R(16,16,8,3,c['light']); R(19,17,2,2,c['dark']); R(11,20,23,11,c['suit']); R(18,20,4,9,c['tie']); R(30,22,5,5,c['skin']); R(33,19,4,6,c['skin']); R(35,16,3,5,c['light']); R(12,31,7,4,c['dark']); R(24,31,7,4,c['dark'])

class CharacterLayer(BaseCharacterLayer):
 # Origin is the character's top-left. Each origin is centered on its own desk,
 # with the feet/seat line aligned to the front edge of that desk.
 DESKS={'현무':(55,244,175),'김선달':(320,244,175),'이묵':(585,244,175),'너부리':(850,244,175),'알프레도':(1115,244,175)}
 POSITIONS={n:(x+w//2-40,182,0) for n,(x,y,w) in DESKS.items()}
 # During a meeting they gather around the actual meeting table at the bottom.
 MEETING_POSITIONS={'현무':(480,500),'김선달':(620,500),'이묵':(760,500),'너부리':(900,500),'알프레도':(1040,500)}
 DOOR=(58.0,205.0)
 def __init__(self):
  super().__init__(); self.characters={n:PixelCharacter(n) for n in self.POSITIONS}; self.pos={n:(float(v[0]),float(v[1])) for n,v in self.POSITIONS.items()}; self.active={n:True for n in self.POSITIONS}; self.mode='idle'; self.queue=[]; self.move_speed=22; self.bubbles={}; self.bubble_until={}; self.stage='idle'
  now=time.localtime(); self.office_open=9<=now.tm_hour<18
  if not self.office_open:
   self.mode='off_hours'
   for n in self.POSITIONS:self.active[n]=False;self.pos[n]=self.DOOR
 def set_office_hours(self,hour,immediate=False):
  open_now=9<=hour<18
  if open_now==self.office_open:
   if immediate and self.mode not in ('meeting_arrival','meeting','verdict'): self.reset_office() if open_now else self.reset_off_hours()
   return
  self.office_open=open_now
  self.reset_office() if open_now else self.reset_off_hours()
 def reset_office(self):
  self.mode='idle';self.stage='idle';self.queue=[];self.bubbles={}
  for n,(x,y,_) in self.POSITIONS.items():self.active[n]=True;self.pos[n]=(float(x),float(y))
 def reset_off_hours(self):
  self.mode='off_hours';self.stage='idle';self.queue=[];self.bubbles={}
  for n in self.POSITIONS:self.active[n]=False;self.pos[n]=self.DOOR
 def summon_for_question(self,overtime=False):
  self.mode='meeting_arrival';self.stage='summon';self.move_speed=28;self.queue=[];self.bubbles={}
  for n in self.POSITIONS:
   self.active[n]=True;self.pos[n]=self.DOOR;self.queue.append(n)
 def set_meeting_stage(self,stage):
  if stage=='summon':self.summon_for_question()
  elif stage=='meeting':
   self.mode='meeting';self.stage='meeting';self.move_speed=28;self.queue=[]
   for n in self.POSITIONS:self.active[n]=True;self.pos[n]=(float(self.MEETING_POSITIONS[n][0]),float(self.MEETING_POSITIONS[n][1]))
  elif stage=='verdict':self.mode='verdict';self.stage='verdict';self.queue=[]
  elif stage=='return':self.reset_office() if self.office_open else self.reset_off_hours()
 def set_bubble(self,name,text,duration_ms=3600):
  if name not in self.POSITIONS:return
  self.bubbles[name]=str(text)[:170];self.bubble_until[name]=time.time()+duration_ms/1000.0
 def clear_bubbles(self):self.bubbles={};self.bubble_until={}
 def tick(self):
  now=time.time()
  for c in self.characters.values():c.tick()
  for n,t in list(self.bubble_until.items()):
   if now>t:self.bubble_until.pop(n,None);self.bubbles.pop(n,None)
  if self.mode=='meeting_arrival':
   remaining=[]
   for n in self.queue:
    tx,ty=self.MEETING_POSITIONS[n];x,y=self.pos[n];dx,dy=tx-x,ty-y;d=(dx*dx+dy*dy)**0.5
    if d<=self.move_speed:self.pos[n]=(float(tx),float(ty))
    else:self.pos[n]=(x+dx/d*self.move_speed,y+dy/d*self.move_speed);remaining.append(n)
   self.queue=remaining
   if not self.queue:self.mode='meeting';self.stage='meeting'
 def paint(self,p):
  # Characters are drawn after the room but before no additional furniture is
  # required here. Their feet align to the desk/chair line.
  for n in self.POSITIONS:
   if self.active[n]:self.characters[n].paint(p,self.pos[n][0],self.pos[n][1],2)
  for n,text in self.bubbles.items():
   if n not in self.active or not self.active[n]:continue
   self._bubble(p,n,text,self.pos[n][0],self.pos[n][1])
 def _bubble(self,p,name,text,x,y):
  lines=[]; words=text.split()
  line=''
  for word in words:
   test=(line+' '+word).strip()
   if len(test)>27 and line:lines.append(line);line=word
   else:line=test
  if line:lines.append(line)
  lines=lines[:4]
  bw=max(150,min(330,max([len(v) for v in lines] or [10])*8+26));bh=25+len(lines)*18
  bx=int(x+18);by=int(y-bh-8)
  if bx+bw>1470:bx=int(x-bw+25)
  if bx<10:bx=10
  p.setPen(QColor('#d6c7a5'));p.setBrush(QColor('#f1eadb'));p.drawRoundedRect(bx,by,bw,bh,7,7)
  p.setBrush(QColor('#f1eadb'));p.drawPolygon(QPolygon([Qt.QPoint(int(x+12),by+bh),Qt.QPoint(int(x+27),by+bh),Qt.QPoint(int(x+18),by+bh+10)]))
  p.setPen(QColor('#29251f'));p.setFont(QFont('Malgun Gothic',8,QFont.Bold));p.drawText(bx+10,by+7,bw-20,bh-10,Qt.AlignLeft|Qt.AlignVCenter,'\n'.join(lines))
