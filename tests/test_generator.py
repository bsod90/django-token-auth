import mock
import time
from django.conf import settings
from django.test import TestCase
from django_token_auth import generate_auth_token
from django_token_auth import validate_auth_token


class GenerateValidateTestCase(TestCase):

    class DummyUser(object):

        username = 'john'
        username2 = 'johny'

    def test_correct_token(self):
        """
            Generate a token and then validate it. Assume it must be valid.
        """
        token, _ = generate_auth_token(self.DummyUser(), 30)
        username = validate_auth_token(token)

        self.assertEqual(username, 'john')

    def test_custom_id_field(self):
        """
            We should be able to use any other then username field to store in token
        """
        token, _ = generate_auth_token(self.DummyUser(), 30, 'username2')
        username = validate_auth_token(token)

        self.assertEqual(username, 'johny')

    def test_incorrect_token(self):
        """
            Should not validate an invalid token value.
        """
        self.assertIsNone(validate_auth_token("noise"))

    def test_signature_mismatch_wrong_public_key(self):
        """
            We should not validate a token if our public key does not match the private one used to sign
        """
        token, _ = generate_auth_token(self.DummyUser(), 30)

        with self.settings(TOKEN_AUTH_PUBLIC_KEY=settings.TOKEN_AUTH_PUBLIC_KEY.replace('public.pub', 'wrong.pub')):
            with mock.patch('django_token_auth._cached_public_key', None):
                username = validate_auth_token(token)
                self.assertIsNone(username)

    def test_signature_mismatch_wrong_content(self):
        """
            We should not validate a token if our public key does not match the private one used to sign
        """
        token, _ = generate_auth_token(self.DummyUser(), 30)
        token = token.replace('john', 'jane')
        username = validate_auth_token(token)
        self.assertIsNone(username)

    def test_expired_token(self):
        """
            Expired token should not be validated
        """
        token, _ = generate_auth_token(self.DummyUser(), 1)
        username = validate_auth_token(token)
        self.assertEqual(username, 'john')

        time.sleep(2)

        username = validate_auth_token(token)
        self.assertIsNone(username)

    def test_non_auth_token(self):
        """
            Tokens without 'auth' prefix should not pass
        """
        @mock.patch('django_token_auth.TOKEN_NAME', 'activation')
        def get_token():
            return generate_auth_token(self.DummyUser(), 30)[0]

        token = get_token()

        username = validate_auth_token(token)
        self.assertIsNone(username)
