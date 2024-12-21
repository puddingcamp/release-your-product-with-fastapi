import enum

class AttendanceStatus(enum.StrEnum):
    """참석 상태 종류
    - SCHEDULED: 예정
    - ATTENDED: 참석
    - NO_SHOW: 노쇼
    - CANCELLED: 취소
    - SAME_DAY_CANCEL: 당일 취소
    - LATE: 지각
    """
    SCHEDULED = enum.auto()
    ATTENDED = enum.auto()
    NO_SHOW = enum.auto()
    CANCELLED = enum.auto()
    SAME_DAY_CANCEL = enum.auto()
    LATE = enum.auto()
