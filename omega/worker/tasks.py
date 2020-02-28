from datetime import datetime, timedelta

from celery.utils.log import get_task_logger
from omega.extensions import db
from omega.lib.scrape_tools import parse_page
from omega.model.watch import (Currency, ScopeOfDelivery, WatchBrand,
                               WatchCondition, WatchType)
from omega.worker import celery
from stringcase import snakecase

log = get_task_logger(__name__)


@celery.task
def fetch_watch_offers_since(date_from=None):
    date_from = date_from if date_from else datetime.now() - timedelta(days=1)


@celery.task
def fetch_currency():
    soup = parse_page("https://www.chrono24.com/offer/watch-details.htm")

    watch_types = (
        watch_type.text
        for watch_type in soup.find("select", {"id": "currency"}).find_all("option")[1:]
    )
    for type_name in watch_types:
        Currency.insert_or_update_one(code=type_name.lower(), name=type_name)
    db.session.commit()


@celery.task
def fetch_scopes_of_delivery():
    soup = parse_page("https://www.chrono24.com/offer/watch-details.htm")

    watch_types = (
        watch_type.text
        for watch_type in soup.find("select", {"name": "scopeOfDelivery"}).find_all(
            "option"
        )[1:]
    )
    for type_name in watch_types:
        ScopeOfDelivery.insert_or_update_one(code=snakecase(type_name), name=type_name)
    db.session.commit()


@celery.task
def fetch_watch_conditions():
    soup = parse_page("https://www.chrono24.com/offer/watch-details.htm")

    watch_types = (
        watch_type.text
        for watch_type in soup.find("select", {"name": "watch.condition"}).find_all(
            "option"
        )[1:]
    )
    for type_name in watch_types:
        WatchCondition.insert_or_update_one(code=snakecase(type_name), name=type_name)
    db.session.commit()


@celery.task
def fetch_watch_types():
    soup = parse_page("https://www.chrono24.com/offer/watch-details.htm")

    watch_types = (
        watch_type.text
        for watch_type in soup.find("select", {"id": "watchtypeName"}).find_all(
            "option"
        )
    )
    for type_name in watch_types:
        WatchType.insert_or_update_one(code=snakecase(type_name), name=type_name)
    db.session.commit()


@celery.task
def fetch_watch_brands():
    soup = parse_page("https://www.chrono24.com/search/browse.htm")
    watch_brands = (
        brand.get("title")
        for brand in soup.find("div", {"class": "brand-list"}).find_all("a")[:-1]
    )

    for brand_name in watch_brands:
        WatchBrand.insert_or_update_one(code=snakecase(brand_name), name=brand_name)
    db.session.commit()
