from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


# ---------------------------------------------------------------------------
# DONMULWON CHARACTER LAYER
# ---------------------------------------------------------------------------
# The previous renderer used large geometric blocks.  This version uses a
# 40x60 logical sprite grid and renders each logical pixel as a tiny 2x2
# screen pixel.  The characters are intentionally a little smaller than the
# old ones, while the finer grid makes faces, clothes and animal silhouettes
# much cleaner.

PALETTE = {
    "ink": "#171619",
    "outline": "#202024",
    "shirt": "#eee7d7",
    "tie": "#8b4d4c",
    "gold": "#d6b86b",
    "shoe": "#101114",
}


class PixelCharacter:
    SPECS = {
        "현무": {"kind": "turtle", "main": "#52775b", "dark": "#294637", "light": "#8da874", "skin": "#b7a77d", "suit": "#26322e"},
        "김선달": {"kind": "bird", "main": "#a85d43", "dark": "#60372f", "light": "#d79b58", "skin": "#d8b98d", "suit": "#30343a"},
        "이묵": {"kind": "snake", "main": "#60774f", "dark": "#33462f", "light": "#aeb16b", "skin": "#c9b07d", "suit": "#29332f"},
        "너부리": {"kind": "raccoon", "main": "#777a7d", "dark": "#3d4146", "light": "#c5b9a6", "skin": "#b8a68e", "suit": "#34373c"},
        "알프레도": {"kind": "cat", "main": "#17181d", "dark": "#08090c", "light": "#444750", "skin": "#bcae98", "suit": "#111316"},
    }

    def __init__(self, name):
        self.name = name
        self.frame = 0

    def tick(self):
        self.frame = (self.frame + 1) % 90

    def paint(self, p, x, y, scale=2):
        spec = self.SPECS[self.name]
        s = max(1, int(scale))
        ox, oy = int(x), int(y)
        # Very small idle motion; never changes the character's proportions.
        bob = -1 if 70 <= self.frame % 90 <= 73 else 0
        blink = self.frame % 90 in (58, 59)

        def cell(px, py, color, w=1, h=1, move=True):
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(color))
            yy = py + (bob if move else 0)
            p.drawRect(ox + px * s, oy + yy * s, max(1, w * s), max(1, h * s))

        def pixels(points, color):
            for px, py in points:
                cell(px, py, color)

        def box(px, py, w, h, color):
            cell(px, py, color, w, h)

        main, dark, light = spec["main"], spec["dark"], spec["light"]
        skin, suit = spec["skin"], spec["suit"]
        ink, white, gold = PALETTE["ink"], PALETTE["shirt"], PALETTE["gold"]

        # Ground shadow
        box(8, 57, 24, 2, "#121316")
        box(12, 59, 16, 1, "#0a0b0d")

        # Legs / trousers / shoes.  Deliberately narrow so the character
        # reads as a person in a suit rather than a block.
        box(13, 45, 7, 12, suit)
        box(21, 45, 7, 12, suit)
        box(11, 55, 10, 4, PALETTE["shoe"])
        box(20, 55, 10, 4, PALETTE["shoe"])
        cell(13, 56, "#4c5052"); cell(28, 56, "#4c5052")

        # Torso: outline first, then tailored jacket.
        box(9, 27, 24, 20, ink)
        box(10, 28, 22, 18, suit)
        box(13, 30, 16, 15, suit)
        # shirt opening + lapels
        box(18, 29, 4, 16, white)
        pixels([(17, 30), (16, 31), (15, 32), (14, 33), (13, 34)], "#565b60")
        pixels([(22, 30), (23, 31), (24, 32), (25, 33), (26, 34)], "#202428")
        # tie
        box(19, 34, 2, 10, PALETTE["tie"])
        box(18, 34, 4, 2, "#aa6861")
        cell(19, 43, "#623c3a")
        # buttons / pocket
        for py in (36, 40, 44):
            cell(16, py, gold)
        box(25, 39, 4, 1, "#858078")
        cell(26, 38, "#d0c1a4")

        # Arms, elbows and hands
        box(5, 29, 5, 16, suit)
        box(31, 29, 5, 16, suit)
        box(4, 42, 7, 5, skin)
        box(31, 42, 7, 5, skin)
        cell(5, 46, light); cell(36, 46, light)

        # Neck and base of head
        box(17, 24, 8, 6, skin)
        box(11, 8, 21, 17, ink)
        box(12, 9, 19, 15, main)
        box(14, 22, 15, 4, skin)

        kind = spec["kind"]

        if kind == "cat":
            # Alfredo — black cat, glasses and clean formal silhouette.
            pixels([(12, 9), (13, 7), (14, 5), (15, 7), (16, 9),
                    (27, 9), (28, 7), (29, 5), (30, 7), (31, 9)], main)
            pixels([(14, 6), (15, 7), (28, 6), (29, 7)], light)
            box(14, 11, 16, 11, main)
            # subtle fur highlights
            pixels([(13, 13), (14, 12), (29, 13), (30, 15), (15, 20), (28, 20)], light)
            # muzzle
            box(17, 19, 10, 5, skin)
            box(19, 20, 6, 3, "#d0c1aa")
            # gold glasses, separated into tiny pixels
            box(13, 14, 7, 1, gold); box(25, 14, 7, 1, gold)
            box(13, 14, 1, 5, gold); box(19, 14, 1, 5, gold)
            box(25, 14, 1, 5, gold); box(31, 14, 1, 5, gold)
            box(20, 15, 5, 1, gold)
            # eyes
            if blink:
                box(15, 17, 3, 1, "#e0ca72"); box(27, 17, 3, 1, "#e0ca72")
            else:
                box(15, 16, 3, 3, "#e5cf72"); box(27, 16, 3, 3, "#e5cf72")
                cell(16, 16, ink); cell(16, 18, ink); cell(28, 16, ink); cell(28, 18, ink)
            cell(20, 20, "#b97680"); cell(23, 20, "#b97680")
            # whiskers
            pixels([(14, 21), (13, 22), (12, 22), (26, 21), (27, 22), (28, 22)], "#aaa6a0")

        elif kind == "turtle":
            # Hyeonmu — head peeking right, patterned shell, turtle limbs.
            box(27, 12, 7, 11, skin)
            box(30, 11, 5, 5, skin)
            cell(32, 15, ink); cell(33, 14, "#eee0a5")
            box(29, 21, 6, 3, skin)
            # shell outline and shell plates
            box(7, 27, 22, 19, dark)
            box(9, 28, 18, 16, main)
            box(12, 30, 12, 12, "#63805a")
            box(17, 29, 2, 14, light)
            box(11, 35, 14, 2, light)
            pixels([(12, 30), (13, 31), (21, 30), (22, 31), (12, 39), (13, 40), (21, 39), (22, 40)], dark)
            pixels([(16, 32), (19, 32), (16, 38), (19, 38)], "#b0bd82")
            # flippers
            box(5, 38, 6, 7, skin); box(27, 38, 7, 7, skin)
            box(4, 44, 7, 4, skin); box(28, 44, 7, 4, skin)
            # shirt collar / tie over shell
            box(17, 43, 5, 5, suit); box(18, 43, 3, 2, white)
            box(19, 46, 2, 5, PALETTE["tie"])

        elif kind == "bird":
            # Seondal — bird head/crest, beak and feather layering.
            pixels([(13, 9), (13, 7), (14, 5), (15, 7), (16, 9),
                    (27, 9), (28, 7), (29, 6), (30, 8)], main)
            box(12, 11, 19, 12, main)
            pixels([(12, 14), (13, 13), (14, 14), (27, 13), (29, 14), (30, 16)], light)
            # white eye patches
            box(15, 12, 5, 4, white); box(24, 12, 5, 4, white)
            if not blink:
                cell(17, 13, ink); cell(26, 13, ink)
            else:
                box(15, 14, 5, 1, dark); box(24, 14, 5, 1, dark)
            # beak
            box(29, 16, 6, 3, light); box(34, 17, 3, 2, "#b56e3c")
            cell(35, 18, gold)
            # cheek feathers
            pixels([(14, 17), (15, 18), (16, 19), (27, 18), (29, 19)], dark)
            box(10, 21, 6, 6, dark); box(27, 21, 6, 6, dark)
            pixels([(11, 22), (12, 23), (28, 22), (29, 23)], light)

        elif kind == "snake":
            # Imuk — clean scale pattern, slit pupils and forked tongue.
            box(12, 9, 19, 14, main)
            box(14, 12, 15, 9, "#587047")
            # scales as tiny repeated pixels
            for px, py in ((14, 11), (18, 11), (22, 11), (26, 11),
                           (16, 15), (20, 15), (24, 15), (28, 15),
                           (14, 19), (18, 19), (22, 19), (26, 19)):
                cell(px, py, light)
                cell(px + 1, py, light)
            # eyes
            box(15, 12, 5, 4, skin); box(24, 12, 5, 4, skin)
            if not blink:
                box(17, 12, 1, 4, ink); box(26, 12, 1, 4, ink)
            else:
                box(16, 14, 4, 1, dark); box(25, 14, 4, 1, dark)
            # mouth + forked tongue
            box(19, 20, 7, 1, dark)
            box(21, 21, 2, 5, "#b76c70")
            cell(20, 25, "#b76c70"); cell(23, 25, "#b76c70")
            # side coils
            box(8, 20, 6, 8, main); box(29, 20, 6, 8, main)
            pixels([(9, 22), (10, 24), (30, 22), (31, 24)], light)

        elif kind == "raccoon":
            # Neoburi — ears, mask, muzzle and striped tail.
            box(12, 6, 5, 6, main); box(27, 6, 5, 6, main)
            cell(13, 7, light); cell(29, 7, light)
            box(12, 10, 20, 14, main)
            # characteristic dark face mask
            box(13, 13, 18, 6, dark)
            box(15, 13, 5, 5, "#2e3236"); box(24, 13, 5, 5, "#2e3236")
            # eyes
            box(16, 14, 3, 3, "#d7c775"); box(25, 14, 3, 3, "#d7c775")
            cell(17, 14, ink); cell(26, 14, ink)
            # muzzle and nose
            box(17, 18, 10, 5, light)
            box(20, 19, 4, 3, "#d0bea2")
            cell(21, 19, "#86565b")
            pixels([(18, 22), (19, 23), (26, 22), (25, 23)], dark)
            # ears and cheek accents
            pixels([(12, 11), (13, 10), (14, 11), (30, 11), (31, 10)], light)
            box(7, 22, 6, 7, dark); box(29, 22, 6, 7, dark)
            # tail peeking behind right side
            box(32, 38, 6, 5, main)
            box(34, 39, 4, 2, light); box(34, 42, 4, 2, dark)


class CharacterLayer:
    # Horizontal one-line office arrangement. Hyeonmu is nearest the door;
    # Alfredo is isolated at the far end as team leader.
    POSITIONS = {
        "현무": (105, 385, 0),
        "김선달": (380, 385, 0),
        "이묵": (655, 385, 0),
        "너부리": (930, 385, 0),
        "알프레도": (1215, 385, 0),
    }

    def __init__(self):
        self.characters = {name: PixelCharacter(name) for name in self.POSITIONS}

    def tick(self):
        for character in self.characters.values():
            character.tick()

    def paint(self, p):
        # Keep the tiny sprite pixels crisp.  No scaling/antialiasing is used.
        for name, (x, y, _) in self.POSITIONS.items():
            self.characters[name].paint(p, x, y, 2)


__all__ = ["PixelCharacter", "CharacterLayer"]
