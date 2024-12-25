import enum


class AccountStatus(enum.Enum):
    # 활동 중
    ACTIVE = "active"
    # 탈퇴
    WITHDRAWAL = "withdrawal"
    # 정지
    SUSPENDED = "suspended"
    # 삭제
    DELETED = "deleted"
