from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


class PixelCharacter:
    """Layered pixel-art character renderer. Uses small logical pixels scaled up."""
    SPECS = {
        "현무": {"kind": "turtle", "body": "#3f674e", "accent": "#89a77a", "skin": "#b9a77d", "suit": "#26352e"},
        "김선달": {"kind": "bird", "body": "#a95f42", "accent": "#e0a55c", "skin": "#d8b889", "suit": "#30343a"},
        "이묵": {"kind": "snake", "body": "#62764f", "accent": "#b9a85f", "skin": "#c8b27f", "suit": "#29362f"},
        "너부리": {"kind": "raccoon", "body": "#777777", "accent": "#c7b79e", "skin": "#b9a58c", "suit": "#34373a"},
        "알프레도": {"kind": "cat", "body": "#17181b", "accent": "#363941", "skin": "#bcae96", "suit": "#111316"},
    }

    def __init__(self, name):
        self.name = name
        self.frame = 0

    def tick(self):
        self.frame = (self.frame + 1) % 48

    def paint(self, p, x, y, scale=4):
        spec = self.SPECS[self.name]
        s = int(scale)
        ox, oy = int(x), int(y)
        # subtle idle animation, never changes the layout
        bob = 0 if self.frame % 24 < 20 else -1
        blink = self.frame % 48 in (42, 43)
        def rect(px, py, w, h, color):
            p.setBrush(QColor(color)); p.setPen(Qt.NoPen)
            p.drawRect(ox + px*s, oy + (py+bob)*s, w*s, h*s)

        body, accent, skin, suit = spec["body"], spec["accent"], spec["skin"], spec["suit"]
        dark = "#090a0c"
        white = "#e8e0cf"
        gold = "#c8aa68"

        # shadow
        rect(8, 69, 34, 3, "#111214")
        # legs / shoes
        rect(14, 58, 9, 13, suit); rect(29, 58, 9, 13, suit)
        rect(11, 68, 13, 4, dark); rect(28, 68, 13, 4, dark)
        # large tailored torso
        rect(9, 29, 35, 31, suit); rect(13, 30, 27, 28, suit)
        rect(19, 31, 5, 24, white); rect(26, 31, 2, 24, "#87534d")
        rect(21, 48, 5, 7, "#713b3b")
        # arms
        rect(3, 31, 8, 24, suit); rect(42, 31, 8, 24, suit)
        rect(2, 51, 10, 7, skin); rect(41, 51, 10, 7, skin)
        # neck/head base
        rect(19, 24, 11, 8, skin)
        rect(11, 6, 28, 20, body); rect(15, 3, 20, 5, body)
        rect(14, 22, 22, 5, skin)

        kind = spec["kind"]
        if kind == "cat":
            # black cat ears + muzzle + round gold glasses
            rect(9, 0, 10, 11, body); rect(31, 0, 10, 11, body)
            rect(12, 3, 5, 5, "#55414a"); rect(33, 3, 5, 5, "#55414a")
            rect(17, 13, 21, 8, body)
            frame = "#d8c8a7"
            rect(12, 9, 12, 2, frame); rect(27, 9, 12, 2, frame)
            rect(12, 9, 2, 10, frame); rect(22, 9, 2, 10, frame)
            rect(27, 9, 2, 10, frame); rect(37, 9, 2, 10, frame); rect(23, 12, 5, 2, frame)
            if blink:
                rect(17, 15, 5, 1, "#d9c98b"); rect(30, 15, 5, 1, "#d9c98b")
            else:
                rect(17, 14, 5, 4, "#e6d27e"); rect(30, 14, 5, 4, "#e6d27e")
                rect(19, 14, 1, 4, dark); rect(32, 14, 1, 4, dark)
            rect(24, 19, 4, 2, "#c88994")
            rect(12, 20, 10, 1, skin); rect(30, 20, 10, 1, skin)
        elif kind == "turtle":
            # shell replaces head/torso details while keeping suit silhouette
            rect(4, 27, 43, 27, body); rect(9, 28, 33, 23, "#315b46")
            rect(13, 31, 25, 16, accent); rect(20, 10, 11, 16, skin); rect(29, 13, 9, 10, skin)
            rect(32, 15, 3, 3, dark)
            rect(8, 45, 9, 10, skin); rect(38, 45, 9, 10, skin)
            rect(17, 31, 3, 8, "#426f56"); rect(29, 30, 3, 9, "#426f56"); rect(13, 39, 27, 3, "#426f56")
        elif kind == "bird":
            rect(12, 2, 21, 7, body); rect(8, 8, 30, 18, body)
            rect(3, 17, 12, 14, body); rect(34, 16, 12, 13, body)
            rect(40, 14, 9, 5, "#d59a45")
            rect(16, 10, 6, 6, white); rect(29, 10, 6, 6, white)
            if not blink: rect(18, 11, 2, 3, dark); rect(31, 11, 2, 3, dark)
            rect(15, 19, 20, 6, "#874936")
        elif kind == "snake":
            rect(9, 2, 28, 7, body); rect(7, 8, 32, 18, body); rect(12, 11, 22, 11, "#536945")
            rect(16, 10, 6, 5, "#d8c47f"); rect(28, 10, 6, 5, "#d8c47f")
            if not blink: rect(18, 11, 2, 3, dark); rect(30, 11, 2, 3, dark)
            rect(3, 19, 11, 7, body); rect(0, 24, 10, 7, body); rect(33, 19, 10, 7, body)
        elif kind == "raccoon":
            rect(8, 2, 12, 9, body); rect(30, 2, 12, 9, body); rect(8, 8, 33, 19, body)
            rect(11, 10, 12, 8, "#4b4d50"); rect(27, 10, 12, 8, "#4b4d50")
            rect(14, 12, 6, 5, skin); rect(30, 12, 6, 5, skin)
            if not blink: rect(16, 13, 2, 3, dark); rect(32, 13, 2, 3, dark)
            rect(20, 18, 12, 7, "#c8b7a0"); rect(24, 20, 4, 3, "#8d5b55")
            rect(6, 21, 9, 9, body); rect(35, 21, 9, 9, body)
        # suit buttons / pixel highlights
        rect(16, 35, 2, 2, gold); rect(16, 43, 2, 2, gold); rect(34, 35, 2, 2, gold); rect(34, 43, 2, 2, gold)


class CharacterLayer:
    POSITIONS = {"현무": (145, 385), "김선달": (420, 385), "이묵": (695, 385), "너부리": (970, 385), "알프레도": (1235, 365)}

    def __init__(self):
        self.agents = {n: PixelCharacter(n) for n in self.POSITIONS}

    def tick(self):
        for a in self.agents.values(): a.tick()

    def paint(self, p):
        for name, (x, y) in self.POSITIONS.items():
            self.agents[name].paint(p, x, y, 4)
