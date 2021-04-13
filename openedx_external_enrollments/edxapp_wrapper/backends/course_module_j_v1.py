""" Backend abstraction. """
from course_modes.models import CourseMode  # pylint: disable=import-error


def get_course_mode():
    """Return CourseMode class."""
    return CourseMode
