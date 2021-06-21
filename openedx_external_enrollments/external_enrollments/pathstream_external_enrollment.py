"""PathstreamExternalEnrollment class file."""
import datetime as dt
import logging
from random import randint
import os

import boto3
from botocore.exceptions import ClientError
from django.utils.timezone import make_aware

from openedx_external_enrollments.edxapp_wrapper.get_site_configuration import configuration_helpers
from openedx_external_enrollments.external_enrollments.base_external_enrollment import BaseExternalEnrollment
from openedx_external_enrollments.models import EnrollmentRequestLog

LOG = logging.getLogger(__name__)


class S3NotInitialized(Exception):
    """Exception when _init_s3 has not been initialized before calling _upload_file or _download_file """

# pendings
# error if not called init_s3 first
# AttributeError: 'PathstreamExternalEnrollment' object has no attribute 'client'
## How to check if this fuction was already called if _update
# keyerror if no enrollment.details['enrollment_data']
class PathstreamExternalEnrollment(BaseExternalEnrollment):
    """
    PathstreamExternalEnrollment class.
    """
    def __str__(self):
        return 'pathstream'

    def __init__(self):
        self.TIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

    def _init_s3(self):
        """Start S3 connection and retrieve the names for both bucket and file.
        """
        self.client = boto3.client(
            's3',
            aws_access_key_id=configuration_helpers.get_value('ACCESS_KEY', 'AKIA2DFCAATKKPOO2EAS'),
            aws_secret_access_key=configuration_helpers.get_value('SECRET_KEY', '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'),
        )
        self.S3_BUCKET = configuration_helpers.get_value('S3_BUCKET', 'remoteloggerpathstream')
        self.S3_FILE = configuration_helpers.get_value('S3_FILE', 'pathstream_external_enrollments.log')

    def _get_enrollment_data(self, data, course_settings):
        """
        Returns a string with the data required to be treated as a log.
        String format: 'course_key,email,date_time,status'
        """
        time_zone = dt.timezone.utc
        date_time = dt.datetime.now(time_zone).strftime(self.TIME_FORMAT)

        enrollment_data = u'{course_key},{email},{date_time},{status}\n'.format(
            course_key=course_settings.get('external_course_run_id'),
            email=data.get('user_email'),
            date_time=date_time,
            status=str(data.get('is_active')).lower(),
        )
        return enrollment_data

    def _post_enrollment(self, data, course_settings=None):
        """
        Save enrollment data in EnrollmentRequestLog.
        """
        enrollment_data = self._get_enrollment_data(data, course_settings)
        LOG.info('calling enrollment for [%s] with data: %s', self.__str__(), enrollment_data)
        LOG.info('calling enrollment for [%s] with course settings: %s', self.__str__(), course_settings)

        log_details = {
            'enrollment_data': enrollment_data,
            'course_advanced_settings': course_settings,
        }

        enrollment = EnrollmentRequestLog()
        enrollment.request_type = str(self)
        enrollment.details = log_details
        enrollment.save()

        LOG.info('Saving External enrollment object for [%s] -- EnrollmentRequestLog.id = %s', self.__str__(), enrollment.id)

    def _download_file(self):
        """Download the file from an S3 Bucket"""
        try:
            self.client.download_file(
                self.S3_BUCKET,
                self.S3_FILE,
                self.S3_FILE
            )
        except AttributeError:
            raise S3NotInitialized

    def _get_last_enrollment_datetime(self):
        """Returns the last EnrollmentRequestLog object's datetime stored in the S3 file.
        __download_file must be called first.

        Returns:
            - False if file is empty
            - DateTime if file has at leats one line with the format (Open edX Course Key, Email, Date/time, Status)
        """
        last_dt = int()
        last_line = '\n'
        try:

            with open(self.S3_FILE, 'r') as f:
                last_line = f.readlines()[-1]

            if last_line == '\n':
                LOG.info('Empty S3 file, new file')
                # Heads up, if just the end of the file is a emty line
                #it could be a potential risk to override everything
                return False
            else:
                last_dt_str = last_line.split(',')[2]
                last_dt = dt.datetime.strptime(last_dt_str, self.TIME_FORMAT)

                last_dt = make_aware(last_dt)
                return last_dt

        except FileNotFoundError as error:
            LOG.error('File was not downloaded or _download_file was not called first.')
        except IndexError as error:
            LOG.error('No está en el formato %s',last_line)

    def _update_file(self, enrollments_data):
        """Append enrollment data to the downloaded S3 file

        :param enrollments_data: List of the enrollments data
        """
        try:

            with open(self.S3_FILE, 'a') as f:
                f.writelines(enrollments_data)

        except FileNotFoundError as error:
            LOG.error('File was not downloaded or _download_file was not called.')

    def _upload_file(self):
        """Upload the file to an S3 bucket

        :param file_name: File to upload
        :param bucket: Bucket to upload to
        """

        try:
            self.client.upload_file(
                self.S3_FILE,
                self.S3_BUCKET,
                self.S3_FILE
            )
        except AttributeError:
            raise S3NotInitialized

        except ClientError as error:
            LOG.error('Failed to upload the file to S3. Reason: %s', str(error))

        LOG.info('File [%s] was uploaded to S3 for [%s]', self.S3_FILE, self.__str__())

    def _delete_downloaded_file(self):
        """Delete the downloaded file.
        """
        try:
            os.remove(self.S3_FILE)
        except FileNotFoundError:
            LOG.error('File was not downloaded or _download_file was not called.')

    def _execute_upload(self):
        """
        Context: This method will download, update and upload an S3 File.

        Warning: Must be called just once per day after midnight
        """

        self._init_s3()

        self._download_file()

        last_datetime = self._get_last_enrollment_datetime()

        if last_datetime:
            enrollments_qs = EnrollmentRequestLog.objects.filter(request_type=str(self), created_at__gt=last_datetime)
        else:
            enrollments_qs = EnrollmentRequestLog.objects.filter(request_type=str(self))

        if enrollments_qs.count() > 0:

            enrollments_data = [enrollment.details['enrollment_data'] for enrollment in enrollments_qs]

            self._update_file(enrollments_data)

            self._upload_file()
        else:
            LOG.info('There are no new enrollments to update the S3 file')

        self._delete_downloaded_file()