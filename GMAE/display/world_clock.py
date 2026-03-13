from dataclasses import dataclass


@dataclass(frozen=True)
class KeepTime:
    days: int
    hours: int
    minutes: int

    def add_time(self, amount_of_time: int) -> "KeepTime":
        total = self.days * 24 * 60 + self.hours * 60 + self.minutes + amount_of_time
        if total < 0:
            total = 0

        new_days = total // (24 * 60)
        hours_left = total % (24 * 60)
        new_hours = hours_left // 60
        new_minutes = hours_left % 60

        return KeepTime(new_days, new_hours, new_minutes)

    def __str__(self) -> str:
        return f"Day: {self.days}, {self.hours:02d}:{self.minutes:02d}"


class WorldClock:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WorldClock, cls).__new__(cls)
            cls._instance.days = 0
            cls._instance.hours = 0
            cls._instance.minutes = 0
        return cls._instance

    def set_time(self, days: int, hours: int, minutes: int) -> None:
        self.days = days
        self.hours = hours
        self.minutes = minutes

    def get_time(self) -> KeepTime:
        return KeepTime(self.days, self.hours, self.minutes)

    def increment_time(self, amount: int) -> None:
        total = self.days * 24 * 60 + self.hours * 60 + self.minutes + amount

        if total < 0:
            total = 0

        self.days = total // (24 * 60)
        hours_left = total % (24 * 60)
        self.hours = hours_left // 60
        self.minutes = hours_left % 60

    def __str__(self) -> str:
        return f"Day: {self.days}, {self.hours:02d}:{self.minutes:02d}"