from restclients_core.util.mock import load_resource_from_path
from restclients_core.models import MockHTTP
from restclients_core.exceptions import ImproperlyConfigured
from restclients_core.cache import NoCache
from restclients_core.util.performance import PerformanceDegradation
from importlib import import_module
from commonconf import settings
import time


class DAO(object):
    def __init__(self):
        self.implementation = None

    def service_name(self):
        raise Exception("service_name must be defined per DAO")

    def _custom_headers(self, method, url, headers, body):
        # to handle things like adding a bearer token
        pass

    def _custom_response_edit(self, method, url, headers, body, response):
        # when using mock resources, this is called to allow swapping out
        # static responses w/ a generated response
        if self.get_implementation().is_mock():
            self._edit_mock_response(method, url, headers, body, response)

    def _edit_mock_responsex(self, method, url, headers, body, response):
        pass

    def getURL(self, url, headers):
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
        start_time = time.time()
        service = self.service_name()

        bad_response = PerformanceDegradation.get_response(service, url)
        if bad_response:
            return bad_response

        custom_headers = self._custom_headers(method, url, headers, body)
        if custom_headers:
            headers.update(custom_headers)

        is_cacheable = self._is_cacheable(method, url, headers, body)

        cache = self.get_cache()

        if is_cacheable:
            cache_response = cache.getCache(service, url, headers)
            if cache_response:
                if "response" in cache_response:
                    self._log(service=service, url=url, method=method,
                              cached=True, start_time=start_time)
                    return cache_response["response"]
                if "headers" in cache_response:
                    headers = cache_response["headers"]

        backend = self.get_implementation()

        response = backend.load(method, url, headers, body)
        self._custom_response_edit(method, url, headers, body, response)

        if is_cacheable:
            cache_post_response = cache.processResponse(service, url, response)
            if cache_post_response is not None:
                if "response" in cache_post_response:
                    self._log(service=service, url=url, method=method,
                              cached=True, start_time=start_time)
                    return cache_post_response["response"]

        return response

    def get_cache(self):
        implementation = self.get_setting("DAO_CACHE_CLASS", None)
        return self._getModule(implementation, NoCache)

    def get_implementation(self):
        implementation = self.get_service_setting("DAO_CLASS", None)

        # Handle the easy built-ins
        if "Live" == implementation:
            return self._get_live_implementation()

        if "Mock" == implementation:
            return self._get_mock_implementation()

        # Legacy settings support
        live = "restclients.dao_implementation.%s.Live" % (self.service_name())
        mock = "restclients.dao_implementation.%s.Live" % (self.service_name())

        if live == implementation:
            return self._get_live_implementation()

        if mock == implementation:
            return self._get_mock_implementation()

        try:
            val = self._getModule(implementation, None, self.service_name(), self)
            if val:
                return val
        except Exception as ex:
            pass

        return self._get_mock_implementation()

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

    def get_service_setting(self, key, default=None):
        return self.get_setting("%s_%s" % (self.service_name().upper(), key),
                                default)

    def get_setting(self, key, default=None):
        key = "RESTCLIENTS_%s" % key
        return getattr(settings, key, default)

    def service_mock_paths(self):
        return []

    def _getModule(self, value, default_class, *args):
        if not value:
            return default_class()

        module, attr = value.rsplit('.', 1)
        try:
            mod = import_module(module)
        except ImportError as e:
            raise ImproperlyConfigured('Error importing module %s: "%s"' %
                                       (module, e))
        try:
            config_module = getattr(mod, attr)
        except AttributeError:
            raise ImproperlyConfigured('Module "%s" does not define a '
                                       '"%s" class' % (module, attr))
        return config_module(*args)

    def _log(self, *args, **kwargs):
        pass


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
        socket_timeout = self.dao.get_service_setting("TIMEOUT", 2)
        max_pool_size = self.dao.get_service_setting("POOL_SIZE", 10)
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
        return True

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
