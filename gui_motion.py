from PySide6.QtCore import QTimer


class MotionController:
    """Owns animation timing only; visual layers remain independent."""
    def __init__(self, office):
        self.office = office
        self.timer = QTimer(office)
        self.timer.timeout.connect(self.tick)
        self.timer.start(120)

    def tick(self):
        self.office.background.tick()
        self.office.characters.tick()
        self.office.update()
