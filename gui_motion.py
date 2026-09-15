from PySide6.QtCore import QTimer
from datetime import datetime

class MotionController:
    """Real-time office schedule. The GUI may use this controller or call the same CharacterLayer API directly."""
    def __init__(self,office):
        self.office=office
        self.timer=QTimer(office); self.timer.timeout.connect(self.tick); self.timer.start(250)
        self.last_minute=None; self.last_day=None; self.overtime=False
        self.sync_schedule(datetime.now())
    def sync_schedule(self,now):
        key=(now.strftime('%Y-%m-%d'),now.hour,now.minute)
        if self.last_day!=key[0]: self.last_day=key[0]; self.last_minute=None; self.overtime=False
        if self.last_minute==key:return
        self.last_minute=key; c=self.office.characters
        if now.hour<9:
            self.overtime=False
            if c.mode not in ('meeting_arrival','meeting','verdict'): c.reset_off_hours()
        elif now.hour==9 and now.minute==0:
            self.overtime=False; c.start_arrival()
        elif 9<=now.hour<18:
            if c.mode=='off_hours': c.reset_office()
        else:
            if not self.overtime and c.mode not in ('meeting_arrival','meeting','verdict','arrival'):
                c.reset_off_hours()
    def on_question(self):
        now=datetime.now(); c=self.office.characters
        if now.hour>=18 or now.hour<9:
            self.overtime=True; c.summon_for_question(overtime=True); return 'summoned'
        if now.hour==17 and now.minute>=50:
            self.overtime=True; c.summon_for_question(overtime=True); return 'overtime'
        c.summon_for_question(overtime=False); return 'normal'
    def tick(self):
        now=datetime.now(); self.sync_schedule(now); self.office.background.tick(); self.office.characters.tick(); self.office.update()
