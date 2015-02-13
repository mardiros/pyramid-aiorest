import venusian

from pyramid_yards.yards import RequestSchema
from .views import AioViewMapperFactory


class resource_config(object):
    """
    A patched version of view_config used for view methods
    """
    venusian = venusian # for testing injection
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


def ioschema(request_schema=None, response_schema=None):

    if request_schema:
        request_schema = RequestSchema(request_schema())

    def wrapper(view_method):
        def wrapped(view_class, request):
            if request_schema:
                request_schema(request)
            return view_method(view_class, request)
        return wrapped

    return wrapper
