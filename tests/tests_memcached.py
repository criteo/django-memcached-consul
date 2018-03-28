import unittest
from django_memcached_consul import memcached
import os
from httmock import response, all_requests, HTTMock

os.environ["DJANGO_SETTINGS_MODULE"] = "tests.test_settings"

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

CONSUL_HEADERS = {
    'content-type': 'application/json',
    'X-Consul-Index': 1234567,
    'X-Consul-Knownleader': True,
    'X-Consul-Lastcontact': 0
}
PARAMS = {
    "CONSUL_HOST": "host",
    "CONSUL_PORT": "123456",
    "CONSUL_SERVICE": "memcached_service",
}


def get_file(filename):
    """Get file for tests from tests_data directory."""
    file = open(os.path.join(os.path.join(DIR_PATH, 'tests_data/'), filename))
    content = file.read()
    file.close()
    return content


class TestAll(unittest.TestCase):
    def test_cache(self):
        """Test that it's possible to use memcached with consul."""
        @all_requests
        def response_content(url, request):
            content = get_file("consul_api_health_mock_with_memcached.json")
            return response(200, content, CONSUL_HEADERS, None, 5, request)

        from django.core.cache import cache
        with HTTMock(response_content):
            cache.set("consul_memcache_test", "test")
            # TODO: find a way to properly mock memcached
            self.assertEqual(cache.get("consul_memcache_test"), "test")


class TestStringMethods(unittest.TestCase):
    def test_get_servers_list_from_consul(self):
        """Test that it's possible to get a list of servers from Consul."""
        @all_requests
        def response_content(url, request):
            content = get_file("consul_api_health_mock.json")
            return response(200, content, CONSUL_HEADERS, None, 5, request)

        with HTTMock(response_content):
            self.assertEqual(memcached.get_servers_list_from_consul(PARAMS), [
                             'memcached-mock-node1:80', 'memcached-mock-node2:80'])

    def test_get_servers_without_consul_cache(self):
        """Test that it's possible to return servers list without using cache."""
        @all_requests
        def response_content(url, request):
            content = get_file("consul_api_health_mock.json")
            return response(200, content, CONSUL_HEADERS, None, 5, request)

        with HTTMock(response_content):
            self.assertEqual(memcached.get_servers(PARAMS), [
                             'memcached-mock-node1:80', 'memcached-mock-node2:80'])

    def test_get_servers_fail_without_consul_cache(self):
        """If consul fail without being cached, empty list should be returned."""
        self.assertEqual(memcached.get_servers(PARAMS), [])

    def test_get_servers_with_consul_cache(self):
        """If consul fail without being cached, empty list should be returned."""
        params = PARAMS
        params["CONSUL_CACHE"] = "consul-memcached"
        params["CONSUL_TTL"] = 30
        params["CONSUL_ALT_TTL"] = 60

        self.assertEqual(memcached.get_servers(PARAMS), [])


if __name__ == '__main__':
    unittest.main()
