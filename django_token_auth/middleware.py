import logging
from django.contrib.auth import authenticate

logger = logging.getLogger(__name__)


class TokenAuthenticationMiddleware(object):

    """
        Check for authorization token on each request and authenticate a user if token is valid
    """

    def process_request(self, request):
        try:
            token = request.META['HTTP_AUTHORIZATION'].split('API-TOKEN ')[1]
        except:
            logger.warning("No API-TOKEN found in request. Skipping token authentication.")
            return None

        if not hasattr(request, 'user') or not request.user.is_authenticated():
            # Authenticate only if user didn't authenticate before
            # We don't want to collide with django cookies auth needed for admin site for example
            user = authenticate(token=token)
            if not user:
                logger.error("Unable to authenticate request. Invalid API-TOKEN.")
                logger.debug("Invalid API-TOKEN: %s" % token)
                # Continue the request flow, just remain user Anonymous
                return None
            else:
                request.user = user
                logger.info("Authenticated user `%s` by API-TOKEN" % request.user.username)
