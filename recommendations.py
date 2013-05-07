from models import Post

class User():
    def __init__(self, p, uuid):
        self.conn = p.conn if hasattr(p, 'conn') else p
        self.uuid = uuid

    def train(self, post):
        url = post.url if hasattr(post, 'url') else post
        res = self.conn._request_endpoint('/profile', {'uuid': self.uuid, 'url': url})
        if res['success']:
            return True
        return False

    def history(self):
        return self.conn._request_endpoint('/history', {'uuid': self.uuid})['data']

    def related(self, days=14, limit=10, page=10, section=""):
        options = {'uuid': self.uuid, 'days': days, 'limit': limit, 'page': page}
        res = self.conn._request_endpoint('/related', options)
        return [Post.new_from_json_dict(x) for x in res['data']]
