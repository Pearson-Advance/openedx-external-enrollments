"""Student backend file."""

from common.djangoapps.student.models import (  # pylint: disable=no-name-in-module, import-error
    CourseEnrollment,
    get_user,
)
from common.djangoapps.student.signals import (  # pylint: disable=no-name-in-module, import-error
    ENROLLMENT_TRACK_UPDATED,
    UNENROLL_DONE,
)


def get_user_backend(*args, **kwargs):
    """Return the method get_user from student.models."""
    return get_user(*args, **kwargs)


def get_course_enrollment_backend():
    """Return the model CourseEnrollment from the module student.models."""
    return CourseEnrollment


def get_enrollment_track_updated_signal():
    """Return ENROLLMENT_TRACK_UPDATED signal."""
    return ENROLLMENT_TRACK_UPDATED


def get_unenroll_done_signal():
    """Return UNENROLL_DONE signal."""
    return UNENROLL_DONE
