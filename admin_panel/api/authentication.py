from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import Node
import uuid

class ApiKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('ApiKey '):
            return None

        try:
            key = uuid.UUID(auth_header.split(' ')[1])
        except (ValueError, IndexError):
            raise AuthenticationFailed('Invalid API Key format.')

        try:
            node = Node.objects.get(api_key=key)
        except Node.DoesNotExist:
            raise AuthenticationFailed('Invalid API Key')

        return (node, None)