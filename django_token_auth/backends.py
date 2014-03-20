from django_token_auth import validate_auth_token
from django_token_auth.user import TokenAuthenticatedUser


class TokenAuthenticationBackend(object):

    def authenticate(self, token):
        username = validate_auth_token(token)
        if not username:
            return None

        return TokenAuthenticatedUser(username, token)
