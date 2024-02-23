from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select

from sparse_history.user.domain import User, UserHistoryLayer
from sparse_history.user.model import UserHistoryLayerModel
from sparse_history.user.repository.queries import (
    build_list_user_historical_state_query,
    build_list_users_query,
)


def create_user(
    db: Session,
    name: str | None = None,
    email: str | None = None,
    company: str | None = None,
):
    db_user = UserHistoryLayerModel(name=name, email=email, company=company)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return User(
        id=db_user.user_id,
        name=db_user.name,
        email=db_user.email,
        company=db_user.company,
        created_at=db_user.created_at,
        updated_at=db_user.created_at,
        last_edit_id=db_user.id,
    )


def get_user(db: Session, user_id: str):
    user = db.execute(
        build_list_users_query().filter(UserHistoryLayerModel.user_id == user_id)
    ).one_or_none()
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
    db_user = UserHistoryLayerModel(
        user_id=user_id, name=name, email=email, company=company
    )
    db.add(db_user)
    db.commit()
    return get_user(db, user_id)


def get_user_history(db: Session, user_id: str):
    user_history = (
        db.query(UserHistoryLayerModel)
        .filter(UserHistoryLayerModel.user_id == user_id)
        .all()
    )
    return [
        UserHistoryLayer(
            id=layer.id,
            user_id=layer.user_id,
            name=layer.name,
            email=layer.email,
            company=layer.company,
            created_at=layer.created_at,
        )
        for layer in user_history
    ]


def get_user_history_layer(db: Session, user_id: str, layer_id: str):
    layer = (
        db.query(UserHistoryLayerModel)
        .filter(
            UserHistoryLayerModel.id == layer_id,
            UserHistoryLayerModel.user_id == user_id,
        )
        .one_or_none()
    )
    if not layer:
        return None
    return UserHistoryLayer(
        id=layer.id,
        user_id=layer.user_id,
        name=layer.name,
        email=layer.email,
        company=layer.company,
        created_at=layer.created_at,
    )


def get_user_at_history_layer(db: Session, user_id: str, layer_id: str):
    history_layer_created_at = (
        select(UserHistoryLayerModel.created_at)
        .filter(UserHistoryLayerModel.id == layer_id)
        .scalar_subquery()
    )

    user = db.execute(
        build_list_users_query().filter(
            UserHistoryLayerModel.user_id == user_id,
            UserHistoryLayerModel.created_at <= history_layer_created_at,
        )
    ).one_or_none()

    if not user:
        return None
    return User(**user._mapping)


def get_user_at_all_history_layers(db: Session, user_id: str):
    query = build_list_user_historical_state_query(user_id)
    layers = db.execute(query).all()
    return [User(**layer._mapping) for layer in layers]
