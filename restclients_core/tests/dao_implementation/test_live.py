from unittest import TestCase, skipUnless
from restclients_core.dao import DAO
import os
from urllib3.exceptions import SSLError


class TDAO(DAO):
    def service_name(self):
        return "live_test"

    def get_default_service_setting(self, key):
        if "DAO_CLASS" == key:
            return "Live"

        if "HOST" == key:
            return "http://localhost:9876/"


class SSLTDAO(DAO):
    def service_name(self):
        return "live_ssl_test"

    def get_default_service_setting(self, key):
        if "DAO_CLASS" == key:
            return "Live"

        if "HOST" == key:
            return "https://localhost:9443/"


class SSLBadFailTDAO(DAO):
    def service_name(self):
        return "live_ssl_test_fail"

    def get_default_service_setting(self, key):
        if "DAO_CLASS" == key:
            return "Live"

        if "HOST" == key:
            return "https://localhost:9444/"


class SSLBadIgnoreTDAO(DAO):
    def service_name(self):
        return "live_ssl_test_ignore"

    def get_default_service_setting(self, key):
        if "DAO_CLASS" == key:
            return "Live"

        if "HOST" == key:
            return "https://localhost:9444/"

        if "VERIFY_HTTPS" == key:
            return False


@skipUnless("RUN_LIVE_TESTS" in os.environ, "RUN_LIVE_TESTS=1 to run tests")
class TestLive(TestCase):
    def test_found_resource(self):
        response = TDAO().getURL('/ok', {})
        self.assertEquals(response.status, 200)
        self.assertEquals(response.data, b'ok')
        self.assertEquals(response.headers["X-Custom-Header"], "header-test")
        self.assertEquals(response.getheader("X-Custom-Header"), "header-test")

    def test_missing_resource(self):
        response = TDAO().getURL('/missing.json', {})
        self.assertEquals(response.status, 404)

    def test_other_status(self):
        response = TDAO().getURL('/403', {})
        self.assertEquals(response.status, 403)

    def test_ssl_found_resource(self):
        response = SSLTDAO().getURL('/ok', {})
        self.assertEquals(response.status, 200)
        self.assertEquals(response.data, b'ok')
        self.assertEquals(response.headers["X-Custom-Header"], "header-test")
        self.assertEquals(response.getheader("X-Custom-Header"), "header-test")

    def test_ssl_non_validated_cert(self):
        self.assertRaises(SSLError, SSLBadFailTDAO().getURL, "/")

    def test_ssl_non_valid_ignore(self):
        response = SSLBadIgnoreTDAO().getURL('/ok', {})
        self.assertEquals(response.status, 200)
        self.assertEquals(response.data, b'ok')
