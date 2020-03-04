import logging

import requests
from bs4 import BeautifulSoup as bs

log = logging.getLogger(__name__)


def parse_page(url, session=None):
    request = session if session else requests

    log.info(url)
    page = request.get(url, allow_redirects=False)
    log.info(page.status_code)
    if page.status_code != 200:
        log.error("Invalid response status, abort")
        return

    log.debug("Page %s fetched successfuly", url)
    return bs(page.text, "lxml")
