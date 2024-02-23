from sparse_history.database import BaseModel, engine

from sparse_history.user.model import UserRevisionModel  # noqa


BaseModel.metadata.create_all(engine)
