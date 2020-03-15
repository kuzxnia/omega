from gevent import monkey, lock  # isort:skip

monkey.patch_all()  # isort:skip

import logging
import random

from omega.util.class_tools import Singleton
from omega.util.functools import timed_cache
from omega.util.scrape_tools import parse_page
from pycountry_convert import country_alpha2_to_continent_code

import requests

log = logging.getLogger(__name__)
sem = lock.Semaphore()


class ProxyPool(metaclass=Singleton):
    def __init__(self):
        self.proxy_list = None
        self.last_proxy = None

    @timed_cache(seconds=60)
    def get_recent_proxy_list(self):
        sem.acquire(timeout=1)
        log.info("Fetching new proxy list")
        page = parse_page("https://www.sslproxies.org/#", throught_proxy=False)

        self.proxy_list = []
        for row in page.find("tbody").find_all("tr"):
            (host, port, code, anonymity, https) = map(
                [cell.text for cell in row.find_all("td")].__getitem__, [0, 1, 2, 4, 6]
            )

            try:
                if (
                    anonymity == "elite proxy"
                    and https == "yes"
                    and country_alpha2_to_continent_code(code) == "EU"
                ):
                    self.proxy_list.append(f"https://{host}:{port}")
            except KeyError:
                pass
        sem.release()

    def get_proxy_address(self):
        with sem:
            if not self.proxy_list:
                self.get_recent_proxy_list()

            if not self.last_proxy:
                self.last_proxy = random.choice(self.proxy_list)

        return self.last_proxy

    def remove_last_proxy(self):
        with sem:
            if self.last_proxy in self.proxy_list:
                self.proxy_list.remove(self.last_proxy)
            self.last_proxy = None


def proxy_request(method, url, **kwargs):
    proxy_pool = ProxyPool()

    try:
        with requests.Session() as session:
            session.proxies = {"https": proxy_pool.get_proxy_address()}
            log.debug(
                "Starting new HTTPS connection to %s throught %r proxy",
                url,
                session.proxies,
            )
            return session.request(method=method, url=url, **kwargs)
    except Exception:
        proxy_pool.remove_last_proxy()
        raise


def get(url, params=None, **kwargs):
    kwargs.setdefault("allow_redirects", True)
    return proxy_request("get", url, params=params, **kwargs)


def options(url, **kwargs):
    kwargs.setdefault("allow_redirects", True)
    return proxy_request("options", url, **kwargs)


def head(url, **kwargs):
    kwargs.setdefault("allow_redirects", False)
    return proxy_request("head", url, **kwargs)


def post(url, data=None, json=None, **kwargs):
    return proxy_request("post", url, data=data, json=json, **kwargs)


def put(url, data=None, **kwargs):
    return proxy_request("put", url, data=data, **kwargs)


def patch(url, data=None, **kwargs):
    return proxy_request("patch", url, data=data, **kwargs)


def delete(url, **kwargs):
    return proxy_request("delete", url, **kwargs)
