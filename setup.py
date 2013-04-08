from distutils.core import setup

setup(
    name='python-parsely',
    version='1.2',
    py_modules=['parsely'],
    requires=['requests'],

    author='emmett butler',
    author_email='emmett.butler321@gmail.com',
    url='http://github.com/emmett9001/python-parsely',
    description='Python bindings for the Parsely API'
)
