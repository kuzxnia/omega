from sqlalchemy import Column, Integer, Unicode

from omega.lib.database_tools import BaseEntity, CreateEditMixin
from omega.model.enums import Role


class User(BaseEntity, CreateEditMixin):
    __tablename__ = "users"

    first_name = Column(Unicode(255))
    last_name = Column(Unicode(255))
    login = Column(Unicode(255))
    email_address = Column(Unicode(255), nullable=False, unique=True)
    password = Column(Unicode(255), nullable=False)
    role = Column(Integer, nullable=False, default=Role.USER)
