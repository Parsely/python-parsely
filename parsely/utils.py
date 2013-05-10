import requests
import json


def _format_analytics_args(days, start, end, pub_start,
                                pub_end, sort, limit, page):
    dates = _format_date_args(start, end, pub_start, pub_end)
    rest = {'sort': sort, 'limit': limit, 'page': page, 'days': days}
    return dict(dates.items() + rest.items())

def _format_date_args(start, end, pub_start, pub_end):
    if _require_both(start, end):
        raise ValueError("start and end must be specified together")
    start = start.strftime("%Y-%m-%d") if start else ''
    end = end.strftime("%Y-%m-%d") if end else ''

    if _require_both(pub_start, pub_end):
        raise ValueError("pub start and pub end must be specified together")
    pub_start = pub_start.strftime("%Y-%m-%d") if pub_start else ''
    pub_end = pub_end.strftime("%Y-%m-%d") if pub_end else ''

    return {'period_start': start, 'period_end': end,
        'pub_date_start': pub_start, 'pub_date_end': pub_end}

def _require_both(first, second):
    return (first and not second) or (second and not first)

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

    def _request_endpoint(self, endpoint, options={}):
        url = self.rooturl + endpoint + "?apikey=%s&" % self.apikey
        url += "secret=%s&" % self.secret if self.secret else ""
        for k in options.keys():
            if options[k]:
                url += "%s=%s&" % (k, options[k])
        r = requests.get(url)
        if r.status_code == 200:
            js = json.loads(r.text)
            return js
        else:
            print "Error status %d" % r.status_code
            return None
