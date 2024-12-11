import pytest
from appserver.libs.datetime.calendar import (
    get_start_weekday_of_month,
    get_last_day_of_month,
    get_range_days_of_month,
)


@pytest.mark.parametrize("year, month, expected", [
    (2024, 12, 6),
    (2025, 2, 5),
])
def test_get_start_weekday_of_month(year, month, expected):
    assert get_start_weekday_of_month(year, month) == expected


@pytest.mark.parametrize("year, month, expected", [
    (2024, 2, 29),
    (2025, 2, 28),
    (2024, 4, 30),
    (2024, 12, 31),
])
def test_get_last_day_of_month(year, month, expected):
    assert get_last_day_of_month(year, month) == expected


@pytest.mark.parametrize("year, month, expected_padding_count, expected_total_count", [
    # 2024년 3월: 금요일(5)에 시작, 31일까지
    (2024, 3, 5, 36),
    # 2024년 2월: 목요일(4)에 시작, 윤년으로 29일까지
    (2024, 2, 4, 33),
    # 2024년 2월: 목요일(4)에 시작, 윤년으로 29일까지
    (2025, 2, 6, 34),
    # 2024년 4월: 월요일(1)에 시작, 30일까지
    (2024, 4, 1, 31),
    # 2024년 12월: 일요일(0)에 시작, 31일까지
    (2024, 12, 0, 31),
])
def test_get_range_days_of_month(year, month, expected_padding_count, expected_total_count):
    days = get_range_days_of_month(year, month)
    padding_count = days[:expected_padding_count]
    
    assert sum(padding_count) == 0
    assert days[expected_padding_count] == 1
    assert len(days) == expected_total_count

