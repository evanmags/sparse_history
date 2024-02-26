from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select

from sparse_history.user.domain import User, UserRevision
from sparse_history.user.model import UserRevisionModel
from sparse_history.user.repository.queries import (
    build_get_user_query,
    build_list_user_historical_state_query,
    build_list_users_query,
)


def create_user(
    db: Session,
    name: str | None = None,
    email: str | None = None,
    company: str | None = None,
):
    db_user = UserRevisionModel(name=name, email=email, company=company)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return User(
        id=db_user.user_id,
        name=db_user.name,
        email=db_user.email,
        company=db_user.company,
        created_at=db_user.revised_at,
        revised_at=db_user.revised_at,
        revision_id=db_user.revision_id,
    )


def get_user(db: Session, user_id: str):
    user = db.execute(build_get_user_query(user_id)).one_or_none()
    if not user:
        return None
    return User(**user._mapping)


def get_users(db: Session):
    users = db.execute(build_list_users_query()).all()
    return [User(**user._mapping) for user in users]


def update_user(
    db: Session,
    user_id: str,
    name: str | None = None,
    email: str | None = None,
    company: str | None = None,
):
    db_user = UserRevisionModel(
        user_id=user_id, name=name, email=email, company=company
    )
    db.add(db_user)
    db.commit()
    return get_user(db, user_id)


def get_user_revisions(db: Session, user_id: str):
    user_revisions = (
        db.query(UserRevisionModel).filter(UserRevisionModel.user_id == user_id).all()
    )
    return [
        UserRevision(
            id=revision.user_id,
            name=revision.name,
            email=revision.email,
            company=revision.company,
            revised_at=revision.revised_at,
            revision_id=revision.revision_id,
        )
        for revision in user_revisions
    ]


def get_user_revision(db: Session, user_id: str, revision_id: str):
    revision = (
        db.query(UserRevisionModel)
        .filter(
            UserRevisionModel.revision_id == revision_id,
            UserRevisionModel.user_id == user_id,
        )
        .one_or_none()
    )
    print(revision)
    if not revision:
        return None
    return UserRevision(
        id=revision.user_id,
        name=revision.name,
        email=revision.email,
        company=revision.company,
        revised_at=revision.revised_at,
        revision_id=revision.revision_id,
    )


def get_user_at_revision(db: Session, user_id: str, revision_id: str):
    user = db.execute(build_get_user_query(user_id, revision_id)).one_or_none()

    if not user:
        return None
    print(user._mapping)
    return User(**user._mapping)


def get_user_at_all_revisions(db: Session, user_id: str):
    query = build_list_user_historical_state_query(user_id)
    revisions = db.execute(query).all()
    return [User(**revision._mapping) for revision in revisions]
