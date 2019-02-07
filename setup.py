from __future__ import absolute_import
from distutils.core import setup

setup(
    name="python-parsely",
    version="1.5.0",
    packages=["parsely"],
    requires=["tornado", "six"],
    author="Emmett Butler",
    author_email="emmett@parsely.com",
    url="http://github.com/Parsely/python-parsely",
    description="Python bindings for the Parsely API",
)
