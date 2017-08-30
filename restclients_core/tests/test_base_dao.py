"""
Tests the base DAO
"""
from unittest import TestCase

from restclients_core.dao import DAO


class TestBaseDAO(TestCase):

    def setUp(self):
        self.dao = DAO()

    def test_url_process(self):
        url = "/uw-it-aca/myuw"
        params ={}
        params['Hello'] = 'hi'
        params['Howdy'] = 'hi'

        processed_url = self.dao._process_url(url, params)
        self.assertIn(processed_url, "hello=hi")
        self.assertIn(processed_url, 'howdy=hi')

