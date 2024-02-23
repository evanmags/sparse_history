from datetime import datetime
from dataclasses import dataclass


@dataclass
class User:
    id: str
    name: str | None
    email: str | None
    company: str | None
    created_at: datetime
    revised_at: datetime
    revision_id: str


@dataclass
class UserRevision:
    id: str
    name: str | None
    email: str | None
    company: str | None
    revised_at: datetime
    revision_id: str
