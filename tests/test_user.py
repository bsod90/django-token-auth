from django.test import TestCase
from django_token_auth.user import TokenAuthenticatedUser
from django_token_auth.user import UserHasNoData


class TokenAuthenticatedUserTestCase(TestCase):

    def test_user_class(self):
        user = TokenAuthenticatedUser('john', 'some_token')
        self.assertEqual(user.username, 'john')
        self.assertTrue(user.is_authenticated())
        self.assertRaises(UserHasNoData, getattr, user, 'email')
