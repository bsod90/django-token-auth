from django.test import TestCase
from django.contrib.auth import authenticate
from django_token_auth import generate_auth_token


class BackendTestCase(TestCase):

    class DummyUser(object):

        username = 'john'
        username2 = 'johny'

    def test_authenticate_correct_token(self):
        token, _ = generate_auth_token(self.DummyUser(), 30)
        user = authenticate(token=token)
        self.assertTrue(user.is_authenticated())
        self.assertEqual(user.username, 'john')

    def test_authenticate_incorrect_token(self):
        user = authenticate(token='Some_token')
        self.assertIsNone(user)
