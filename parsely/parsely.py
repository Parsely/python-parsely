from models import Post, Author, Section, Topic, Tag, Referrer, Shares
from utils import _format_analytics_args, _format_date_args, _require_both
from utils import ParselyAPIConnection, valid_kwarg


aspect_map = {"posts": Post, "authors": Author, "sections": Section,
              "topics": Topic, "tags": Tag}
ref_types = ['internal', 'social', 'search', 'other']


class Parsely():
    def __init__(self, apikey, secret=None, root=None):
        self.conn = ParselyAPIConnection(apikey, secret=secret, root=root)
        if not self.authenticated():
            raise ValueError("Authentication failed")

    def authenticated(self):
        res = self.conn._request_endpoint('/analytics/posts', {})
        if 'code' in res and res['code'] == 403:
            return False
        return True

    def _build_callback(self, datafunc, _callback=None):
        def handle(res):
            res = datafunc(res)
            if not _callback:
                return res
            _callback(res)
        return handle

    @valid_kwarg(aspect_map.keys())
    def analytics(self, aspect="posts", _callback=None, **kwargs):
        handler = self._build_callback(
            lambda res: [aspect_map[aspect].new_from_json_dict(x) for x in res['data']],
            _callback)
        options = _format_analytics_args(**kwargs)
        res = self.conn._request_endpoint('/analytics/%s' % aspect, options,
                                          _callback=handler if _callback else None)
        return handler(res) if not _callback else None

    def post_detail(self, post, days='', _callback=None):
        url = post.url if hasattr(post, 'url') else post
        handler = self._build_callback(
            lambda res: Post.new_from_json_dict(res['data'][0]),
            _callback)
        res = self.conn._request_endpoint('/analytics/post/detail',
                                          {'url': url, 'days': days},
                                          _callback=handler if _callback else None)
        return handler(res) if not _callback else None

    @valid_kwarg([x[:-1] for x in aspect_map.keys() if x is not "posts"])
    def meta_detail(self, meta_obj, aspect="author", _callback=None, **kwargs):
        value = getattr(meta_obj, aspect) if hasattr(meta_obj, aspect) else meta_obj
        options = _format_analytics_args(**kwargs)

        handler = self._build_callback(
            lambda res: [Post.new_from_json_dict(x) for x in res['data']],
            _callback)
        res = self.conn._request_endpoint('/analytics/%s/%s/detail' % (aspect, value),
                                          options, _callback=handler if _callback else None)
        return handler(res) if not _callback else None

    @valid_kwarg(ref_types, arg_name="ref_type")
    def referrers(self, ref_type="social", section='', tag='', domain='', days=3,
                  _callback=None, **kwargs):
        dates = _format_date_args(**kwargs)
        options = {'section': section, 'tag': tag,
                   'domain': domain, 'days': days}

        def inner(res):
            for r in res['data']:
                r['ref_type'] = ref_type
            return [Referrer.new_from_json_dict(x) for x in res['data']]
        handler = self._build_callback(inner, _callback)

        res = self.conn._request_endpoint('/referrers/%s' % ref_type,
                                          dict(options.items() + dates.items()),
                                          _callback=handler if _callback else None)
        return handler(res) if not _callback else None

    @valid_kwarg(ref_types, arg_name="ref_type")
    @valid_kwarg(aspect_map.keys(), arg_name="meta")
    def referrers_meta(self, ref_type="social", meta="posts", section='', domain='',
                       days=3, _callback=None, **kwargs):
        dates = _format_date_args(**kwargs)
        options = {'section': section, 'domain': domain, 'days': days}

        endpoint = '/referrers/%s/%s' % (ref_type, meta)

        handler = self._build_callback(
            lambda res: [aspect_map[meta].new_from_json_dict(x) for x in res['data']],
            _callback)
        res = self.conn._request_endpoint(endpoint,
                                          dict(options.items() + dates.items()),
                                          _callback=handler if _callback else None)
        return handler(res) if not _callback else None

    @valid_kwarg(ref_types, arg_name="ref_type")
    @valid_kwarg([x[:-1] for x in aspect_map.keys() if x is not "posts"], arg_name="meta")
    def referrers_meta_detail(self, meta_obj, ref_type="social", meta="author",
                              domain='', days=3, _callback=None, **kwargs):
        value = getattr(meta_obj, meta) if hasattr(meta_obj, meta) else meta_obj

        dates = _format_date_args(**kwargs)
        options = {'domain': domain, 'days': days}

        handler = self._build_callback(
            lambda res: [Post.new_from_json_dict(x) for x in res['data']],
            _callback)

        res = self.conn._request_endpoint('/referrers/%s/%s/%s/detail' % (ref_type, meta, value),
                                          dict(options.items() + dates.items()),
                                          _callback=handler if _callback else None)
        return handler(res) if not _callback else None

    def referrers_post_detail(self, post, days=3, _callback=None, **kwargs):
        url = post.url if hasattr(post, 'url') else post
        dates = _format_date_args(**kwargs)
        options = {'days': days, 'url': url}

        handler = self._build_callback(
            lambda res: [Referrer.new_from_json_dict(x) for x in res['data']],
            _callback)
        res = self.conn._request_endpoint('/referrers/post/detail',
                                          dict(options.items() + dates.items()),
                                          _callback=handler if _callback else None)
        return handler(res) if not _callback else None

    @valid_kwarg(["posts", "authors"])
    def shares(self, aspect="posts", days=14, start=None,
               end=None, limit=10, page=1, post='', _callback=None):
        url = post.url if hasattr(post, 'url') else post
        if url:
            handler = self._build_callback(
                lambda res: Shares.new_from_json_dict(res['data'][0]),
                _callback)
            res = self.conn._request_endpoint('/shares/post/detail', {'url': url},
                                              _callback=handler if _callback else None)
            return handler(res) if not _callback else None
        else:
            if _require_both(start, end):
                raise ValueError("Start and end must be specified together")

            start = start.strftime("%Y-%m-%d") if start else ''
            end = end.strftime("%Y-%m-%d") if end else ''

            handler = self._build_callback(
                lambda res: [aspect_map[aspect].new_from_json_dict(x) for x in res['data']],
                _callback)
            res = self.conn._request_endpoint('/shares/%s' % aspect,
                                              {'pub_days': days,
                                               'pub_date_start': start,
                                               'pub_date_end': end,
                                               'limit': 10, 'page': 1},
                                              _callback=handler if _callback else None)

            return handler(res) if not _callback else None

    @valid_kwarg(aspect_map.keys())
    def realtime(self, aspect="posts", per=None, limit=10, page=1, _callback=None):
        options = {'limit': limit, 'page': page}
        if per:
            options['time'] = "%dh" % per.hours if per.hours else "%dm" % per.minutes

        handler = self._build_callback(
            lambda res: [Post.new_from_json_dict(x) for x in res['data']],
            _callback)
        res = self.conn._request_endpoint('/realtime/%s' % aspect, options,
                                          _callback=handler if _callback else None)
        return handler(res) if not _callback else None

    def related(self, url, days=14, limit=10, page=1, section="", _callback=None):
        options = {'url': url, 'days': days, 'limit': limit, 'page': page}
        handler = self._build_callback(
            lambda res: [Post.new_from_json_dict(x) for x in res['data']],
            _callback)
        res = self.conn._request_endpoint('/related', options,
                                          _callback=handler if _callback else None)
        return handler(res) if not _callback else None

    def search(self, query, limit=10, page=1, _callback=None):
        handler = self._build_callback(
            lambda res: [Post.new_from_json_dict(x) for x in res['data']],
            _callback)
        res = self.conn._request_endpoint('/search', {'q': query, 'limit': limit,
                                                      'page': page},
                                          _callback=handler if _callback else None)
        return handler(res) if not _callback else None
