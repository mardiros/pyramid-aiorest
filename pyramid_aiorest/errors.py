import sys
import simplejson as json
from pyramid.response import Response
from pyramid.view import view_config
from pyramid_yards import ValidationFailure

from .i18n import gettext as _

@view_config(context=ValidationFailure)
def http_exception(exc, request):
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

