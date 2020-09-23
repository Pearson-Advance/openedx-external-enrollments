"""Openedx external enrollments receivers file."""
import logging

from django.dispatch import receiver

from openedx_external_enrollments.edxapp_wrapper.get_courseware import get_course_by_id
from openedx_external_enrollments.edxapp_wrapper.get_site_configuration import configuration_helpers
from openedx_external_enrollments.external_enrollments import execute_external_enrollment
from student.signals import ENROLL_STATUS_CHANGE
from student.models import EnrollStatusChange

LOG = logging.getLogger(__name__)


def update_external_enrollment(sender, created, instance, **kwargs):  # pylint: disable=unused-argument
    """
    This receiver is called when the django.db.models.signals.post_save signal is sent,
    it will execute an enrollment or unenrollment based on the value of instance.is_active.
    """
    if (not configuration_helpers.get_value('ENABLE_EXTERNAL_ENROLLMENTS', False)
            or (created and not instance.is_active)):
        return

    data = {
        'user_email': instance.user.email,
        'course_mode': instance.mode,
        'is_active': instance.is_active,
    }

    execute_external_enrollment(data=data, course=get_course_by_id(instance.course.id))


def delete_external_enrollment(sender, instance, **kwargs):  # pylint: disable=unused-argument
    """
    This receiver is called when the django.db.models.signals.post_delete signal is sent,
    it will always execute an unenrollment.
    """
    if not configuration_helpers.get_value('ENABLE_EXTERNAL_ENROLLMENTS', False):
        return

    data = {
        'user_email': instance.user.email,
        'course_mode': instance.mode,
        'is_active': False,
    }

    execute_external_enrollment(data=data, course=get_course_by_id(instance.course.id))


@receiver(ENROLL_STATUS_CHANGE)
def change_external_enrollment(sender, event=None, user=None, mode=None, course_id=None ,**kwargs):  # pylint: disable=unused-argument
    """
    Awards enrollment badge to the given user on new enrollments.
    """
    if not configuration_helpers.get_value('ENABLE_EXTERNAL_ENROLLMENTS', False):
        return

    data = {
        'user_email': user.email,
        'course_mode': mode,
        'is_active': True if event == EnrollStatusChange.enroll else False,
    }

    LOG.info(
        'The event %s has been triggered for course [%s] and user [%s]. Calling external enrollment controller...',
        event.upper(),
        course_id,
        user.email,
    )

    execute_external_enrollment(data=data, course=get_course_by_id(course_id))
