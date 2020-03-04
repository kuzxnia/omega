from gevent import monkey
monkey.patch_all()

import gevent.pool
import gevent.queue
import requests
from celery.utils.log import get_task_logger
from stringcase import snakecase

from omega.extensions import db
from omega.model.watch import Currency
from omega.model.watch import ScopeOfDelivery
from omega.model.watch import WatchBrand
from omega.model.watch import WatchCondition
from omega.model.watch import WatchType
from omega.util.scrape_tools import parse_page
from omega.util.watch import extract_watch_offer_data
from omega.worker import celery

log = get_task_logger(__name__)


@celery.task
def fetch_offer_details():

    with requests.Session() as request_session:
        if (page := record.text.split(',')):  # noqa
            extract_watch_offer_data(page)


@celery.task
def fetch_recent_watch_offers():
    pool = gevent.pool.Pool(10)
    queue = gevent.queue.Queue()
    offers = []
    with requests.Session() as request_session:
        first_page = parse_page(
            f"https://www.chrono24.com/watches/recently-added-watches--270.htm?pageSize=120", request_session
        )

        page_numbers = (
            int(page.text)
            for page in first_page.find("ul", {"class": "pagination"}).find_all("a")
            if page.text.isnumeric()
        )

        def scrape_data():
            url = queue.get(timeout=0)
            offers.extend(extract_offers_from_page(parse_page(url, request_session)))

        for page_number in range(2, max(page_numbers)):
            queue.put(
                f"https://www.chrono24.com/watches/recently-added-watches--270-{page_number}.htm?pageSize=120"
            )

        pool.spawn()
        while not queue.empty() and not pool.free_count() == 10:
            gevent.sleep(0.1)
            for x in range(0, min(queue.qsize(), pool.free_count())):
                pool.spawn(scrape_data)
        pool.join()


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
