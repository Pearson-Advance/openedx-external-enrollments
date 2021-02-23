"""ICCExternalEnrollment class file."""
import logging
from uuid import uuid4

import requests
import xmltodict
from django.conf import settings

from openedx_external_enrollments.edxapp_wrapper.get_site_configuration import configuration_helpers
from openedx_external_enrollments.edxapp_wrapper.get_student import get_user
from openedx_external_enrollments.external_enrollments.base_external_enrollment import BaseExternalEnrollment
from openedx_external_enrollments.models import EnrollmentRequestLog

LOG = logging.getLogger(__name__)


class ICCExternalEnrollment(BaseExternalEnrollment):
    """
    ICCExternalEnrollment class.
    """
    USER_CREATION_MAX_RETRIES = 5
    USERNAME_SUFFIX_LENGTH = 5

    def __str__(self):
        return 'ICC'

    def _execute_post(self, url, data=None, headers=None, json_data=None):
        """
        Execute post request to achieve the ICC external enrollment.
        """
        return requests.post(
            url=url,
            data=json_data,
        )

    def _get_enrollment_headers(self):
        """
        Method that returns None by default, ICC integration does not require headers.
        """
        return

    def _get_enrollment_data(self, data, course_settings):
        """
        Method that provide the relevant data for the enrollment.
        """
        log_details = {
            'url': settings.ICC_CREATE_USER_API_FUNCTION,
        }
        enrollment_data = {}

        try:
            enrollment_data = {
                'wstoken': settings.ICC_API_TOKEN,
                'wsfunction': settings.ICC_ENROLLMENT_API_FUNCTION,
                'enrolments[0][roleid]': settings.ICC_LEARNER_ROLE_ID,
                'enrolments[0][userid]': self._get_icc_user(data).get('id'),
                'enrolments[0][courseid]': course_settings.get('external_course_run_id'),
            }
        except Exception as error:  # pylint: disable=broad-except
            log_details['response'] = {'error': 'Failed to retrieve ICC enrollment data. Reason: %s' % str(error)}

            LOG.error('Failed to retrieve ICC enrollment data. Reason: %s', str(error))
            EnrollmentRequestLog.objects.create(  # pylint: disable=no-member
                request_type=str(self),
                details=log_details,
            )

        return enrollment_data

    def _get_enrollment_url(self, course_settings):
        """
        Method that returns base url for the ICC integration API.
        """
        return settings.ICC_BASE_URL

    def _get_icc_user(self, data):
        """
        Method that look for the user in ICC database through the API, if the user is not
        found then it calls create method.
        """
        log_details = {
            'url': settings.ICC_API_TOKEN,
        }
        icc_user = {}

        try:
            request_data = {
                'wstoken': settings.ICC_API_TOKEN,
                'wsfunction': settings.ICC_GET_USER_API_FUNCTION,
                'criteria[0][key]': 'email',
                'criteria[0][value]': data.get('user_email'),
            }
            response = requests.post(
                url=settings.ICC_BASE_URL,
                data=request_data,
            )
            log_details['request_payload'] = request_data
        except Exception as error:  # pylint: disable=broad-except
            log_details['request_payload']['wstoken'] = 'icc-api-token'
            log_details['response'] = {'error': 'Failed to retrieve ICC user. Reason: %s' % str(error)}

            LOG.error('Failed to retrieve ICC user. Reason: %s', str(error))
            EnrollmentRequestLog.objects.create(  # pylint: disable=no-member
                request_type=str(self),
                details=log_details,
            )
        else:
            icc_user = self._get_icc_user_from_xml_response(response, 'get_user')
            icc_user = self._validate_icc_user(data, icc_user)

        return icc_user

    def _create_icc_user(self, data, duplicated_username):
        """
        Method that creates a user in the ICC database based in the current user logged in data.
        Also takes care of duplicated usernames.
        """
        log_details = {
            'url': settings.ICC_CREATE_USER_API_FUNCTION,
        }
        icc_user = {}

        try:
            user, _ = get_user(email=data.get('user_email'))
            request_data = {
                'wstoken': settings.ICC_API_TOKEN,
                'wsfunction': settings.ICC_CREATE_USER_API_FUNCTION,
                'users[0][username]': user.username + self._get_random_string(
                    self.USERNAME_SUFFIX_LENGTH) if duplicated_username else user.username,
                'users[0][password]': self._get_random_string(settings.ICC_HASH_LENGTH),
                'users[0][firstname]': user.first_name,
                'users[0][lastname]': user.last_name,
                'users[0][email]': user.email,
                'users[0][auth]': 'saml2',
            }

            response = requests.post(
                url=settings.ICC_BASE_URL,
                data=request_data,
            )
            log_details['request_payload'] = request_data
        except Exception as error:  # pylint: disable=broad-except
            log_details['request_payload']['wstoken'] = 'icc-api-token'
            log_details['response'] = {'error': 'Failed to create ICC user. Reason: %s' % str(error)}

            LOG.error('Failed to create ICC user. Reason: %s', str(error))
            EnrollmentRequestLog.objects.create(  # pylint: disable=no-member
                request_type=str(self),
                details=log_details,
            )
        else:
            icc_user = self._get_icc_user_from_xml_response(response, 'create_user')

        return icc_user

    def _validate_icc_user(self, data, icc_user):
        """
        Ensure the user creation avoiding failure for username duplicates.
        """
        duplicated_username = False
        call_counter = 0

        while not icc_user and call_counter <= self.USER_CREATION_MAX_RETRIES:
            icc_user = self._create_icc_user(data, duplicated_username)
            duplicated_username = True
            call_counter += 1

        return icc_user

    def _get_icc_user_from_xml_response(self, response, method_type):
        """
        Method that receives a xml response and convert it to json object and returns it.
        """
        icc_user = {}
        OBJECT_POSITION = 0

        try:
            response = xmltodict.parse(response.content)
            fields = (response['RESPONSE']['MULTIPLE']['SINGLE']['KEY'] if method_type == 'create_user' else
                      response['RESPONSE']['SINGLE']['KEY'][OBJECT_POSITION]['MULTIPLE']['SINGLE']['KEY'])

            for field in fields:
                if field.get('@name') == 'id':
                    icc_user['id'] = field.get('VALUE')
                if field.get('@name') == 'username':
                    icc_user['username'] = field.get('VALUE')
                    break
        except Exception:  # pylint: disable=broad-except
            pass

        return icc_user

    def _get_random_string(self, length):
        """
        Method that generates and return a random string.
        """
        random_string = (
            uuid4().hex[:length] if length == self.USERNAME_SUFFIX_LENGTH else
            configuration_helpers.get_value('DEFAULT_USER_TESTING_PASSWORD')
        )

        return uuid4().hex[:length] if not random_string else random_string
