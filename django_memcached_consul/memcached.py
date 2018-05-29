from django.core.cache import caches
from django.core.cache.backends import memcached


import consul
import requests
import logging


def get_servers(params):
    """Get the list of cache servers either from cache or directly from Consul."""
    try:
        consul_cache = caches[params['CONSUL_CACHE']]
    except(KeyError):
        consul_cache = False

    cache_key = params["CONSUL_SERVICE"]
    alt_cache_key = "alt:%s" % params["CONSUL_SERVICE"]

    if consul_cache:
        cached = consul_cache.get(cache_key)
    else:
        cached = False

    if cached:
        return cached
    else:
        try:
            servers = get_servers_list_from_consul(params)
            if consul_cache:
                consul_cache.set(cache_key, servers, params["CONSUL_TTL"])
                consul_cache.set(alt_cache_key, servers, params["CONSUL_ALT_TTL"])
        except(requests.exceptions.ConnectionError):
            logging.warning("Cannot connect to Consul")
            if consul_cache:
                alt_cached = consul_cache.get(alt_cache_key)
                if alt_cached:
                    return alt_cached

            servers = []
        return servers


def get_servers_list_from_consul(params):
    """Get the list of cache servers using Consul."""
    servers = []
    consul_api = consul.Consul(host=params["CONSUL_HOST"], port=params["CONSUL_PORT"])
    index, data = consul_api.health.service(service=params["CONSUL_SERVICE"], passing=True)
    for node in data:
        servers.append("%s:%s" % (node["Node"]["Node"], node["Service"]["Port"]))
    return servers


class BaseMemcachedCache(memcached.BaseMemcachedCache):
    def __init__(self, server, params, library, value_not_found_exception):
        server = get_servers(params)
        memcached.BaseMemcachedCache.__init__(
            self, server, params, library, value_not_found_exception)


class MemcachedCache(memcached.MemcachedCache, BaseMemcachedCache):
    def __init__(self, server, params):
        import memcache
        BaseMemcachedCache.__init__(
            self, server, params, library=memcache, value_not_found_exception=ValueError)
