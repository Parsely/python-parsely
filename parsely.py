"""
    Copyright (C) 2013 Emmett Butler, Parsely Inc.

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

from models import Post, Author, Section, Topic, Tag, Referrer


class Parsely():
    def __init__(self, apikey, secret=None, root=None):
        self.rooturl = root if root else "http://api.parsely.com/v2"
        self.apikey = apikey
        self.secret = secret

    def analytics(self, aspect="posts", days=14, start=None, end=None, pub_start=None,
                    pub_end=None, sort="_hits", limit=10, page=1):
        if aspect not in ["posts", "authors", "sections", "topics", "tags"]:
            raise ValueError("Invalid aspect %s" % aspect)

        options = self._format_analytics_args(days, start, end, pub_start, pub_end,
                                            sort, limit, page)

        res = self._request_endpoint('/analytics/%s' % aspect, options)
        if aspect == "posts":
            return [Post.new_from_json_dict(x) for x in res['data']]
        elif aspect == "authors":
            return [Author.new_from_json_dict(x) for x in res['data']]
        elif aspect == "sections":
            return [Section.new_from_json_dict(x) for x in res['data']]
        elif aspect == "topics":
            return [Topic.new_from_json_dict(x) for x in res['data']]
        elif aspect == "tags":
            return [Tag.new_from_json_dict(x) for x in res['data']]

    def post_detail(self, url, days=''):
        res = self._request_endpoint('/analytics/post/detail',
            {'url': url, 'days': days}
        )
        return Post.new_from_json_dict(res['data'][0])

    def meta_detail(self, value, aspect="author", days=14, start=None, end=None,
                        pub_start=None, pub_end=None, sort="_hits", limit=10, page=1):
        if aspect not in ["author", "section", "topic", "tag"]:
            raise ValueError("Invalid aspect %s" % aspect)

        options = self._format_analytics_args(days, start, end, pub_start, pub_end,
                                            sort, limit, page)

        return self._request_endpoint('/analytics/%s/%s/detail' % (aspect, value), options)

    def referrers(self, ref_type="social", section='', tag='', domain='', days=3,
                    start=None, end=None, pub_start=None, pub_end=None):
        if ref_type not in ["social", "search", "other", "internal"]:
            raise ValueError("Invalid referrer type %s" % ref_type)

        dates = self._format_date_args(start, end, pub_start, pub_end)
        options = {'section': section, 'tag': tag,
                    'domain': domain, 'days': days}

        res = self._request_endpoint('/referrers/%s' % ref_type,
                                dict(options.items()+dates.items()))
        for r in res['data']:
            r['ref_type'] = ref_type
        return [Referrer.new_from_json_dict(x) for x in res['data']]

    def referrers_meta(self, ref_type="social", meta="posts", section='', domain='',
                        days=3, start=None, end=None, pub_start=None, pub_end=None):
        if ref_type not in ["social", "search", "other", "internal"]:
            raise ValueError("Invalid referrer type %s" % ref_type)

        if meta not in ["posts", "authors", "sections", "topics", "tags"]:
            raise ValueError("Invalid meta type %s" % meta)

        dates = self._format_date_args(start, end, pub_start, pub_end)
        options = {'section': section, 'domain': domain, 'days': days}

        return self._request_endpoint('/referrers/%s/%s' % (ref_type, meta),
                                    dict(options.items() + dates.items()))

    def referrers_meta_detail(self, value, ref_type="social", meta="posts",
                                domain='', days=3, start=None, end=None, pub_start=None,
                                pub_end=None):
        if ref_type not in ["social", "search", "other", "internal"]:
            raise ValueError("Invalid referrer type %s" % ref_type)

        if meta not in ["author", "section", "topic", "tag"]:
            raise ValueError("Invalid meta type %s" % meta)

        dates = self._format_date_args(start, end, pub_start, pub_end)
        options = {'domain': domain, 'days': days}

        return self._request_endpoint('/referrers/%s/%s/%s/detail' % (ref_type, meta, value),
                                    dict(options.items() + dates.items()))

    def referrers_post_detail(self, url, days=3, start=None, end=None, pub_start=None,
                                pub_end=None):

        dates = self._format_date_args(start, end, pub_start, pub_end)
        options = {'days': days, 'url': url}

        return self._request_endpoint('/referrers/post/detail',
                                    dict(options.items() + dates.items()))


    def shares(self, aspect="posts", detail=False, days=14, start=None,
                end=None, limit=10, page=1, url=''):
        if detail:
            if not url:
                raise ValueError("Url required for shares detail")
            return self._request_endpoint('/shares/post/detail', {'url': url})
        else:
            if aspect not in ["posts", "authors"]:
                raise ValueError("Aspect must be one of posts, authors")

            if self._require_both(start, end):
                raise ValueError("Start and end must be specified together")

            start = start.strftime("%Y-%m-%d") if start else ''
            end = end.strftime("%Y-%m-%d") if end else ''

            res = self._request_endpoint('/shares/%s' % aspect,
                {'pub_days': days, 'pub_date_start': start, 'pub_date_end': end,
                'limit': 10, 'page': 1}
            )

            if aspect == "posts":
                return [Post.new_from_json_dict(x) for x in res['data']]
            elif aspect == "authors":
                return [Author.new_from_json_dict(x) for x in res['data']]

    def realtime(self, aspect="posts", per=None, limit=10, page=1):
        if aspect not in ["posts", "authors", "sections", "topics", "tags", "referrers"]:
            raise ValueError("Invalid realtime type %s" % aspect)
        # should be a datetime.timedelta
        options = {'limit': limit, 'page': page}
        if per:
            options['time'] = "%dh" % per.hours if per.hours else "%dm" % per.minutes
        return self._request_endpoint('/realtime/%s' % aspect, options)

    def train(self, uuid, url):
        return self._request_endpoint('/profile', {'uuid': uuid, 'url': url})

    def related(self, url='', uuid='', days=14, limit=10, page=1, section=""):
        if url == '' and uuid == '':
            raise ValueError("Must specify url or uuid")
        if url != '' and uuid != '':
            raise ValueError("Must specify only url or uuid, not both")
        return self._request_endpoint('/related',
            {'url': url, 'uuid': uuid, 'days': days, 'limit': limit, 'page': page}
        )

    def history(self, uuid):
        return self._request_endpoint('/history', {'uuid': uuid})

    def search(self, query, limit=10, page=1):
        return self._request_endpoint('/search', {'limit': limit, 'page': page})

    def _format_analytics_args(self, days, start, end, pub_start,
                                    pub_end, sort, limit, page):
        dates = self._format_date_args(start, end, pub_start, pub_end)
        rest = {'sort': sort, 'limit': limit, 'page': page, 'days': days}
        return dict(dates.items() + rest.items())

    def _format_date_args(self, start, end, pub_start, pub_end):
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
        return (first and not second) or (second and not first)

    def _request_endpoint(self, endpoint, options={}):
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
