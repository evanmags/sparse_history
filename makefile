.EXPORT_ALL_VARIABLES:
PYTHONPATH=.

create-db:
	@python scripts/create_db.py

seed-db: create-db
	@python scripts/seed.py

run:
	litestar --app sparse_history.api.app:app run --reload --debug