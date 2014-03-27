from django.test import TestCase
from django.test import Client
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from django_token_auth import generate_auth_token


def open_view(request):
    return HttpResponse('open view data')


@login_required
def protected_view(request):
    return HttpResponse('protected view data for user %s' % request.user.username)


class IntegrationTestCase(TestCase):

    class DummyUser(object):

        username = 'john'
        username2 = 'johny'

    def setUp(self):
        self.client = Client()

    def test_authenticated(self):
        token, _ = generate_auth_token(self.DummyUser(), 30)
        response = self.client.get('/tests/protected_url/', HTTP_AUTHORIZATION=token)
        self.assertEquals(response.status_code, 200)
        self.assertIn('john', response.content)

    def test_wrong_token(self):
        response = self.client.get('/tests/protected_url/', HTTP_AUTHORIZATION="wrong token")
        # Expect redirect to login page
        self.assertEquals(response.status_code, 302)

    def test_anonymous_access(self):
        response = self.client.get('/tests/open_url/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content, 'open view data')
