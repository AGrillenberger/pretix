from django.core.urlresolvers import resolve
from django.utils.deprecation import MiddlewareMixin

from pretix.presale.signals import process_response

from .utils import _detect_event


class EventMiddleware(MiddlewareMixin):
    def process_request(self, request):
        url = resolve(request.path_info)
        request._namespace = url.namespace
        if url.namespace != 'presale':
            return

        if 'organizer' in url.kwargs or 'event' in url.kwargs:
            redirect = _detect_event(request)
            if redirect:
                return redirect

        if '_' not in request.session:
            # We need to create session even if we do not yet store something there, because we need the session
            # key for e.g. saving the user's cart
            request.session['_'] = '_'

    def process_response(self, request, response):
        if hasattr(request, '_namespace') and request._namespace == 'presale' and hasattr(request, 'event'):
            for receiver, r in process_response.send(request.event, request=request, response=response):
                response = r
        return response
