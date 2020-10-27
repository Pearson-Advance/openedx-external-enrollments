"""Openedx external enrollments receivers file."""
import logging

from django.dispatch import receiver

from course_modes.models import CourseMode
from openedx_external_enrollments.edxapp_wrapper.get_courseware import get_course_by_id
from openedx_external_enrollments.edxapp_wrapper.get_site_configuration import configuration_helpers
from openedx_external_enrollments.external_enrollments import execute_external_enrollment
from student.signals import (
    ENROLLMENT_TRACK_UPDATED,
    UNENROLL_DONE,
)

LOG = logging.getLogger(__name__)


@receiver(ENROLLMENT_TRACK_UPDATED)
@receiver(UNENROLL_DONE)
def update_external_enrollment(sender, **kwargs):  # pylint: disable=unused-argument
    """
    This receiver is attached to enrollment/unenrollments events. It applies
    the required action when course mode is 'verified'.
    If kwargs['course_enrollment'].is_active is True, an external 'enrollment' request
    will be trigger, otherwise the 'unenroll' action will be called.
    """
    if not configuration_helpers.get_value('ENABLE_EXTERNAL_ENROLLMENTS', False):
        return

    if kwargs['course_enrollment'].mode == CourseMode.VERIFIED:
        LOG.info(
        'The event %s has been triggered for course [%s] and user [%s]. Calling external enrollment controller...',
            'Enroll' if kwargs['course_enrollment'].is_active else 'Unenroll',
            kwargs['course_enrollment'].course_id,
            kwargs['course_enrollment'].user.email,
        )

        data = {
            'user_email': kwargs['course_enrollment'].user.email,
            'course_mode': kwargs['course_enrollment'].mode,
            'is_active': kwargs['course_enrollment'].is_active,
        }

        execute_external_enrollment(
            data=data,
            course=get_course_by_id(kwargs['course_enrollment'].course_id)
        )
