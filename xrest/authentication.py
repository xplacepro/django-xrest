import base64
import binascii

from .settings import XREST_BASIC_AUTH_USER, XREST_BASIC_AUTH_PASSWORD


class NoAuthentication(object):
    def authenticate(self, request):
        return True


class BasicAuthentication(object):
    def authenticate(self, request):
        if not request.META.get('HTTP_AUTHORIZATION'):
            return None

        try:
            (auth_type, token) = request.META['HTTP_AUTHORIZATION'].split()
            if auth_type.lower() != 'basic':
                return None
        except (KeyError, ValueError, TypeError):
            return None

        encoded = token.strip()

        if not encoded:
            return None

        user, password = XREST_BASIC_AUTH_USER, XREST_BASIC_AUTH_PASSWORD

        try:
            decoded = base64.decodebytes(encoded.encode())
            u, p = decoded.decode().split(':')
            return u == user and p == password
        except (binascii.Error, IndexError):
            pass

        return None
