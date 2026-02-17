import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock
from src.tickshock.ground.types import Session
from src.tickshock.ground.exceptions import TickShockException, TickShockTimezoneException


DT_2026_01_01_0000 = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
DT_2026_01_01_0100 = datetime(2026, 1, 1, 1, 0, tzinfo=timezone.utc)


def create_mock_candle(dt: datetime):
    candle = MagicMock()
    candle.time = dt
    return candle


class TestSession:
    def test_session_init_success(self):
        start = DT_2026_01_01_0000
        end = DT_2026_01_01_0100
        c1 = create_mock_candle(start + timedelta(minutes=10))
        c2 = create_mock_candle(start + timedelta(minutes=5))
        
        session = Session("BTC", "5m", [c1, c2], start, end)
        
        assert session.num_candles == 2
        assert session.candles[0].time < session.candles[1].time
        assert session.symbol == "BTC"

    @pytest.mark.parametrize("start, end, candle_times, expected_msg", [
        (DT_2026_01_01_0000, DT_2026_01_01_0100, [DT_2026_01_01_0000 + timedelta(minutes=5)], "needs more candles"),
        (DT_2026_01_01_0100, DT_2026_01_01_0000, [DT_2026_01_01_0000, DT_2026_01_01_0100], "must occur before"),
        (DT_2026_01_01_0100, DT_2026_01_01_0100 + timedelta(hours=1), [DT_2026_01_01_0000, DT_2026_01_01_0100], "can not start before start-time"),
        (DT_2026_01_01_0000, DT_2026_01_01_0100, [DT_2026_01_01_0000, DT_2026_01_01_0100 + timedelta(minutes=1)], "can not end after end-time"),
    ])
    def test_session_validation_errors(self, start, end, candle_times, expected_msg):
        candles = [create_mock_candle(dt) for dt in candle_times]
        
        with pytest.raises(TickShockException, match=expected_msg):
            Session("TEST", "m", candles, start, end)

    @pytest.mark.parametrize("interval, candle_times, expected_gaps", [
        (
            "m",
            [DT_2026_01_01_0000, DT_2026_01_01_0000 + timedelta(minutes=1), DT_2026_01_01_0000 + timedelta(minutes=2)],
            [],
        ),
        (
            "m",
            [DT_2026_01_01_0000, DT_2026_01_01_0000 + timedelta(minutes=2)],
            [DT_2026_01_01_0000 + timedelta(minutes=1)],
        ),
        (
            "h",
            [DT_2026_01_01_0000, DT_2026_01_01_0000 + timedelta(hours=4)],
            [DT_2026_01_01_0000 + timedelta(hours=i) for i in range(1, 4)],
        ),
        (
            "15m",
            [DT_2026_01_01_0000, DT_2026_01_01_0000 + timedelta(minutes=15), DT_2026_01_01_0000 + timedelta(minutes=60)],
            [DT_2026_01_01_0000 + timedelta(minutes=30), DT_2026_01_01_0000 + timedelta(minutes=45)],
        ),
    ])
    def test_gap_detection(self, interval, candle_times, expected_gaps):
        start = DT_2026_01_01_0000
        end = DT_2026_01_01_0000 + timedelta(days=1)
        candles = [create_mock_candle(dt) for dt in candle_times]
        
        session = Session("GAP-TEST", interval, candles, start, end)
        
        assert session.gaps == expected_gaps

    @pytest.mark.parametrize("interval, offsets, expected_gap_offsets", [
        ("m", [0], []),
        ("m", [], []),
        ("m", [0, 1, 2], []),
        ("m", [0, 2], [1]),
        ("h", [0, 180], [60, 120]),
        ("15m", [0, 15, 60], [30, 45]),
    ])
    def test_get_gaps_logic(self, interval, offsets, expected_gap_offsets):
        session = Session.__new__(Session)

        base_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
        candles = []
        for o in offsets:
            c = MagicMock()
            c.time = base_time + timedelta(minutes=o)
            candles.append(c)

        expected_gaps = [base_time + timedelta(minutes=o) for o in expected_gap_offsets]

        assert session._get_gaps(candles, interval) == expected_gaps

    @pytest.mark.parametrize("invalid_tz", [
        None,
        timezone(timedelta(hours=-5)),
        timezone(timedelta(hours=8)),
    ])
    def test_session_timezone_validation(self, invalid_tz):
        valid_dt = datetime(2026, 1, 1, tzinfo=timezone.utc)
        invalid_dt = datetime(2026, 1, 1, tzinfo=invalid_tz)

        c1 = create_mock_candle(valid_dt)
        c2 = create_mock_candle(valid_dt + timedelta(minutes=5))

        with pytest.raises(TickShockTimezoneException):
            Session("TEST", "m", [c1, c2], invalid_dt, valid_dt + timedelta(hours=1))

        with pytest.raises(TickShockTimezoneException):
            Session("TEST", "m", [c1, c2], valid_dt, invalid_dt)
