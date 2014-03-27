django-token-auth
=================

Token based authorization for django.
This library aimed to help providing API authentication in distributed systems.
Let's assume we have an authentication center (AC) and several APIs that expect user to be authenticated in AC.
In our case AC should use it's own authentication methods to authenticate user against AC (user can be prompted to enter his login and password for example). And then AC should issue a token - encrypted string that tells "User X authenticated against AC and can use this authentication elsewhere in the system for N minutes". Using crypto algorithms we can assure that token has been issued by our AC and not been forged.

How it works
-----------------
Each token consists of \<token_name\>::\<username\>::\<expiration_time\>|\<signature\>.
+ **token_name** - just a string prefix that should distinguish our authentication token from any other same formated tokens
+ **username** - authenticated user identifier
+ **expiration_time** - after this time token can not be used anymore
+ **signature** - cryptographical signature verifies that token has been issued by AC

AC computes token content, encodes it in string and then uses RSA algorithm to sign the content using private key.
Every consumer API then decodes token and verifies signature and expiration time first. We must share corresponding public key across our consumer APIs to make possible signature verification. 
This library provides a middleware for consumer APIs that expect token to be passed as ```Authorization``` HTTP header.

How to use it
------------------

**AC**

First of all you should generate RSA keypair in PEM format.
Then 
```
    pip install git+https://github.com/WiserTogether/django-token-auth.git
```

In your AC you should do
```
    export DJANGO_TOKEN_AUTH_PRIVATE_KEY='/path/to/private.pem
```
or just set TOKEN_AUTH_PRIVATE_KEY settings variable.

and then you can use generate_auth_token as following
```
from django_token_auth import generate_auth_token

TTL = 60*30 # 30 minutes in seconds
token, expiration_time = generate_auth_token(request.user, TTL)

# optionally, you can pass custom field to use as user_id

token, expiration_time = generate_auth_token(request.user, TTL, 'email')
```
Then just give this token to consumer API users.

**consumer API**

Start from installing django_token_auth
Then you should set a path to public key in the same way you did for AC

```
    export DJANGO_TOKEN_AUTH_PUBLIC_KEY='/path/to/public.pub
```
or just set TOKEN_AUTH_PUBLIC_KEY settings variable.

WARNING: don't store your private key along with your consumer applications, it's not secure.

Add *TokenAuthenticationMiddleware* and *TokenAuthenticationBackend* to your app:

```
    MIDDLEWARE_CLASSES += 'django_token_auth.middleware.TokenAuthenticationMiddleware'
```

```
    AUTHENTICATION_BACKENDS += 'django_token_auth.backends.TokenAuthenticationBackend'
```

Now, if request contains AC issued token in Authorization header, the middleware will pass it to TokenAuthenticationBackend and in case of success authentication, it will set request.user to ```TokenAuthenticatedUser```

It's a special type of user that does not have anything but ```username```. As we can not easily obtain it from token, we should ask AC instead. If you will try to access any attribute you will get an exception.

User model extension
---------------
TBD

For developers
---------------

To run tests use:
```
    export DJANGO_SETTINGS_MODULE=tests.settings
    nosetests
```

feel free to leave pull requests :)
