"""EdxInstanceExternalEnrollment class file."""
import json
import logging
from uuid import uuid4

import requests
from django.conf import settings
from rest_framework import status
import xmltodict

from openedx_external_enrollments.external_enrollments.base_external_enrollment import BaseExternalEnrollment
from openedx_external_enrollments.edxapp_wrapper.get_student import get_user
from openedx_external_enrollments.models import EnrollmentRequestLog

LOG = logging.getLogger(__name__)


class ICCExternalEnrollment(BaseExternalEnrollment):
    """
    EdxInstanceExternalEnrollment class.
    """

    def __str__(self):
        return "ICC"

    def _execute_post(self, url, data=None, headers=None, json_data=None):
        """
        Execute post request from parent.
        """
        response = requests.post(
            url=url,
            data=json_data,
        )

        return response

    def _get_enrollment_headers(self):
        """
        Method that returns None by default, ICC integration does not headers.
        """
        return None

    def _get_enrollment_data(self, data, course_settings):
        """Method that provide the relevant data for the enrollment."""
        icc_user = self._get_icc_user(data)

        return {
            "wstoken": settings.ICC_API_TOKEN,
            "wsfunction": settings.ICC_ENROLLMENT_API_FUNCTION,
            "enrolments[0][roleid]": settings.ICC_LEARNER_ROLE_ID,
            "enrolments[0][userid]": icc_user.get('id'),
            "enrolments[0][courseid]": course_settings.get("external_course_run_id"),
        }

    def _get_enrollment_url(self, course_settings):
        """
        method that returns base url for the ICC integration API
        """

        return settings.ICC_BASE_URL

    def _get_icc_user(self, data):
        """
        Method that look for the user in ICC database through the API, if the user is not
        found then it calls create method.
        """
        log_details = {
            "url": settings.ICC_API_TOKEN,
        }

        try:
            _data = {
                "wstoken": settings.ICC_API_TOKEN,
                "wsfunction": settings.ICC_GET_USER_API_FUNCTION,
                "criteria[0][key]": "email",
                "criteria[0][value]": data.get('user_email'),
            }

            response = requests.post(
                url=settings.ICC_BASE_URL,
                data=_data,
            )
            _data['wstoken'] = 'icc-api-token'
            log_details['request_payload'] = _data

        except Exception as error:
            LOG.error('Failed to retrieve ICC user. Reason: %s', str(error))
            log_details['response'] = {'error': 'Failed to retrieve ICC user. Reason: ' + str(error)}
            EnrollmentRequestLog.objects.create(  # pylint: disable=no-member
                request_type=str(self),
                details=log_details,
            )

            return str(error), status.HTTP_500_INTERNAL_SERVER_ERROR
        else:
            icc_user = self._get_icc_user_from_xml_response(response, 'get_user')
            if not icc_user:
                icc_user = self._create_icc_user(data)

            return icc_user

    def _create_icc_user(self, data):
        """
        Method that creates a user in the ICC database taking care to send the data
        from the current user logged in.
        """
        log_details = {
            "url": settings.ICC_CREATE_USER_API_FUNCTION,
        }
        try:
            user, _ = get_user(email=data.get('user_email'))
            _data = {
                "wstoken": settings.ICC_API_TOKEN,
                "wsfunction": settings.ICC_CREATE_USER_API_FUNCTION,
                "users[0][username]": user.username,
                "users[0][password]": self._get_random_string(),
                "users[0][firstname]": user.first_name,
                "users[0][lastname]": user.last_name,
                "users[0][email]": user.email,
                "users[0][auth]": "saml2",
            }

            response = requests.post(
                url=settings.ICC_BASE_URL,
                data=_data,
            )
            _data['wstoken'] = 'icc-api-token'
            log_details['request_payload'] = _data

        except Exception as error:
            LOG.error('Failed to create ICC user. Reason: %s', str(error))
            log_details['response'] = {'error': 'Failed to create ICC user. Reason: ' + str(error)}
            EnrollmentRequestLog.objects.create(  # pylint: disable=no-member
                request_type=str(self),
                details=log_details,
            )

            return str(error), status.HTTP_500_INTERNAL_SERVER_ERROR
        else:
            icc_user = self._get_icc_user_from_xml_response(response, 'create_user')

            return icc_user

    def _get_icc_user_from_xml_response(self, response, method_type):
        """
        Method that receives a xml response and convert it to json object and returns it.
        """
        icc_user = {}
        try:
            str_response = xmltodict.parse(response.content)
            json_str_response = json.dumps(str_response)
            json_obj_response = json.loads(json_str_response)

            if method_type == 'create_user':
                fields = json_obj_response['RESPONSE']['MULTIPLE']['SINGLE']['KEY']
            else:
                fields = json_obj_response['RESPONSE']['SINGLE']['KEY'][0]['MULTIPLE']['SINGLE']['KEY']

            for field in fields:
                if field['@name'] == 'id':
                    icc_user['id'] = field['VALUE']
                if field['@name'] == 'username':
                    icc_user['username'] = field['VALUE']
                    break

        except Exception:
            pass

        finally:
            return icc_user

    def _get_random_string(self):
        """
        Method that generates and return a random string
        """

        return uuid4().hex[:settings.ICC_HASH_LENGTH]
