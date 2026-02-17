from typing import (
    Final as _Final,
    Literal as _Literal,
)
from datetime import (
    datetime as _datetime,
    timezone as _timezone,
)
from decimal import (
    Decimal as _Decimal,
)
from ..exceptions import (
    TickShockTimezoneException as _TickShockTimezoneException,
)


CandleIntervalLiteral = _Literal["m", "5m", "15m", "30m", "h", "2h", "4h", "d", "w"]


class Candle[SymbolStrT]:
    def __init__(
        self,
        symbol_: SymbolStrT,
        type_: CandleIntervalLiteral,
        open_: float,
        close_: float,
        high_: float,
        low_: float,
        volume_: float,
        dt_: _datetime,
    ) -> None:
        self.symbol: _Final = symbol_
        self.type: _Final = type_
        self.open: _Final = open_
        self.high: _Final = high_
        self.low: _Final = low_
        self.close: _Final = close_
        self.volume: _Final = volume_
        self.time: _Final = self._vet_datetime(dt_)
        self.middle: _Final = self._get_middle(
            open_,
            close_,
            high_,
            low_,
        )

    def _vet_datetime(self, dt: _datetime) -> _datetime:
        if dt.tzinfo != _timezone.utc:
            raise _TickShockTimezoneException(dt, _timezone.utc)
        return dt

    def _get_middle(
        self,
        open_: float,
        close_: float,
        high_: float,
        low_: float,
    ) -> _Decimal:
        is_increasing = open_ < close_

        top_val = high_
        top_body = close_ if is_increasing else open_
        bottom_body = open_ if is_increasing else close_
        bottom_val = low_

        top_middle = (top_val + top_body) / 2
        bottom_middle = (bottom_body + bottom_val) / 2

        return _Decimal.from_float(
            round(
                (top_middle + bottom_middle) / 2,
                8,
            )
        )
