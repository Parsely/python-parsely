import requests
import json
import datetime as dt


class Parsely():
    def __init__(self, apikey, secret=None):
        self.rooturl = "http://api.parsely.com/v2"
        self.apikey = apikey
        self.secret = secret

    def analytics(self, aspect="posts", days=14, start=None, end=None, pub_start=None,
                    pub_end=None, sort="_hits", limit=10, page=1):
        if aspect not in ["posts", "authors", "sections", "topics", "tags"]:
            raise ValueError("Invalid aspect")

        options = self.formatAnalyticsArguments(days, start, end, pub_start, pub_end,
                                            sort, limit, page)

        return self.requestEndpoint('/analytics/%s' % aspect, options)

    def post_detail(self, url, days=''):
        return self.requestEndpoint('/analytics/post/detail',
            {'url': url, 'days': days}
        )

    def formatAnalyticsArguments(self, days, start, end, pub_start,
                                    pub_end, sort, limit, page):
        if self.requireBoth(start, end):
            raise ValueError("start and end must be specified together")
        start = start.strftime("%Y-%m-%d") if start else ''
        end = end.strftime("%Y-%m-%d") if end else ''

        if self.requireBoth(pub_start, pub_end):
            raise ValueError("pub start and pub end must be specified together")
        pub_start = pub_start.strftime("%Y-%m-%d") if pub_start else ''
        pub_end = pub_end.strftime("%Y-%m-%d") if pub_end else ''

        return {'period_start': start, 'period_end': end, 'pub_date_start': pub_start,
                    'pub_date_end': pub_end, 'sort': sort, 'limit': limit, 'page': page,
                    'days': days}

    def meta_detail(self, value, aspect="author", days=14, start=None, end=None,
                        pub_start=None, pub_end=None, sort="_hits", limit=10, page=1):
        if aspect not in ["author", "section", "topic", "tag"]:
            raise ValueError("Invalid aspect")

        options = self.formatAnalyticsArguments(days, start, end, pub_start, pub_end,
                                            sort, limit, page)

        return self.requestEndpoint('/analytics/%s/%s/detail' % (aspect, value), options)

    def referrers(self, ref_type="social", section='', tag='', domain='', days=3,
                    start=None, end=None, pub_start=None, pub_end=None):
        if ref_type not in ["social", "search", "other", "internal"]:
            raise ValueError("Invalid referrer type")

        if self.requireBoth(start, end):
            raise ValueError("start and end must be specified together")
        start = start.strftime("%Y-%m-%d") if start else ''
        end = end.strftime("%Y-%m-%d") if end else ''

        if self.requireBoth(pub_start, pub_end):
            raise ValueError("pub start and pub end must be specified together")
        pub_start = pub_start.strftime("%Y-%m-%d") if pub_start else ''
        pub_end = pub_end.strftime("%Y-%m-%d") if pub_end else ''

        options = {'period_start': start, 'period_end': end, 'pub_date_start': pub_start,
                    'pub_date_end': pub_end, 'section': section, 'tag': tag,
                    'domain': domain, 'days': days}

        return self.requestEndpoint('/referrers/%s' % ref_type, options)

    def referrers_meta(self, ref_type="social", meta="posts", section='', domain='',
                        days=3, start=None, end=None, pub_start=None, pub_end=None):
        if ref_type not in ["social", "search", "other", "internal"]:
            raise ValueError("Invalid referrer type")

        if meta not in ["posts", "authors", "sections", "topics", "tags"]:
            raise ValueError("Invalid meta type")

        if self.requireBoth(start, end):
            raise ValueError("start and end must be specified together")
        start = start.strftime("%Y-%m-%d") if start else ''
        end = end.strftime("%Y-%m-%d") if end else ''

        if self.requireBoth(pub_start, pub_end):
            raise ValueError("pub start and pub end must be specified together")
        pub_start = pub_start.strftime("%Y-%m-%d") if pub_start else ''
        pub_end = pub_end.strftime("%Y-%m-%d") if pub_end else ''

        options = {'period_start': start, 'period_end': end, 'pub_date_start': pub_start,
                    'pub_date_end': pub_end, 'section': section,
                    'domain': domain, 'days': days}

        return self.requestEndpoint('/referrers/%s/%s' % (ref_type, meta), options)

    def referrers_meta_detail(self, value, ref_type="social", meta="posts",
                                domain='', days=3, start=None, end=None, pub_start=None,
                                pub_end=None):
        if ref_type not in ["social", "search", "other", "internal"]:
            raise ValueError("Invalid referrer type")

        if meta not in ["posts", "authors", "sections", "topics", "tags"]:
            raise ValueError("Invalid meta type")

        if self.requireBoth(start, end):
            raise ValueError("start and end must be specified together")
        start = start.strftime("%Y-%m-%d") if start else ''
        end = end.strftime("%Y-%m-%d") if end else ''

        if self.requireBoth(pub_start, pub_end):
            raise ValueError("pub start and pub end must be specified together")
        pub_start = pub_start.strftime("%Y-%m-%d") if pub_start else ''
        pub_end = pub_end.strftime("%Y-%m-%d") if pub_end else ''

        options = {'period_start': start, 'period_end': end, 'pub_date_start': pub_start,
                    'pub_date_end': pub_end, 'domain': domain, 'days': days}

        return self.requestEndpoint('/referrers/%s/%s/%s' % (ref_type, meta, value), options)

    def referrers_post_detail(self, url, days=3, start=None, end=None, pub_start=None,
                                pub_end=None):
        if self.requireBoth(start, end):
            raise ValueError("start and end must be specified together")
        start = start.strftime("%Y-%m-%d") if start else ''
        end = end.strftime("%Y-%m-%d") if end else ''

        if self.requireBoth(pub_start, pub_end):
            raise ValueError("pub start and pub end must be specified together")
        pub_start = pub_start.strftime("%Y-%m-%d") if pub_start else ''
        pub_end = pub_end.strftime("%Y-%m-%d") if pub_end else ''

        options = {'period_start': start, 'period_end': end, 'pub_date_start': pub_start,
                    'pub_date_end': pub_end, 'days': days, 'url': url}

        return self.requestEndpoint('/referrers/post/detail', options)


    def shares(self, aspect="posts", detail=False, days=14, start=None,
                end=None, limit=10, page=1, url=''):
        if detail:
            if not url:
                raise ValueError("Url required for shares detail")
            return self.requestEndpoint('/shares/post/detail', {'url': url})
        else:
            if aspect not in ["posts", "authors"]:
                raise ValueError("Aspect must be one of posts, authors")

            if self.requireBoth(start, end):
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

    def requireBoth(self, first, second):
        return (first and not second) or (second and not first)

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
