import time
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPolygon
from gui_characters import CharacterLayer as BaseCharacterLayer

# Animal-first pixel characters. Only Alfredo keeps clothing/accessories.
PALETTE={
 '현무':{'skin':'#5d8b5b','light':'#91ad72','dark':'#294833','shell':'#345b40','shell2':'#73945c'},
 '김선달':{'skin':'#20242b','light':'#59606a','dark':'#090b10','wing':'#303641','beak':'#c29a55'},
 '이묵':{'skin':'#66864e','light':'#b3c582','dark':'#253827','scale':'#3d5b3a'},
 '너부리':{'skin':'#93887e','light':'#c8b8a7','dark':'#4d4540','mask':'#403b3a','tail':'#756a63'},
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
  R(11,2,14,8,c['skin']); R(8,6,20,7,c['skin']); R(13,7,4,4,c['dark']); R(22,7,4,4,c['dark']); R(14,8,3,2,c['light']); R(22,8,3,2,c['light'])
  R(8,11,23,18,c['shell']); R(5,15,29,10,c['shell']); R(11,11,17,18,c['shell2'])
  for px,py,w,h in [(14,12,3,6),(21,12,3,6),(11,18,6,3),(18,17,5,5),(25,18,4,3),(14,23,5,5),(21,23,6,5)]: R(px,py,w,h,c['shell'])
  R(5,14,7,7,c['skin']); R(28,14,7,7,c['skin']); R(7,26,7,7,c['skin']); R(26,26,7,7,c['skin'])
  R(9,20,5,8,c['skin']); R(26,20,5,8,c['skin'])
 def crow(self,R,c):
  R(10,3,20,10,c['dark']); R(7,7,27,12,c['skin']); R(9,5,6,5,c['dark']); R(23,5,6,5,c['dark']); R(12,8,5,4,c['light']); R(22,8,5,4,c['light']); R(13,9,2,3,c['dark']); R(23,9,2,3,c['dark']); R(29,11,10,4,c['beak']); R(31,14,6,3,c['dark'])
  R(5,16,11,12,c['wing']); R(25,16,11,12,c['wing']); R(9,22,8,10,c['skin']); R(24,22,8,10,c['skin']); R(11,30,7,5,c['dark']); R(24,30,7,5,c['dark']); R(4,31,9,3,c['beak']); R(29,31,9,3,c['beak'])
 def snake(self,R,c):
  R(10,3,20,13,c['skin']); R(8,7,25,12,c['skin']); R(12,5,15,7,c['light']); R(14,8,3,3,c['dark']); R(23,8,3,3,c['dark']); R(28,12,9,2,c['light']); R(35,11,3,1,'#d05a69'); R(35,14,3,1,'#d05a69')
  for px,py in [(10,14),(14,15),(18,14),(22,15),(26,14),(30,15)]: R(px,py,2,2,c['scale'])
  R(9,19,24,8,c['skin']); R(7,23,10,6,c['skin']); R(27,22,9,7,c['skin']); R(10,28,10,5,c['dark']); R(24,29,10,4,c['dark'])
 def raccoon(self,R,c):
  R(10,4,20,13,c['skin']); R(7,8,26,12,c['skin']); R(9,4,6,6,c['dark']); R(23,4,6,6,c['dark']); R(11,7,18,11,c['light']); R(8,10,25,7,c['mask']); R(12,10,6,5,c['dark']); R(22,10,6,5,c['dark']); R(14,11,3,3,'#dfcf7a'); R(23,11,3,3,'#dfcf7a'); R(15,12,1,3,c['dark']); R(23,12,1,3,c['dark']); R(17,16,6,4,c['light'])
  R(9,20,24,11,c['skin']); R(6,22,8,7,c['skin']); R(27,21,8,8,c['skin']); R(28,20,7,7,c['tail']); R(33,24,6,7,c['skin']); R(29,29,7,5,c['tail']); R(12,30,7,5,c['dark']); R(24,30,7,5,c['dark'])
 def cat(self,R,c):
  # Alfredo is the only one with office clothing and glasses.
  R(10,4,20,13,c['skin']); R(7,8,26,12,c['skin']); R(9,2,7,7,c['dark']); R(23,2,7,7,c['dark']); R(12,5,4,4,c['ear']); R(24,5,4,4,c['ear']); R(11,8,18,10,c['skin']); R(12,10,6,4,c['glass']); R(22,10,6,4,c['glass']); R(14,11,2,3,c['dark']); R(23,11,2,3,c['dark']); R(18,13,4,2,c['light']); R(16,16,8,3,c['light']); R(19,17,2,2,c['dark'])
  R(11,20,23,11,c['suit']); R(18,20,4,9,c['tie']); R(30,22,5,5,c['skin']); R(33,19,4,6,c['skin']); R(35,16,3,5,c['light']); R(12,31,7,4,c['dark']); R(24,31,7,4,c['dark'])

class CharacterLayer(BaseCharacterLayer):
 DESKS={'현무':(55,244,175),'김선달':(320,244,175),'이묵':(585,244,175),'너부리':(850,244,175),'알프레도':(1115,244,175)}
 POSITIONS={n:(x+w//2-40,166,0) for n,(x,y,w) in DESKS.items()}
 MEETING_POSITIONS={'현무':(480,500),'김선달':(620,500),'이묵':(760,500),'너부리':(900,500),'알프레도':(1040,500)}
 DOOR=(58.0,205.0)
 def __init__(self):
  super().__init__(); self.characters={n:PixelCharacter(n) for n in self.POSITIONS}; self.pos={n:(float(v[0]),float(v[1])) for n,v in self.POSITIONS.items()}; self.active={n:True for n in self.POSITIONS}; self.mode='idle'; self.queue=[]; self.move_speed=28; self.bubbles={}; self.bubble_until={}; self.stage='idle'; self.office_open=9<=time.localtime().tm_hour<18
  if not self.office_open:self.reset_off_hours()
 def set_office_hours(self,hour,immediate=False):
  open_now=9<=hour<18
  if open_now==self.office_open:
   if immediate and self.mode not in ('meeting_arrival','meeting','verdict'): self.reset_office() if open_now else self.reset_off_hours()
   return
  self.office_open=open_now; self.reset_office() if open_now else self.reset_off_hours()
 def reset_office(self):
  self.mode='idle';self.stage='idle';self.queue=[];self.clear_bubbles()
  for n,(x,y,_) in self.POSITIONS.items():self.active[n]=True;self.pos[n]=(float(x),float(y))
 def reset_off_hours(self):
  self.mode='off_hours';self.stage='idle';self.queue=[];self.clear_bubbles()
  for n in self.POSITIONS:self.active[n]=False;self.pos[n]=self.DOOR
 def summon_for_question(self,overtime=False):
  self.mode='meeting_arrival';self.stage='summon';self.move_speed=28;self.queue=[];self.clear_bubbles()
  for n in self.POSITIONS:self.active[n]=True;self.pos[n]=self.DOOR;self.queue.append(n)
  self.set_bubble('알프레도','긴급 호출이다. 전원 회의실로!',2400)
 def set_meeting_stage(self,stage):
  if stage=='summon': self.summon_for_question()
  elif stage=='meeting':
   self.mode='meeting';self.stage='meeting';self.queue=[]
   for n in self.POSITIONS:self.active[n]=True;self.pos[n]=(float(self.MEETING_POSITIONS[n][0]),float(self.MEETING_POSITIONS[n][1]))
  elif stage=='verdict': self.mode='verdict';self.stage='verdict';self.queue=[]
  elif stage=='return': self.reset_office() if self.office_open else self.reset_off_hours()
 def set_bubble(self,name,text,duration_ms=3600):
  if name not in self.POSITIONS:return
  self.bubbles[name]=str(text)[:170];self.bubble_until[name]=time.time()+duration_ms/1000.0
 def set_meeting_log(self,log):
  # Show the actual four agents' latest readable lines after the analysis finishes.
  patterns={'현무':r'(?:현무)[^\n:：]*[:：]\s*(.+)','김선달':r'(?:김선달)[^\n:：]*[:：]\s*(.+)','이묵':r'(?:이묵)[^\n:：]*[:：]\s*(.+)','너부리':r'(?:너부리)[^\n:：]*[:：]\s*(.+)'}
  for name,pat in patterns.items():
   m=None
   for match in __import__('re').finditer(pat,log): m=match
   if m:self.set_bubble(name,m.group(1).strip(),7000)
 def show_final_verdict(self,error=False):
  self.mode='verdict';self.stage='verdict';self.clear_bubbles();self.set_bubble('알프레도','분석완료! 회의완료! 최종 판단을 정리하겠습니다.',6000)
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
   if not self.queue:
    self.mode='meeting';self.stage='meeting'
    self.set_bubble('현무','거시환경부터 보겠습니다. 시장 분위기부터 확인하죠.',5000)
    self.set_bubble('김선달','기업 실적과 최근 뉴스 흐름은 이렇습니다.',5000)
    self.set_bubble('이묵','차트상 가격과 추세는 조금 다르게 보입니다.',5000)
    self.set_bubble('너부리','현재 계좌 비중까지 같이 봐야 합니다.',5000)
 def paint(self,p):
  for n in self.POSITIONS:
   if self.active[n]:self.characters[n].paint(p,self.pos[n][0],self.pos[n][1],2)
  for n,text in list(self.bubbles.items()):
   if self.active.get(n,False):self._bubble(p,n,text,self.pos[n][0],self.pos[n][1])
 def _bubble(self,p,name,text,x,y):
  words=str(text).split(); lines=[]; line=''
  for word in words:
   test=(line+' '+word).strip()
   if len(test)>27 and line:lines.append(line);line=word
   else:line=test
  if line:lines.append(line)
  lines=lines[:4]; bw=max(170,min(360,max([len(v) for v in lines] or [10])*8+30)); bh=24+len(lines)*18; bx=int(x+18); by=int(y-bh-10)
  if bx+bw>1470:bx=int(x-bw+25)
  if bx<10:bx=10
  p.setPen(QColor('#d6c7a5'));p.setBrush(QColor('#f1eadb'));p.drawRoundedRect(bx,by,bw,bh,7,7);p.setBrush(QColor('#f1eadb'));p.drawPolygon(QPolygon([Qt.QPoint(int(x+12),by+bh),Qt.QPoint(int(x+27),by+bh),Qt.QPoint(int(x+18),by+bh+10)]));p.setPen(QColor('#29251f'));p.setFont(QFont('Malgun Gothic',8,QFont.Bold));p.drawText(QRect(bx+10,by+7,bw-20,bh-10),Qt.AlignLeft|Qt.AlignVCenter,'\n'.join(lines))
