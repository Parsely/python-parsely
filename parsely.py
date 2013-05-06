
import json
import datetime as dt

from models import Post, Author, Section, Topic, Tag, Referrer
from recommendations import Recommendations
from utils import _format_analytics_args, _format_date_args, _require_both
from utils import ParselyAPIConnection


class Parsely():
    def __init__(self, apikey, secret=None, root=None):
        self.conn = ParselyAPIConnection(apikey, secret=secret, root=root)
        self.recs = Recommendations(self.conn)

    def analytics(self, aspect="posts", days=14, start=None, end=None, pub_start=None,
                    pub_end=None, sort="_hits", limit=10, page=1):
        if aspect not in ["posts", "authors", "sections", "topics", "tags"]:
            raise ValueError("Invalid aspect %s" % aspect)

        options = _format_analytics_args(days, start, end, pub_start, pub_end,
                                            sort, limit, page)

        res = self.conn._request_endpoint('/analytics/%s' % aspect, options)
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
        res = self.conn._request_endpoint('/analytics/post/detail',
            {'url': url, 'days': days}
        )
        return Post.new_from_json_dict(res['data'][0])

    def meta_detail(self, value, aspect="author", days=14, start=None, end=None,
                        pub_start=None, pub_end=None, sort="_hits", limit=10, page=1):
        if aspect not in ["author", "section", "topic", "tag"]:
            raise ValueError("Invalid aspect %s" % aspect)

        options = _format_analytics_args(days, start, end, pub_start, pub_end,
                                            sort, limit, page)

        return self.conn._request_endpoint('/analytics/%s/%s/detail' % (aspect, value), options)

    def referrers(self, ref_type="social", section='', tag='', domain='', days=3,
                    start=None, end=None, pub_start=None, pub_end=None):
        if ref_type not in ["social", "search", "other", "internal"]:
            raise ValueError("Invalid referrer type %s" % ref_type)

        dates = _format_date_args(start, end, pub_start, pub_end)
        options = {'section': section, 'tag': tag,
                    'domain': domain, 'days': days}

        res = self.conn._request_endpoint('/referrers/%s' % ref_type,
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

        dates = _format_date_args(start, end, pub_start, pub_end)
        options = {'section': section, 'domain': domain, 'days': days}

        return self.conn._request_endpoint('/referrers/%s/%s' % (ref_type, meta),
                                    dict(options.items() + dates.items()))

    def referrers_meta_detail(self, value, ref_type="social", meta="posts",
                                domain='', days=3, start=None, end=None, pub_start=None,
                                pub_end=None):
        if ref_type not in ["social", "search", "other", "internal"]:
            raise ValueError("Invalid referrer type %s" % ref_type)

        if meta not in ["author", "section", "topic", "tag"]:
            raise ValueError("Invalid meta type %s" % meta)

        dates = _format_date_args(start, end, pub_start, pub_end)
        options = {'domain': domain, 'days': days}

        return self.conn._request_endpoint('/referrers/%s/%s/%s/detail' % (ref_type, meta, value),
                                    dict(options.items() + dates.items()))

    def referrers_post_detail(self, url, days=3, start=None, end=None, pub_start=None,
                                pub_end=None):

        dates = _format_date_args(start, end, pub_start, pub_end)
        options = {'days': days, 'url': url}

        return self.conn._request_endpoint('/referrers/post/detail',
                                    dict(options.items() + dates.items()))


    def shares(self, aspect="posts", detail=False, days=14, start=None,
                end=None, limit=10, page=1, url=''):
        if detail:
            if not url:
                raise ValueError("Url required for shares detail")
            return self.conn._request_endpoint('/shares/post/detail', {'url': url})
        else:
            if aspect not in ["posts", "authors"]:
                raise ValueError("Aspect must be one of posts, authors")

            if _require_both(start, end):
                raise ValueError("Start and end must be specified together")

            start = start.strftime("%Y-%m-%d") if start else ''
            end = end.strftime("%Y-%m-%d") if end else ''

            res = self.conn._request_endpoint('/shares/%s' % aspect,
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
        return self.conn._request_endpoint('/realtime/%s' % aspect, options)

    def train(self, uuid, url):
        return self.recs.train(uuid, url)

    def related(self, url='', uuid='', days=14, limit=10, page=1, section=""):
        return self.recs.related(days, limit, page, section, url=url, uuid=uuid)

    def history(self, uuid):
        return self.recs.history(uuid)

    def search(self, query, limit=10, page=1):
        return self.conn._request_endpoint('/search', {'limit': limit, 'page': page})
