import logging
from datetime import datetime

from omega.extensions import db
from omega.util.collection_tools import copy_to
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Unicode
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from stringcase import snakecase

log = logging.getLogger(__name__)


class BaseEntity(db.Model):
    __abstract__ = True
    __table_args__ = {"schema": "public"}

    @declared_attr
    def __tablename__(self):
        return snakecase(self.__name__.lower())

    id = Column(Integer, autoincrement=True, primary_key=True)

    @declared_attr
    def uuid(self):
        return Column(UUID(as_uuid=True), unique=True, nullable=False)


class CreateEditMixin(object):
    @declared_attr
    def creation_date(self):
        return Column(DateTime, default=datetime.now)

    @declared_attr
    def update_date(self):
        return Column(DateTime, onupdate=datetime.now)


class BasicDictionaryTable(BaseEntity, CreateEditMixin):
    __abstract__ = True

    code = Column(Unicode(255), nullable=False, unique=True)
    name = Column(Unicode(255), nullable=False)

    def as_dict(self):
        return {"code": self.code, "name": self.name}

    def props_dict(self):
        values = self.as_dict()
        return (values, values.pop("code"))[0]

    @classmethod
    def insert_or_update_one(cls, **data):
        obj = cls.query(code=data["code"]).one_or_none()  # pylint: disable=not-callable
        if obj:
            log.info("update %r", obj.__dict__)
            obj = copy_to(obj, data)
        else:
            db.session.add(cls(**data))

    @classmethod
    def update_or_insert_many(cls, data):
        pass

    def __repr__(self):
        return f"<{self.__class__} code={self.code} name={self.name}>"


def make_dictionary_table(table_name):
    return type(table_name, (BasicDictionaryTable,), {})


def FKColumn(ref, **kwargs):
    return Column(Integer, ForeignKey(ref.id), **kwargs)
