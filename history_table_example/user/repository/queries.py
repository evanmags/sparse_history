from sqlalchemy import TEXT
from sqlalchemy.sql.expression import func, select, case

from history_table_example.user.model import UserHistoryLayerModel


def build_list_users_query():
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
    return (
        select(
            UserHistoryLayerModel.user_id.label("id"),
            (
                func.any_value(UserHistoryLayerModel.name)
                .over(**list_users_query_partition)
                .label("name")
            ),
            (
                func.any_value(UserHistoryLayerModel.email)
                .over(**list_users_query_partition)
                .label("email")
            ),
            (
                func.any_value(UserHistoryLayerModel.company)
                .over(**list_users_query_partition)
                .label("company")
            ),
            UserHistoryLayerModel.created_at,
            (
                func.max(UserHistoryLayerModel.created_at)
                .over(**list_users_query_partition)
                .label("updated_at")
            ),
            (
                func.first_value(UserHistoryLayerModel.id)
                .over(**list_users_query_partition)
                .cast(TEXT)
                .label("last_edit_id")
            ),
        )
        .order_by(UserHistoryLayerModel.user_id, UserHistoryLayerModel.created_at.asc())
        .distinct(UserHistoryLayerModel.user_id)
    )


def build_list_user_historical_state_query(user_id: str):
    """
    builds the following query:
    select
        id
        , user_id
        , first_value(name) over(partition by name_partition order by created_at asc)
        , first_value(email) over(partition by email_partition order by created_at asc)
        , first_value(company) over(partition by company_partition order by created_at asc)
        , created_at
    from (
        select
            id
            , user_id
            , name
            , sum(case when name is null then 0 else 1 end) over(order by created_at asc) as name_partition
            , email
            , sum(case when email is null then 0 else 1 end) over(order by created_at asc) as email_partition
            , company
            , sum(case when company is null then 0 else 1 end) over(order by created_at asc) as company_partition
            , created_at
        from users
        where user_id='<user_id>'
    )
    """
    subquery = (
        select(
            UserHistoryLayerModel.id,
            UserHistoryLayerModel.user_id,
            UserHistoryLayerModel.name,
            (
                func.sum(case((UserHistoryLayerModel.name.is_(None), 0), else_=1))
                .over(order_by=UserHistoryLayerModel.created_at)
                .label("name_partition")
            ),
            UserHistoryLayerModel.email,
            (
                func.sum(case((UserHistoryLayerModel.email.is_(None), 0), else_=1))
                .over(order_by=UserHistoryLayerModel.created_at)
                .label("email_partition")
            ),
            UserHistoryLayerModel.company,
            (
                func.sum(case((UserHistoryLayerModel.company.is_(None), 0), else_=1))
                .over(order_by=UserHistoryLayerModel.created_at)
                .label("company_partition")
            ),
            UserHistoryLayerModel.created_at,
        )
        .filter(UserHistoryLayerModel.user_id == user_id)
        .subquery("subquery")
    )

    # Main query
    return select(
        subquery.c.user_id.label("id"),
        (
            func.first_value(subquery.c.name)
            .over(
                partition_by=subquery.c.name_partition, order_by=subquery.c.created_at
            )
            .label("name")
        ),
        (
            func.first_value(subquery.c.email)
            .over(
                partition_by=subquery.c.email_partition, order_by=subquery.c.created_at
            )
            .label("email")
        ),
        (
            func.first_value(subquery.c.company)
            .over(
                partition_by=subquery.c.company_partition,
                order_by=subquery.c.created_at,
            )
            .label("company")
        ),
        subquery.c.created_at.label("updated_at"),
        (
            func.first_value(subquery.c.created_at)
            .over(order_by=subquery.c.created_at)
            .label("created_at")
        ),
        subquery.c.id.label("last_edit_id"),
    )
