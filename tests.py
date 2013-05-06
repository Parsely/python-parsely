import unittest

import parsely
from secret import secrets

class TestParselyBindings(unittest.TestCase):
    def setUp(self):
        self.apikey = 'arstechnica.com'
        self.uuid = 'emmett9001'
        self.p = parsely.Parsely(self.apikey, secrets[self.apikey])

    def test_train(self):
        t = self.p.train(self.uuid, 'http://arstechnica.com/gadgets/2013/04/tunein-radio-app-update-makes-it-easier-for-users-to-discover-new-music/')
        self.assertEquals(t['success'], True)

    def test_related(self):
        r = self.p.related(uuid=self.uuid)
        self.assertTrue(len(r) > 0)

    def test_history(self):
        h = self.p.history(self.uuid)
        self.assertEquals(h['data']['uuid'], self.uuid)

    def test_search(self):
        s = self.p.search("security")
        self.assertTrue(len(s) > 0)

    def test_realtime(self):
        r = self.p.realtime()
        self.assertTrue(len(r) > 0)

    def test_shares(self):
        s = self.p.shares()
        self.assertTrue(len(s) > 0)

    def test_referrers_post_detail(self):
        r = self.p.referrers_post_detail('http://arstechnica.com/information-technology/2013/04/memory-that-never-forgets-non-volatile-dimms-hit-the-market/')
        self.assertTrue(len(r) > 0)

    def test_referrers_meta_detail(self):
        r = self.p.referrers_meta_detail('Ars Staff', meta="author")
        self.assertEquals(r[3].author, "Ars Staff")

    def test_referrers_meta(self):
        r = self.p.referrers_meta()
        self.assertTrue(len(r['data']) > 0)

    def test_referrers(self):
        r = self.p.referrers()
        self.assertTrue(len(r) > 0)

    def test_meta_detail(self):
        r = self.p.meta_detail('Uncategorized', aspect="section")
        self.assertEquals(r[3].section, "Uncategorized")

    def test_post_detail(self):
        r = self.p.post_detail('http://arstechnica.com/science/2013/04/inside-science-selling-and-upsizing-the-meal/')
        self.assertTrue(r.title == "Inside science: Selling and upsizing the meal")

    def test_analytics(self):
        r = self.p.analytics()
        self.assertTrue(len(r) > 0)


if __name__ == '__main__':
    unittest.main()
