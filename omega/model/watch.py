from sqlalchemy import Column, Float, Unicode
from sqlalchemy.dialects.postgresql import JSON

from omega.lib.database_tools import (
    BaseEntity,
    BasicDictionaryTable,
    CreateEditMixin,
    FKColumn,
)


class Currency(BasicDictionaryTable):
    pass


class ScopeOfDelivery(BasicDictionaryTable):
    pass


class WatchCondition(BasicDictionaryTable):
    pass


class WatchType(BasicDictionaryTable):
    pass


class WatchBrand(BasicDictionaryTable):
    pass


class Watch(BaseEntity, CreateEditMixin):

    brand = FKColumn(WatchBrand, nullable=False)
    model = Column(Unicode(255), nullable=False)
    watch_type = FKColumn(WatchType, nullable=False)
    reference_number = Column(Unicode(255), nullable=False)
    condition = FKColumn(WatchCondition, nullable=False)
    scope_of_delivery = FKColumn(ScopeOfDelivery)

    basic_info = Column(JSON)
    price = Column(Float(asdecimal=False))
    currency = FKColumn(Currency)

    caliber = Column(JSON)
    case = Column(JSON)
    dial_and_hands = Column(JSON)
    brancelet = Column(JSON)
    functions = Column(JSON)
