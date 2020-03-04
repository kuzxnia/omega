from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Unicode

from omega.model.enums import Role
from omega.util.database_tools import BaseEntity
from omega.util.database_tools import CreateEditMixin


class User(BaseEntity, CreateEditMixin):
    __tablename__ = "users"

    first_name = Column(Unicode(255))
    last_name = Column(Unicode(255))
    login = Column(Unicode(255))
    email_address = Column(Unicode(255), nullable=False, unique=True)
    password = Column(Unicode(255), nullable=False)
    role = Column(Integer, nullable=False, default=Role.USER)
