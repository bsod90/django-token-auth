from django.test import TestCase
from django_token_auth import generate_auth_token
from django_token_auth import validate_auth_token


class GenerateValidateTestCase(TestCase):

    # def setUp(self):
    #     pass

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
