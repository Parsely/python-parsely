from __future__ import absolute_import
from datetime import datetime
import unittest
import random

from . import parsely
from .recommendations import User
from .secret import secrets


class TestParselyBindings(unittest.TestCase):
    def setUp(self):
        self.apikey = "arstechnica.com"
        self.uuid = "user%d" % random.randint(1000, 9999)
        self.p = parsely.Parsely(self.apikey, secrets[self.apikey])
        self.train_link = "https://arstechnica.com/gadgets/2017/09/android-8-0-oreo-thoroughly-reviewed/"  #'http://arstechnica.com/gadgets/2013/04/tunein-radio-app-update-makes-it-easier-for-users-to-discover-new-music/'
        self.user = User(self.p, self.uuid)

    def test_train(self):
        t = self.user.train(self.train_link)
        self.assertEqual(t, True)

        def handle_train(res):
            self.assertEqual(res, True)

        self.user.train(self.train_link, _callback=handle_train)

        h = self.user.history()
        self.assertEqual(h["uuid"], self.uuid)
        self.assertIn(self.train_link, h["urls"])

        def handle_history(res):
            self.assertEqual(res["uuid"], self.uuid)
            self.assertIn(self.train_link, res["urls"])

        self.user.history(_callback=handle_history)

    def test_related_user(self):
        r = self.user.related()
        self.assertTrue(r[3].title != "")

        def handle(res):
            self.assertTrue(res[3].title != "")

        self.user.related(_callback=handle)

    def test_related_url(self):
        r = self.p.related(self.train_link)
        self.assertTrue(r[3].title != "")

        def handle(res):
            self.assertTrue(res[3].title != "")

        self.p.related(self.train_link, _callback=handle)

    def test_search(self):
        s = self.p.search("security", limit=4)
        self.assertTrue(s[3].title != "")

        def handle(res):
            self.assertTrue(res[3].title != "")

        self.p.search("security", limit=4, _callback=handle)

    def test_realtime(self):
        r = self.p.realtime(limit=4)
        self.assertTrue(r[3].title != "")
        self.assertTrue(len(r) == 4)

        def handle(res):
            self.assertTrue(res[3].title != "")
            self.assertTrue(len(res) == 4)

        self.p.realtime(limit=4, _callback=handle)

    def test_shares_detail(self):
        s = self.p.shares(post=self.train_link)
        self.assertTrue(s.total > 0)

        def handle(res):
            self.assertTrue(res.total > 0)

        self.p.shares(post=self.train_link, _callback=handle)

    def test_referrers_post_detail(self):
        r = self.p.referrers_post_detail(
            "https://arstechnica.com/gaming/2017/09/the-pc-issues-that-need-fixing-before-final-fantasy-xv-launches-on-windows/"
        )  #'http://arstechnica.com/information-technology/2013/04/memory-that-never-forgets-non-volatile-dimms-hit-the-market/')
        self.assertTrue(r[0].hits > 0)

        def handle(res):
            self.assertTrue(res[0].hits > 0)

        self.p.referrers_post_detail(
            "https://arstechnica.com/gaming/2017/09/the-pc-issues-that-need-fixing-before-final-fantasy-xv-launches-on-windows/",
            _callback=handle,
        )  #'http://arstechnica.com/information-technology/2013/04/memory-that-never-forgets-non-volatile-dimms-hit-the-market/',

    def test_referrers_meta_detail(self):
        r = self.p.referrers_meta_detail("Ars Staff", meta="author")
        self.assertEqual(r[3].author, "Ars Staff")

        def handle(res):
            self.assertEqual(res[3].author, "Ars Staff")

        self.p.referrers_meta_detail("Ars Staff", meta="author", _callback=handle)

    def test_referrers_meta(self):
        r = self.p.referrers_meta()
        self.assertTrue(r[0].hits > 0)

        def handle(res):
            self.assertTrue(res[0].hits > 0)

        self.p.referrers_meta(_callback=handle)

    def test_referrers(self):
        r = self.p.referrers(tag="copyright")
        self.assertTrue(r[2].hits > 0)
        self.assertTrue(r[2].ref_type == "social")

        def handle(res):
            self.assertTrue(res[2].hits > 0)
            self.assertTrue(res[2].ref_type == "social")

        self.p.referrers(tag="copyright", _callback=handle)

    def test_meta_detail(self):
        r = self.p.meta_detail("Tech", aspect="section")
        self.assertEqual(r[3].section, "Tech")

        def handle(res):
            self.assertEqual(res[3].section, "Tech")

        self.p.meta_detail("Tech", aspect="section", _callback=handle)

    def test_post_detail(self):
        r = self.p.post_detail(
            "https://arstechnica.com/gadgets/2017/09/android-8-0-oreo-thoroughly-reviewed/"
        )
        self.assertTrue(r.title == "Android 8.0 Oreo, thoroughly reviewed")
        self.assertTrue(r.visitors > 0)

        def handle(res):
            self.assertTrue(res.title == "Android 8.0 Oreo, thoroughly reviewed")
            self.assertTrue(res.visitors > 0)

        self.p.post_detail(
            "https://arstechnica.com/gadgets/2017/09/android-8-0-oreo-thoroughly-reviewed/",
            _callback=handle,
        )

    def test_analytics(self):
        r = self.p.analytics(aspect="authors")
        self.assertTrue(r[7].hits > 0)

        def handle(res):
            self.assertTrue(res[7].hits > 0)

        self.p.analytics(aspect="authors", _callback=handle)

    def test_analytics_one_pubdate(self):
        with self.assertRaises(ValueError):
            self.p.analytics(
                aspect="authors", pub_start=datetime(2017, 9, 4)
            )  # 2013, 10, 01))

    def test_invalid_aspect(self):
        """when passed an invalid aspect, parsely should not return"""
        r = "sentinel"
        try:
            r = self.p.meta_detail("unimportant", aspect="post")
        except:
            pass
        self.assertTrue(r == "sentinel")

    def test_invalid_ref_type(self):
        """when passed an invalid referrer type, parsely should not return"""
        r = "sentinel"
        try:
            r = self.p.referrers_meta(ref_type="fgsfds")
        except:
            pass
        self.assertTrue(r == "sentinel")

    def test_analytics_sort(self):
        r = self.p.analytics(aspect="posts", sort="mobile_views")
        self.assertTrue(r[0].mobile_views > 0)

        def handle(res):
            self.assertTrue(res[0].mobile_views > 0)

        self.p.analytics(aspect="posts", sort="mobile_views", _callback=handle)

    def test_related_boost(self):
        r = self.p.related(self.train_link, boost="visitors_returning")
        self.assertTrue(r[0].title != "")

        def handle(res):
            self.assertTrue(res[0].title != "")

        self.p.related(self.train_link, boost="visitors_returning", _callback=handle)

    def test_search_boost(self):
        s = self.p.search("security", limit=4, boost="visitors_new")
        self.assertTrue(s[0].title != "")

        def handle(res):
            self.assertTrue(res[0].title != "")

        self.p.search("security", limit=4, boost="visitors_new", _callback=handle)

    def test_wrong_metric(self):
        with self.assertRaises(ValueError):
            r = self.p.analytics(aspect="posts", sort="Mobile_view")


if __name__ == "__main__":
    unittest.main()
