"""
Schema that describe the response of the API.

If a method return something that does not match the schema,
a ResponseError is raised and is re raised as an HTTP Internal Server Error,
status code 500 by pyramid_aiorest.

Furthermore, if the view return a dict containing items that are
not present in the schema, instead of raise, they are filtered while
processing the response schema.

"""

import logging
import datetime
from decimal import Decimal

import simplejson as json
import colander
from pyramid.response import Response




class JSONEncoder(json.JSONEncoder):
    """JSON encoder which understands decimals and datetimes"""
    _datetypes = (datetime.date, datetime.datetime)

    def default(self, obj):
        """Convert object to JSON encodable type."""
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, self._datetypes):
            return obj.strftime('%Y-%m-%dT%H:%M:%SZ')
        return super(JSONEncoder, self).default(obj)


class ResponseError(Exception):
    def __init__(self, errors):
        self.errors = errors

log = logging.getLogger(__name__)


class ResponseSchema:
    _status_code_schema = colander.MappingSchema(name='status_code')
    def __init__(self, schema):
        self.schema = schema

    def validate(self, data, schema, filldict, errors, prefix=''):
        for attr in schema.children:
            val = data.get(attr.name) or attr.default
            log.info('Validating {nam}: {val}'.format(nam=prefix + attr.name,
                                                       val=val))
            try:
                if attr.children:
                    if isinstance(attr, colander.SequenceSchema):
                        val = attr.deserialize(val)
                        if val != colander.drop:
                            filldict['json'][attr.name] = val
                    else:
                        subdict = {'json': {},
                                   'status_code': None,
                                   'headerlist': []}
                        self.validate(val, attr, filldict[attr.name], errors,
                                      attr.name + '.')
                        filldict['json'][attr.name] = subdict['json']
                else:
                    location = getattr(attr, 'location', 'json')
                    if location == 'status_code':
                        filldict['status_code'] =  colander.Integer().\
                            deserialize(self._status_code_schema, val)
                    elif location == 'header':
                        val = attr.serialize(val)  # A header is a string
                        if val is not colander.null:
                            filldict['headerlist'].append((attr.name, val))
                    else:  # json
                        val = attr.deserialize(val)
                        if val != colander.drop:
                            filldict['json'][attr.name] = val
            except colander.Invalid as exc:
                log.info(exc)
                for key, val in exc.asdict().items():
                    errors[prefix + key] = val

    def __call__(self, response):

        assert isinstance(response, dict), "%r" % response

        resp = {'status_code': 200, 'json': {}, 'headerlist': []}
        errors = {}
        self.validate(response, self.schema, resp, errors)
        if errors:
            raise ResponseError(errors)
        log.info(resp['json'])
        resp['body'] = json.dumps(resp.pop('json'), cls=JSONEncoder)
        return Response(**resp)
