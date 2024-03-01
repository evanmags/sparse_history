from datetime import datetime
from pydantic import BaseModel


class UserInput(BaseModel):
    name: str | None
    email: str | None
    company: str | None


class UserReturn(BaseModel):
    id: str
    name: str | None
    email: str | None
    company: str | None
    created_at: datetime
    revised_at: datetime
    revision_id: str


class UserRevisionReturn(BaseModel):
    id: str
    name: str | None
    email: str | None
    company: str | None
    revised_at: datetime
    revision_id: str
