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
from pyramid import httpexceptions


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
            if val is colander.null:
                continue
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
                        # XXX json is in a deserialized format,
                        # except date and datetime that don't have a type
                        # they are string
                        if isinstance(attr.typ, (colander.Date,
                                                 colander.DateTime)):
                            val = attr.serialize(val)
                        else:
                            val = attr.deserialize(val)
                        if val != colander.drop:
                            filldict['json'][attr.name] = val
            except colander.Invalid as exc:
                log.error(exc)
                for key, val in exc.asdict().items():
                    errors[prefix + key] = val

    def __call__(self, response):
        resp = {'status_code': 200, 'json': {}, 'headerlist': []}
        errors = {}
        if isinstance(self.schema, colander.SequenceSchema):
            json_resp = []
            schema = self.schema.children[0]
            if isinstance(response, (list, tuple)):
                for val in response:
                    self.validate(val, schema, resp, errors)
                    json_resp.append(resp['json'])
                    resp['json'] = {}
                resp['json'] = json_resp
            else:
                # XXX Let colander handle error messages
                try:
                    self.schema.deserialize(response)
                except colander.Invalid as exc:
                    log.info(exc)
                    for key, val in exc.asdict().items():
                        errors[key] = val
        else:
            self.validate(response, self.schema, resp, errors)
        if errors:
            raise ResponseError(errors)
        json_body = resp.pop('json')
        if (json_body is not None and
                resp['status_code'] != httpexceptions.HTTPNoContent and
                not (300 <= resp['status_code'] <= 400)
                ):
            resp['body'] = json.dumps(json_body, cls=JSONEncoder)
        return Response(**resp)
