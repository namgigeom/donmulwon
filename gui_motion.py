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
        self.overtime=False
        self.sync_schedule(datetime.now())

    def sync_schedule(self, now):
        day=now.strftime('%Y-%m-%d')
        key=(day,now.hour,now.minute)
        if self.last_day!=day:
            self.last_day=day
            self.last_minute=None
            self.overtime=False
        if self.last_minute==key:
            return
        self.last_minute=key
        c=self.office.characters
        if now.hour < 9:
            self.overtime=False
            c.reset_office()
            for n in c.POSITIONS: c.active[n]=False
        elif now.hour==9 and now.minute==0:
            self.overtime=False
            c.start_arrival()
        elif 9 < now.hour < 17 or (now.hour==9 and now.minute>0):
            if c.mode=='leaving': c.reset_office()
            if c.mode=='idle' and not any(c.active.values()): c.reset_office()
        elif now.hour==17 and now.minute>=50:
            # Once closing is near, a new question means overtime rather than departure.
            if c.mode=='leaving': c.reset_office()
            if not self.overtime and c.mode not in ('overtime','summoned'):
                c.reset_office()
        elif now.hour==18 and now.minute==0:
            if not self.overtime:
                c.start_departure()
        elif now.hour > 18:
            if not self.overtime and c.mode not in ('summoned','overtime'):
                c.mode='idle'; c.queue=[]
                for n in c.POSITIONS: c.active[n]=False

    def on_question(self):
        now=datetime.now()
        c=self.office.characters
        # 17:50-18:00: agents stay at work and treat the request as overtime.
        # After 18:00: agents rush back through the entrance to answer the user.
        if 17 <= now.hour < 18 and now.minute >= 50:
            self.overtime=True
            c.summon_for_question(overtime=True)
            return 'overtime'
        if now.hour >= 18 or now.hour < 9:
            self.overtime=False
            c.summon_for_question(overtime=False)
            return 'summoned'
        return 'normal'

    def tick(self):
        now=datetime.now()
        self.sync_schedule(now)
        self.office.background.tick()
        self.office.characters.tick()
        self.office.update()
