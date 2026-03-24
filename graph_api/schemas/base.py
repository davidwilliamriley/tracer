from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AuditSchema(BaseModel):
    created_by: Optional[str] = None
    created_on: Optional[datetime] = None
    modified_by: Optional[str] = None
    modified_on: Optional[datetime] = None
