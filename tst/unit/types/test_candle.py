import pytest
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from src.tickshock.ground.types import Candle
from src.tickshock.ground.exceptions import TickShockTimezoneException


def utc_now():
    return datetime.now(timezone.utc)


class TestCandle:
    @pytest.mark.parametrize("symbol, interval, o, c, h, l, vol", [
        ("BTCUSDT", "1m", 100.0, 110.0, 115.0, 95.0, 1000),
        ("ETHUSD", "h", 2500.50, 2480.25, 2510.0, 2470.0, 500),
    ])
    def test_candle_initialization(self, symbol, interval, o, c, h, l, vol):
        dt = utc_now()
        candle = Candle(symbol, interval, o, c, h, l, vol, dt)
        
        assert candle.symbol == symbol
        assert candle.type == interval
        assert candle.open == o
        assert candle.close == c
        assert candle.high == h
        assert candle.low == l
        assert candle.volume == vol
        assert candle.time == dt

    def test_vet_datetime_valid_utc(self):
        dt = datetime(2026, 1, 1, tzinfo=timezone.utc)
        Candle("BTC", "m", 10, 11, 12, 9, 100, dt)

    @pytest.mark.parametrize("tz", [
        None,
        timezone(timedelta(hours=5)), # Offset aware
    ])
    def test_vet_datetime_invalid_raises_exception(self, tz):
        dt = datetime(2026, 1, 1, tzinfo=tz)
        with pytest.raises(TickShockTimezoneException):
            Candle("BTC", "m", 10, 11, 12, 9, 100, dt)

    @pytest.mark.parametrize("o, c, h, l, expected_middle", [
        (100.0, 110.0, 120.0, 90.0, Decimal("105.0")),
        (110.0, 100.0, 120.0, 90.0, Decimal("105.0")),
        (100.0, 100.0, 110.0, 90.0, Decimal("100.0")),
    ])
    def test_get_middle_calculation(self, o, c, h, l, expected_middle):
        candle = Candle("TEST", "m", o, c, h, l, 1, utc_now())
        assert candle.middle == expected_middle
        assert isinstance(candle.middle, Decimal)
