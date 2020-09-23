"""Backend for courseware module."""

from lms.djangoapps.courseware.courses import get_course_by_id # pylint: disable=import-error

def get_course_by_id_backend(*args, **kwargs):
    """Return the method get_course_by_id from courseware.courses."""
    return get_course_by_id(*args, **kwargs)
