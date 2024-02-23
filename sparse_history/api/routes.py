from typing import Literal

from sqlalchemy.orm import Session
from litestar import get, patch, post

from sparse_history.api.dto import (
    UserHistoryLayerReturn,
    UserInput,
    UserReturn,
)
from sparse_history.user.repository import (
    get_user,
    get_users,
    get_user_at_all_history_layers,
    get_user_history_layer,
    get_user_at_history_layer,
    get_user_history,
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


@get("/users/{user_id:str}/history")
async def get_user_history_route(
    user_id: str,
    database: Session,
    display: DisplayType = "sparse",
) -> list[UserHistoryLayerReturn] | list[UserReturn]:
    match display:
        case "sparse":
            return get_user_history(database, user_id)
        case "dense":
            return get_user_at_all_history_layers(database, user_id)


@get("/users/{user_id:str}/history/{layer_id:str}")
async def get_user_history_layer_route(
    user_id: str,
    layer_id: str,
    database: Session,
    display: DisplayType = "sparse",
) -> UserHistoryLayerReturn | UserReturn:
    match display:
        case "sparse":
            return get_user_history_layer(database, layer_id)
        case "dense":
            return get_user_at_history_layer(database, user_id, layer_id)
