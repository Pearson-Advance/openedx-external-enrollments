"""MITHzInstanceExternalEnrollment class file."""
import logging
from urllib.parse import quote_plus

import requests
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status

from openedx_external_enrollments.edxapp_wrapper.get_site_configuration import configuration_helpers
from openedx_external_enrollments.external_enrollments.base_external_enrollment import BaseExternalEnrollment
from openedx_external_enrollments.models import EnrollmentRequestLog, ExternalEnrollment

LOG = logging.getLogger(__name__)


class MITHzInstanceExternalEnrollment(BaseExternalEnrollment):
    """
    MITHzInstanceExternalEnrollment class.
    """

    def __init__(self):
        self.MIT_HZ_PROVIDER = configuration_helpers.get_value(
            'MIT_HZ_PROVIDER',
            'samlp',
        )
        self.MIT_HZ_ORG = configuration_helpers.get_value(
            'MIT_HZ_ORG',
            'Pearson',
        )

    def __str__(self):
        return 'mit_hz'

    def _execute_post(self, url, data=None, headers=None, json_data=None):
        """
        Execute post request which is in charge to refresh the user subscription,
        in case the user does not exist, it will return 404 but the enrollment/subscription
        should be saved whether it is ok or not in order to track all enrollments.
        """
        user_subscription = {}
        response = super()._execute_post(url, data, headers, json_data)

        # If the response is ok then it means the user exists, and the subscription expiration date
        # should be updated to the corresponding MIT HZ courses.
        if response.ok:
            user_subscription = response.json().get('user', {})

            ExternalEnrollment.objects.filter(  # pylint: disable=no-member
                controller_name=str(self),
                email=json_data.get('user_email'),
            ).update(meta=user_subscription)

        ExternalEnrollment.objects.update_or_create(  # pylint: disable=no-member
            controller_name=str(self),
            course_shell_id=json_data.get('course_id'),
            email=json_data.get('user_email'),
            defaults={'meta': user_subscription},
        )

        return response

    def _get_bearer_token(self):
        """
        Returns a bearer token required for the Authorization header.
        """
        url = '{root_url}{path}'.format(
            root_url=settings.MIT_HZ_API_URL,
            path=settings.MIT_HZ_LOGIN_PATH,
        )
        data = {
            'id': settings.MIT_HZ_ID,
            'secret': settings.MIT_HZ_SECRET,
        }
        log_details = {
            'url': url,
        }

        try:
            response = requests.post(
                url=url,
                json=data,
            )
        except Exception as error:  # pylint: disable=broad-except
            msg_error = 'Failed to authenticate at MIT HZ API. Reason: %s' % str(error)
            log_details['response'] = {'error': msg_error}
            LOG.error(msg_error)
            EnrollmentRequestLog.objects.create(  # pylint: disable=no-member
                request_type=str(self),
                details=log_details,
            )
        else:
            if not response.ok:
                log_details['response'] = response.text
                EnrollmentRequestLog.objects.create(  # pylint: disable=no-member
                    request_type=str(self),
                    details=log_details,
                )
                LOG.error('failed when trying to authenticate with MIT HORIZON')
                return 'missing token'

            return response.json()['access_token']
        return 'missing token'

    def _get_enrollment_headers(self):
        """
        Formats headers for MIT_HZ API.
        """
        return {
            'Authorization': 'Bearer {token}'.format(token=self._get_bearer_token()),
            'Content-Type': 'application/json',
        }

    def _check_user(self, user_id):
        """
        Check if user exists in MIT HORIZON.
        """
        headers = self._get_enrollment_headers()
        url = '{root_url}{get_user_path}{user_id}'.format(
            root_url=settings.MIT_HZ_API_URL,
            get_user_path=settings.MIT_HZ_GET_USER_PATH,
            user_id=user_id,
        )
        log_details = {
            'url': url,
            'user': user_id,
        }

        try:
            response = requests.get(url, headers=headers)
        except Exception as error:  # pylint: disable=broad-except
            LOG.error('Failed to get user at MIT HZ API.')
            log_details['response'] = {'error': 'Failed to get user at MIT HZ API. Reason: %s' % str(error)}
            EnrollmentRequestLog.objects.create(  # pylint: disable=no-member
                request_type=str(self),
                details=log_details,
            )
            return str(error), status.HTTP_500_INTERNAL_SERVER_ERROR
        else:
            if not response.ok:
                log_details['response'] = response.text
                LOG.error('User not found at MIT HZ API.')
                EnrollmentRequestLog.objects.create(  # pylint: disable=no-member
                    request_type=str(self),
                    details=log_details,
                )
                return {}

            json_response = response.json()
            log_details['response'] = json_response
            log_details['message'] = 'User found'
            EnrollmentRequestLog.objects.create(  # pylint: disable=no-member
                request_type=str(self),
                details=log_details,
            )

            return json_response

    def _get_enrollment_data(self, data, course_settings):
        """
        Returns the data required to refresh a user in the MIT HORIZON API.
        """
        enrollment_data = {
            'user_email': data.get('user_email'),
            'course_id': str(data.get('course_id')),
        }
        user_id = self._get_user_id(data.get('user_email'))
        if self._check_user(user_id):
            enrollment_data.update({'user_id': user_id})

        return enrollment_data

    def _get_enrollment_url(self, course_settings):
        """Format the url to refresh a user."""
        return '{root_url}{path}'.format(
            root_url=settings.MIT_HZ_API_URL,
            path=settings.MIT_HZ_REFRESH_PATH,
        )

    def _get_user_id(self, email):
        """formats a valid user for the MIT HORIZON API."""
        user_id = '{provider}|{org}|{email}'.format(
            provider=self.MIT_HZ_PROVIDER,
            org=self.MIT_HZ_ORG,
            email=email,
        )

        return quote_plus(user_id)

    def _get_course_home_url(self, course_settings, data=None):
        """Check the user subscription and return the course home URL."""
        self._check_user_subscription(data)

        return course_settings.get('external_course_target')

    def _check_user_subscription(self, data):
        """Method to verify and update the user subscription data."""
        try:
            enrollment = ExternalEnrollment.objects.get(  # pylint: disable=no-member
                controller_name=str(self),
                course_shell=data.get('course_id'),
                email=data.get('user_email'),
                meta={},
            )
        except ObjectDoesNotExist:
            return

        enrollment.meta = self._check_user(self._get_user_id(data.get('user_email')))
        enrollment.save()
