"""DropboxInstanceExternalEnrollment class file."""
import io
import logging

import requests
from rest_framework import status
from django.conf import settings

from openedx_external_enrollments.edxapp_wrapper.get_site_configuration import configuration_helpers
from openedx_external_enrollments.edxapp_wrapper.get_student import get_user
from openedx_external_enrollments.external_enrollments.base_external_enrollment import BaseExternalEnrollment
from openedx_external_enrollments.models import EnrollmentRequestLog

LOG = logging.getLogger(__name__)


class DropboxInstanceExternalEnrollment(BaseExternalEnrollment):
    """
    DropboxInstanceExternalEnrollment class.
    """

    def __init__(self):
        self.DROPBOX_API_URL = configuration_helpers.get_value('DROPBOX_API_URL', 'https://content.dropboxapi.com/2')
        self.DROPBOX_FILE_PATH = configuration_helpers.get_value('DROPBOX_FILE_PATH', '/courses.txt')
        self.DROPBOX_TOKEN = configuration_helpers.get_value('DROPBOX_TOKEN', 'token')

    def __str__(self):
        return "dropbox"

    def _execute_post(self, url, headers=None, json_data=None):
        """
        """
        response = requests.post(
            url=url,
            data=json_data,
            headers=headers
        )
        return response

    def _get_enrollment_headers(self):
        """
        """
        headers = {
            "Authorization": "Bearer {token}".format(token=self.DROPBOX_TOKEN),
            "Content-Type": "application/octet-stream",
            "Dropbox-API-Arg": "{\"path\":\"%s\",\"mode\":{\".tag\":\"overwrite\"}}" % self.DROPBOX_FILE_PATH
        }

        return headers

    def _get_download_headers(self):
        """
        """
        headers = {
            "Authorization": "Bearer {token}".format(token=self.DROPBOX_TOKEN),
            "Dropbox-API-Arg": "{\"path\":\"%s\"}" % self.DROPBOX_FILE_PATH
        }

        return headers

    def _get_enrollment_data(self, data, course_settings):
        """
        """
        user, _ = get_user(email=data.get("user_email"))
        dropbox_file = self._get_course_list(course_settings)
        dropbox_file = dropbox_file.text.split('\n')
        enrollment_data = u"{first_name}, {last_name}, {email}, {course_id}\n".format(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            course_id=course_settings.get("external_course_run_id"),
        )
        enrollment_search_pattern = u"{email}, {course_id}".format(
            email=user.email,
            course_id=course_settings.get("external_course_run_id"),
        )
        enrolled = False

        for enrollment in dropbox_file:
            if enrollment_search_pattern in enrollment:
                enrolled = True
                dropbox_file.remove(enrollment)

        dropbox_file = "\n".join(dropbox_file)

        if not enrolled:
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
            "url": url,
            "course_advanced_settings": course_settings,
        }
        try:
            response = requests.post(url, headers=self._get_download_headers())
        except Exception as error:
            LOG.error("Failed to download course list. Reason: %s", str(error))
            log_details["response"] = {"error": "Failed to download dropbox course list. Reason: " + str(error)}
            EnrollmentRequestLog.objects.create(
                request_type=str(self),
                details=log_details,
            )
            return str(error), status.HTTP_400_BAD_REQUEST
        else:
            return response
