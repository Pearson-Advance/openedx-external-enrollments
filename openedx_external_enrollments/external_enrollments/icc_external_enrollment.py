"""EdxInstanceExternalEnrollment class file."""
import requests

from django.conf import settings

from openedx_external_enrollments.edxapp_wrapper.get_student import get_user
from openedx_external_enrollments.external_enrollments.base_external_enrollment import BaseExternalEnrollment


class ICCExternalEnrollment(BaseExternalEnrollment):
    """
    EdxInstanceExternalEnrollment class.
    """

    def __str__(self):
        return "ICC"

    def _execute_post(self, url, data=None, headers=None, json_data=None):
        """
        Execute overrided post request from parent.
        """
        from pudb import set_trace
        set_trace()
        response = requests.post(
            url=url,
            data=json_data,
            # headers=headers,
            # json=json_data,
        )
        return response

    def _get_enrollment_headers(self):
        """
        """
        return None

    def _get_enrollment_data(self, data, course_settings):
        """
        """
        return {
            "enrolments[0][roleid]": "1",
            "enrolments[0][userid]": "1100",
            "enrolments[0][courseid]": course_settings.get("external_course_run_id"),
            "wstoken": settings.ICC_API_TOKEN,
            "wsfunction": settings.ICC_ENROLLMENT_API_FUNCTION,
        }

    def _get_enrollment_url(self, course_settings):
        """
        """
        return settings.ICC_BASE_URL
