import os
from setuptools import setup, find_packages

#from django_token_auth import __version__


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

requirements = []

setup(
    name = "Django token authorization",
    version = ".".join(map(str, (0,0,1))),
    description = "",
    long_description = read('README.md'),
    url = '',
    license = 'MIT',
    author = 'Maxim Leonovich',
    author_email = 'maxim.leonovich@upsilonit.com',
    packages = find_packages(exclude=['tests']),
    include_package_data = True,
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        #'Framework :: Django',
    ],
    install_requires = ["Django>=1.5", "pycrypto>=2.6", "pytz"],
    tests_require = [],
)
