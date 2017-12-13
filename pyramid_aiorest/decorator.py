import asyncio

import venusian
from pyramid.exceptions import Forbidden
from pyramid_yards.yards import RequestSchema

from .views import AioViewMapperFactory
from .response import ResponseSchema


class resource_config(object):
    """
    A patched version of view_config used for view methods
    """
    venusian = venusian  # for testing injection
    def __init__(self, **settings):
        if 'for_' in settings:
            if settings.get('context') is None:
                settings['context'] = settings['for_']
        self.__dict__.update(settings)

    def __call__(self, wrapped):
        settings = self.__dict__.copy()
        depth = settings.pop('_depth', 0)

        def callback(context, name, ob):
            config = context.config.with_package(info.module)

            mapper = config.get_routes_mapper()
            config.commit()
            routes = [route.name for route in mapper.get_routes()]

            resource_name = settings.pop('resource_name')
            settings['mapper'] = AioViewMapperFactory
            route_name = 'collection_{}'.format(resource_name)
            if route_name in routes:
                settings['route_name'] = route_name
                config.add_coroutine_view(view=ob, **settings)
            route_name = 'resource_{}'.format(resource_name)
            if route_name in routes:
                settings['route_name'] = route_name
                config.add_coroutine_view(view=ob, **settings)

        info = self.venusian.attach(wrapped, callback, category='pyramid',
                                    depth=depth + 1)

        if info.scope == 'class':
            # if the decorator was attached to a method in a class, or
            # otherwise executed at class scope, we need to set an
            # 'attr' into the settings if one isn't already in there
            if settings.get('attr') is None:
                settings['attr'] = wrapped.__name__

        settings['_info'] = info.codeinfo # fbo "action_method"
        return wrapped


def async_view(request_schema=None,
               response_schema=None,
               permission=None):
    """Define a pyramid view to run as a asyncio coroutine."""
    if request_schema:
        validate_req = RequestSchema(request_schema)

    if response_schema:
        validate_resp = ResponseSchema(response_schema)

    def wrapper(view_method):

        @asyncio.coroutine
        def wrapped(view_class, request):
            if permission:
                perm = yield from request.has_permission(permission)
                if not perm:
                    raise Forbidden()
            if request_schema:
                request = validate_req(request)
            response = yield from view_method(view_class, request)
            if response_schema:
                response = validate_resp(response)
            return response

        # Keep reference of the schema in the view for introspection
        wrapped.request_schema = request_schema
        wrapped.response_schema = response_schema
        return wrapped

    return wrapper
