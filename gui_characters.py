from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

# Compact top-down pixel sprites. Each character is a clean 24x24 sprite.
SPECS={
 '현무':('#4f7657','#263f32','#a79570','turtle'),
 '김선달':('#a75d43','#5d352d','#d8b56f','bird'),
 '이묵':('#60774f','#30432e','#c4ad79','snake'),
 '너부리':('#777b7c','#3d4145','#c5b9a6','raccoon'),
 '알프레도':('#17191d','#08090b','#d5bb6b','cat')}

class PixelCharacter:
    def __init__(self,name): self.name=name; self.frame=0
    def tick(self): self.frame=(self.frame+1)%90
    def paint(self,p,x,y,scale=4):
        main,dark,accent,kind=SPECS[self.name]; s=int(scale); x=int(x); y=int(y)
        def r(px,py,w,h,c): p.setBrush(QColor(c)); p.drawRect(x+px*s,y+py*s,w*s,h*s)
        p.setPen(Qt.NoPen)
        # chair / shadow, seen from above
        r(6,19,12,4,'#272321'); r(4,20,16,2,'#171719')
        # suit shoulders
        r(4,10,16,10,dark); r(2,12,4,6,dark); r(18,12,4,6,dark)
        r(8,11,8,7,'#eee6d4'); r(11,11,2,8,accent)
        r(5,17,5,3,'#171719'); r(14,17,5,3,'#171719')
        # head / species silhouette
        r(6,3,12,9,main); r(8,1,8,3,main)
        if kind=='cat':
            r(6,2,3,4,main); r(15,2,3,4,main)
            r(7,6,10,4,'#202228')
            # black cat + gold glasses
            r(7,6,5,1,accent); r(12,6,5,1,accent); r(7,6,1,3,accent); r(11,6,1,3,accent); r(14,6,1,3,accent); r(17,6,1,3,accent)
            r(9,7,2,1,'#e1c965'); r(14,7,2,1,'#e1c965'); r(11,7,3,1,accent)
            r(10,9,4,1,'#c8b69a')
        elif kind=='turtle':
            r(5,6,14,9,dark); r(7,5,10,10,main); r(9,7,6,6,'#6f8d5c')
            r(11,5,2,10,'#9aaa70'); r(8,9,8,2,'#9aaa70')
            r(2,9,5,5,main); r(17,9,5,5,main); r(18,5,4,5,'#b5a47d')
            r(19,6,1,1,'#171719')
        elif kind=='bird':
            r(7,2,3,3,main); r(14,2,3,3,main); r(7,5,10,7,main)
            r(8,6,3,3,'#eee6d4'); r(13,6,3,3,'#eee6d4'); r(9,7,1,1,'#171719'); r(14,7,1,1,'#171719')
            r(17,8,5,2,accent); r(20,9,2,1,'#b86d3d')
        elif kind=='snake':
            r(6,4,12,8,main); r(8,5,8,6,'#587047')
            for px in (8,11,14): r(px,5,1,1,accent)
            r(8,7,3,2,'#d0b27e'); r(13,7,3,2,'#d0b27e'); r(9,7,1,2,'#171719'); r(14,7,1,2,'#171719')
            r(10,10,5,1,dark); r(12,11,1,3,'#b76c70'); r(11,14,1,1,'#b76c70'); r(13,14,1,1,'#b76c70')
        else:
            r(6,2,3,4,main); r(15,2,3,4,main); r(7,5,10,7,main)
            r(7,7,4,3,dark); r(13,7,4,3,dark); r(8,7,2,2,'#d8c875'); r(14,7,2,2,'#d8c875'); r(9,8,1,1,'#171719'); r(15,8,1,1,'#171719'); r(10,10,4,2,'#c7b99e')

class CharacterLayer:
    # left-to-right: door -> Hyeonmu -> Seondal -> Imuk -> Neoburi -> isolated Alfredo
    POSITIONS={'현무':(125,365,0),'김선달':(395,365,0),'이묵':(665,365,0),'너부리':(935,365,0),'알프레도':(1225,365,0)}
    def __init__(self): self.characters={n:PixelCharacter(n) for n in self.POSITIONS}
    def tick(self):
        for c in self.characters.values(): c.tick()
    def paint(self,p):
        for n,(x,y,_) in self.POSITIONS.items(): self.characters[n].paint(p,x,y,4)
