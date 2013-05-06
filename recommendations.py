from models import Post

class Recommendations():
    def __init__(self, conn):
        self.conn = conn

    def train(self, uuid, url):
        return self.conn._request_endpoint('/profile', {'uuid': uuid, 'url': url})

    def history(self, uuid):
        return self.conn._request_endpoint('/history', {'uuid': uuid})

    def related(self, days, limit, page, section, url="", uuid=""):
        if url == '' and uuid == '':
            raise ValueError("Must specify url or uuid")
        if url != '' and uuid != '':
            raise ValueError("Must specify only url or uuid, not both")
        res = self.conn._request_endpoint('/related',
            {'url': url, 'uuid': uuid, 'days': days, 'limit': limit, 'page': page}
        )
        return [Post.new_from_json_dict(x) for x in res['data']]
