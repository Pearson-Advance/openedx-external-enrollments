"""PathstreamExternalEnrollment class file."""
import logging
from datetime import datetime

from django.db import IntegrityError

from openedx_external_enrollments.edxapp_wrapper.get_student import get_user
from openedx_external_enrollments.external_enrollments.base_external_enrollment import BaseExternalEnrollment
from openedx_external_enrollments.models import EnrollmentRequestLog, ExternalEnrollment

LOG = logging.getLogger(__name__)


class PathstreamExternalEnrollment(BaseExternalEnrollment):
    """
    PathstreamExternalEnrollment class.
    """
    def __str__(self):
        return 'pathstream'

    def _get_enrollment_data(self, data):  # pylint: disable=arguments-differ
        """
        Returns a string with the data required to be treated as a log.
        String format: 'course_key,email,username,first_name,last_name,date_time,status'
        """
        user, _ = get_user(email=data.get('user_email'))
        return (
            '{course_key},{email},{username},{fullname},'
            '{first_name},{last_name},{date_time},{status}\n'.format(
                course_key=data.get('course_id'),
                email=data.get('user_email'),
                username=user.username,
                fullname=user.profile.name,
                first_name=user.first_name,
                last_name=user.last_name,
                date_time=datetime.utcnow(),
                status=str(data.get('is_active')).lower(),
            )
        )

    def _post_enrollment(self, data, course_settings=None):
        """
        Save enrollment data in ExternalEnrollment model.
        """
        LOG.info('Calling enrollment for [%s] with data: %s', self.__str__(), data)
        LOG.info('Calling enrollment for [%s] with course settings: %s', self.__str__(), course_settings)

        log_details = {
            'data': str(data),
            'course_advanced_settings': course_settings,
        }

        try:
            enrollment, created = ExternalEnrollment.objects.get_or_create(  # pylint: disable=no-member
                controller_name=str(self),
                course_shell_id=data.get('course_id'),
                email=data.get('user_email'),
            )
        except IntegrityError:
            error_msg = 'Failed to complete enrollment, course_id and user_email can\'t be None.'
            log_details['status'] = error_msg

            LOG.error(error_msg)
            EnrollmentRequestLog.objects.create(  # pylint: disable=no-member
                request_type=str(self),
                details=log_details,
            )
        else:
            enrollment.meta = [] if created else enrollment.meta
            enrollment_data = self._get_enrollment_data(data)

            enrollment.meta.append(
                {
                    'enrollment_data_formated': enrollment_data,
                    'is_uploaded': False,
                },
            )
            enrollment.save()
            LOG.info(
                'Saving External enrollment object for [%s] -- ExternalEnrollment.id = %s -- Enrollment data = [%s]',
                self.__str__(),
                enrollment.id,
                enrollment_data,
            )

            log_details['status'] = 'success'
            log_details['payload'] = enrollment_data

            EnrollmentRequestLog.objects.create(  # pylint: disable=no-member
                request_type=str(self),
                details=log_details,
            )

    def _get_enrollment_headers(self):
        pass

    def _get_enrollment_url(self, course_settings):
        pass
