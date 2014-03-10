import json
import urllib

import tornado.gen
from tornado.httpclient import HTTPClient, AsyncHTTPClient


def async(func):
    @tornado.gen.coroutine
    def inner(*args, **kwargs):
        raise tornado.gen.Return(func(*args, **kwargs))
    return inner


class BaseParselyClient():
    def _format_analytics_args(self, days=14, start=None, end=None, pub_start=None,
                               pub_end=None, sort="_hits", limit=10, page=1):
        dates = self._format_date_args(start, end, pub_start, pub_end)
        rest = {'sort': sort, 'limit': limit, 'page': page, 'days': days}
        return dict(dates.items() + rest.items())

    def _format_date_args(self, start=None, end=None, pub_start=None, pub_end=None):
        if self._require_both(start, end):
            raise ValueError("start and end must be specified together")
        start = start.strftime("%Y-%m-%d") if start else ''
        end = end.strftime("%Y-%m-%d") if end else ''

        if self._require_both(pub_start, pub_end):
            raise ValueError("pub start and pub end must be specified together")
        pub_start = pub_start.strftime("%Y-%m-%d") if pub_start else ''
        pub_end = pub_end.strftime("%Y-%m-%d") if pub_end else ''

        return {'period_start': start, 'period_end': end,
                'pub_date_start': pub_start, 'pub_date_end': pub_end}

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
    def _valid_aspect(func):
        def inner(*args, **kwargs):
            name = arg_name if arg_name else "aspect"
            if name in kwargs.keys() and kwargs[name] not in aspects:
                raise ValueError("Invalid %s: %s" % (name, kwargs[name]))
            return func(*args, **kwargs)
        return inner
    return _valid_aspect


class ParselyAPIConnection():
    def __init__(self, apikey, secret=None, root=None):
        self.rooturl = root if root else "http://api.parsely.com/v2"
        self.apikey = apikey
        self.secret = secret

    def _request_endpoint(self, endpoint, options={}, _callback=None, async=False):
        url = self.rooturl + endpoint + "?apikey=%s&" % self.apikey
        url += "secret=%s&" % self.secret if self.secret else ""
        url += urllib.urlencode({k: v for k, v in options.iteritems() if v})

        if _callback:
            def __callback(response):
                result = json.loads(response.body)
                _callback(result)
                self._end_request_handler(result, response.error)
            AsyncHTTPClient().fetch(url, __callback, method="GET", validate_cert=True)
            self._should_stop_ioloop_on_finish = True
            if tornado.ioloop.IOLoop.instance()._running:
                self._should_stop_ioloop_on_finish = False
            else:
                tornado.ioloop.IOLoop.instance().start()
            return
        else:
            ret = HTTPClient().fetch(url, method="GET", validate_cert=True)

        js = json.loads(ret.body)
        return js

    def _end_request_handler(self, response, error):
        """
        Helper, called once an asynchronous request ends

        Stops the IOLoop that was started when the async request was
        initialized

        Args:
        response (Dict) -- Dictionary representing the returned JSON
        error           -- The request error, if any
        """
        if self._should_stop_ioloop_on_finish:
            tornado.ioloop.IOLoop.instance().stop()
