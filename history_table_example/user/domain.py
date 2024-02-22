from datetime import datetime
from dataclasses import dataclass


@dataclass
class User:
    id: str
    name: str | None
    email: str | None
    company: str | None
    created_at: datetime
    updated_at: datetime
    last_edit_id: str


@dataclass
class UserHistoryLayer:
    id: str
    user_id: str
    name: str | None
    email: str | None
    company: str | None
    created_at: datetime
