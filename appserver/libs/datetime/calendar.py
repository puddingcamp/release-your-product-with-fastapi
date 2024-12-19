from datetime import date, timedelta


def get_start_weekday_of_month(year, month):
    """
    월의 시작 요일을 가져옴 (월요일=0 ~ 일요일=6)
    
    >>> get_start_weekday_of_month(2024, 12)
    6
    >>> get_start_weekday_of_month(2025, 2)
    5
    """
    return date(year, month, 1).weekday()


def get_last_day_of_month(year, month):
    """
    월의 마지막 날짜를 가져옴
    
    >>> get_last_day_of_month(2024, 2)
    29
    >>> get_last_day_of_month(2025, 2)
    28
    >>> get_last_day_of_month(2024, 4)
    30
    >>> get_last_day_of_month(2024, 12)
    31
    """
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)

    result = next_month - timedelta(days=1)
    return result.day


def get_range_days_of_month(year, month):
    """월의 일수를 가져옴

    >>> result = get_range_days_of_month(2024, 3)
    >>> result[:5]
    [0, 0, 0, 0, 0]
    >>> result[5]
    1
    >>> len(result)
    36
    >>> result = get_range_days_of_month(2024, 2)  # 윤년
    >>> result[:4]
    [0, 0, 0, 0]
    >>> result[4]
    1
    >>> len(result)
    33
    """

    # 월의 시작 요일을 가져옴 (월요일=0 ~ 일요일=6)
    start_weekday = get_start_weekday_of_month(year, month)
    
    # 월의 마지막 날짜를 가져옴
    last_day = get_last_day_of_month(year, month)
    
    # 월요일=0을 월요일=1로 변환 (일요일=0으로 만들기 위해)
    start_weekday = (start_weekday + 1) % 7
    
    # 결과 리스트 생성
    result = [0] * start_weekday  # 시작 요일 전까지 0으로 채움
    
    # 1일부터 마지막 날까지 추가
    # for day in range(1, last_day + 1):
    #     result.append(day)
    
    return result + list(range(1, last_day + 1))


from datetime import date, timedelta

def get_next_weekday(weekday: int, start_date: date = None) -> date:
    """
    주어진 날짜를 기준으로 가장 가까운 요일의 날짜를 반환합니다.
    만약 주어진 날짜가 없으면 오늘 날짜를 기준으로 합니다.

    :param start_date: 기준 날짜 (기본값: 오늘)
    :return: 가장 가까운 요일의 날짜

    >>> import calendar
    >>> from datetime import date
    >>> target_date = date(2024, 12, 1)
    >>> get_next_weekday(calendar.MONDAY, target_date)
    datetime.date(2024, 12, 2)
    >>> get_next_weekday(calendar.TUESDAY, target_date)
    datetime.date(2024, 12, 3)
    >>> get_next_weekday(calendar.WEDNESDAY, target_date)
    datetime.date(2024, 12, 4)
    """
    if start_date is None:
        start_date = date.today()

    days_ahead = (weekday - start_date.weekday() + 7) % 7
    if days_ahead == 0:
        return start_date
    else:
        return start_date + timedelta(days=days_ahead)
