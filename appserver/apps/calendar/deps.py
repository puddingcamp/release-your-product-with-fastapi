from datetime import datetime
from typing import Annotated

from fastapi import Depends

from appserver.libs.datetime.datetime import utcnow


UtcNow = Annotated[datetime, Depends(utcnow)]
