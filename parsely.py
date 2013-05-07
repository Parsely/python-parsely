
import json
import datetime as dt

from models import Post, Author, Section, Topic, Tag, Referrer, Shares
from utils import _format_analytics_args, _format_date_args, _require_both
from utils import ParselyAPIConnection, valid_kwarg


aspect_map = {"posts": Post, "authors": Author, "sections": Section,
                    "topics": Topic, "tags": Tag}
ref_types = ['internal', 'social', 'search', 'other']

class Parsely():
    def __init__(self, apikey, secret=None, root=None):
        self.conn = ParselyAPIConnection(apikey, secret=secret, root=root)

    @valid_kwarg(aspect_map.keys())
    def analytics(self, aspect="posts", days=14, start=None, end=None,
                  pub_start=None, pub_end=None, sort="_hits", limit=10, page=1):

        options = _format_analytics_args(days, start, end, pub_start, pub_end,
                                         sort, limit, page)

        res = self.conn._request_endpoint('/analytics/%s' % aspect, options)
        return [aspect_map[aspect].new_from_json_dict(x) for x in res['data']]

    def post_detail(self, post, days=''):
        url = post.url if hasattr(post, 'url') else post
        res = self.conn._request_endpoint('/analytics/post/detail',
            {'url': url, 'days': days}
        )
        return Post.new_from_json_dict(res['data'][0])

    @valid_kwarg([x[:-1] for x in aspect_map.keys() if x is not "posts"])
    def meta_detail(self, meta_obj, aspect="author", days=14, start=None, end=None,
                    pub_start=None, pub_end=None, sort="_hits", limit=10, page=1):

        value = getattr(meta_obj, aspect) if hasattr(meta_obj, aspect) else meta_obj
        options = _format_analytics_args(days, start, end, pub_start, pub_end,
                                         sort, limit, page)

        res = self.conn._request_endpoint('/analytics/%s/%s/detail' % (aspect, value), options)
        return [Post.new_from_json_dict(x) for x in res['data']]

    @valid_kwarg(ref_types, arg_name="ref_type")
    def referrers(self, ref_type="social", section='', tag='', domain='', days=3,
                  start=None, end=None, pub_start=None, pub_end=None):

        dates = _format_date_args(start, end, pub_start, pub_end)
        options = {'section': section, 'tag': tag,
                   'domain': domain, 'days': days}

        res = self.conn._request_endpoint('/referrers/%s' % ref_type,
                                          dict(options.items()+dates.items()))
        for r in res['data']:
            r['ref_type'] = ref_type
        return [Referrer.new_from_json_dict(x) for x in res['data']]

    @valid_kwarg(ref_types, arg_name="ref_type")
    @valid_kwarg(aspect_map.keys(), arg_name="meta")
    def referrers_meta(self, ref_type="social", meta="posts", section='', domain='',
                       days=3, start=None, end=None, pub_start=None, pub_end=None):

        dates = _format_date_args(start, end, pub_start, pub_end)
        options = {'section': section, 'domain': domain, 'days': days}

        endpoint = '/referrers/%s/%s' % (ref_type, meta)
        res = self.conn._request_endpoint(endpoint,
                                          dict(options.items() + dates.items()))
        return [aspect_map[meta].new_from_json_dict(x) for x in res['data']]

    @valid_kwarg(ref_types, arg_name="ref_type")
    @valid_kwarg([x[:-1] for x in aspect_map.keys() if x is not "posts"], arg_name="meta")
    def referrers_meta_detail(self, meta_obj, ref_type="social", meta="author",
                              domain='', days=3, start=None, end=None,
                              pub_start=None, pub_end=None):

        value = getattr(meta_obj, meta) if hasattr(meta_obj, meta) else meta_obj

        dates = _format_date_args(start, end, pub_start, pub_end)
        options = {'domain': domain, 'days': days}

        res = self.conn._request_endpoint('/referrers/%s/%s/%s/detail' % (ref_type, meta, value),
                                          dict(options.items() + dates.items()))
        return [Post.new_from_json_dict(x) for x in res['data']]

    def referrers_post_detail(self, post, days=3, start=None, end=None, pub_start=None,
                              pub_end=None):

        url = post.url if hasattr(post, 'url') else post
        dates = _format_date_args(start, end, pub_start, pub_end)
        options = {'days': days, 'url': url}

        res = self.conn._request_endpoint('/referrers/post/detail',
                                          dict(options.items() + dates.items()))
        return [Referrer.new_from_json_dict(x) for x in res['data']]


    @valid_kwarg(["posts", "authors"])
    def shares(self, aspect="posts", days=14, start=None,
               end=None, limit=10, page=1, post=''):
        url = post.url if hasattr(post, 'url') else post
        if url:
            res = self.conn._request_endpoint('/shares/post/detail', {'url': url})
            return Shares.new_from_json_dict(res['data'][0])
        else:
            if _require_both(start, end):
                raise ValueError("Start and end must be specified together")

            start = start.strftime("%Y-%m-%d") if start else ''
            end = end.strftime("%Y-%m-%d") if end else ''

            res = self.conn._request_endpoint('/shares/%s' % aspect,
                {'pub_days': days, 'pub_date_start': start, 'pub_date_end': end,
                'limit': 10, 'page': 1}
            )

            return [aspect_map[aspect].new_from_json_dict(x) for x in res['data']]

    @valid_kwarg(aspect_map.keys())
    def realtime(self, aspect="posts", per=None, limit=10, page=1):
        options = {'limit': limit, 'page': page}
        if per:
            options['time'] = "%dh" % per.hours if per.hours else "%dm" % per.minutes

        res = self.conn._request_endpoint('/realtime/%s' % aspect, options)
        return [Post.new_from_json_dict(x) for x in res['data']]

    def related(self, url, days=14, limit=10, page=1, section=""):
        options = {'url': url, 'days': days, 'limit': limit, 'page': page}
        res = self.conn._request_endpoint('/related', options)
        return [Post.new_from_json_dict(x) for x in res['data']]

    def search(self, query, limit=10, page=1):
        res = self.conn._request_endpoint('/search', {'limit': limit, 'page': page})
        return [Post.new_from_json_dict(x) for x in res['data']]
