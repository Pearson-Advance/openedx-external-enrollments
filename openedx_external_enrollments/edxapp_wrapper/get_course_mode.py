"""Course mode definitions."""
from importlib import import_module

from django.conf import settings


def get_course_mode():
    """ Get get_course_mode Method. """
    backend_function = settings.OEE_COURSE_BACKEND
    backend = import_module(backend_function)

    return backend.get_course_mode()
