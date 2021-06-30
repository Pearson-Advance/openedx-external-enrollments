"""PathstreamExternalEnrollment class file."""
import logging
import os
from datetime import datetime

import boto3
import botocore
from botocore.exceptions import ClientError
from django.conf import settings

from openedx_external_enrollments.external_enrollments.base_external_enrollment import BaseExternalEnrollment
from openedx_external_enrollments.models import PathstreamEnrollment

LOG = logging.getLogger(__name__)


class S3NotInitialized(BaseException):
    """Exception when _init_s3 has not been initialized before calling _upload_file or _download_file """


class PathstreamExternalEnrollment(BaseExternalEnrollment):
    """
    PathstreamExternalEnrollment class.
    """
    def __init__(self):
        self.client = None
        self.S3_BUCKET = settings.OEE_PATHSTREAM_S3_BUCKET
        self.S3_FILE = settings.OEE_PATHSTREAM_S3_FILE

    def __str__(self):
        return 'pathstream'

    def _init_s3(self):
        """Start S3 connection.
        """
        self.client = boto3.client(
            's3',
            aws_access_key_id=settings.OOE_PATHSTREAM_S3_ACCESS_KEY,
            aws_secret_access_key=settings.OOE_PATHSTREAM_S3_SECRET_KEY,
        )

    def _get_enrollment_data(self, data, course_settings):
        """
        Returns a dict with the data required to be treated as a log.
        """
        date_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")

        enrollment_data = u'{course_key},{email},{date_time},{status}\n'.format(
            # data.get('course_id')
            course_key=course_settings.get('external_course_run_id'),
            email=data.get('user_email'),
            date_time=date_time,
            status=str(data.get('is_active')).lower(),
        )
        return enrollment_data

    def _get_format_data(self, enrollment_data, created_datetime):
        """
        Returns the string with the enrollment data in the File Format.
        String file format: 'course_key,email,date_time,status\\n'

        Param: created_datetime (datetime)
        """
        date_time_str = created_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")
        formated_enrollment_data = u'{course_key},{email},{date_time},{status}\n'.format(
            course_key=enrollment_data.get('course_key'),
            email=enrollment_data.get('email'),
            date_time=date_time_str,
            status=enrollment_data.get('status'),
        )
        return formated_enrollment_data

    def _post_enrollment(self, data, course_settings=None):
        """
        Save enrollment data in EnrollmentRequestLog.
        """
        enrollment_data = self._get_enrollment_data(data, course_settings)
        LOG.info('calling enrollment for [%s] with data: %s', self.__str__(), data)
        LOG.info('calling enrollment for [%s] with course settings: %s', self.__str__(), course_settings)

        details = {
            'enrollment_data_formated': enrollment_data,
            'course_advanced_settings': course_settings,
        }

        enrollment = PathstreamEnrollment.objects.create(  # pylint: disable=no-member
            controller_name=str(self),
            course_shell_id=data.get('course_id'),
            email=data.get('user_email'),
            meta=details
        )

        LOG.info('Saving External enrollment object for [%s]'
                 ' -- PathstreamEnrollment.id = %s', self.__str__(), enrollment.id)

    def _download_file(self):
        """Download the file from an S3 Bucket.

        :param file_name: File to download
        :param bucket: Bucket to download from

        :return: True if file was downloaded, else False"""
        if self.client is None:
            raise S3NotInitialized

        try:

            self.client.download_file(
                self.S3_BUCKET,
                self.S3_FILE,
                self.S3_FILE
            )

        except ClientError as error:
            LOG.error('Failed to download the file to S3. Reason: %s', str(error))
            return False

        LOG.info('File [%s] was downloaded from S3 for [%s]', self.S3_FILE, self.__str__())
        return True

    def _update_file(self, enrollments_data):
        """Append enrollment data to the downloaded S3 file

        :param enrollments_data: List of the enrollments data
        """
        if os.path.exists(self.S3_FILE):

            with open(self.S3_FILE, 'a') as f:
                f.writelines(enrollments_data)
        else:
            LOG.error('File does not exist or _download_file has not been called')

    def _upload_file(self, client):
        """Upload the file to an S3 bucket

        :param file_name: File to upload
        :param bucket: Bucket to upload to

        :return: True if file was uploaded, else False
        """
        if self.client is None:
            raise S3NotInitialized

        try:
            client.upload_file(
                self.S3_FILE,
                self.S3_BUCKET,
                self.S3_FILE
            )

        except ClientError as error:
            LOG.error('Failed to upload the file to S3. Reason: %s', str(error))
            return False

        LOG.info('File [%s] was uploaded to S3 for [%s]', self.S3_FILE, self.__str__())
        return True

    def _delete_downloaded_file(self):
        """Delete the downloaded file.
        """
        if os.path.exists(self.S3_FILE):
            os.remove(self.S3_FILE)
        else:
            LOG.error('File could not be deleted, File does not exist')

    def execute_upload(self):
        """
        Context: This method will download, update and upload an S3 File.

        Warning: Must be called just once per day after midnight
        """

        enrollments_qs = PathstreamEnrollment.objects.filter(  # pylint: disable=no-member
            controller_name=str(self),
            is_uploaded=False,
        )

        if enrollments_qs.count() > 0:

            self._init_s3()

            is_file_downloaded = self._download_file()

            if is_file_downloaded:

                enrollments_data = [enrollment.meta['enrollment_data_formated'] for enrollment in enrollments_qs]

                self._update_file(enrollments_data)

                is_uploaded = self._upload_file()

                if is_uploaded:

                    enrollments_qs.update(is_uploaded=True)

                self._delete_downloaded_file()
        else:
            LOG.info('There are no new enrollments to update the S3 file')

    def _get_enrollment_headers(self):
        pass

    def _get_enrollment_url(self, course_settings):
        pass
