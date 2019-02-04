from __future__ import absolute_import

import json

from six.moves.urllib.parse import quote, urlencode

import tornado.gen
from tornado.httpclient import HTTPClient, AsyncHTTPClient


class BaseParselyClient(object):
    def _format_analytics_args(
        self,
        days=14,
        start=None,
        end=None,
        pub_start=None,
        pub_end=None,
        sort="_hits",
        limit=10,
        page=1,
    ):
        dates = self._format_date_args(start, end, pub_start, pub_end)
        rest = {"sort": sort, "limit": limit, "page": page, "days": days}
        return dict(list(dates.items()) + list(rest.items()))

    def _format_date_args(self, start=None, end=None, pub_start=None, pub_end=None):
        if self._require_both(start, end):
            raise ValueError("start and end must be specified together")
        start = start.strftime("%Y-%m-%d") if start else ""
        end = end.strftime("%Y-%m-%d") if end else ""

        if self._require_both(pub_start, pub_end):
            raise ValueError("pub start and pub end must be specified together")
        pub_start = pub_start.strftime("%Y-%m-%d") if pub_start else ""
        pub_end = pub_end.strftime("%Y-%m-%d") if pub_end else ""

        return {
            "period_start": start,
            "period_end": end,
            "pub_date_start": pub_start,
            "pub_date_end": pub_end,
        }

    def _require_both(self, first, second):
        return bool(first) != bool(second)

    def _build_callback(self, datafunc, _callback=None):
        def handle(res):
            res = datafunc(res)
            if not _callback:
                return res
            _callback(res)

        return handle


def valid_kwarg(aspects, arg_name=""):
    allowed_metrics = [
        "views",
        "mobile_views",
        "tablet_views",
        "desktop_views",
        "visitors",
        "visitors_new",
        "visitors_returning",
        "engaged_minutes",
        "avg_engaged",
        "avg_engaged_new",
        "avg_engaged_returning",
        "social_interactions",
        "fb_interactions",
        "tw_interactions",
        "li_interactions",
        "pi_interactions",
        "social_referrals",
        "fb_referrals",
        "tw_referrals",
        "li_referrals",
        "pi_referrals",
    ]

    def _valid_aspect(func):
        def inner(*args, **kwargs):
            name = arg_name if arg_name else "aspect"
            if name in list(kwargs.keys()) and kwargs[name] not in aspects:
                if name in ("sort", "boost"):
                    raise ValueError(
                        "Invalid %s: %s. \nAllowed metrics: \n%s"
                        % (
                            name,
                            kwargs[name],
                            "\n".join(str(p) for p in allowed_metrics),
                        )
                    )
                else:
                    raise ValueError("Invalid %s: %s" % (name, kwargs[name]))
            return func(*args, **kwargs)

        return inner

    return _valid_aspect


def is_loop_running(loop):
    """
    Return whether an IOLoop is running. (Stolen from Dask)
    """
    # Tornado < 5.0
    r = getattr(loop, "_running", None)
    if r is not None:
        return r
    try:
        # Tornado 5.0 with AsyncIOLoop (default setting)
        return loop.asyncio_loop.is_running()
    except AttributeError:
        raise TypeError(
            "don't know how to query the running state of %s" % (type(loop),)
        )


class ParselyAPIConnection(object):
    def __init__(self, apikey, secret=None, root=None):
        self.rooturl = root if root else "http://api.parsely.com/v2"
        self.apikey = apikey
        self.secret = secret

    def _request_endpoint(self, endpoint, options={}, _callback=None):
        url = "{root}{endpoint}?apikey={apikey}&secret={secret}&{query}".format(
            root=self.rooturl,
            endpoint=quote(endpoint),
            apikey=self.apikey,
            secret=self.secret if self.secret else "",
            query=urlencode({k: v for k, v in options.items() if v}),
        )

        if _callback:

            def __callback(response):
                result = json.loads(response.body)
                _callback(result)
                self._end_request_handler()

            AsyncHTTPClient().fetch(url, __callback, method="GET", validate_cert=True)
            self._should_stop_ioloop_on_finish = True
            if is_loop_running(tornado.ioloop.IOLoop.instance()):
                self._should_stop_ioloop_on_finish = False
            else:
                tornado.ioloop.IOLoop.instance().start()
            return None
        else:
            ret = HTTPClient().fetch(url, method="GET", validate_cert=True)

        js = json.loads(ret.body)
        return js

    def _end_request_handler(self):
        """
        Helper, called once an asynchronous request ends

        Stops the IOLoop that was started when the async request was
        initialized

        """
        if self._should_stop_ioloop_on_finish:
            tornado.ioloop.IOLoop.instance().stop()
