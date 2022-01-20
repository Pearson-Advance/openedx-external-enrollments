""" Backend abstraction. """
from common.djangoapps.course_modes.models import CourseMode  # pylint: disable=no-name-in-module, import-error
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview  # pylint: disable=import-error


def get_course_mode():
    """Return CourseMode class."""
    return CourseMode


def get_course_overview():
    """Return CourseOverview class."""
    return CourseOverview
