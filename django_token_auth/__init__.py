__version__ = (0, 0, 1)

import os
import pytz
import datetime
import base64
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

from django.conf import settings


def get_private_key():
    assert 'DJANGO_TOKEN_AUTH_PRIVATE_KEY' in os.environ or hasattr(settings, 'TOKEN_AUTH_PRIVATE_KEY'), \
        """
            You must define path to private key either in DJANGO_TOKEN_AUTH_PRIVATE_KEY environment variable or
            TOKEN_AUTH_PRIVATE_KEY settings variable
        """
    # We use 'or' because settings may not have TOKEN_AUTH_PRIVATE_KEY entry
    key_path = os.environ.get('DJANGO_TOKEN_AUTH_PRIVATE_KEY', None) or settings.TOKEN_AUTH_PRIVATE_KEY
    key = open(key_path, 'r').read()
    return RSA.importKey(key)


def get_public_key():
    assert 'DJANGO_TOKEN_AUTH_PUBLIC_KEY' in os.environ or hasattr(settings, 'TOKEN_AUTH_PUBLIC_KEY'), \
        """
            You must define path to public key either in DJANGO_TOKEN_AUTH_PUBLIC_KEY environment variable or
            TOKEN_AUTH_PUBLIC_KEY settings variable
        """
    # We use 'or' because settings may not have TOKEN_AUTH_PUBLIC_KEY entry
    key_path = os.environ.get('DJANGO_TOKEN_AUTH_PUBLIC_KEY', None) or settings.TOKEN_AUTH_PUBLIC_KEY
    key = open(key_path, 'r').read()
    return RSA.importKey(key)


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
        token_name='auth',
        user_id=getattr(user, identification_field),
        expiration_time=expiration_time.strftime("%Y-%m-%dT%H:%M:%S")
    )

    signer = PKCS1_v1_5.new(private_key)
    token_hash = SHA.new(token_content)
    signature = signer.sign(token_hash)

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
    token = token[10:]

    token_content, signature = token.split('|')
    signature = base64.b64decode(signature)

    public_key = get_public_key()
    verifier = PKCS1_v1_5.new(public_key)
    token_hash = SHA.new(token_content)

    if not verifier.verify(token_hash, signature):
        # Token is not valid!
        return None

    token_name, user_id, expiration_time = token_content.split('::')

    if token_name != 'auth':
        # This is not an auth token!
        return None

    expiration_time = datetime.datetime.strptime(expiration_time, "%Y-%m-%dT%H:%M:%S")
    expiration_time = expiration_time.replace(tzinfo=pytz.utc)
    now = datetime.datetime.now(pytz.utc)

    if now > expiration_time:
        # Token expired!
        return None

    return user_id
