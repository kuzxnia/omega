from gevent import monkey; monkey.patch_all()  # noqa isort:skip

import logging
import requests
from omega.util.proxy.pool import proxy_pool_by_key
from flask import current_app

log = logging.getLogger(__name__)


def proxy_request(method, url, **kwargs):
    proxy_pool = proxy_pool_by_key[current_app.config.get('PROXY_POOL')]()

    try:
        with requests.Session() as session:
            session.proxies = {"https": proxy_pool.get_proxy_address()}
            log.debug(
                "Starting new HTTPS connection to %s throught %r proxy",
                url,
                session.proxies,
            )
            return session.request(method=method, url=url, **kwargs)
    except Exception as e:
        proxy_pool.remove_last_proxy()
        proxy_pool.handle_exception(e)


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
