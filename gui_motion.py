from PySide6.QtCore import QTimer
from datetime import datetime

class MotionController:
    def __init__(self, office):
        self.office=office
        self.timer=QTimer(office)
        self.timer.timeout.connect(self.tick)
        self.timer.start(120)
        self.last_minute=None
        self.last_day=None
        self.sync_schedule(datetime.now())

    def sync_schedule(self, now):
        day=now.strftime('%Y-%m-%d')
        key=(day,now.hour,now.minute)
        if self.last_day!=day:
            self.last_day=day
            self.last_minute=None
        if self.last_minute==key:
            return
        self.last_minute=key
        c=self.office.characters
        if now.hour < 9:
            c.reset_office()
            for n in c.POSITIONS: c.active[n]=False
        elif now.hour==9 and now.minute==0:
            c.start_arrival()
        elif 9 < now.hour < 18 or (now.hour==9 and now.minute>0):
            if c.mode=='leaving': c.reset_office()
            if c.mode=='idle' and not any(c.active.values()): c.reset_office()
        elif now.hour==18 and now.minute==0:
            c.start_departure()
        elif now.hour > 18:
            c.mode='idle'; c.queue=[]
            for n in c.POSITIONS: c.active[n]=False

    def tick(self):
        now=datetime.now()
        self.sync_schedule(now)
        self.office.background.tick()
        self.office.characters.tick()
        self.office.update()
