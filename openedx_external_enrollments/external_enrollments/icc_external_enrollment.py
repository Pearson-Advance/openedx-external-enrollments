"""EdxInstanceExternalEnrollment class file."""
import logging

import requests
from django.conf import settings

from openedx_external_enrollments.edxapp_wrapper.get_student import get_user
from openedx_external_enrollments.external_enrollments.base_external_enrollment import BaseExternalEnrollment

LOG = logging.getLogger(__name__)


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
        response = requests.post(
            url=url,
            data=json_data,
        )
        return response

    def _get_enrollment_headers(self):
        """
        """
        return {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

    def _get_enrollment_data(self, data, course_settings):
        """
        """
        icc_user = self._get_icc_user(data)
        return {
            "wstoken": settings.ICC_API_TOKEN,
            "wsfunction": settings.ICC_ENROLLMENT_API_FUNCTION,
            "enrolments[0][roleid]": "1",
            "enrolments[0][userid]": icc_user.get('id'),
            "enrolments[0][courseid]": course_settings.get("external_course_run_id"),
        }

    def _get_enrollment_url(self, course_settings):
        """
        """
        return settings.ICC_BASE_URL

    def _get_icc_user(self, data):
        try:
            response = requests.post(
                url=settings.ICC_BASE_URL,
                data={
                    "wstoken": settings.ICC_API_TOKEN,
                    "wsfunction": settings.ICC_GET_USER_API_FUNCTION,
                    "criteria[0][key]": "email",
                    "criteria[0][value]": data.get('user_email'),
                },
            )
        except Exception as error:
            LOG.error('Failed to retrieve ICC user. Reason: %s', str(error))
            log_details['response'] = {'error': 'Failed to retrieve ICC user. Reason: ' + str(error)}
            EnrollmentRequestLog.objects.create(  # pylint: disable=no-member
                request_type=str(self),
                details=log_details,
            )
            return str(error), status.HTTP_500_INTERNAL_SERVER_ERROR
        else:
            json_response = self._get_json_response(response)
            if json_response.get('data'):
                icc_user_id = json_response.get('id')
            else:
                icc_user = self._create_icc_user(data)
                icc_user_id =  icc_user.get('id')
            return icc_user_id

    def _create_icc_user(self, data):
        try:
            from pudb import set_trace
            set_trace()
            user, _ = get_user(email=data.get('user_email'))
            data = {
                "wstoken": settings.ICC_API_TOKEN,
                "wsfunction": settings.ICC_CREATE_USER_API_FUNCTION,
                "users[0][username]": user.username,
                "users[0][password]": "asdasd",
                "users[0][firstname]": "userfirstname",
                "users[0][lastname]": "userlastname",
                "users[0][email]": user.email,
            }
            response = requests.post(
                url=settings.ICC_BASE_URL,
                data=data,
            )
        except Exception as error:
            LOG.error('Failed to create ICC user. Reason: %s', str(error))
            log_details['response'] = {'error': 'Failed to create ICC user. Reason: ' + str(error)}
            EnrollmentRequestLog.objects.create(  # pylint: disable=no-member
                request_type=str(self),
                details=log_details,
            )
            return str(error), status.HTTP_500_INTERNAL_SERVER_ERROR
        else:
            user = xmltodict.parse(response.content)
            return user
