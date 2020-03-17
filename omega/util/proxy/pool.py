from gevent import monkey, lock, sleep; monkey.patch_all()  # noqa isort:skip

from omega.util.scrape_tools import parse_page
from omega.util.class_tools import Singleton
from abc import abstractmethod
from omega.util.functools import timed_cache
from pycountry_convert import country_alpha2_to_continent_code
import random
import logging

sem = lock.Semaphore()
log = logging.getLogger(__name__)


class ProxyPool(metaclass=Singleton):
    def __init__(self):
        self.proxy_list = None
        self.last_proxy = None

    @abstractmethod
    def get_recent_proxy_list(self):
        """ supposed to be time cached """
        pass

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


class FreeProxyPool(ProxyPool):
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


class DelayWithoutProxy(ProxyPool):
    def get_recent_proxy_list(self):
        pass

    def get_proxy_address(self):
        sleep(2)
        return None


proxy_pool_by_key = {
    'FREE': FreeProxyPool,
    'DELAY': DelayWithoutProxy
}
