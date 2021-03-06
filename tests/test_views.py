import unittest

from pyramid import testing


class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_index(self):
        from publication.views import index
        request = testing.DummyRequest()
        info = index(request)
        self.assertEqual(info.body, b'Publication Stats API by SciELO')
