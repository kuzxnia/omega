from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup as bs
from celery.utils.log import get_task_logger
from omega.extensions import db
from omega.model.watch import WatchBrand
from omega.worker import celery
from stringcase import snakecase

log = get_task_logger(__name__)


@celery.task
def fetch_watch_offers_since(date_from=None):
    date_from = date_from if date_from else datetime.now() - timedelta(days=1)


@celery.task
def fetch_watch_types():
    pass


@celery.task
def fetch_watch_brands():
    def scrape_all_brands_names():
        url = "https://www.chrono24.com/search/browse.htm"
        page = requests.get(url)
        if page.status_code != 200:
            log.error("Invalid response status, abort")
            page.raise_for_status()

        log.info("Started parsing html")
        soup = bs(page.text, "lxml")
        return (
            brand.get("title")
            for brand in soup.find("div", {"class": "brand-list"}).find_all("a")[:-1]
        )

    for brand_name in scrape_all_brands_names():
        log.info(brand_name)
        WatchBrand(code=snakecase(brand_name), name=brand_name).update_or_insert()
    db.session.commit()
