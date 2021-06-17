"""ViperExternalEnrollment class file."""
import logging

import requests
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status

from openedx_external_enrollments.external_enrollments.base_external_enrollment import BaseExternalEnrollment
from openedx_external_enrollments.models import EnrollmentRequestLog, ExternalEnrollment

LOG = logging.getLogger(__name__)


class ViperExternalEnrollment(BaseExternalEnrollment):
    """
    ViperExternalEnrollment class.
    """
    CREATE_ENROLLMENT_ACTION = 'createEnrolment'
    INVITE_LINK_KEYWORD = 'invitations'

    def __str__(self):
        return 'viper'

    def _execute_post(self, url, data=None, headers=None, json_data=None):
        """
        Execute post request.
        """
        course_shell_id = json_data.get('variables').pop('shellCourseId')
        response = requests.post(
            url=url,
            json=json_data,
            headers=headers,
        )

        if response.status_code == status.HTTP_200_OK:
            enrollment_data = json_data.get('variables')

            ExternalEnrollment.objects.update_or_create(  # pylint: disable=no-member
                controller_name=str(self),
                course_shell_id=course_shell_id,
                email=enrollment_data.get('email'),
                defaults={
                    'meta': {
                        'course_id': enrollment_data.get('courseId'),
                        'class_id': enrollment_data.get('classId'),
                        'course_url': response.json().get('link'),
                        'is_active': self.INVITE_LINK_KEYWORD not in response.json().get('link')
                    },
                }
            )

        return response

    def _get_enrollment_headers(self):
        """
        Method that returns the required header.
        """
        return {
            'x-api-key': settings.OEE_VIPER_MUTATIONS_API_KEY,
        }

    def _get_enrollment_data(self, data, course_settings):
        """
        Method that provide the relevant data for the enrollment.
        """

        return {
            'action': self.CREATE_ENROLLMENT_ACTION,
            'variables': {
                'shellCourseId': data.get('course_id'),
                'classId': course_settings.get('external_course_class_id'),
                'courseId': course_settings.get('external_course_run_id'),
                'email': data.get('user_email'),
                'name': data.get('user_name'),
                'provider': settings.OEE_VIPER_IDP,
            },
        }

    def _get_enrollment_url(self, course_settings):
        """
        Method that returns base url for the Viper integration API.
        """
        return settings.OEE_VIPER_API_URL

    def _get_course_home_url(self, course_settings, data=None):
        """
        Get course url home.
        """
        try:
            enrollment = ExternalEnrollment.objects.get(  # pylint: disable=no-member
                controller_name=str(self),
                course_shell_id=data.get('course_id'),
                email=data.get('user_email')
            )
        except ObjectDoesNotExist:
            LOG.error('Failed to retrieve enrollment for viper, Reason: Does not exist')

            return None

        if enrollment.meta.get('is_active'):
            return enrollment.meta.get('course_url')

        return self._get_course_home_url_from_enrollment(course_settings, data)

    def _get_course_home_url_from_enrollment(self, course_settings, data=None):
        """
        Retrieve the invitation/course url through an enrollment.
        This operation will happen until invitation link is replaced by the actual course enrollment target.
        """
        try:
            response = self._execute_post(
                url=settings.OEE_VIPER_API_URL,
                headers=self._get_enrollment_headers(),
                json_data=self._get_enrollment_data(data, course_settings),
            )
        except Exception as error:  # pylint: disable=broad-except
            error_msg = 'Failed to complete re-enrollment. Reason: {}'.format(str(error))

            LOG.error(error_msg)
            EnrollmentRequestLog.objects.create(  # pylint: disable=no-member
                request_type=str(self),
                details={'response': error_msg},
            )
            return None
        else:
            return response.json().get('link')
