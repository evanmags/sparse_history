from faker import Faker

from sparse_history.user.repository import create_user, update_user
from sparse_history.database import SessionLocal


def seed_users():
    """
    creates 100,000 user history layers broken down to 1000 users with 100 updates each
    """
    f = Faker()
    with SessionLocal() as session:
        for _ in range(1000):
            user = create_user(session, name=f.name())
            for _ in range(100):
                update_user(
                    session,
                    user_id=user.id,
                    name=f.name() if f.random_int() % 2 == 0 else None,
                    email=f.email() if f.random_int() % 2 == 0 else None,
                    company=f.company() if f.random_int() % 2 == 0 else None,
                )
                session.commit()
