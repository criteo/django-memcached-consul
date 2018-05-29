# django-memcached-consul

Django-memcached-consul helps use consul for memcached servers.
It will query Consul Health API to get list of servers every time we use the cache.

## Usage

The configuration is done in the cache part of local_settings.py in the Django project.
Django-memcached-consul use the Django memcached driver so all configuration related to the
caching itself should be done like in django memcached.

To use consul you need to use the specific Django-memcached-consul driver:
`django-consul-memcached.memcached.MemcachedCache`

And to provide informations about Consul and the required services:
```
CONSUL_HOST # The Consul API host
CONSUL_PORT # The Consul API port
CONSUL_SERVICE # The service of the memcached servers in Consul
```
It is possible and strongly recommended to use a cache for the consul, otherwise an Consul API call
will be issued every time we use the cache.

Django-memcached-consul use two layer of cache: the first layer should be short lived (`CONSUL_TTL`)
and is used to cache the list of memcached servers and is retrieved everytime we use the
django-consul-memcached driver. The second one is long lived (`CONSUL_TTL_ALT`) and retrieved when
Consul API is unreachable. The name of the cache to be used is set in `CONSUL_CACHE` and the cache
should be preferably a filebased cache to be shared accross all workers.

## Example

```
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
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/django_consul_cache',
    }
}
```

## Testing

Testing require memcached and tox.

First you need to run memcached on default configuration (usually at localhost:11211) or you will
have to change informations in `tests/tests_data/consul_api_health_mock_with_memcached.json`).

Then you can run tox at the root of the project to start the tests:
```
tox
```
