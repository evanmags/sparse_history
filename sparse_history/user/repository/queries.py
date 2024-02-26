from sqlalchemy import TEXT
from sqlalchemy.sql.expression import func, select, case

from sparse_history.user.model import UserRevisionModel


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
        , revised_at
        , max(revised_at) over(w_uid) revised_at
        , first_value(id) over(w_uid) revision_id
    from users
    window w_uid as (partition by user_id order by revised_at desc)
    order by user_id, revised_at asc;
    """

    list_users_query_partition = dict(
        partition_by=UserRevisionModel.user_id,
        order_by=UserRevisionModel.revised_at.desc(),
    )
    return (
        select(
            UserRevisionModel.user_id.label("id"),
            (
                func.any_value(UserRevisionModel.name)
                .over(**list_users_query_partition)
                .label("name")
            ),
            (
                func.any_value(UserRevisionModel.email)
                .over(**list_users_query_partition)
                .label("email")
            ),
            (
                func.any_value(UserRevisionModel.company)
                .over(**list_users_query_partition)
                .label("company")
            ),
            UserRevisionModel.revised_at.label("created_at"),
            (
                func.first_value(UserRevisionModel.revised_at)
                .over(**list_users_query_partition)
                .label("revised_at")
            ),
            (
                func.first_value(UserRevisionModel.revision_id)
                .over(**list_users_query_partition)
                .cast(TEXT)
                .label("revision_id")
            ),
        )
        .order_by(UserRevisionModel.user_id, UserRevisionModel.revised_at.asc())
        .distinct(UserRevisionModel.user_id)
    )


def build_list_user_historical_state_query(user_id: str):
    """
    builds the following query:
    select
        id
        , user_id
        , first_value(name) over(partition by name_partition order by revised_at asc)
        , first_value(email) over(partition by email_partition order by revised_at asc)
        , first_value(company) over(partition by company_partition order by revised_at asc)
        , revised_at
    from (
        select
            id
            , user_id
            , name
            , sum(case when name is null then 0 else 1 end) over(order by revised_at asc) as name_partition
            , email
            , sum(case when email is null then 0 else 1 end) over(order by revised_at asc) as email_partition
            , company
            , sum(case when company is null then 0 else 1 end) over(order by revised_at asc) as company_partition
            , revised_at
        from users
        where user_id='<user_id>'
    )
    """
    subquery = (
        select(
            UserRevisionModel.revision_id,
            UserRevisionModel.user_id,
            UserRevisionModel.name,
            (
                func.sum(case((UserRevisionModel.name.is_(None), 0), else_=1))
                .over(order_by=UserRevisionModel.revised_at)
                .label("name_partition")
            ),
            UserRevisionModel.email,
            (
                func.sum(case((UserRevisionModel.email.is_(None), 0), else_=1))
                .over(order_by=UserRevisionModel.revised_at)
                .label("email_partition")
            ),
            UserRevisionModel.company,
            (
                func.sum(case((UserRevisionModel.company.is_(None), 0), else_=1))
                .over(order_by=UserRevisionModel.revised_at)
                .label("company_partition")
            ),
            UserRevisionModel.revised_at,
        )
        .filter(UserRevisionModel.user_id == user_id)
        .subquery("subquery")
    )

    # Main query
    return select(
        subquery.c.user_id.label("id"),
        (
            func.first_value(subquery.c.name)
            .over(
                partition_by=subquery.c.name_partition, order_by=subquery.c.revised_at
            )
            .label("name")
        ),
        (
            func.first_value(subquery.c.email)
            .over(
                partition_by=subquery.c.email_partition, order_by=subquery.c.revised_at
            )
            .label("email")
        ),
        (
            func.first_value(subquery.c.company)
            .over(
                partition_by=subquery.c.company_partition,
                order_by=subquery.c.revised_at,
            )
            .label("company")
        ),
        subquery.c.revised_at.label("revised_at"),
        (
            func.first_value(subquery.c.revised_at)
            .over(order_by=subquery.c.revised_at)
            .label("created_at")
        ),
        subquery.c.revision_id.label("revision_id"),
    )


def build_get_user_query(user_id: str, revision_id: str | None = None):
    q = (
        select(
            UserRevisionModel.user_id.label("id"),
            (
                func.any_value(UserRevisionModel.name)
                .over(order_by=UserRevisionModel.revised_at.desc())
                .label("name")
            ),
            (func.any_value(UserRevisionModel.email).over().label("email")),
            (func.any_value(UserRevisionModel.company).over().label("company")),
            UserRevisionModel.revised_at.label("created_at"),
            (func.first_value(UserRevisionModel.revised_at).over().label("revised_at")),
            UserRevisionModel.revision_id,
        )
        .filter(UserRevisionModel.user_id == user_id)
        .order_by(UserRevisionModel.revised_at.asc())
        .limit(1)
    )

    if revision_id:
        q.where(
            UserRevisionModel.revised_at
            <= select(UserRevisionModel.revised_at)
            .where(UserRevisionModel.revision_id == revision_id)
            .subquery()
        )
    return q
