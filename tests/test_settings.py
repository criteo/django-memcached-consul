SECRET_KEY = 'test'

CACHES = {
    'default': {
        'BACKEND': 'django_memcached_consul.memcached.MemcachedCache',
        'TIMEOUT': 60,
        'CONSUL_TTL': 60,
        # Alt cache will be used if consul is unreachable
        'CONSUL_ALT_TTL': 3600,
        'CONSUL_CACHE': 'consul-memcached',
        'CONSUL_HOST': 'consul.organization.com',
        'CONSUL_PORT': 8500,
        'CONSUL_SERVICE': 'memcached-service',
    },
    'consul-memcached': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'consul_memory_cache',
    }
}
