from datetime import datetime
import unittest
import random

import parsely
from recommendations import User
from secret import secrets


class TestParselyBindings(unittest.TestCase):
    def setUp(self):
        self.apikey = 'arstechnica.com'
        self.uuid = 'user%d' % random.randint(1000, 9999)
        self.p = parsely.Parsely(self.apikey, secrets[self.apikey])
        self.train_link = 'http://arstechnica.com/gadgets/2013/04/tunein-radio-app-update-makes-it-easier-for-users-to-discover-new-music/'
        self.user = User(self.p, self.uuid)

    def test_train(self):
        t = self.user.train(self.train_link)
        self.assertEquals(t, True)

        h = self.user.history()
        self.assertEquals(h['uuid'], self.uuid)
        self.assertIn(self.train_link, h['urls'])

    def test_related_user(self):
        r = self.user.related()
        self.assertTrue(r[3].title != "")

    def test_related_url(self):
        r = self.p.related(self.train_link)
        self.assertTrue(r[3].title != "")

    def test_search(self):
        s = self.p.search("security", limit=4)
        self.assertTrue(s[3].title != "")

    def test_realtime(self):
        r = self.p.realtime(limit=4)
        self.assertTrue(r[3].title != "")
        self.assertTrue(len(r) == 4)

    def test_shares(self):
        s = self.p.shares(aspect="authors")
        self.assertTrue(s[3].name != "")

    def test_shares_detail(self):
        s = self.p.shares(post=self.train_link)
        self.assertTrue(s.total > 0)

    def test_referrers_post_detail(self):
        r = self.p.referrers_post_detail('http://arstechnica.com/information-technology/2013/04/memory-that-never-forgets-non-volatile-dimms-hit-the-market/')
        self.assertTrue(r[0].hits > 0)

    def test_referrers_meta_detail(self):
        r = self.p.referrers_meta_detail('Ars Staff', meta="author")
        self.assertEquals(r[3].author, "Ars Staff")

    def test_referrers_meta(self):
        r = self.p.referrers_meta()
        self.assertTrue(r[0].hits > 0)

    def test_referrers(self):
        r = self.p.referrers(tag='copyright')
        self.assertTrue(r[2].hits > 0)

    def test_meta_detail(self):
        r = self.p.meta_detail('Technology Lab', aspect="section")
        self.assertEquals(r[3].section, "Technology Lab")

    def test_post_detail(self):
        r = self.p.post_detail('http://arstechnica.com/science/2013/04/inside-science-selling-and-upsizing-the-meal/')
        self.assertTrue(r.title == "Inside science: Selling and upsizing the meal")

        def handle(res):
            self.assertTrue(r.title == "Inside science: Selling and upsizing the meal")
        self.p.post_detail('http://arstechnica.com/science/2013/04/inside-science-selling-and-upsizing-the-meal/', _callback=handle)

    def test_analytics(self):
        r = self.p.analytics(aspect="authors")
        self.assertTrue(r[7].hits > 0)

        def handle(result):
            self.assertTrue(result[7].hits > 0)
        r = self.p.analytics(aspect="authors")

    def test_analytics_one_pubdate(self):
        with self.assertRaises(ValueError):
            self.p.analytics(aspect="authors", pub_start=datetime(2013, 10, 01))

    def test_invalid_aspect(self):
        """when passed an invalid aspect, parsely should not return"""
        r = "sentinel"
        try:
            r = self.p.meta_detail('unimportant', aspect="post")
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


if __name__ == '__main__':
    unittest.main()
