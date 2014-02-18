from models import Post
from utils import _build_callback


class User():
    def __init__(self, p, uuid):
        self.conn = p.conn if hasattr(p, 'conn') else p
        self.uuid = uuid

    def train(self, post, _callback=None):
        url = post.url if hasattr(post, 'url') else post
        handler = _build_callback(
            lambda res: True if res['success'] else False, _callback)
        res = self.conn._request_endpoint('/profile', {'uuid': self.uuid, 'url': url},
                                          _callback=handler if _callback else None)
        return handler(res) if not _callback else None

    def history(self, _callback=None):
        handler = _build_callback(lambda res: res['data'], _callback)
        res = self.conn._request_endpoint('/history', {'uuid': self.uuid},
                                          _callback=handler if _callback else None)
        return handler(res) if not _callback else None

    def related(self, days=14, limit=10, page=10, section="", _callback=None):
        options = {'uuid': self.uuid, 'days': days, 'limit': limit, 'page': page}
        handler = _build_callback(
            lambda res: [Post.new_from_json_dict(x) for x in res['data']],
            _callback)
        res = self.conn._request_endpoint('/related', options,
                                          _callback=handler if _callback else None)
        return handler(res) if not _callback else None
