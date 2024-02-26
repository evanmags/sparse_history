import logging
from random import randint
import sys

from faker import Faker

from sparse_history.user.repository import create_user, update_user
from sparse_history.database import SessionLocal

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_users():
    """
    creates 30,000 users with a variable (10, 50] history revisions
    on the average this will create ~900_000 rows in the database
    """
    f = Faker()
    with SessionLocal() as session:
        for _i in range(30000):
            user = create_user(session, name=f.name())
            logger.info("created user: %s user count: %d", user.id, _i)
            revision_count = randint(10, 50)
            for _ in range(revision_count):
                update_user(
                    session,
                    user_id=user.id,
                    name=f.name() if f.random_int() % 2 == 0 else None,
                    email=f.email() if f.random_int() % 2 == 0 else None,
                    company=f.company() if f.random_int() % 2 == 0 else None,
                )
                session.commit()
            logger.info("created %d revisions for user: %s", revision_count, user.id)


if __name__ == "__main__":
    seed_users()
