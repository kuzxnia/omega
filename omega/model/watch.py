from omega.util.database_tools import (
    BaseEntity,
    CreateEditMixin,
    FKColumn,
    make_dictionary_table,
)
from sqlalchemy import Column, Float, Integer, Unicode
from sqlalchemy.dialects.postgresql import JSON

Currency = make_dictionary_table("Currency")
ScopeOfDelivery = make_dictionary_table("ScopeOfDelivery")
WatchCondition = make_dictionary_table("WatchCondition")
WatchType = make_dictionary_table("WatchType")
WatchBrand = make_dictionary_table("WatchBrand")
WatchFetchJobGroupStatus = make_dictionary_table("WatchFetchJobGroupStatus")
WatchFetchJobStatus = make_dictionary_table("WatchFetchJobStatus")


class Watch(BaseEntity, CreateEditMixin):

    brand = FKColumn(WatchBrand, nullable=False)
    model = Column(Unicode(255), nullable=False)
    watch_type = FKColumn(WatchType, nullable=False)
    reference_number = Column(Unicode(255), nullable=False)
    condition = FKColumn(WatchCondition, nullable=False)
    scope_of_delivery = FKColumn(ScopeOfDelivery)

    basic_info = Column(JSON)
    caliber = Column(JSON)
    case = Column(JSON)
    dial_and_hands = Column(JSON)
    brancelet = Column(JSON)
    functions = Column(JSON)

    price = Column(Float(asdecimal=False))
    currency = FKColumn(Currency)

    offer_link = Column(Unicode(1000), unique=True, nullable=False)


class WatchFetchJobGroup(BaseEntity, CreateEditMixin):
    amount_offers_to_fetch = Column(Integer, nullable=False)
    group_fetch_status_id = FKColumn(WatchFetchJobGroupStatus, default=0)


class WatchFetchJob(BaseEntity, CreateEditMixin):
    fetch_group_id = FKColumn(WatchFetchJobGroup)
    fetch_status_id = FKColumn(WatchFetchJobStatus)
    error_stacktrace = Column(Unicode(4000))
    offer_link = Column(Unicode(1000), nullable=False, unique=True)
