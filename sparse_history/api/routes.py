from typing import Literal

from sqlalchemy.orm import Session
from pydantic import TypeAdapter
from litestar import get, patch, post

from sparse_history.api.dto import (
    UserRevisionReturn,
    UserInput,
    UserReturn,
)
from sparse_history.user.repository import (
    get_user,
    get_users,
    get_user_at_all_revisions,
    get_user_revision,
    get_user_at_revision,
    get_user_revisions,
    update_user,
    create_user,
)

DisplayType = Literal["sparse", "dense"]


@get("/users")
async def get_users_route(database: Session) -> list[UserReturn]:
    return get_users(database)


@post("/users")
async def create_user_route(user: UserInput, database: Session) -> UserReturn:
    return create_user(database, user.name, user.email, user.company)


@get("/users/{user_id:str}")
async def get_user_route(user_id: str, database: Session) -> UserReturn:
    return get_user(database, user_id)


@patch("/users/{user_id:str}")
async def update_user_route(
    user_id: str, user: UserInput, database: Session
) -> UserReturn:
    return update_user(database, user_id, user.name, user.email, user.company)


@get("/users/{user_id:str}/revisions")
async def get_user_revisions_route(
    user_id: str,
    database: Session,
    display: DisplayType = "sparse",
) -> list[UserRevisionReturn] | list[UserReturn]:
    match display:
        case "sparse":
            revisions = get_user_revisions(database, user_id)
            model = UserRevisionReturn
        case "dense":
            revisions = get_user_at_all_revisions(database, user_id)
            model = UserReturn

    return TypeAdapter(list[model]).validate_python(revisions, from_attributes=True)


@get("/users/{user_id:str}/revisions/{revision_id:str}")
async def get_user_revision_route(
    user_id: str,
    revision_id: str,
    database: Session,
    display: DisplayType = "sparse",
) -> UserRevisionReturn | UserReturn:
    match display:
        case "sparse":
            revisions = get_user_revision(database, user_id, revision_id)
            model = UserRevisionReturn
        case "dense":
            revisions = get_user_at_revision(database, user_id, revision_id)
            model = UserReturn
    return model.model_validate(revisions, from_attributes=True)
