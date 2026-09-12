from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


class PixelCharacter:
    """Detailed pixel-art office characters.

    The artwork keeps the current on-screen character size, but renders the
    same silhouettes on a finer logical grid: 1 source unit becomes 1.5
    logical pixels and each final pixel is 2x2 screen pixels. This makes
    faces, glasses, eyes, clothing and species features visibly finer without
    shrinking the characters.
    """
    SPECS = {
        "현무": {"kind": "turtle", "body": "#4f7657", "dark": "#294333", "light": "#8fae78", "skin": "#b7aa82", "suit": "#26312d"},
        "김선달": {"kind": "bird", "body": "#a85f42", "dark": "#63372f", "light": "#d79a55", "skin": "#d8b88b", "suit": "#30343b"},
        "이묵": {"kind": "snake", "body": "#657b52", "dark": "#35472f", "light": "#b7a961", "skin": "#c9b17d", "suit": "#29332f"},
        "너부리": {"kind": "raccoon", "body": "#777b7d", "dark": "#424548", "light": "#c4b8a4", "skin": "#b9a68e", "suit": "#34373b"},
        "알프레도": {"kind": "cat", "body": "#17181c", "dark": "#08090b", "light": "#3b3d45", "skin": "#b9aa94", "suit": "#111316"},
    }

    def __init__(self, name):
        self.name = name
        self.frame = 0

    def tick(self):
        self.frame = (self.frame + 1) % 72

    def paint(self, p, x, y, scale=2):
        spec = self.SPECS[self.name]
        s = max(1, int(scale))
        # 1.5x logical subdivision preserves the existing visual size while
        # reducing the visible pixel block from 3x3 to 2x2.
        GRID = 1.5
        ox, oy = int(x), int(y)
        bob = -1 if 60 <= self.frame % 72 <= 63 else 0
        blink = self.frame % 72 in (56, 57)

        def gx(v):
            return int(round(float(v) * GRID))

        def gy(v):
            return int(round((float(v) + bob) * GRID))

        def gw(v):
            return max(1, int(round(float(v) * GRID)))

        def rect(px, py, w, h, color, dy=bob):
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(color))
            p.drawRect(ox + gx(px) * s, oy + int(round((float(py) + dy) * GRID)) * s, gw(w) * s, gw(h) * s)

        def pixel(px, py, color):
            rect(px, py, 1, 1, color, 0)

        body, dark, light = spec["body"], spec["dark"], spec["light"]
        skin, suit = spec["skin"], spec["suit"]
        black, white, gold = "#08090b", "#eee5d3", "#d4b86f"

        # Pixel shadow
        rect(12, 104, 47, 3, "#111214", 0)
        rect(19, 107, 31, 1, "#0a0b0d", 0)

        # Legs and shoes
        rect(17, 86, 14, 17, suit)
        rect(39, 86, 14, 17, suit)
        rect(14, 101, 18, 6, black)
        rect(38, 101, 18, 6, black)
        pixel(16, 103, "#4b4e50"); pixel(53, 103, "#4b4e50")

        # Tailored suit body
        rect(13, 48, 44, 42, suit)
        rect(16, 51, 38, 36, suit)
        rect(20, 52, 11, 31, "#3b4145")
        rect(39, 52, 11, 31, "#24292c")
        rect(32, 53, 5, 34, white)
        rect(33, 53, 3, 34, "#d6ccb9")
        # Lapels
        rect(25, 51, 7, 16, "#4a4e52")
        rect(38, 51, 7, 16, "#1f2427")
        rect(26, 54, 5, 2, "#77716a")
        rect(39, 54, 5, 2, "#5c5a58")
        # Tie
        rect(33, 59, 3, 18, "#824e4b")
        rect(32, 59, 5, 4, "#a66a61")
        rect(34, 77, 2, 7, "#613937")
        # Buttons and pocket
        for by in (67, 75, 83):
            pixel(28, by, gold); pixel(42, by, gold)
        rect(45, 72, 6, 2, "#171a1c")
        rect(46, 71, 5, 1, "#8e806d")

        # Arms and hands
        rect(7, 50, 9, 34, suit)
        rect(54, 50, 9, 34, suit)
        rect(5, 78, 12, 9, skin)
        rect(53, 78, 12, 9, skin)
        rect(7, 84, 8, 5, skin)
        rect(55, 84, 8, 5, skin)
        pixel(6, 87, light); pixel(61, 87, light)

        # Neck and head base
        rect(27, 42, 16, 10, skin)
        rect(29, 43, 12, 8, skin)
        rect(18, 10, 34, 34, body)
        rect(22, 6, 26, 7, body)
        rect(21, 15, 30, 24, body)
        rect(23, 37, 24, 7, skin)

        kind = spec["kind"]

        if kind == "cat":
            # Alfredo: black cat, sharp ears, gold glasses, expressive eyes.
            rect(15, 1, 14, 16, body); rect(41, 1, 14, 16, body)
            rect(18, 4, 7, 8, "#34313a"); rect(45, 4, 7, 8, "#34313a")
            pixel(21, 4, "#70505a"); pixel(48, 4, "#70505a")
            rect(20, 14, 31, 25, body)
            pixel(20, 17, light); pixel(49, 17, light)
            pixel(18, 24, light); pixel(51, 24, light)
            # muzzle
            rect(25, 32, 21, 8, skin); rect(29, 34, 13, 5, "#d0c1a8")
            # glasses
            rect(18, 18, 14, 3, gold); rect(38, 18, 14, 3, gold)
            rect(18, 18, 3, 12, gold); rect(29, 18, 3, 12, gold)
            rect(38, 18, 3, 12, gold); rect(49, 18, 3, 12, gold)
            rect(31, 21, 8, 3, gold); rect(15, 20, 4, 2, gold); rect(52, 20, 4, 2, gold)
            # eyes
            if blink:
                rect(23, 25, 6, 2, "#d7c96f"); rect(41, 25, 6, 2, "#d7c96f")
            else:
                rect(23, 24, 6, 6, "#e5cf72"); rect(41, 24, 6, 6, "#e5cf72")
                pixel(25, 24, black); pixel(26, 25, black); pixel(25, 27, black)
                pixel(43, 24, black); pixel(44, 25, black); pixel(43, 27, black)
            # nose, mouth, whiskers
            rect(32, 31, 6, 4, "#b97882")
            pixel(31, 36, skin); pixel(38, 36, skin)
            rect(20, 35, 10, 1, skin); rect(40, 35, 10, 1, skin)
            rect(17, 38, 11, 1, "#8e8c88"); rect(43, 38, 11, 1, "#8e8c88")

        elif kind == "turtle":
            # Hyeonmu: turtle head and a strongly patterned shell.
            rect(47, 20, 13, 18, skin); rect(51, 18, 9, 7, skin)
            rect(55, 22, 3, 3, black); pixel(57, 21, "#f0e2ae")
            rect(48, 32, 12, 5, skin)
            # shell
            rect(8, 46, 54, 40, dark); rect(12, 48, 46, 35, body)
            rect(17, 51, 36, 29, "#63805b")
            rect(30, 48, 6, 33, light); rect(17, 62, 36, 6, light)
            rect(22, 51, 5, 11, dark); rect(41, 51, 5, 11, dark)
            rect(19, 69, 8, 10, dark); rect(43, 69, 8, 10, dark)
            pixel(31, 55, "#b0bf83"); pixel(34, 72, "#b0bf83")
            # arms/flippers
            rect(5, 66, 12, 13, skin); rect(53, 66, 12, 13, skin)
            rect(4, 76, 10, 8, skin); rect(56, 76, 10, 8, skin)
            # collar and tie in front
            rect(31, 82, 7, 9, suit); rect(32, 82, 5, 5, "#d7d0c1")
            rect(33, 87, 3, 7, "#83504b")

        elif kind == "bird":
            # Seondal: layered feathers, expressive eyes and beak.
            rect(13, 3, 18, 12, body); rect(39, 5, 14, 10, body)
            rect(14, 13, 38, 28, body)
            rect(10, 21, 11, 19, body); rect(47, 20, 12, 20, body)
            rect(17, 18, 9, 3, light); rect(37, 18, 10, 3, light)
            rect(14, 25, 8, 3, dark); rect(45, 25, 8, 3, dark)
            rect(18, 29, 8, 3, dark); rect(39, 29, 9, 3, dark)
            rect(20, 12, 9, 8, white); rect(38, 12, 9, 8, white)
            if not blink:
                rect(23, 14, 3, 4, black); rect(41, 14, 3, 4, black)
                pixel(23, 14, light); pixel(41, 14, light)
            rect(47, 17, 15, 7, light); rect(55, 21, 10, 4, "#b66f38")
            pixel(60, 20, gold)
            rect(3, 35, 14, 8, dark); rect(50, 34, 15, 9, dark)
            rect(7, 42, 10, 5, body); rect(51, 42, 10, 5, body)

        elif kind == "snake":
            # Imuk: layered scales, slit pupils and forked tongue.
            rect(16, 3, 38, 11, body); rect(12, 11, 45, 30, body)
            rect(17, 16, 35, 20, "#586d49")
            for px, py in ((15, 13), (22, 12), (30, 13), (38, 12), (46, 14),
                           (19, 21), (27, 20), (36, 21), (44, 20),
                           (22, 29), (31, 28), (40, 29)):
                rect(px, py, 5, 4, light)
            rect(19, 16, 11, 8, skin); rect(39, 16, 11, 8, skin)
            if not blink:
                rect(23, 17, 2, 6, black); rect(43, 17, 2, 6, black)
            else:
                rect(22, 20, 6, 2, dark); rect(42, 20, 6, 2, dark)
            rect(31, 34, 3, 9, "#b76d6f")
            rect(28, 41, 6, 2, "#b76d6f"); rect(34, 41, 6, 2, "#b76d6f")
            rect(7, 31, 13, 12, body); rect(49, 31, 13, 12, body)
            rect(4, 40, 12, 8, dark); rect(54, 40, 12, 8, dark)

        elif kind == "raccoon":
            # Neoburi: ears, dark mask, muzzle and striped tail.
            rect(14, 3, 13, 13, body); rect(43, 3, 13, 13, body)
            rect(18, 7, 6, 6, light); rect(46, 7, 6, 6, light)
            rect(15, 13, 41, 28, body)
            rect(17, 17, 36, 11, dark)
            rect(19, 18, 12, 8, "#303337"); rect(39, 18, 12, 8, "#303337")
            rect(21, 19, 7, 6, "#d5bd75"); rect(42, 19, 7, 6, "#d5bd75")
            if not blink:
                rect(23, 19, 2, 6, black); rect(44, 19, 2, 6, black)
            else:
                rect(21, 22, 7, 2, black); rect(42, 22, 7, 2, black)
            rect(25, 27, 21, 11, light); rect(31, 30, 9, 5, "#d2c1a7")
            rect(34, 31, 4, 3, "#85575a")
            pixel(30, 36, dark); pixel(39, 36, dark)
            rect(9, 27, 10, 13, body); rect(51, 27, 10, 13, body)
            rect(6, 36, 12, 8, dark); rect(52, 36, 12, 8, dark)
            # tail behind suit
            rect(52, 61, 13, 9, body); rect(58, 68, 10, 8, body)
            rect(54, 76, 11, 8, dark); rect(59, 84, 9, 7, body)

        # Foreground suit details keep the office-worker silhouette consistent.
        rect(31, 87, 7, 3, suit)
        rect(32, 88, 5, 2, "#ddd4c4")
        rect(33, 90, 3, 7, "#804d49")
        pixel(28, 67, gold); pixel(43, 67, gold)
        pixel(28, 75, gold); pixel(43, 75, gold)


class CharacterLayer:
    POSITIONS = {
        "현무": (135, 350),
        "김선달": (410, 350),
        "이묵": (685, 350),
        "너부리": (960, 350),
        "알프레도": (1230, 330),
    }
    # Keep the current character size while using a finer 2x screen pixel.
    SCALE = 2

    def __init__(self):
        self.agents = {name: PixelCharacter(name) for name in self.POSITIONS}

    def tick(self):
        for agent in self.agents.values():
            agent.tick()

    def paint(self, p):
        for name, (x, y) in self.POSITIONS.items():
            self.agents[name].paint(p, x, y, self.SCALE)
