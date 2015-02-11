pyramid_aiorest
===============

A lib to build a rest api using the Pyramid framework and asyncio.


Getting Started
---------------

This is distributed as a Pyramid plugin, that add a directive
``add_resource_route`` for the configurator and a decorator
``resource_config`` for decorated class that handle resources.

::

   config.add_resource_route('bar', path='/bars/{id}', collection_path='/bars')
    
   from pyramid_aiorest import resource_config

   @resource_config(resource_name='bar', renderer='json')
   class Bar:

       @asyncio.coroutine
       def collection_get(self, request):
           """ Handle http GET on /bars """
  
       @asyncio.coroutine
       def collection_post(self, request):
           """ Handle http POST on /bars """

       @asyncio.coroutine
       def get(self, request):
           """ Handle http GET on /bars/{id} """
  
       @asyncio.coroutine
       def post(self, request):
           """ Handle http POST on /bars/{id} """
