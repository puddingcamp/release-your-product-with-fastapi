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
