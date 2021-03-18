""" Backend abstraction """
from importlib import import_module

from django.conf import settings


def get_oauth2_authentication():
    """ Get OAuth2Authentication Class """
    backend_function = settings.OEE_OPENEDX_AUTH
    backend = import_module(backend_function)

    return backend.OAuth2Authentication
