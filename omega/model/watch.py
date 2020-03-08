from omega.util.database_tools import (
    BaseEntity,
    CreateEditMixin,
    FKColumn,
    make_dictionary_table,
)
from sqlalchemy import Column, Float, Integer, Unicode, UnicodeText
from sqlalchemy.dialects.postgresql import JSON

Currency = make_dictionary_table("Currency")
ScopeOfDelivery = make_dictionary_table("ScopeOfDelivery")
WatchCondition = make_dictionary_table("WatchCondition")
WatchType = make_dictionary_table("WatchType")
WatchBrand = make_dictionary_table("WatchBrand")
WatchFetchJobGroupStatus = make_dictionary_table("WatchFetchJobGroupStatus")
WatchFetchJobStatus = make_dictionary_table("WatchFetchJobStatus")


class Watch(BaseEntity, CreateEditMixin):

    basic_info = Column(JSON)
    basic_info = Column(JSON)
    caliber = Column(JSON)
    case = Column(JSON)
    dial_and_hands = Column(JSON)
    bracelet_strap = Column(JSON)
    functions = Column(JSON)
    description = Column(UnicodeText)
    others = Column(JSON)

    price = Column(Float(asdecimal=False))
    currency = Column(Unicode(100))  # FKColumn(Currency)

    offer_link = Column(Unicode(1000), unique=True, nullable=False)


class WatchFetchJobGroup(BaseEntity, CreateEditMixin):
    amount_offers_to_fetch = Column(Integer, nullable=False)
    group_fetch_status_id = FKColumn(WatchFetchJobGroupStatus, default=1)
    job_fetch_time = Column(Float(10), nullable=False)
    fetch_time = Column(Float(10))


class WatchFetchJob(BaseEntity, CreateEditMixin):
    fetch_group_id = FKColumn(WatchFetchJobGroup)
    fetch_status_id = FKColumn(WatchFetchJobStatus, default=1)
    error_stacktrace = Column(UnicodeText)
    offer_link = Column(Unicode(1000), nullable=False, unique=True)
