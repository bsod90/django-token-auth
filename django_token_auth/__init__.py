__version__ = (0, 0, 1)

import os
import pytz
import datetime
import base64
import M2Crypto

from django.conf import settings

_cached_public_key = None

TOKEN_NAME = 'auth'


def get_private_key():

    assert 'DJANGO_TOKEN_AUTH_PRIVATE_KEY' in os.environ or hasattr(settings, 'TOKEN_AUTH_PRIVATE_KEY'), \
        """
            You must define path to private key either in DJANGO_TOKEN_AUTH_PRIVATE_KEY environment variable or
            TOKEN_AUTH_PRIVATE_KEY settings variable
        """
    # We use 'or' because settings may not have TOKEN_AUTH_PRIVATE_KEY entry
    key_path = os.environ.get('DJANGO_TOKEN_AUTH_PRIVATE_KEY', None) or settings.TOKEN_AUTH_PRIVATE_KEY
    return M2Crypto.RSA.load_key(key_path)


def get_public_key():
    # Do not read public key every time, check if we already have it in memory first
    # It's safe to keep it in memory as it's public
    global _cached_public_key
    if _cached_public_key:
        return _cached_public_key

    assert 'DJANGO_TOKEN_AUTH_PUBLIC_KEY' in os.environ or hasattr(settings, 'TOKEN_AUTH_PUBLIC_KEY'), \
        """
            You must define path to public key either in DJANGO_TOKEN_AUTH_PUBLIC_KEY environment variable or
            TOKEN_AUTH_PUBLIC_KEY settings variable
        """
    # We use 'or' because settings may not have TOKEN_AUTH_PUBLIC_KEY entry
    key_path = os.environ.get('DJANGO_TOKEN_AUTH_PUBLIC_KEY', None) or settings.TOKEN_AUTH_PUBLIC_KEY
    _cached_public_key = M2Crypto.RSA.load_pub_key(key_path)
    return _cached_public_key


def generate_auth_token(user, ttl, identification_field='username'):
    """
        Args:
            user:
                User we issue token for. Should be an instance of django.contrib.auth.models.User
                or any custom user model.
            ttl:
                Token time to live in seconds. Token will expire after now + ttl.
            identification_field:
                Optionally you can specify a field that should be used as user identifier in token.
                defualt='username'
        Return:
            (token, expiration_time):
                token: string token
                expiration_time: now + ttl
    """

    assert hasattr(user, identification_field), "User must have {0} field".format(identification_field)

    # Make sure we work in UTC
    now = datetime.datetime.now(pytz.utc)
    expiration_time = now + datetime.timedelta(seconds=ttl)

    private_key = get_private_key()

    # Use token name to avoid potential collisions
    # if we will use the same tokenizing mechanism for other then auth purposes
    token_content = "{token_name}::{user_id}::{expiration_time}".format(
        token_name=TOKEN_NAME,
        user_id=getattr(user, identification_field),
        expiration_time=expiration_time.strftime("%Y-%m-%dT%H:%M:%S")
    )

    signature = private_key.sign(token_content)

    signed_token = "{token_content}|{signature}".format(
        token_content=token_content,
        signature=base64.b64encode(signature)
    )

    envelope = "API-TOKEN {0}".format(signed_token)

    return envelope, expiration_time


def validate_auth_token(token):
    """
        Args:
            token:
                Token to verify
        Return:
            user_id: decoded user_id or None if token is not valid
    """

    # Cut the API-TOKEN part
    token = token.replace('API-TOKEN ', '')

    try:
        token_content, signature = token.split('|')
    except:
        # We got malformed token, nothing to look at
        return None

    signature = base64.b64decode(signature)

    public_key = get_public_key()
    try:
        if not public_key.verify(token_content, signature):
            return None
    except:
        # Token is not valid!
        return None

    try:
        token_name, user_id, expiration_time = token_content.split('::')
    except:
        # Token must contain 3 components, otherwise it's invalid
        return None

    if token_name != TOKEN_NAME:
        # This is not an auth token!
        return None

    expiration_time = datetime.datetime.strptime(expiration_time, "%Y-%m-%dT%H:%M:%S")
    expiration_time = expiration_time.replace(tzinfo=pytz.utc)
    now = datetime.datetime.now(pytz.utc)

    if now > expiration_time:
        # Token expired!
        return None

    return user_id
