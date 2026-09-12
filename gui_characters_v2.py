from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from gui_characters import CharacterLayer as BaseCharacterLayer

# Detailed 40x40 logical-pixel top-down sprites.
# Animals remain animals; the only "human" convention is the business suit.
# The silhouettes are deliberately different so no agent looks like a blob.

PALETTE = {
    '현무': {'body':'#587f55','light':'#8eaa70','dark':'#294433','shell':'#345b40','shell2':'#71935b','suit':'#202328','tie':'#b99a63'},
    '김선달': {'body':'#17191f','light':'#4a4e58','dark':'#080a0f','wing':'#242832','beak':'#75624b','suit':'#1d2026','tie':'#8d2630'},
    '이묵': {'body':'#66814e','light':'#afbf78','dark':'#263827','scale':'#3f5c3b','suit':'#22252a','tie':'#6f8fb0'},
    '너부리': {'body':'#91877e','light':'#c1b3a4','dark':'#514842','mask':'#403b39','tail':'#776b64','suit':'#24262b','tie':'#527694'},
    '알프레도': {'body':'#181a20','light':'#343740','dark':'#08090d','ear':'#3b2630','suit':'#17191e','tie':'#9d3038','glass':'#d9bd72'},
}

class PixelCharacter:
    def __init__(self, name):
        self.name = name
        self.frame = 0

    def tick(self):
        self.frame = (self.frame + 1) % 60

    def paint(self, p, x, y, scale=2):
        s = max(1, int(scale)); x = int(x); y = int(y); c = PALETTE[self.name]
        p.setPen(Qt.NoPen)
        def R(px,py,w,h,col):
            p.setBrush(QColor(col)); p.drawRect(x+px*s,y+py*s,w*s,h*s)
        # pixel contact shadow
        R(8,36,24,2,'#111216'); R(5,38,30,1,'#242326')
        # suit jacket first: visible under the animal head/shell/wing
        R(9,22,22,12,c['suit']); R(7,25,4,8,c['dark']); R(29,25,4,8,c['dark'])
        R(12,23,16,10,'#303239'); R(15,24,10,9,c['suit'])
        R(18,24,4,10,c['tie']); R(19,27,2,7,'#101116')
        R(10,33,7,4,'#101216'); R(23,33,7,4,'#101216')
        if self.name == '알프레도': self.cat(R,c)
        elif self.name == '김선달': self.crow(R,c)
        elif self.name == '이묵': self.snake(R,c)
        elif self.name == '현무': self.turtle(R,c)
        else: self.raccoon(R,c)

    def cat(self,R,c):
        # 40x40 black cat, glasses are the signature.
        R(9,6,22,17,c['dark']); R(7,10,26,11,c['body'])
        R(10,3,7,7,c['dark']); R(23,3,7,7,c['dark'])
        R(12,5,4,4,c['ear']); R(24,5,4,4,c['ear'])
        R(10,12,20,7,c['body']); R(13,16,14,5,c['light'])
        # eyes
        R(11,12,6,4,c['glass']); R(23,12,6,4,c['glass']); R(13,13,2,3,c['dark']); R(25,13,2,3,c['dark'])
        # unmistakable gold glasses frame
        R(9,11,9,1,c['glass']); R(22,11,9,1,c['glass']); R(9,12,1,6,c['glass']); R(29,12,1,6,c['glass']); R(19,12,3,1,c['glass']); R(10,17,8,1,c['glass']); R(22,17,8,1,c['glass'])
        # muzzle/nose/whiskers
        R(16,17,8,4,c['light']); R(19,18,2,1,c['dark']); R(13,20,6,1,c['light']); R(21,20,6,1,c['light'])
        # tail curling beside suit
        R(29,27,5,4,c['body']); R(32,25,4,5,c['body']); R(34,22,3,5,c['body']); R(35,19,2,4,c['light'])
        R(18,22,4,2,c['tie'])

    def crow(self,R,c):
        # Black crow: beak + broad folded wings.
        R(10,6,20,15,c['dark']); R(7,10,24,10,c['body']); R(11,4,6,6,c['dark']); R(23,4,6,6,c['dark'])
        R(9,12,8,7,c['wing']); R(23,12,8,7,c['wing']); R(7,17,7,10,c['dark']); R(27,17,7,10,c['dark'])
        R(12,11,5,4,'#c8b982'); R(23,11,5,4,'#c8b982'); R(14,12,2,3,c['dark']); R(24,12,2,3,c['dark'])
        R(29,14,9,4,c['dark']); R(34,16,5,3,c['beak']); R(29,18,7,2,c['dark'])
        # feather pixels
        for px,py in [(9,20),(12,22),(15,19),(25,20),(28,22),(31,19)]: R(px,py,3,3,c['light'])
        R(18,21,4,2,c['tie']); R(19,23,2,5,'#b14a50')
        # tail feathers
        R(12,27,5,7,c['dark']); R(16,28,4,7,c['wing']); R(24,28,4,7,c['wing']); R(28,27,5,7,c['dark'])

    def snake(self,R,c):
        # Snake has no fake arms/legs: head, coils, tongue and suit collar do the job.
        R(11,5,18,12,c['dark']); R(8,9,25,10,c['body']); R(12,6,16,9,c['body'])
        R(14,8,5,4,c['light']); R(22,8,5,4,c['light']); R(16,9,2,3,c['dark']); R(23,9,2,3,c['dark'])
        # scales, deliberately small
        for px,py in [(10,14),(14,15),(18,14),(22,15),(26,14),(30,15)]: R(px,py,2,2,c['scale'])
        # forked tongue
        R(28,17,7,1,'#a64b5b'); R(34,16,3,1,'#a64b5b'); R(34,18,3,1,'#a64b5b')
        # long coil around the lower suit
        R(7,21,7,5,c['body']); R(6,24,7,6,c['body']); R(9,29,8,5,c['body']); R(27,21,7,5,c['body']); R(29,25,7,6,c['body']); R(25,30,9,5,c['body'])
        R(10,23,3,2,c['scale']); R(8,27,3,2,c['scale']); R(13,31,3,2,c['scale']); R(29,27,3,2,c['scale'])
        R(17,21,6,3,'#d0bd8b'); R(18,24,4,2,c['suit']); R(19,26,2,5,c['tie'])

    def turtle(self,R,c):
        # Turtle shell dominates the silhouette; head and four feet remain visible.
        R(8,8,24,21,c['shell']); R(5,13,30,12,c['shell']); R(10,7,20,24,c['shell2'])
        # shell mosaic, many tiny pixels
        R(14,8,4,8,c['shell']); R(20,8,4,8,c['shell']); R(10,14,6,4,c['shell']); R(18,15,5,5,c['shell']); R(25,14,5,4,c['shell']); R(13,21,5,7,c['shell']); R(20,21,6,7,c['shell'])
        R(15,11,2,2,c['light']); R(21,11,2,2,c['light']); R(11,16,2,2,c['light']); R(26,17,2,2,c['light']); R(17,24,2,2,c['light']); R(22,23,2,2,c['light'])
        # head
        R(14,2,12,8,c['body']); R(11,5,18,7,c['body']); R(14,7,12,5,c['light']); R(14,7,3,3,c['dark']); R(23,7,3,3,c['dark'])
        # feet
        R(4,14,7,6,c['body']); R(29,14,7,6,c['body']); R(7,27,7,7,c['body']); R(26,27,7,7,c['body'])
        # tiny suit/tie visible at neck
        R(17,19,6,3,c['suit']); R(19,21,2,5,c['tie'])

    def raccoon(self,R,c):
        # Raccoon mask + ringed tail gives a clean silhouette.
        R(9,7,22,17,c['body']); R(7,11,26,10,c['body']); R(11,4,6,6,c['dark']); R(23,4,6,6,c['dark'])
        R(12,7,16,12,c['light']); R(8,12,24,6,c['mask']); R(12,12,6,5,c['dark']); R(22,12,6,5,c['dark'])
        R(14,13,3,3,'#d9c875'); R(23,13,3,3,'#d9c875'); R(15,13,1,3,c['dark']); R(23,13,1,3,c['dark'])
        R(17,17,6,4,c['light']); R(19,18,2,1,c['dark'])
        # striped tail, clearly visible from above
        R(28,22,6,6,c['tail']); R(32,25,5,6,c['body']); R(34,29,4,5,c['tail']); R(31,31,4,4,c['body']); R(27,33,6,4,c['tail'])
        R(29,23,3,2,c['dark']); R(33,27,3,2,c['dark']); R(30,31,3,2,c['dark'])
        R(18,21,4,2,c['tie']); R(19,23,2,5,'#6f9abb')

class CharacterLayer(BaseCharacterLayer):
    """Drop-in replacement for the existing motion system with richer sprites."""
    def __init__(self):
        super().__init__()
        self.characters = {n: PixelCharacter(n) for n in self.POSITIONS}
