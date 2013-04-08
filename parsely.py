"""
    Copyright (C) 2013 Emmett Butler

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import requests
import json
import datetime as dt


class Parsely():
    def __init__(self, apikey, secret=None, root=None):
        self.rooturl = root if root else "http://api.parsely.com/v2"
        self.apikey = apikey
        self.secret = secret

    def analytics(self, aspect="posts", days=14, start=None, end=None, pub_start=None,
                    pub_end=None, sort="_hits", limit=10, page=1):
        if aspect not in ["posts", "authors", "sections", "topics", "tags"]:
            raise ValueError("Invalid aspect %s" % aspect)

        options = self.formatAnalyticsArguments(days, start, end, pub_start, pub_end,
                                            sort, limit, page)

        return self.requestEndpoint('/analytics/%s' % aspect, options)

    def post_detail(self, url, days=''):
        return self.requestEndpoint('/analytics/post/detail',
            {'url': url, 'days': days}
        )

    def meta_detail(self, value, aspect="author", days=14, start=None, end=None,
                        pub_start=None, pub_end=None, sort="_hits", limit=10, page=1):
        if aspect not in ["author", "section", "topic", "tag"]:
            raise ValueError("Invalid aspect %s" % aspect)

        options = self.formatAnalyticsArguments(days, start, end, pub_start, pub_end,
                                            sort, limit, page)

        return self.requestEndpoint('/analytics/%s/%s/detail' % (aspect, value), options)

    def referrers(self, ref_type="social", section='', tag='', domain='', days=3,
                    start=None, end=None, pub_start=None, pub_end=None):
        if ref_type not in ["social", "search", "other", "internal"]:
            raise ValueError("Invalid referrer type %s" % ref_type)

        dates = self.formatDateArguments(start, end, pub_start, pub_end)
        options = {'section': section, 'tag': tag,
                    'domain': domain, 'days': days}

        return self.requestEndpoint('/referrers/%s' % ref_type,
                                dict(options.items()+dates.items()))

    def referrers_meta(self, ref_type="social", meta="posts", section='', domain='',
                        days=3, start=None, end=None, pub_start=None, pub_end=None):
        if ref_type not in ["social", "search", "other", "internal"]:
            raise ValueError("Invalid referrer type %s" % ref_type)

        if meta not in ["posts", "authors", "sections", "topics", "tags"]:
            raise ValueError("Invalid meta type %s" % meta)

        dates = self.formatDateArguments(start, end, pub_start, pub_end)
        options = {'section': section, 'domain': domain, 'days': days}

        return self.requestEndpoint('/referrers/%s/%s' % (ref_type, meta),
                                    dict(options.items() + dates.items()))

    def referrers_meta_detail(self, value, ref_type="social", meta="posts",
                                domain='', days=3, start=None, end=None, pub_start=None,
                                pub_end=None):
        if ref_type not in ["social", "search", "other", "internal"]:
            raise ValueError("Invalid referrer type %s" % ref_type)

        if meta not in ["author", "section", "topic", "tag"]:
            raise ValueError("Invalid meta type %s" % meta)

        dates = self.formatDateArguments(start, end, pub_start, pub_end)
        options = {'domain': domain, 'days': days}

        return self.requestEndpoint('/referrers/%s/%s/%s/detail' % (ref_type, meta, value),
                                    dict(options.items() + dates.items()))

    def referrers_post_detail(self, url, days=3, start=None, end=None, pub_start=None,
                                pub_end=None):

        dates = self.formatDateArguments(start, end, pub_start, pub_end)
        options = {'days': days, 'url': url}

        return self.requestEndpoint('/referrers/post/detail',
                                    dict(options.items() + dates.items()))


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
            raise ValueError("Invalid realtime type %s" % aspect)
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


    def formatAnalyticsArguments(self, days, start, end, pub_start,
                                    pub_end, sort, limit, page):

        dates = self.formatDateArguments(start, end, pub_start, pub_end)
        rest = {'sort': sort, 'limit': limit, 'page': page, 'days': days}
        return dict(dates.items() + rest.items())

    def formatDateArguments(self, start, end, pub_start, pub_end):
        if self.requireBoth(start, end):
            raise ValueError("start and end must be specified together")
        start = start.strftime("%Y-%m-%d") if start else ''
        end = end.strftime("%Y-%m-%d") if end else ''

        if self.requireBoth(pub_start, pub_end):
            raise ValueError("pub start and pub end must be specified together")
        pub_start = pub_start.strftime("%Y-%m-%d") if pub_start else ''
        pub_end = pub_end.strftime("%Y-%m-%d") if pub_end else ''

        return {'period_start': start, 'period_end': end,
            'pub_date_start': pub_start, 'pub_date_end': pub_end}

    def requireBoth(self, first, second):
        return (first and not second) or (second and not first)

    def requestEndpoint(self, endpoint, options={}):
        url = self.rooturl + endpoint + "?apikey=%s&" % self.apikey
        if self.secret:
            url += "secret=%s&" % self.secret
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
