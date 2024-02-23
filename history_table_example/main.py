from pprint import pprint

from history_table_example.database import SessionLocal
from history_table_example.user.repository import (
    get_user_history,
    get_users,
    get_user,
    get_user_history_layer,
    get_user_at_history_layer,
    get_user_at_all_history_layers,
)

with SessionLocal() as session:
    user_layers = get_user_at_all_history_layers(
        session, "00366936-7861-4e32-b368-adec69aedf63"
    )
    for user_at_layer in user_layers:
        pprint(user_at_layer)
