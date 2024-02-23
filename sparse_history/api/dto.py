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
    updated_at: datetime
    last_edit_id: str


class UserHistoryLayerReturn(BaseModel):
    id: str
    user_id: str
    name: str | None
    email: str | None
    company: str | None
    created_at: datetime
