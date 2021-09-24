"""GreenfigInstanceExternalEnrollment class file."""
import io
import logging
from datetime import datetime

import requests
from django.conf import settings
from rest_framework import status

from openedx_external_enrollments.edxapp_wrapper.get_site_configuration import configuration_helpers
from openedx_external_enrollments.edxapp_wrapper.get_student import get_user
from openedx_external_enrollments.external_enrollments.base_external_enrollment import BaseExternalEnrollment
from openedx_external_enrollments.models import EnrollmentRequestLog

LOG = logging.getLogger(__name__)


class GreenfigInstanceExternalEnrollment(BaseExternalEnrollment):
    """
    GreenfigInstanceExternalEnrollment class.
    """

    def __init__(self):
        self.DROPBOX_API_URL = configuration_helpers.get_value('DROPBOX_API_URL', 'https://content.dropboxapi.com/2')
        self.DROPBOX_FILE_PATH = configuration_helpers.get_value('DROPBOX_FILE_PATH', '/courses.txt')
        self.DROPBOX_TOKEN = configuration_helpers.get_value('DROPBOX_TOKEN', 'token')

    def __str__(self):
        return 'greenfig'

    def _execute_post(self, url, data=None, headers=None, json_data=None):
        """
        Send updated list of courses to dropbox.
        """
        return requests.post(
            url=url,
            data=json_data,
            headers=headers,
        )

    def _get_enrollment_headers(self):
        """Returns headers required to upload a file to dropbox."""
        return {
            'Authorization': 'Bearer {token}'.format(token=self.DROPBOX_TOKEN),
            'Content-Type': 'application/octet-stream',
            'Dropbox-API-Arg': settings.DROPBOX_API_ARG_UPLOAD % self.DROPBOX_FILE_PATH,
        }

    def _get_download_headers(self):
        """Returns headers required to download a dropbox file."""
        return {
            'Authorization': 'Bearer {token}'.format(token=self.DROPBOX_TOKEN),
            'Dropbox-API-Arg': settings.DROPBOX_API_ARG_DOWNLOAD % self.DROPBOX_FILE_PATH,
        }

    def _get_enrollment_data(self, data, course_settings):
        """Returns a file in memory with a new or updated enroll."""
        user, _ = get_user(email=data.get('user_email'))
        dropbox_file = self._get_course_list(course_settings).text
        enrollment_data = u'{date}, {fullname}, {first_name}, {last_name}, {email}, {course_id}, {enrolled}\n'.format(
            date=datetime.now().strftime(settings.DROPBOX_DATE_FORMAT),
            fullname=user.profile.name,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            course_id=course_settings.get('external_course_run_id'),
            enrolled=str(data.get('is_active')).lower(),
        )
        dropbox_file += enrollment_data
        temp_file = io.StringIO()
        temp_file.write(dropbox_file)
        temp_file.seek(0)

        return temp_file.getvalue()

    def _get_enrollment_url(self, course_settings):
        """Gets dropbox upload file url."""
        return '{root_url}{path}'.format(root_url=self.DROPBOX_API_URL, path=settings.DROPBOX_API_UPLOAD_URL)

    def _get_course_list(self, course_settings):
        """Gets the enrollment list."""
        url = '{root_url}{path}'.format(root_url=self.DROPBOX_API_URL, path=settings.DROPBOX_API_DOWNLOAD_URL)
        log_details = {
            'url': url,
            'course_advanced_settings': course_settings,
        }

        try:
            response = requests.post(url, headers=self._get_download_headers())
        except Exception as error:  # pylint: disable=broad-except
            LOG.error('Failed to download course list. Reason: %s', str(error))
            log_details['response'] = {'error': 'Failed to download dropbox course list. Reason: ' + str(error)}
            EnrollmentRequestLog.objects.create(  # pylint: disable=no-member
                request_type=str(self),
                details=log_details,
            )

            return str(error), status.HTTP_500_INTERNAL_SERVER_ERROR
        else:
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