import requests
import json
import datetime as dt


class Parsely():
    def __init__(self, apikey, secret=None):
        self.rooturl = "http://api.parsely.com/v2"
        self.apikey = apikey
        self.secret = secret

    def shares(self, aspect="posts", detail=False, days=14, start=None,
                end=None, limit=10, page=1, url=''):
        if detail:
            if not url:
                raise ValueError("Url required for shares detail")
            return self.requestEndpoint('/shares/post/detail', {'url': url})
        else:
            if aspect not in ["posts", "authors"]:
                raise ValueError("Aspect must be one of posts, authors")

            if (start and not end) or (end and not start):
                raise ValueError("Start and end must be specified together")

            start = start.strftime("%Y-%m-%d") if start else ''
            end = end.strftime("%Y-%m-%d") if end else ''

            return self.requestEndpoint('/shares/%s' % aspect,
                {'pub_days': days, 'pub_date_start': start, 'pub_date_end': end,
                'limit': 10, 'page': 1}
            )

    def realtime(self, aspect="posts", per=None, limit=10, page=1):
        if aspect not in ["posts", "authors", "sections", "topics", "tags", "referrers"]:
            raise ValueError("Invalid realtime type")
        # should be a datetime.timedelta
        options = {'limit': limit, 'page': page}
        if per:
            options['time'] = "%dh" % per.hours if per.hours else "%dm" % per.minutes
        return self.requestEndpoint('/realtime/%s' % aspect, options)

    def train(self, uuid, url):
        return self.requestEndpoint('/profile', {'uuid': uuid, 'url': url})

    def related(self, url='', uuid='', days=14, limit=10, page=1, section=""):
        if url == '' and uuid == '':
            raise ValueError("Must specify url or uuid")
        if url != '' and uuid != '':
            raise ValueError("Must specify only url or uuid, not both")
        return self.requestEndpoint('/related',
            {'url': url, 'uuid': uuid, 'days': days, 'limit': limit, 'page': page}
        )

    def history(self, uuid):
        return self.requestEndpoint('/history', {'uuid': uuid})

    def search(self, query, limit=10, page=1):
        return self.requestEndpoint('/search', {'limit': limit, 'page': page})

    def requestEndpoint(self, endpoint, options={}):
        url = self.rooturl + endpoint + "?apikey=%s&" % self.apikey
        if self.secret:
            url += "secret=%s&" % self.secret
        for k in options.keys():
            url += "%s=%s&" % (k, options[k])
        print url
        r = requests.get(url)
        if r.status_code == 200:
            js = json.loads(r.text)
            return js
        else:
            print "Error status %d" % r.status_code
            return None
