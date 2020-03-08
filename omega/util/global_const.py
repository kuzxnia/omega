import logging

from omega.extensions import db
from omega.model.watch import WatchFetchJobGroupStatus, WatchFetchJobStatus

log = logging.getLogger(__name__)
update_functions = []


def make_dictionary_table(table_name, entity, statuses: dict):
    attrs = {}
    description = {}
    for i, code in enumerate(statuses, 1):
        attrs[code.upper()] = i
        description[i] = statuses[code]

    def update():
        for i, code in enumerate(statuses, 1):
            db.session.add(entity(id=i, code=code, name=statuses[code]))
            log.info("added entity=%r code=%s name=%s", entity, code, statuses[code])
        db.session.commit()

    attrs["description"] = description
    attrs["update"] = staticmethod(update)
    update_functions.append(update)

    return type(table_name, (object,), attrs)


BASE_URL = "https://www.chrono24.com"
RECENTLY_ADDED_OFFERS = (
    BASE_URL + "/watches/recently-added-watches--270.htm?pageSize=120"
)
RECENTLY_ADDED_OFFERS_PAGINATE = (
    BASE_URL + "/watches/recently-added-watches--270-{}.htm?pageSize=120"
)

JOB_STATUSES = make_dictionary_table(
    "JOB_STATUSES",
    WatchFetchJobStatus,
    {"new": "New", "success": "Success", "error": "Error"},
)

JOB_GROUP_STATUSES = make_dictionary_table(
    "JOB_GROUP_STATUSES",
    WatchFetchJobGroupStatus,
    {"new": "New", "in_process": "In process", "success": "Success", "error": "Error"},
)
