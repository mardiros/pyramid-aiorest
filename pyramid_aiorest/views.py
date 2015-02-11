import asyncio
from zope.interface import implementer, provider
from pyramid.interfaces import IViewMapper, IViewMapperFactory


@implementer(IViewMapper)
class AioViewMapper:
    def __init__(self, view):
        self.view = view

    @asyncio.coroutine
    def __call__(self, root_factory, request):
        route_name = request.matched_route.name
        method = request.method.lower()
        if route_name.startswith('collection'):
            method = 'collection_' + method
        return getattr(self.view(), method)(request)


@provider(IViewMapperFactory)
class AioViewMapperFactory:

    def __init__(self, **kwargs):
        pass

    def __call__(self, view):
        return AioViewMapper(view)


def add_resource_route(config, resource_name, collection_path=None, path=None):

    if collection_path is not None:
        config.add_route('collection_{}'.format(resource_name),
                         collection_path)
    if path is not None:
        config.add_route('resource_{}'.format(resource_name),
                         path)

