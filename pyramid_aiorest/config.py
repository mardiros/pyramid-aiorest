
from .views import add_resource_route

def includeme(config):
    config.add_directive('add_resource_route', add_resource_route)
    config.scan('pyramid_aiorest.errors')
