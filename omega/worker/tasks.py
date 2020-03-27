from gevent import monkey  # isort:skip

monkey.patch_all()  # isort:skip

from time import time

from omega.extensions import db
from omega.model.watch import (
    Currency,
    ScopeOfDelivery,
    Watch,
    WatchBrand,
    WatchCondition,
    WatchFetchJob,
    WatchFetchJobGroup,
    WatchType,
)
from omega.util.global_const import (
    BASE_URL,
    JOB_GROUP_STATUSES,
    JOB_STATUSES,
    RECENTLY_ADDED_OFFERS,
    RECENTLY_ADDED_OFFERS_PAGINATE,
)
from omega.util.scrape_tools import parse_page, pool_queue_session
from omega.util.watch import extract_watch_offer_data
from omega.worker import celery

import requests
from celery.utils.log import get_task_logger
from stringcase import snakecase
from flask import current_app, copy_current_request_context

log = get_task_logger(__name__)


@celery.task
def fetch_offer_details(fetch_group_id):
    fetch_group = WatchFetchJobGroup.query(id=fetch_group_id).one()
    fetch_group.group_fetch_status_id = JOB_GROUP_STATUSES.IN_PROCESS
    db.session.commit()

    offers_to_fetch = (
        wfj
        for wfj in WatchFetchJob.query().filter(
            WatchFetchJob.fetch_group_id == fetch_group_id,
            WatchFetchJob.fetch_status_id.in_([JOB_STATUSES.NEW, JOB_STATUSES.ERROR]),
        )
    )

    start = time()
    with requests.Session() as request_session:
        for offer in offers_to_fetch:
            try:
                page = parse_page(BASE_URL + offer.offer_link, request_session)
                if not page:
                    offer.fetch_status_id = JOB_STATUSES.ERROR

                data = extract_watch_offer_data(page)
                watch = Watch(**data)
                watch.offer_link = offer.offer_link
                offer.fetch_status_id = JOB_STATUSES.SUCCESS
                db.session.add(watch)
            except Exception as e:  # pylint: disable=broad-except
                offer.fetch_status_id = JOB_STATUSES.ERROR
                offer.error_stacktrace = str(e)
            finally:
                db.session.commit()

    fetch_group.fetch_time = time() - start
    db.session.commit()


@celery.task(time_limit=60)
def fetch_recent_watch_offers():
    log.info(current_app.config['PROXY_POOL'])

    @copy_current_request_context
    def scrape_data():
        url = queue.get(timeout=0)
        try:
            offers.extend(offers_for_url(url))
        except requests.exceptions.RequestException:
            # log.error("error")
            queue.put(url)

    offers = []
    start_time = time()
    try:
        with pool_queue_session(scrape_data) as (pool, queue):
            first_page = parse_page(RECENTLY_ADDED_OFFERS, throught_proxy=False)

            last_page_number = max(
                int(page.text)
                for page in first_page.find("ul", {"class": "pagination"}).find_all("a")
                if page.text.isnumeric()
            )
            log.info("pages to fetch %s", last_page_number)

            for page_number in range(2, last_page_number):
                queue.put(RECENTLY_ADDED_OFFERS_PAGINATE.format(page_number))
    except celery.exceptions.SoftTimeLimitExceeded:
        log.info("task time ends")
    finally:
        offers_to_fetch = set(offers) - {
            offer
            for offer, in db.session.query(WatchFetchJob.offer_link).filter(
                WatchFetchJob.offer_link.in_(offers)
            )
        }

        fetch_group = WatchFetchJobGroup(
            amount_offers_to_fetch=len(offers_to_fetch),
            job_fetch_time=(time() - start_time),
        )
        db.session.add(fetch_group)
        db.session.flush()

        for link in offers_to_fetch:
            db.session.add(
                WatchFetchJob(fetch_group_id=fetch_group.id, offer_link=link)
            )


def offers_for_url(url):
    return extract_offers_from_page(parse_page(url))


def extract_offers_from_page(page):
    return [
        link["href"]
        for link in page.find("div", {"id": "wt-watches"}).find_all(
            "a", {"class": "article-item"}
        )
    ]


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
