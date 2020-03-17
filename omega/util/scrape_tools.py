from gevent import monkey; monkey.patch_all()  # noqa isort:skip

import logging
from contextlib import contextmanager

from bs4 import BeautifulSoup as bs

import requests
from gevent import pool, queue, sleep

log = logging.getLogger(__name__)


def parse_page(url, throught_proxy=True, timeout=2):
    """
    Raises:
        requests.exceptions.RequestException
    """
    request = requests
    if throught_proxy:
        from omega.util.proxy import request

        request = request

    page = request.get(url, verify=False, allow_redirects=False, timeout=timeout)
    page.raise_for_status()
    log.info("Page Fetched")
    return bs(page.text, "lxml")


@contextmanager
def pool_queue_session(function, pool_size=10):
    """Funcion yields pool queue and requests session"""
    gevent_pool = pool.Pool(pool_size)
    gevent_queue = queue.Queue()

    yield gevent_pool, gevent_queue

    gevent_pool.spawn(function)
    while not gevent_queue.empty() and not gevent_pool.free_count() == 10:
        sleep(0.25)
        for x in range(0, min(gevent_queue.qsize(), gevent_pool.free_count())):
            gevent_pool.spawn(function)
    gevent_pool.join()
