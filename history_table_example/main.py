from pprint import pprint

from history_table_example.database import SessionLocal
from history_table_example.user.repository import (
    get_user_history,
    get_users,
    get_user,
    get_user_history_layer,
    get_user_at_history_layer,
)

with SessionLocal() as session:
    user = get_user(session, "00366936-7861-4e32-b368-adec69aedf63")
    pprint(user)
    user_at_layer = get_user_at_history_layer(
        session, user.id, "99ee9626-65b5-40ee-93f1-690b816c2474"
    )
    pprint(user_at_layer)
