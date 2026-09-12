# DONMULWON - TOP DOWN PIXEL OFFICE
import os, sys, io, contextlib, traceback
from datetime import datetime
from PySide6.QtCore import QObject, QThread, Signal, Slot, Qt, QRect, QTimer
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QPlainTextEdit, QProgressBar, QComboBox
from gui_background import PixelBackground
from gui_characters_v2 import CharacterLayer
from gui_motion import MotionController

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


class AnalysisWorker(QObject):
    output = Signal(str)
    finished = Signal()
    failed = Signal(str)

    def __init__(self, question):
        super().__init__()
        self.question = question

    @Slot()
    def run(self):
        try:
            import main
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                if hasattr(main, 'run_analysis'):
                    result = main.run_analysis(self.question)
                elif hasattr(main, 'main'):
                    result = main.main(self.question)
                else:
                    raise AttributeError('main.py에 분석 실행 함수가 없습니다.')
            text = buf.getvalue()
            if result is not None:
                text += '\n\n' + str(result)
            self.output.emit(text)
            self.finished.emit()
        except Exception:
            self.failed.emit(traceback.format_exc())


class PixelOffice(QWidget):
    """돈물원 탑뷰 사무실.

    - 위쪽: 개인 책상 5개 + 각자 컴퓨터/의자
    - 아래쪽: 회의 테이블
    - 회의 테이블 뒤: 벽에 실제로 붙어 있는 대형 시장 전광판
    - 캐릭터는 home position에서 자기 책상에 앉아 있다가 MotionController가 이동시킨다.
    """

    DESK_LAYOUT = [
        ('현무', 55, 244, 175),
        ('김선달', 320, 244, 175),
        ('이묵', 585, 244, 175),
        ('너부리', 850, 244, 175),
        ('알프레도', 1115, 244, 175),
    ]

    def __init__(self):
        super().__init__()
        self.background = PixelBackground()
        self.characters = CharacterLayer()
        self.motion = MotionController(self)
        self.setMinimumHeight(620)

    def set_weather(self, value):
        self.background.set_weather(value)
        self.update()

    def set_time(self, value):
        self.background.set_time(value)
        self.update()

    def auto_time(self):
        now = datetime.now()
        hour = now.hour
        self.background.set_clock(now)
        if 5 <= hour < 11:
            period = '아침'
        elif 11 <= hour < 17:
            period = '낮'
        elif 17 <= hour < 21:
            period = '저녁'
        else:
            period = '밤'
        self.background.set_time(period)
        self.update()
        return period

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, False)
        try:
            w, h = self.width(), self.height()
            self.background.paint(p, w, h)
            self.draw_desks(p, w)
            self.draw_conference_area(p, w, h)
            self.characters.paint(p)
            self.draw_character_labels(p)
            self.draw_side_monitor(p, w)
        finally:
            if p.isActive():
                p.end()

    @staticmethod
    def _rect(p, x, y, w, h, color, pen=None):
        p.setPen(Qt.NoPen if pen is None else QColor(pen))
        p.setBrush(QColor(color))
        p.drawRect(int(x), int(y), int(w), int(h))

    @staticmethod
    def _text(p, x, y, w, h, text, size=8, color='#eee4d2', align=Qt.AlignLeft):
        p.setPen(QColor(color))
        p.setFont(QFont('Malgun Gothic', size, QFont.Bold))
        p.drawText(QRect(int(x), int(y), int(w), int(h)), align, str(text))

    def draw_desks(self, p, w):
        """개별 책상: 상판 + 두께 + 서랍 + 네 다리 + 모니터 + 키보드 + 마우스 + 의자."""
        for name, x, y, desk_w in self.DESK_LAYOUT:
            # floor shadow
            self._rect(p, x + 10, y + 68, desk_w - 20, 8, '#30251e')

            # chair, behind the character
            chair_x = x + desk_w // 2 - 31
            self._rect(p, chair_x + 4, y + 74, 54, 30, '#17191d')
            self._rect(p, chair_x + 8, y + 78, 46, 22, '#34363a')
            self._rect(p, chair_x + 12, y + 82, 38, 14, '#4b4d50')
            self._rect(p, chair_x + 3, y + 101, 56, 5, '#17191d')
            self._rect(p, chair_x + 8, y + 106, 5, 7, '#202124')
            self._rect(p, chair_x + 49, y + 106, 5, 7, '#202124')

            # four table legs, visibly supporting the top
            leg_color = '#2a1e17'
            metal = '#4b392d'
            for lx in (x + 9, x + desk_w - 19):
                self._rect(p, lx, y + 53, 10, 24, leg_color)
                self._rect(p, lx + 2, y + 55, 5, 20, metal)
            # rear legs peek out above the top for top-down depth
            self._rect(p, x + 13, y - 3, 7, 9, '#302219')
            self._rect(p, x + desk_w - 20, y - 3, 7, 9, '#302219')

            # tabletop outline and wooden top
            self._rect(p, x - 3, y - 3, desk_w + 6, 64, '#201713')
            self._rect(p, x, y, desk_w, 56, '#5c3e28')
            self._rect(p, x + 5, y + 5, desk_w - 10, 46, '#795337')
            self._rect(p, x + 9, y + 9, desk_w - 18, 38, '#68472f')

            # wood grain pixels
            self._rect(p, x + 12, y + 12, 38, 3, '#8d6542')
            self._rect(p, x + desk_w - 58, y + 37, 42, 3, '#513621')
            self._rect(p, x + 65, y + 28, 25, 2, '#8a5f3d')

            # monitor stand
            mon_x = x + desk_w // 2 - 39
            self._rect(p, mon_x + 28, y + 42, 22, 6, '#171b1f')
            self._rect(p, mon_x + 33, y + 37, 12, 7, '#555a5d')
            # monitor bezel
            self._rect(p, mon_x, y + 7, 78, 34, '#1a2024')
            self._rect(p, mon_x + 4, y + 4, 70, 34, '#2c3438')
            self._rect(p, mon_x + 8, y + 8, 62, 26, '#16242b')
            # tiny screen graph
            pts = [
                (mon_x + 11, y + 28), (mon_x + 20, y + 24),
                (mon_x + 29, y + 26), (mon_x + 38, y + 18),
                (mon_x + 48, y + 22), (mon_x + 59, y + 13),
            ]
            p.setPen(QColor('#bba16c'))
            for a, b in zip(pts, pts[1:]):
                p.drawLine(a[0], a[1], b[0], b[1])
            p.setPen(Qt.NoPen)

            # keyboard and mouse
            self._rect(p, x + desk_w // 2 - 45, y + 44, 70, 8, '#25282b')
            self._rect(p, x + desk_w // 2 - 39, y + 46, 58, 4, '#7b7e7d')
            self._rect(p, x + desk_w // 2 + 32, y + 44, 7, 9, '#292c2e')

            # drawer unit + handle
            self._rect(p, x + desk_w - 31, y + 35, 22, 18, '#4a3021')
            self._rect(p, x + desk_w - 28, y + 39, 16, 5, '#60432d')
            self._rect(p, x + desk_w - 28, y + 46, 16, 5, '#60432d')
            self._rect(p, x + desk_w - 21, y + 41, 3, 2, '#c0a06c')
            self._rect(p, x + desk_w - 21, y + 48, 3, 2, '#c0a06c')

            # tiny desk placard
            self._rect(p, x + 7, y + 52, 58, 8, '#2b211c')
            self._text(p, x + 8, y + 50, 56, 12, name, 6, '#d4bd8d', Qt.AlignLeft | Qt.AlignVCenter)

    def draw_conference_area(self, p, w, h):
        """작은 회의 테이블 + 실제 바닥에 놓인 대형 전광판."""
        cx = w // 2

        # Wall-mounted market board: not floating. It has a thick frame, wall brackets,
        # vertical support posts and a floor/base strip.
        board_w = min(620, max(500, w - 760))
        board_h = 112
        board_x = cx - board_w // 2
        board_y = 345

        # wall brackets/supports
        self._rect(p, board_x + 22, board_y + board_h, 16, 48, '#28201b')
        self._rect(p, board_x + board_w - 38, board_y + board_h, 16, 48, '#28201b')
        self._rect(p, board_x + 12, board_y + board_h + 44, board_w - 24, 8, '#211916')
        self._rect(p, board_x + 28, board_y - 6, board_w - 56, 7, '#4c392c')

        # board outer frame
        self._rect(p, board_x - 7, board_y - 7, board_w + 14, board_h + 14, '#211914')
        self._rect(p, board_x - 3, board_y - 3, board_w + 6, board_h + 6, '#6b5138')
        self._rect(p, board_x + 3, board_y + 3, board_w - 6, board_h - 6, '#11171a')
        self._rect(p, board_x + 9, board_y + 9, board_w - 18, board_h - 18, '#17252a')

        self._text(p, board_x + 17, board_y + 10, 180, 18, 'DONMULWON · TEAM MARKET', 8, '#d8c48e')
        self._text(p, board_x + board_w - 130, board_y + 10, 110, 18, 'LIVE', 8, '#b5c08e', Qt.AlignRight)

        # board grid
        grid_top = board_y + 35
        grid_bottom = board_y + board_h - 16
        p.setPen(QColor('#293d42'))
        for i in range(1, 4):
            yy = grid_top + i * (grid_bottom - grid_top) // 4
            p.drawLine(board_x + 18, yy, board_x + board_w - 18, yy)
        for i in range(1, 8):
            xx = board_x + 18 + i * (board_w - 36) // 8
            p.drawLine(xx, grid_top, xx, grid_bottom)

        # board price line
        values = [.44, .40, .47, .43, .52, .49, .60, .56, .67, .63, .76, .72, .84, .79]
        points = []
        plot_w = board_w - 44
        plot_h = grid_bottom - grid_top - 3
        for i, value in enumerate(values):
            px = board_x + 22 + int(i * plot_w / (len(values) - 1))
            py = grid_bottom - int(value * plot_h)
            points.append((px, py))
        p.setPen(QColor('#d0b477'))
        for a, b in zip(points, points[1:]):
            p.drawLine(a[0], a[1], b[0], b[1])
        p.setPen(Qt.NoPen)
        p.setBrush(QColor('#e1c681'))
        for px, py in points:
            p.drawRect(px - 2, py - 2, 5, 5)

        # ticker strip on the actual screen
        self._rect(p, board_x + 18, board_y + board_h - 25, board_w - 36, 10, '#202f33')
        self._text(p, board_x + 25, board_y + board_h - 26, board_w - 50, 12, 'VOO  +0.8%     JOBY  +2.4%     SOFI  +1.6%     KO  +0.3%', 6, '#cdb985', Qt.AlignLeft | Qt.AlignVCenter)

        # Conference table is deliberately compact.
        table_w = min(520, max(450, w - 820))
        table_h = 58
        table_x = cx - table_w // 2
        table_y = 515

        # table legs first, so the top sits on them
        for lx in (table_x + 28, table_x + table_w - 42):
            self._rect(p, lx, table_y + 42, 14, 35, '#241a15')
            self._rect(p, lx + 3, table_y + 45, 7, 29, '#4e3829')
        self._rect(p, cx - 7, table_y + 42, 14, 35, '#241a15')
        self._rect(p, cx - 4, table_y + 45, 8, 29, '#4e3829')

        # top outline / wood layers
        self._rect(p, table_x - 5, table_y - 5, table_w + 10, table_h + 10, '#211713')
        self._rect(p, table_x, table_y, table_w, table_h, '#4d3323')
        self._rect(p, table_x + 6, table_y + 6, table_w - 12, table_h - 12, '#725037')
        self._rect(p, table_x + 13, table_y + 13, table_w - 26, table_h - 26, '#825c3e')
        self._rect(p, table_x + 22, table_y + 25, table_w - 44, 2, '#5e402b')

        # six seats around the table, separate from the tabletop
        seat_positions = [
            table_x + 30, table_x + 132, table_x + 234,
            table_x + table_w - 264, table_x + table_w - 162, table_x + table_w - 60,
        ]
        for sx in seat_positions:
            self._rect(p, sx, table_y - 17, 40, 12, '#252326')
            self._rect(p, sx + 5, table_y - 14, 30, 6, '#4a4548')
            self._rect(p, sx, table_y + table_h + 5, 40, 12, '#252326')
            self._rect(p, sx + 5, table_y + table_h + 8, 30, 6, '#4a4548')

        # central meeting tablet / papers
        self._rect(p, cx - 62, table_y + 18, 124, 20, '#33261e')
        self._rect(p, cx - 53, table_y + 21, 106, 13, '#b9a27a')
        self._rect(p, cx - 38, table_y + 24, 76, 2, '#806947')
        self._rect(p, cx - 27, table_y + 29, 54, 2, '#806947')

        self._text(p, table_x, table_y + table_h + 24, table_w, 18, '⚔ AI TRADING TEAM  ·  CONFERENCE ROOM', 7, '#bca87e', Qt.AlignCenter)

    def draw_character_labels(self, p):
        p.setPen(QColor('#eee4d2'))
        p.setFont(QFont('Malgun Gothic', 8, QFont.Bold))
        for name, (x, y, _) in self.characters.POSITIONS.items():
            p.drawText(QRect(int(x - 18), int(y + 65), 100, 20), Qt.AlignCenter, str(name))

    def draw_side_monitor(self, p, w):
        """우측 보조 정보 패널. 큰 전광판과 역할이 겹치지 않게 작게 유지."""
        x, y, ww, hh = w - 218, 112, 188, 108
        self._rect(p, x + 4, y + 5, ww, hh, '#17191b')
        self._rect(p, x, y, ww, hh, '#292d2e')
        self._rect(p, x + 5, y + 5, ww - 10, hh - 10, '#172125')
        self._text(p, x + 12, y + 9, 150, 16, 'ACCOUNT MONITOR', 7, '#d8c48e')
        self._text(p, x + 12, y + 30, 165, 16, 'PORTFOLIO', 6, '#8fa69a')
        self._text(p, x + 12, y + 48, 165, 16, 'VOO     50%', 7, '#ded3b6')
        self._text(p, x + 12, y + 64, 165, 16, 'KO      25%', 7, '#ded3b6')
        self._text(p, x + 12, y + 80, 165, 16, 'SOFI    12.5%', 7, '#ded3b6')
        self._text(p, x + 92, y + 80, 80, 16, 'JEPQ 6.25%', 6, '#bca87e', Qt.AlignRight)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('돈물원 · DONMULWON')
        self.resize(1500, 900)
        self.setStyleSheet(
            "QMainWindow{background:#111416;color:#ded7c5;} "
            "QLabel{color:#ded7c5;} "
            "QLineEdit,QPlainTextEdit,QComboBox{background:#202428;color:#eee4d2;border:1px solid #51483b;padding:7px;} "
            "QPushButton{background:#665039;color:#fff2d4;padding:8px 14px;border:1px solid #8a6c4c;} "
            "QProgressBar{border:1px solid #51483b;background:#202428;} "
            "QProgressBar::chunk{background:#806544;}"
        )

        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(18, 14, 18, 14)

        top = QHBoxLayout()
        title = QLabel('🏦 DONMULWON  ·  AI TRADING TEAM')
        title.setStyleSheet('font-size:22px;font-weight:700;')
        top.addWidget(title)
        top.addStretch()
        self.clock = QLabel()
        top.addWidget(self.clock)
        layout.addLayout(top)

        self.office = PixelOffice()
        layout.addWidget(self.office, 1)

        controls = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText('무엇을 분석할까요? (예: JOBY 지금 사도 괜찮아?)')
        self.button = QPushButton('분석 시작')
        self.button.clicked.connect(self.start_analysis)
        self.input.returnPressed.connect(self.start_analysis)
        self.weather = QComboBox()
        self.weather.addItems(['맑음', '비', '눈'])
        self.weather.currentTextChanged.connect(self.office.set_weather)
        controls.addWidget(self.input, 1)
        controls.addWidget(self.weather)
        controls.addWidget(self.button)
        layout.addLayout(controls)

        self.status = QLabel('대기 중 · TOP-DOWN PIXEL OFFICE')
        layout.addWidget(self.status)
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.hide()
        layout.addWidget(self.progress)
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setMaximumHeight(220)
        layout.addWidget(self.output)
        self.setCentralWidget(root)

        self.ui_timer = QTimer(self)
        self.ui_timer.timeout.connect(self.update_clock)
        self.ui_timer.start(1000)
        self.update_clock()
        self.thread = None
        self.worker = None

    def update_clock(self):
        now = datetime.now()
        period = self.office.auto_time()
        self.clock.setText(now.strftime('%Y-%m-%d  %H:%M:%S') + f'  ·  {period}')

    def start_analysis(self):
        q = self.input.text().strip()
        if not q or self.thread is not None:
            return
        behavior = self.office.motion.on_question()
        if behavior == 'summoned':
            self.status.setText('🏃 퇴근 후 긴급 호출 · AI TRADING TEAM 복귀 중...')
        elif behavior == 'overtime':
            self.status.setText('🌙 야근 모드 · AI TRADING TEAM 회의 시작')
        else:
            self.status.setText('⚔️ AI TRADING TEAM 회의 진행 중...')
        self.button.setEnabled(False)
        self.progress.show()
        self.output.clear()
        self.thread = QThread(self)
        self.worker = AnalysisWorker(q)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.output.connect(lambda t: self.output.setPlainText(t))
        self.worker.failed.connect(self.on_failed)
        self.worker.finished.connect(self.on_finished)
        self.worker.finished.connect(self.thread.quit)
        self.thread.finished.connect(self.cleanup_thread)
        self.thread.start()

    def on_failed(self, text):
        self.output.setPlainText('❌ 분석 오류\n\n' + text)
        self.status.setText('오류 발생 · 로그를 확인하세요')

    def on_finished(self):
        self.progress.hide()
        self.button.setEnabled(True)
        self.status.setText('✅ 분석 완료')

    def cleanup_thread(self):
        if self.worker:
            self.worker.deleteLater()
        if self.thread:
            self.thread.deleteLater()
        self.worker = None
        self.thread = None


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
