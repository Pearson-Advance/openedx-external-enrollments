"""ViperExternalEnrollment class file."""
import requests
from django.conf import settings
from rest_framework import status

from openedx_external_enrollments.external_enrollments.base_external_enrollment import BaseExternalEnrollment
from openedx_external_enrollments.models import ExternalEnrollment


class ViperExternalEnrollment(BaseExternalEnrollment):
    """
    ViperExternalEnrollment class.
    """
    ACTION = 'createEnrolment'

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
        enrollment_data = json_data.get('variables')

        if response.status_code == status.HTTP_200_OK:
            ExternalEnrollment.objects.update_or_create(  # pylint: disable=no-member
                controller_name=str(self),
                course_shell_id=course_shell_id,
                email=enrollment_data.get('email'),
                defaults={
                    'meta': {
                        'course_id': enrollment_data.get('courseId'),
                        'class_id': enrollment_data.get('classId'),
                        'course_url': response.json().get('link'),
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
            'action': self.ACTION,
            'variables': {
                'shellCourseId': data.get('course_id'),
                'classId': course_settings.get('external_course_class_id'),
                'courseId': course_settings.get('external_course_run_id'),
                'email': data.get('user_email'),
                'name': data.get('name'),
                'provider': settings.OEE_VIPER_IDP,
            },
        }

    def _get_enrollment_url(self, course_settings):
        """
        Method that returns base url for the Viper integration API.
        """
        return settings.OEE_VIPER_API_URL
