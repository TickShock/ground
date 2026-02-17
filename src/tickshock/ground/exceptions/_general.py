from datetime import (
    datetime as _datetime,
    timezone as _timezone,
)


class TickShockException(Exception):
    pass


class TickShockTimezoneException(TickShockException):
    def __init__(self, dt: _datetime, expected: _timezone) -> None:
        super().__init__(f"'{dt}' must be in '{expected}' timezone")
