"""PathstreamExternalEnrollment class file."""
import logging

import datetime as dt
import boto3
from botocore.exceptions import ClientError


from openedx_external_enrollments.edxapp_wrapper.get_site_configuration import configuration_helpers
from openedx_external_enrollments.external_enrollments.base_external_enrollment import BaseExternalEnrollment
from openedx_external_enrollments.models import EnrollmentRequestLog

LOG = logging.getLogger(__name__)


class PathstreamExternalEnrollment():
    """
    PathstreamExternalEnrollment class.
    """

    def __init__(self):
        self.s3 = boto3.client('s3')
        self.S3_BUCKET = configuration_helpers.get_value('S3_BUCKET', 'remoteloggerpathstream')
        self.S3_FILE = configuration_helpers.get_value('S3_FILE', 'pathstream_external_enrollments.log')

    def __str__(self):
        return 'pathstream'

    def _get_enrollment_data(self, data, course_settings):
        """
        Returns data required to be treated as a log.

        arguments:
            data
            course_settings

        returns:
            string format
            Open edX Course Key, Email, Date/time, Status
        """
        time_zone = dt.timezone.utc
        date_time = dt.datetime.now(time_zone) #.strftime(%Y-%m-%d)

        enrollment_data = u'{course_key}, {email}, {date_time}, {status}\n'.format(
            course_key=course_settings.get('external_course_run_id'),
            email=data.get('user_email'),
            date_time=date_time,
            status=str(data.get('is_active')).lower(),
        )
        return enrollment_data

    def _download_file(self):
        """Download the file from an S3 Bucket"""
        self.s3.download_file(
            self.S3_BUCKET,
            self.S3_FILE,
            self.S3_FILE
        )

    def _update_file(self, data):
        """Append enrollment data to the downloaded S3 file"""
        with open(self.S3_FILE, 'a') as f:
            f.write(data+'\n')

    def _upload_file(self):
        """Upload the file to an S3 bucket

        :param file_name: File to upload
        :param bucket: Bucket to upload to
        :return: True if file was uploaded, else False
        """

        try:
            response = self.s3.upload_file(
                self.S3_FILE,
                self.S3_BUCKET,
                self.S3_FILE
            )
        except ClientError as e:
            # logging.error(e)
            return False
        return True

    def _post_enrollment(self, data, course_settings=None):

        enrollment_data = self._get_enrollment_data(data, course_settings)
        self._download_file()
        self._update_file(enrollment_data)
        self._upload_file()



