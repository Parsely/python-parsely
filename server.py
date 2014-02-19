import tornado.ioloop
import tornado.web

from parsely import Parsely
from parsely.secret import secrets

API_KEY = "samplesite.com"


class TestSyncHandler(tornado.web.RequestHandler):
    def get(self):
        """
        Demonstrates synchronous use of the Parsely client library
        """
        p = Parsely(API_KEY, secrets[API_KEY])
        res = p.analytics(aspect="authors")
        self.write(res)
        self.finish()


class TestCallbackHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        """
        Demonstrates asynchronous use of the Parsely client via a callback function

        Caller must be wrapped in @tornado.web.asynchronous
        Call to client method must include the _callback kwarg
        """
        def callback(result):
            self.write(result)
            self.finish()
        p = Parsely(API_KEY, secrets[API_KEY])
        p.analytics(aspect="authors", _callback=callback)


def get_app():
    application = tornado.web.Application([
        (r"/test_sync", TestSyncHandler),
        (r"/test_callback", TestCallbackHandler),
    ])
    return application

if __name__ == "__main__":
    application = get_app()
    application.listen(5000)
    tornado.ioloop.IOLoop.instance().start()
