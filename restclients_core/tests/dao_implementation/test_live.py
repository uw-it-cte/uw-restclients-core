from unittest import TestCase
from restclients_core.dao import DAO


class TDAO(DAO):
    def service_name(self):
        return "live_test"

    def get_default_service_setting(self, key):
        if "DAO_CLASS" == key:
            return "Live"

        if "HOST" == key:
            return "http://localhost:9876/"


class TestLive(TestCase):
    def test_found_resource(self):
        response = TDAO().getURL('/ok', {})
        self.assertEquals(response.status, 200)
        self.assertEquals(response.data, 'ok')
        self.assertEquals(response.headers["X-Custom-Header"], "header-test")
        self.assertEquals(response.getheader("X-Custom-Header"), "header-test")

    def test_missing_resource(self):
        response = TDAO().getURL('/missing.json', {})
        self.assertEquals(response.status, 404)

    def test_other_status(self):
        response = TDAO().getURL('/403', {})
        self.assertEquals(response.status, 403)