"""DONMULWON meeting animation layer.

Keeps the existing GUI/backend intact and provides a drop-in meeting scene:
research at desks -> typing -> meeting call -> walk to table -> debate -> Alfredo final verdict.
Import MeetingController into gui.py and call start_meeting(question, final_result).
"""
from __future__ import annotations

from PySide6.QtCore import QObject, QTimer, Signal, QPointF
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsRectItem, QGraphicsScene, QGraphicsSimpleTextItem


CHARACTERS = {
    "al": {"name": "알프레도", "emoji": "🐱", "style": "냥", "seat": (500, 360)},
    "kim": {"name": "김선달", "emoji": "🐦", "style": "까악", "seat": (360, 300)},
    "lee": {"name": "이묵", "emoji": "🐍", "style": "쉬이익", "seat": (640, 300)},
    "neo": {"name": "너부리", "emoji": "🦝", "style": "구리", "seat": (360, 460)},
    "hyun": {"name": "현무", "emoji": "🐢", "style": "아...", "seat": (640, 460)},
}


class PixelPerson(QGraphicsRectItem):
    def __init__(self, key: str):
        super().__init__(-14, -18, 28, 36)
        self.key = key
        self.setBrush(QBrush(QColor("#d8d0c4")))
        self.setPen(QPen(QColor("#252a2e"), 2))
        self.bubble = QGraphicsSimpleTextItem("")
        self.bubble.setFont(QFont("Malgun Gothic", 10, QFont.Bold))
        self.bubble.setBrush(QBrush(QColor("#f5f1e8")))
        self.bubble.setZValue(20)
        self.bubble.setParentItem(self)
        self.bubble.setPos(-80, -52)
        self.bubble.setVisible(False)

    def say(self, text: str):
        self.bubble.setText(text)
        self.bubble.setVisible(True)

    def silence(self):
        self.bubble.setVisible(False)


class MeetingController(QObject):
    """Animation-only controller; does not perform or replace AI analysis."""
    finished = Signal()
    phase_changed = Signal(str)
    verdict_ready = Signal(str)

    def __init__(self, scene: QGraphicsScene, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.people = {}
        self.queue = []
        self.final_result = ""
        self.question = ""
        self.phase = "idle"
        self._step = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

        self._draw_table()
        self._make_people()

    def _draw_table(self):
        table = QGraphicsRectItem(300, 330, 400, 130)
        table.setBrush(QBrush(QColor("#6e513d")))
        table.setPen(QPen(QColor("#30241d"), 3))
        table.setZValue(1)
        self.scene.addItem(table)

    def _make_people(self):
        starts = {
            "al": (170, 120), "kim": (350, 120), "lee": (530, 120),
            "neo": (710, 120), "hyun": (890, 120),
        }
        for key, pos in starts.items():
            p = PixelPerson(key)
            p.setPos(*pos)
            p.setZValue(10)
            self.scene.addItem(p)
            self.people[key] = p

    def start_meeting(self, question: str, final_result: str):
        self.question = question
        self.final_result = final_result
        self._step = 0
        self.phase = "research"
        self.phase_changed.emit("각자 자료 수집 중")
        self.queue = ["kim", "lee", "neo", "hyun", "al"]
        self._timer.start(1100)

    def _tick(self):
        if self.phase == "research":
            if self._step < len(self.queue):
                key = self.queue[self._step]
                p = self.people[key]
                styles = {
                    "kim": "까악! 자료 찾는 중!",
                    "lee": "쉬이익... 차트 확인.",
                    "neo": "구리! 계좌 확인한다구리!",
                    "hyun": "아... 시장부터 천천히...",
                    "al": "냥. 전체 자료를 검토하죠.",
                }
                p.say(styles[key])
                self._step += 1
                return
            self.phase = "gather"
            self._step = 0
            self.phase_changed.emit("회의 소집")
            return

        if self.phase == "gather":
            self.phase = "debate"
            self._step = 0
            self.phase_changed.emit("회의 시작")
            return

        if self.phase == "debate":
            order = ["kim", "lee", "neo", "hyun", "al"]
            lines = {
                "kim": "까악! 펀더멘털은 아직 살아있다!",
                "lee": "쉬이익... 하지만 차트가 위험하다.",
                "neo": "구리! 계좌 비중부터 봐야 한다구리!",
                "hyun": "아... 금리와 시장환경도 봐야 합니다...",
                "al": "냥. 모두의 근거를 검증하겠습니다.",
            }
            if self._step < len(order):
                key = order[self._step]
                for p in self.people.values(): p.silence()
                self.people[key].say(lines[key])
                self._step += 1
                return
            self.phase = "verdict"
            self._step = 0
            self.phase_changed.emit("알프레도 최종 검증")
            return

        if self.phase == "verdict":
            for p in self.people.values(): p.silence()
            self.people["al"].say("냥. 최종 판단을 말씀드리죠.")
            self.verdict_ready.emit(self.final_result)
            self.phase = "done"
            self._timer.stop()
            self.phase_changed.emit("분석 완료")
            self.finished.emit()

    def stop(self):
        self._timer.stop()
        for p in self.people.values(): p.silence()
