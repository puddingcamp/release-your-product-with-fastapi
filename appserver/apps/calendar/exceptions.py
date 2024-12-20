from fastapi import HTTPException, status


class HostNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="호스트가 없습니다.",
        )


class CalendarNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="캘린더가 없습니다.",
        )


class CalendarAlreadyExistsError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="캘린더가 이미 존재합니다.",
        )


class GuestPermissionError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="게스트는 캘린더를 생성할 수 없습니다.",
        )


class TimeSlotOverlapError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="겹치는 시간대가 이미 존재합니다.",
        )


class TimeSlotNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="시간대가 없습니다.",
        )


class SelfBookingError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="자기 자신에게는 부킹을 할 수 없습니다.",
        )



class PastBookingError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="과거 일자에는 부킹을 할 수 없습니다.",
        )


class BookingAlreadyExistsError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="이미 예약된 시간대입니다.",
        )


class InvalidYearMonthError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="유효하지 않은 년도 또는 월입니다.",
        )
