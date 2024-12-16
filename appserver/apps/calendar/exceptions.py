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
