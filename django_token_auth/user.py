class UserHasNoData(Exception):
    pass


class TokenAuthenticatedUser(object):

    """
        When we authenticate user by token we can't usually fetch actual user profile, we only know a username.
        This class describes this kind of users. It will trow an error if you'll try to access any
        attribute excepte the username one.
    """

    def __init__(self, username, token):
        self._token = token
        self.username = username

    def is_authenticated(self):
        return True

    def __getattr__(self, attribute):
        raise UserHasNoData(
            'This user has username only.'
            ' You can not access other attributes, try to fetch them from you profile API instead.'
        )
