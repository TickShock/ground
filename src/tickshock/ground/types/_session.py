from typing import (
    List as _List,
    Final as _Final,
    Dict as _Dict,
)
from datetime import (
    datetime as _datetime,
    timedelta as _timedelta,
    timezone as _timezone,
)
from ._candle import (
    Candle as _Candle,
    CandleIntervalLiteral as _CandleIntervalLiteral,
)
from ..exceptions import (
    TickShockException as _TickShockException,
    TickShockTimezoneException as _TickShockTimezoneException,
)


class Session[SymbolStrT]:
    _MIN_MAP: _Final[_Dict[_CandleIntervalLiteral, int]] = {
        "m": 1,
        "5m": 5,
        "15m": 15,
        "30m": 30,
        "h": 60,
        "2h": 120,
        "4h": 240,
        "d": 1440,
        "w": 10080,
    }

    def __init__(
        self,
        symbol: SymbolStrT,
        intervals: _CandleIntervalLiteral,
        candles: _List[_Candle[SymbolStrT]],
        start_time: _datetime,
        end_time: _datetime,
    ) -> None:
        num_candles = len(candles)
        if num_candles <= 1:
            raise _TickShockException(
                f"'{symbol}' needs more candles",
            )

        self.symbol: _Final = symbol
        self.intervals: _Final = intervals
        self.candles: _Final = sorted(
            candles,
            key=lambda candle: candle.time,
        )
        self.num_candles: _Final = num_candles
        self.gaps: _Final = self._get_gaps(self.candles, self.intervals)
        self.start_time: _Final = self._vet_datetime(start_time)
        self.end_time: _Final = self._vet_datetime(end_time)

        if self.start_time >= self.end_time:
            raise _TickShockException(
                f"'{self.symbol}' candles start-time '{self.start_time}' must occur before '{self.end_time}'",
            )

        if self.candles[0].time < self.start_time:
            raise _TickShockException(
                f"'{self.symbol}' candles can not start before start-time '{self.start_time}'"
            )

        if self.candles[-1].time > self.end_time:
            raise _TickShockException(
                f"'{self.symbol}' candles can not end after end-time '{self.end_time}'"
            )

    def _vet_datetime(self, dt: _datetime) -> _datetime:
        if dt.tzinfo != _timezone.utc:
            raise _TickShockTimezoneException(dt, _timezone.utc)
        return dt

    def _get_mins_diff(self, interval: _CandleIntervalLiteral) -> int:
        return self._MIN_MAP[interval]

    def _get_gaps(
        self,
        candles: _List[_Candle[SymbolStrT]],
        intervals: _CandleIntervalLiteral,
    ) -> _List[_datetime]:
        if not candles or len(candles) < 2:
            return []

        mins_diff = self._get_mins_diff(intervals)

        gaps: _List[_datetime] = []

        for i in range(len(candles) - 1):
            current_time = candles[i].time
            next_actual_time = candles[i+1].time
            expected_next_time = current_time + _timedelta(minutes=mins_diff)

            while expected_next_time < next_actual_time:
                gaps.append(expected_next_time)
                expected_next_time += _timedelta(minutes=mins_diff)

        return gaps
