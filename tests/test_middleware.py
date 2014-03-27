import mock
from django.test import TestCase
from django.test import RequestFactory
from django_token_auth.middleware import TokenAuthenticationMiddleware


def mocked_authenticate(*args, **kwargs):
    assert 'token' in kwargs
    return mock.Mock(
        is_authenticated=lambda: True,
        username='john'
    )


class TokenAuthMiddlewareTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.authenticate_mock = mock.patch('django_token_auth.middleware.authenticate', mocked_authenticate)
        self.authenticate_mock.start()
        self.addCleanup(self.authenticate_mock.stop)

    def test_token_authentication(self):
        """
            Should call authenticate if Authorization header exists
        """
        token = 'API-TOKEN sometoken'
        request = self.factory.get('/', HTTP_AUTHORIZATION=token)
        TokenAuthenticationMiddleware().process_request(request)

        self.assertTrue(request.user.is_authenticated())
        self.assertEqual(request.user.username, 'john')

    def test_already_authenticated_user(self):
        """
            Should not replace existing authentication
        """
        token = 'API-TOKEN sometoken'
        request = self.factory.get('/', HTTP_AUTHORIZATION=token)
        request.user = mock.Mock(
            is_authenticated=lambda: True,
            username='jahne'
        )
        TokenAuthenticationMiddleware().process_request(request)

        self.assertTrue(request.user.is_authenticated())
        self.assertEqual(request.user.username, 'jahne')

    def test_no_token(self):
        """
            Should not do anything if there is no Authorization header
        """
        request = self.factory.get('/')
        TokenAuthenticationMiddleware().process_request(request)

        self.assertFalse(hasattr(request, 'user'))
