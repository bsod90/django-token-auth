from django.conf.urls import url
from django.conf.urls import patterns


urlpatterns = patterns(
    '',
    url(r'^tests/protected_url/$',
        'tests.test_integration.protected_view'),
    url(r'^tests/open_url/$',
        'tests.test_integration.open_view')
)
