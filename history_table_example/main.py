from pprint import pprint

from history_table_example.database import SessionLocal
from history_table_example.user.repository import get_users

with SessionLocal() as session:
    users = get_users(session)
    for user in users:
        pprint(user)
