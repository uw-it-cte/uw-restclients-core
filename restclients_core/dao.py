from restclients_core.util.mock import load_resource_from_path
from restclients_core.models import MockHTTP


class DAO(object):
    def __init__(self):
        self.implementation = None

    # will probably be overridden
    def _mock_data_path(self):
        pass

    def service_name(self):
        raise Exception("service_name must be defined per DAO")

    def _custom_headers(self, method, url, headers, body):
        # to handle things like https://github.com/uw-it-aca/uw-restclients/blob/master/restclients/dao_implementation/sws.py#L178
        pass
    def _custom_response(self, method, url, headers, body):
        # when using mock resources, this is called to allow swapping out static responses w/ a code response (e.g. https://github.com/uw-it-aca/uw-restclients/blob/master/restclients/dao_implementation/sws.py#L71)
        pass

    # Probably won't be
    def getURL(self, url, headers): # These have the same args as before, plus an additional optional override of ok_statuses and error_statuses, if a specific resource requires them.
        return self._load_resource("GET", url, headers, None)

    def postURL(self, url, headers, body=None):
        return self._load_resource("POST", url, headers, body)

    def putURL(self, url, headers, body=None):
        return self._load_resource("PUT", url, headers, body)

    def patchURL(self, url, headers, body):
        return self._load_resource("PATCH", url, headers, body)

    def deleteURL(self, url, headers, body):
        return self._load_resource("DELETE", url, headers, body)

    def _load_resource(self, method, url, headers, body):
        custom_response = self._custom_response(method, url, headers, body)
        if custom_response:
            return custom_response

        custom_headers = self._custom_headers(method, url, headers, body)
        if custom_headers:
            headers.update(custom_headers)

        is_cacheable = self._is_cacheable(method, url, headers, body)
        if is_cacheable:
            # Check the cache
            pass

        backend = self.get_implementation()

        response = backend.load(method, url, headers, body)

        if is_cacheable:
            # Save into the cache
            pass

        return response

    def get_implementation(self):
        implementation = self.get_service_setting("DAO_CLASS", None)

        # Handle the easy built-ins
        if "Live" == implementation:
            return self._get_live_implementation()

        if "Mock" == implementation:
            return self._get_mock_implementation()

        # Legacy settings support
        live = "restclients.dao_implementation.%s.Live" % (self.service_name)
        mock = "restclients.dao_implementation.%s.Live" % (self.service_name)

        if live == implementation:
            return self._get_live_implementation()

        if mock == implementation:
            return self._get_mock_implementation()

        # XXX - do we still need to support custom implementations?
        return self._get_mock_implementation()


    def _get_cert_path(): # Can be overridden, but will have useful defaults
        pass
    def _get_key_path():
        pass

    def _build_path(): # gets realpath on arg[0], path.joins the rest then calls realpath on the result
        pass
    def _is_cacheable(self, method, url, headers, body=None):
        if method == "GET":
            return True
        return False

    def _ok_status_codes():
        return [200, 201, 202, 204]

    def _error_status_codes():
        return []

    def _get_live_implementation(self):
        return LiveDAO(self.service_name(), self)

    def _get_mock_implementation(self):
        return MockDAO(self.service_name(), self)

    def get_service_setting(self, key, default):
        pass

    def get_setting(self, key, default):
        pass

    def service_mock_paths(self):
        return []

class DAOImplementation(object):
    def __init__(self, service_name, dao):
        self._service_name = service_name
        self.dao = dao

    def is_live(self):
        return False

    def is_mock(self):
        return False

class LiveDAO(DAOImplementation):
    pools = {}

    def is_live(self):
        return True

    def load(self, method, url, headers, body):
        pool = self.get_pool()
        timeout = pool.timeout.read_timeout

        response = pool.urlopen(method, url, body=body,
                                headers=headers, redirect=True,
                                retries=False, timeout=timeout)

        return response


    def get_pool(self):
        service = self.service()
        if service not in LiveDAO.pools:
            pool = self.create_pool()
            LiveDAO.pools[service] = pool

        return LiveDAO.pools[service]

    def create_pool(self):
        """
        Return a ConnectionPool instance of given host
        :param socket_timeout:
            socket timeout for each connection in seconds
        """

        service = self.service()

        host = self.dao.get_service_setting("HOST")
        socket_timeout = self.dao.get_service_setting("TIMEOUT")
        max_pool_size = self.dao.get_service_setting("POOL_SIZE")
        key_file = self.dao.get_service_setting("KEY_FILE", None)
        cert_file = self.dao.get_service_setting("CERT_FILE", None)
        ca_certs = self.dao.get_setting("CA_BUNDLE",
                                        "/etc/ssl/certs/ca-bundle.crt")

        kwargs = {
            "timeout": socket_timeout,
            "maxsize": max_pool_size,
            "block": True,
            }

        if key_file is not None and cert_file is not None:
            kwargs["key_file"] = key_file
            kwargs["cert_file"] = cert_file

        if urlparse(host).scheme == "https":
            kwargs["ssl_version"] = ssl.PROTOCOL_TLSv1
            if verify_https:
                kwargs["cert_reqs"] = "CERT_REQUIRED"
                kwargs["ca_certs"] = getattr(settings, "RESTCLIENTS_CA_BUNDLE",
                                             "/etc/ssl/certs/ca-bundle.crt")

        return connection_from_url(host, **kwargs)


class MockDAO(DAOImplementation):
    paths = []

    def is_mock(self):
        return False

    def register_mock_path(self, path):
        if path not in paths:
            MockDAO.paths.append(path)

    def get_registered_paths(self):
        return MockDAO.paths


    def _get_mock_paths(self):
        return self.get_registered_paths() + self.dao.service_mock_paths()

    def load(self, method, url, headers, body):
        service = self._service_name

        for path in self._get_mock_paths():
            response = load_resource_from_path(path, service, "file", url,
                                               headers)

            if response:
                return response

        response = MockHTTP()
        response.status = 404
        response.reason = "Not Found"
        return response


