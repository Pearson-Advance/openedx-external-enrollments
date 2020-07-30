"""GreenfigInstanceExternalEnrollment class file."""
import io
from datetime import datetime
import logging

import requests
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

    def _execute_post(self, url, headers=None, json_data=None):
        """
        Send updated list of courses to dropbox
        """
        response = requests.post(
            url=url,
            data=json_data,
            headers=headers,
        )
        return response

    def _get_enrollment_headers(self):
        """
        returns headers required to upload a file to dropbox.
        """
        return {
            'Authorization': 'Bearer {token}'.format(token=self.DROPBOX_TOKEN),
            'Content-Type': 'application/octet-stream',
            'Dropbox-API-Arg': '{\"path\":\"%s\",\"mode\":{\".tag\":\"overwrite\"}}' % self.DROPBOX_FILE_PATH
        }

    def _get_download_headers(self):
        """
        returns headers required to download a dropbox file.
        """
        return {
            'Authorization': 'Bearer {token}'.format(token=self.DROPBOX_TOKEN),
            'Dropbox-API-Arg': '{\"path\":\"%s\"}' % self.DROPBOX_FILE_PATH
        }

    def _get_enrollment_data(self, data, course_settings):
        """
        """
        user, _ = get_user(email=data.get('user_email'))
        dropbox_file = self._get_course_list(course_settings)
        dropbox_file = dropbox_file.text.split('\n')
        enrollment_search_pattern = u'{email}, {course_id}'.format(
            email=user.email,
            course_id=course_settings.get('external_course_run_id'),
        )
        enrolled = 'true'

        for enrollment in dropbox_file:
            if enrollment_search_pattern in enrollment:
                dropbox_file.remove(enrollment)
                if 'true' in enrollment:
                    enrolled = 'false'

        enrollment_data = u'{date}, {fullname}, {email}, {course_id}, {enrolled}\n'.format(
            date=datetime.now().strftime('%m-%d-%Y %H:%M:%S'),
            fullname=user.profile.name,
            email=user.email,
            course_id=course_settings.get('external_course_run_id'),
            enrolled=enrolled,
        )

        dropbox_file = '\n'.join(dropbox_file)
        dropbox_file += enrollment_data
        temp_file = io.StringIO()
        temp_file.write(dropbox_file)
        temp_file.seek(0)

        return temp_file.getvalue()

    def _get_enrollment_url(self, course_settings):
        """
        """
        return '{root_url}{path}'.format(root_url=self.DROPBOX_API_URL, path='/files/upload')

    def _get_course_list(self, course_settings):
        url = '{root_url}{path}'.format(root_url=self.DROPBOX_API_URL, path='/files/download')
        log_details = {
            'url': url,
            'course_advanced_settings': course_settings,
        }

        try:
            response = requests.post(url, headers=self._get_download_headers())
        except Exception as error:
            LOG.error('Failed to download course list. Reason: %s', str(error))
            log_details['response'] = {'error': 'Failed to download dropbox course list. Reason: ' + str(error)}
            EnrollmentRequestLog.objects.create(
                request_type=str(self),
                details=log_details,
            )

            return str(error), status.HTTP_500_INTERNAL_SERVER_ERROR
        else:
            return response
