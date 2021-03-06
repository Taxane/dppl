"""
This allows you to run `$ python manage.py runserver` without specifying the
settings. On different environments, be sure to add their own
`settings/<env>.py` to the repository, and specify which settings to use with
an environment variable.
"""
try:
    from settings.local import *
except ImportError:
    pass
