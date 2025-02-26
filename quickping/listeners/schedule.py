from datetime import datetime

from .base import BaseListener


class ScheduleListener(BaseListener):
    def is_triggered(self) -> bool:
        if not self.is_active():
            return False

        if (
            self.run_on_interval is not None
            and self.last_run + self.run_on_interval > datetime.now()
        ):
            return True

        for run_at in self.run_at:
            if run_at > self.last_run.time() and run_at < datetime.now().time():
                return True

        return False
