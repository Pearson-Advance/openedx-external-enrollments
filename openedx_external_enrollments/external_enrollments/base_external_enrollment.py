"""BaseExternalEnrollment class file."""
import logging

import requests
from rest_framework import status

from openedx_external_enrollments.models import EnrollmentRequestLog

LOG = logging.getLogger(__name__)


class BaseExternalEnrollment():
    """
    Base class for all the enrollments.
    """

    def _execute_post(self, url, data=None, headers=None, json_data=None):
        """
        Execute post request.
        """
        response = requests.post(
            url=url,
            data=data,
            headers=headers,
            json=json_data,
        )
        return response

    def _post_enrollment(self, data, course_settings=None):
        """
        Get request data and execute the post request.
        """
        url = self._get_enrollment_url(course_settings)
        json_data = self._get_enrollment_data(data, course_settings)
        LOG.info('calling enrollment for [%s] with data: %s', self.__str__(), json_data)
        LOG.info('calling enrollment for [%s] with url: %s', self.__str__(), url)
        LOG.info('calling enrollment for [%s] with course settings: %s', self.__str__(), course_settings)
        log_details = {
            'request_payload': json_data,
            'url': url,
            'course_advanced_settings': course_settings,
        }

        try:
            response = self._execute_post(
                url=url,
                headers=self._get_enrollment_headers(),
                json_data=json_data,
            )
        except Exception as error:  # pylint: disable=broad-except
            log_details['response'] = {'error': 'Failed to complete enrollment. Reason: %s' % str(error)}

            LOG.error('Failed to complete enrollment. Reason: %s', str(error))
            EnrollmentRequestLog.objects.create(  # pylint: disable=no-member
                request_type=str(self),
                details=log_details,
            )
            return str(error), status.HTTP_400_BAD_REQUEST
        else:
            json_response = self._get_json_response(response)
            log_details['response'] = json_response

            LOG.info('External enrollment response for [%s] -- %s', self.__str__(), json_response)
            EnrollmentRequestLog.objects.create(  # pylint: disable=no-member
                request_type=str(self),
                details=log_details,
            )

            return json_response, status.HTTP_200_OK

    def _get_json_response(self, response):
        """Method that returns a dict. """
        json_response = {'data': ''}

        try:
            json_response = response.json()
        except Exception:  # pylint: disable=broad-except
            pass

        return json_response

    def _get_enrollment_data(self, data, course_settings):
        """Unimplemented method necessary to execute _post_enrollment."""
        raise NotImplementedError

    def _get_enrollment_headers(self):
        """Unimplemented method necessary to execute _post_enrollment."""
        raise NotImplementedError

    def _get_enrollment_url(self, course_settings):
        """Unimplemented method necessary to execute _post_enrollment."""
        raise NotImplementedError
