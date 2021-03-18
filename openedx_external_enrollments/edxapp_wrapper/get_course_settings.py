""" Course settings backend abstraction """
from importlib import import_module

from django.conf import settings


def update_course_settings(*args, **kwargs):
    """ Return update_course_settings method. """
    backend_module = settings.OEE_COURSE_SETTINGS_MODULE
    backend = import_module(backend_module)

    return backend.update_course_settings(*args, **kwargs)


def migrate_course_settings(*args, **kwargs):
    """ Return migrate_course_settings method."""
    backend_module = settings.OEE_COURSE_SETTINGS_MODULE
    backend = import_module(backend_module)

    return backend.migrate_course_settings(*args, **kwargs)
