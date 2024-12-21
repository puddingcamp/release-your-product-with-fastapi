from datetime import datetime, timezone


def utcnow() -> datetime:
    return aware_datetime(datetime.now())


def aware_datetime(dt: datetime, tzinfo: timezone = timezone.utc) -> datetime:
    return dt.replace(tzinfo=tzinfo)
