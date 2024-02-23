import logging
from litestar import Litestar
from litestar.di import Provide

from history_table_example.database import SessionLocal
from history_table_example.api.routes import (
    get_user_history_layer_route,
    get_user_history_route,
    get_user_route,
    get_users_route,
    update_user_route,
    create_user_route,
)
from litestar.logging import LoggingConfig


def get_database():
    with SessionLocal() as session:
        yield session


app = Litestar(
    route_handlers=[
        create_user_route,
        get_user_route,
        get_users_route,
        update_user_route,
        get_user_history_route,
        get_user_history_layer_route,
    ],
    logging_config=LoggingConfig(
        root={"level": logging.DEBUG, "handlers": ["console"]},
    ),
    dependencies={"database": Provide(get_database)},
)
