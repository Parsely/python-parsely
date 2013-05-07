import unittest
import random

import parsely
from secret import secrets

class TestParselyBindings(unittest.TestCase):
    def setUp(self):
        self.apikey = 'arstechnica.com'
        self.uuid = 'user%d' % random.randint(1000, 9999)
        self.p = parsely.Parsely(self.apikey, secrets[self.apikey])
        self.train_link = 'http://arstechnica.com/gadgets/2013/04/tunein-radio-app-update-makes-it-easier-for-users-to-discover-new-music/'

    def test_train(self):
        t = self.p.train(self.uuid, self.train_link)
        self.assertEquals(t, True)

        h = self.p.history(self.uuid)
        self.assertEquals(h['uuid'], self.uuid)
        self.assertIn(self.train_link, h['urls'])

    def test_related(self):
        r = self.p.related(uuid=self.uuid)
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
        s = self.p.shares(url=self.train_link, detail=True)
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
        r = self.p.meta_detail('Uncategorized', aspect="section")
        self.assertEquals(r[3].section, "Uncategorized")

    def test_post_detail(self):
        r = self.p.post_detail('http://arstechnica.com/science/2013/04/inside-science-selling-and-upsizing-the-meal/')
        self.assertTrue(r.title == "Inside science: Selling and upsizing the meal")

    def test_analytics(self):
        r = self.p.analytics(aspect="authors")
        self.assertTrue(r[7].hits > 0)

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
