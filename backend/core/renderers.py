from rest_framework.renderers import JSONRenderer
from rest_framework import status
from rest_framework.settings import api_settings


class BankJSONRenderer(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        status_code = int(renderer_context['response'].status_code)

        if status_code == status.HTTP_204_NO_CONTENT: # Do not return any data for 204 responses (delete)
            return super(BankJSONRenderer, self).render(data, accepted_media_type, renderer_context)

        response = {
            'status': True,
            'message': None,
            'pagination': data.pop('pagination', None) if data and isinstance(data, dict) else None,
            'data': data.get('data', data) if data and isinstance(data, dict) else list(),
            'error': None,
        }

        if not response['data']: # Get rid of empty data ## TODO: Find a better way to do this
            response['data'] = data if data and isinstance(data, list) else None

        if status_code >= 400:
            response['status'] = False
            response['message'] = data.pop('detail', None) if data and isinstance(data, dict) else None
            response['data'] = None
            response['error'] = data if data and isinstance(data, dict) or isinstance(data, list) else None

        return super(BankJSONRenderer, self).render(response, accepted_media_type, renderer_context)
