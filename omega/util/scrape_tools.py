from gevent import monkey  # isort:skip

monkey.patch_all()  # isort:skip

import logging
from contextlib import contextmanager

from bs4 import BeautifulSoup as bs

import gevent.pool
import gevent.queue
import requests

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


@contextmanager
def pool_queue_session(function, pool_size=10):
    """Funcion yields pool queue and requests session"""
    pool = gevent.pool.Pool(pool_size)
    queue = gevent.queue.Queue()
    with requests.Session() as request_session:

        yield (pool, queue, request_session)

        pool.spawn(function)
        while not queue.empty() and not pool.free_count() == 10:
            gevent.sleep(0.25)
            for x in range(0, min(queue.qsize(), pool.free_count())):
                pool.spawn(function)
        pool.join()
