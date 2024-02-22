from history_table_example.database import BaseModel, engine

from history_table_example.user.model import UserModel  # noqa


BaseModel.metadata.create_all(engine)
