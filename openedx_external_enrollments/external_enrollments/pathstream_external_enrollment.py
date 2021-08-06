"""PathstreamExternalEnrollment class file."""
import logging
import os
from datetime import datetime

import boto3
from botocore.exceptions import ClientError
from django.conf import settings

from openedx_external_enrollments.external_enrollments.base_external_enrollment import BaseExternalEnrollment
from openedx_external_enrollments.models import ExternalEnrollment

LOG = logging.getLogger(__name__)
COMPLETED = True
UNCOMPLETED = False


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

    def _download_file(self):
        """Download the file from an S3 Bucket.

        :return: True if file was downloaded, else False"""
        if self.client is None:
            raise S3NotInitialized('_init_s3 has not been called yet.')

        try:
            self.client.download_file(
                self.S3_BUCKET,
                self.S3_FILE,
                self.S3_FILE,
            )
        except ClientError as error:
            LOG.error('Failed to download the file to S3. Reason: %s', str(error))
            return False

        LOG.info('File [%s] was downloaded from S3 for [%s]', self.S3_FILE, self.__str__())
        return True

    def _update_file(self, enrollments_data):
        """Append enrollment data to the downloaded S3 file

        :param enrollments_data: List of the enrollments data
        :return: True if file was updated, else False"""
        if os.path.exists(self.S3_FILE):
            with open(self.S3_FILE, 'a') as f:
                f.writelines(enrollments_data)
            return True
        else:
            LOG.error('File does not exist or _download_file has not been called')
            return False

    def _upload_file(self):
        """Upload the file to an S3 bucket

        :return: True if file was uploaded, else False
        """
        if self.client is None:
            raise S3NotInitialized('_init_s3 has not been called yet.')

        try:
            self.client.upload_file(
                self.S3_FILE,
                self.S3_BUCKET,
                self.S3_FILE,
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
        Context: This method will download, update and upload an S3 File with the
        corresponding data from new enrollments which have not been uploaded to the S3
        file.

        :return: True if completed, else False.

        Complete means that this method either download-update-upload the S3 file or do not
        proceed to download-update-upload the file because there are no new enrollments.
        """
        enrollments_qs = ExternalEnrollment.objects.filter(  # pylint: disable=no-member
            controller_name=str(self),
            meta__icontains='"is_uploaded":false',
        )

        if enrollments_qs:
            self._init_s3()

            if self._download_file():
                enrollments_data = [enrollment.meta['enrollment_data_formated'] for enrollment in enrollments_qs]

                if self._update_file(enrollments_data):

                    if self._upload_file():
                        for e in enrollments_qs:
                            pass
                            #e.meta.update({'is_uploaded': True})

                        ExternalEnrollment.objects.bulk_update(enrollments_qs, ['meta'])  # pylint: disable=no-member
                        self._delete_downloaded_file()
                        return COMPLETED
            return UNCOMPLETED

        LOG.info('There are no new enrollments to update the S3 file')
        return COMPLETED

    def _get_enrollment_headers(self):
        pass

    def _get_enrollment_url(self, course_settings):
        pass
