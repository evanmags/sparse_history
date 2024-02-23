from sqlalchemy import TEXT
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func, select, case

from history_table_example.user.domain import User, UserHistoryLayer
from history_table_example.user.model import UserHistoryLayerModel


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

list_users_query_partition = dict(
    partition_by=UserHistoryLayerModel.user_id,
    order_by=UserHistoryLayerModel.created_at.desc(),
)
list_users_query = (
    select(
        UserHistoryLayerModel.user_id.label("id"),
        func.any_value(UserHistoryLayerModel.name)
        .over(**list_users_query_partition)
        .label("name"),
        func.any_value(UserHistoryLayerModel.email)
        .over(**list_users_query_partition)
        .label("email"),
        func.any_value(UserHistoryLayerModel.company)
        .over(**list_users_query_partition)
        .label("company"),
        UserHistoryLayerModel.created_at,
        func.max(UserHistoryLayerModel.created_at)
        .over(**list_users_query_partition)
        .label("updated_at"),
        func.first_value(UserHistoryLayerModel.id)
        .over(**list_users_query_partition)
        .cast(TEXT)
        .label("last_edit_id"),
    )
    .order_by(UserHistoryLayerModel.user_id, UserHistoryLayerModel.created_at.asc())
    .distinct(UserHistoryLayerModel.user_id)
)


def build_list_user_historical_state_query(user_id: str):
    subquery = (
        select(
            UserHistoryLayerModel.id,
            UserHistoryLayerModel.user_id,
            UserHistoryLayerModel.name,
            func.sum(case((UserHistoryLayerModel.name.is_(None), 0), else_=1))
            .over(order_by=UserHistoryLayerModel.created_at)
            .label("name_partition"),
            UserHistoryLayerModel.email,
            func.sum(case((UserHistoryLayerModel.email.is_(None), 0), else_=1))
            .over(order_by=UserHistoryLayerModel.created_at)
            .label("email_partition"),
            UserHistoryLayerModel.company,
            func.sum(case((UserHistoryLayerModel.company.is_(None), 0), else_=1))
            .over(order_by=UserHistoryLayerModel.created_at)
            .label("company_partition"),
            UserHistoryLayerModel.created_at,
        )
        .filter(UserHistoryLayerModel.user_id == user_id)
        .subquery("subquery")
    )

    # Main query
    return select(
        subquery.c.user_id.label("id"),
        subquery.c.id.label("last_edit_id"),
        func.first_value(subquery.c.name)
        .over(partition_by=subquery.c.name_partition, order_by=subquery.c.created_at)
        .label("name"),
        func.first_value(subquery.c.email)
        .over(partition_by=subquery.c.email_partition, order_by=subquery.c.created_at)
        .label("email"),
        func.first_value(subquery.c.company)
        .over(partition_by=subquery.c.company_partition, order_by=subquery.c.created_at)
        .label("company"),
        subquery.c.created_at.label("updated_at"),
        func.first_value(subquery.c.created_at)
        .over(order_by=subquery.c.created_at)
        .label("created_at"),
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
        list_users_query.filter(UserHistoryLayerModel.user_id == user_id)
    ).one_or_none()
    if not user:
        return None
    return User(**user._mapping)


def get_users(db: Session):
    users = db.execute(list_users_query).all()
    return [User(**user._mapping) for user in users]


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


def get_user_history_layer(db: Session, layer_id: str):
    layer = (
        db.query(UserHistoryLayerModel)
        .filter(UserHistoryLayerModel.id == layer_id)
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
        list_users_query.filter(
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
