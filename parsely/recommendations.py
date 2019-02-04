from __future__ import absolute_import

from .models import Post
from .utils import BaseParselyClient


class User(BaseParselyClient):
    def __init__(self, p, uuid):
        self.conn = p.conn if hasattr(p, "conn") else p
        self.uuid = uuid

    def train(self, post, _callback=None):
        url = post.url if hasattr(post, "url") else post
        handler = self._build_callback(lambda res: bool(res["success"]), _callback)
        res = self.conn._request_endpoint(
            "/profile",
            {"uuid": self.uuid, "url": url},
            _callback=handler if _callback else None,
        )
        return handler(res) if not _callback else None

    def history(self, _callback=None):
        handler = self._build_callback(lambda res: res["data"], _callback)
        res = self.conn._request_endpoint(
            "/history", {"uuid": self.uuid}, _callback=handler if _callback else None
        )
        return handler(res) if not _callback else None

    def related(
        self, days=14, limit=10, page=10, boost="views", section="", _callback=None
    ):
        options = {
            "uuid": self.uuid,
            "days": days,
            "limit": limit,
            "page": page,
            "boost": boost,
        }
        handler = self._build_callback(
            lambda res: [Post.new_from_json_dict(x) for x in res["data"]], _callback
        )
        res = self.conn._request_endpoint(
            "/related", options, _callback=handler if _callback else None
        )
        return handler(res) if not _callback else None
