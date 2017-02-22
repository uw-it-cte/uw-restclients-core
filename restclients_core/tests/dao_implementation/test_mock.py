from unittest import TestCase
from restclients_core.dao import DAO
from os.path import abspath, dirname


class TDAO(DAO):
    def service_name(self):
        return 'testing'

    def service_mock_paths(self):
        return [abspath(dirname(__file__) + "/resources/")]


class TestMock(TestCase):
    def test_found_resource(self):
        response = TDAO().getURL('/found.json', {})
        self.assertEquals(response.status, 200)

    def test_missing_resource(self):
        response = TDAO().getURL('/missing.json', {})
        self.assertEquals(response.status, 404)
        pass

    def test_file_headers(self):
        response = TDAO().getURL('/with_headers.json', {})
        self.assertEquals(response.status, 202)

        self.assertEquals(response.headers["Custom"], "My Custom Value")
