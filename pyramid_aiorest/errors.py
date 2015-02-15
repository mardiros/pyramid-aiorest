import sys
import simplejson as json
from pyramid.response import Response
from pyramid.view import view_config
from pyramid_yards import ValidationFailure
from pyramid import httpexceptions

from .i18n import gettext as _
from .response import ResponseError

@view_config(context=ValidationFailure)
def validation_failure(exc, request):
    # If the view has two formal arguments, the first is the context.
    # The context is always available as ``request.context`` too.
    error = {
        'message': _('Validation Failed'),
        'errors': exc.errors,
    }
    response = Response(json.dumps(error))
    response.content_type = 'application/json'
    response.status_int = 422
    return response


@view_config(context=ResponseError)
def validation_failure(exc, request):
    # If the view has two formal arguments, the first is the context.
    # The context is always available as ``request.context`` too.
    error = {
        'message': _('Internal Server Error'),
        'errors': exc.errors,
    }
    response = Response(json.dumps(error))
    response.content_type = 'application/json'
    response.status_int = 500
    return response


@view_config(context=httpexceptions.HTTPBadRequest)
@view_config(context=httpexceptions.HTTPUnauthorized)
@view_config(context=httpexceptions.HTTPPaymentRequired)
@view_config(context=httpexceptions.HTTPForbidden)
@view_config(context=httpexceptions.HTTPNotFound)
@view_config(context=httpexceptions.HTTPMethodNotAllowed)
@view_config(context=httpexceptions.HTTPNotAcceptable)
@view_config(context=httpexceptions.HTTPProxyAuthenticationRequired)
@view_config(context=httpexceptions.HTTPRequestTimeout)
@view_config(context=httpexceptions.HTTPConflict)
@view_config(context=httpexceptions.HTTPGone)
@view_config(context=httpexceptions.HTTPLengthRequired)
@view_config(context=httpexceptions.HTTPPreconditionFailed)
@view_config(context=httpexceptions.HTTPRequestEntityTooLarge)
@view_config(context=httpexceptions.HTTPRequestURITooLong)
@view_config(context=httpexceptions.HTTPUnsupportedMediaType)
@view_config(context=httpexceptions.HTTPRequestRangeNotSatisfiable)
@view_config(context=httpexceptions.HTTPExpectationFailed)
@view_config(context=httpexceptions.HTTPUnprocessableEntity)
@view_config(context=httpexceptions.HTTPLocked)
@view_config(context=httpexceptions.HTTPFailedDependency)
@view_config(context=httpexceptions.HTTPInternalServerError)
@view_config(context=httpexceptions.HTTPNotImplemented)
@view_config(context=httpexceptions.HTTPBadGateway)
@view_config(context=httpexceptions.HTTPServiceUnavailable)
@view_config(context=httpexceptions.HTTPGatewayTimeout)
@view_config(context=httpexceptions.HTTPVersionNotSupported)
@view_config(context=httpexceptions.HTTPInsufficientStorage)
def http_exception(exc, request):
    error = {
        'message': exc.title,
        'explanation': exc.explanation,
    }
    response = Response(json.dumps(error))
    response.content_type = 'application/json'
    response.status_int = exc.status_int
    return response
