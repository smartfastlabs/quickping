from datetime import datetime, timedelta


class History:
    def __init__(self, minutes: int):
        self.minutes = minutes
        self._changes = []

    def add(self, change):
        self._changes.append(change)
        self.trim()

    def trim(self):
        now = datetime.now()
        td = timedelta(minutes=self.minutes)
        self._changes = [
            change for change in self._changes if change.timestamp > now - td
        ]
        return self._changes

    def __bool__(self):
        return bool(self.trim())

    def __iter__(self):
        return iter(self.trim())
