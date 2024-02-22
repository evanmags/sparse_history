from sqlalchemy import TEXT
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func, select

from history_table_example.user.domain import User, UserHistoryLayer
from history_table_example.user.model import UserModel


"""
-- the sql equivalent of the query below
-- performed @ ~150 ms compressing 100,000 records to 1000
-- performed @  ~50 ms compressing     100 records to    1

select distinct on (user_id)
	user_id
	, any_value(name) over(w_uid) name
	, any_value(email) over(w_uid) email
	, any_value(company) over(w_uid) company
	, created_at
	, max(created_at) over(w_uid) updated_at
	, first_value(id) over(w_uid) last_edit_id
from users
window w_uid as (partition by user_id order by created_at desc)
order by user_id, created_at asc;
"""

partition = dict(partition_by=UserModel.user_id, order_by=UserModel.created_at.desc())
list_users_query = (
    select(
        UserModel.user_id.label("id"),
        func.any_value(UserModel.name).over(**partition).label("name"),
        func.any_value(UserModel.email).over(**partition).label("email"),
        func.any_value(UserModel.company).over(**partition).label("company"),
        UserModel.created_at,
        func.max(UserModel.created_at).over(**partition).label("updated_at"),
        func.first_value(UserModel.id)
        .over(**partition)
        .cast(TEXT)
        .label("last_edit_id"),
    )
    .order_by(UserModel.user_id, UserModel.created_at.asc())
    .distinct(UserModel.user_id)
)


def create_user(
    db: Session,
    name: str | None = None,
    email: str | None = None,
    company: str | None = None,
):
    db_user = UserModel(name=name, email=email, company=company)
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
        list_users_query.filter(UserModel.user_id == user_id)
    ).one_or_none()
    if not user:
        return None
    return User(**user._mapping)


def get_users(db: Session):
    users = db.execute(list_users_query).all()
    return [User(**user._mapping) for user in users]


def get_user_history(db: Session, user_id: str):
    user_history = db.query(UserModel).filter(UserModel.user_id == user_id).all()
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


def get_user_history_layer(db: Session, layer_id: str):
    layer = db.query(UserModel).filter(UserModel.id == layer_id).one_or_none()
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
        select(UserModel.created_at).filter(UserModel.id == layer_id).scalar_subquery()
    )

    user = db.execute(
        list_users_query.filter(
            UserModel.user_id == user_id,
            UserModel.created_at <= history_layer_created_at,
        )
    ).one_or_none()

    if not user:
        return None
    return User(**user._mapping)


def update_user(
    db: Session,
    user_id: str,
    name: str | None = None,
    email: str | None = None,
    company: str | None = None,
):
    db_user = UserModel(user_id=user_id, name=name, email=email, company=company)
    db.add(db_user)
    db.commit()
    return get_user(db, user_id)
