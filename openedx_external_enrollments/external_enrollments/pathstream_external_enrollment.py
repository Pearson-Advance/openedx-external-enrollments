"""PathstreamExternalEnrollment class file."""
import base64
import hashlib
import logging
from datetime import datetime

import boto3
import botocore
from botocore.exceptions import ClientError
from django.conf import settings
from django.db import IntegrityError

from openedx_external_enrollments.edxapp_wrapper.get_student import get_user
from openedx_external_enrollments.external_enrollments.base_external_enrollment import BaseExternalEnrollment
from openedx_external_enrollments.models import EnrollmentRequestLog, ExternalEnrollment

LOG = logging.getLogger(__name__)
COMPLETED = True
UNCOMPLETED = False


class PathstreamTaskExecutionError(Exception):
    """Exception when the proccess of executing PathstreamExternalEnrollment.execute_upload fails."""


class PathstreamExternalEnrollment(BaseExternalEnrollment):
    """
    PathstreamExternalEnrollment class.
    """
    def __str__(self):
        return 'pathstream'

    def __init__(self):
        self.client = None
        self.S3_BUCKET = settings.OEE_PATHSTREAM_S3_BUCKET
        self.S3_FILE = settings.OEE_PATHSTREAM_S3_FILE

    def _init_s3(self):
        """Define the S3 service client.

        At this point, _init_s3 does not establish any AWS connection,
        nor verify the credentials. That will happen when calling
        _download_file or _upload_file."""
        self.client = boto3.client(
            's3',
            aws_access_key_id=settings.OOE_PATHSTREAM_S3_ACCESS_KEY,
            aws_secret_access_key=settings.OOE_PATHSTREAM_S3_SECRET_KEY,
        )

    def _download_file(self):
        """Download the file content from an S3 Bucket.

        :return: file's content (bytes)"""
        try:
            response = self.client.get_object(
                Bucket=self.S3_BUCKET,
                Key=self.S3_FILE,
            )
        except ClientError as error:
            raise PathstreamTaskExecutionError(
                '_download_file',
                'Failed to download the content of the file from S3. Reason: {}'.format(str(error)),
            )

        LOG.info('File content [%s] was downloaded from S3 for [%s]', self.S3_FILE, self.__str__())

        return response['Body'].read()

    def _prepare_new_content(self, content):
        """This method returns the new content ready to be uploaded to S3. It first sorts the input list
        by date/time and then encode it since this is the way to upload the file content to S3.

        :param: content (list of strings).
            The elements of content are expected to be the following comma-separated format:
            "course,email,2021-08-05 17:53:41.492901,false"

        :return: bytes made up of the data passed in content.

        :raise: AttributeError, IndexError or ValueError in case at least one element in content has a different
        format than expected."""
        try:
            content.sort(
                #  Extract datetime out of every element in content to be the sorting parameter.
                key=lambda data: datetime.strptime(data.split(',')[6], settings.OOE_PATHSTREAM_S3_DATETIME_FORMAT),
            )
        except (AttributeError, IndexError, ValueError) as error:
            raise PathstreamTaskExecutionError(
                '_prepare_new_content',
                'An enrollment data is invalid. Reason: {} \nNew data: {}'.format(str(error), content),
            )

        # Convert elements of content to bytes.
        content = map(lambda data: data.encode(), content)

        return b''.join(content)

    def _upload_file(self, file_content=None):
        """Upload the file to an S3 bucket using MD5 to ensure that data is not corrupted
        traversing the network.

        :param: file_content (bytes)."""
        if not (isinstance(file_content, bytes) and file_content):
            raise PathstreamTaskExecutionError(
                '_upload_file', 'Can\'t upload a file with empty content or invalid content type.',
            )

        hash_algorithm_md5 = hashlib.md5(file_content).digest()
        content_encoded = base64.b64encode(hash_algorithm_md5)

        try:
            response = self.client.put_object(
                Bucket=self.S3_BUCKET,
                Key=self.S3_FILE,
                Body=file_content,
                ContentMD5=content_encoded.decode(),  # String - The base64-encoded 128-bit MD5 digest of the message.
            )
        except ClientError as error:
            raise PathstreamTaskExecutionError(
                '_upload_file',
                'Failed to upload the file to S3. Reason: {}'.format(str(error)),
            )

        LOG.info('File [%s] was uploaded to S3 for [%s], response: [%s]', self.S3_FILE, self.__str__(), response)

    def execute_upload(self):
        """
        Context: This method will download, update and upload the S3 file content with the
        corresponding data from new enrollments which have not been uploaded to the S3
        file. It also updates the key flag 'is_uploaded' which is used to determine if an enrollment is already
        uploaded to the S3 file.

        :return: tuple (boolean, str). (True, 'successful-message') if the method executes properly,
        otherwise (False, 'error-message')

        True means that this method either download-update-upload the S3 file content or do not
        proceed to download-update-upload the content because there are no new enrollments.
        """
        users_enrollments_qs = ExternalEnrollment.objects.filter(  # pylint: disable=no-member
            controller_name=str(self),
            meta__icontains='"is_uploaded":false',
        )

        if not users_enrollments_qs:
            LOG.info('There are no new enrollments to update the S3 file.')
            return COMPLETED, 'execute_upload completed'

        new_content = []

        for user_enrollments in users_enrollments_qs:
            for enrollment in user_enrollments.meta:
                if not enrollment.get('is_uploaded', True):
                    new_content.append(enrollment.get('enrollment_data_formated', ''))

                    enrollment['is_uploaded'] = True

        self._init_s3()

        if not isinstance(self.client, botocore.client.BaseClient):
            LOG.error('_init_s3 has not been called yet or failed.')
            return UNCOMPLETED, '_init_s3 has not been called yet or failed.'

        try:
            file_content = self._download_file()
            file_content += self._prepare_new_content(new_content)

            self._upload_file(file_content)
        except PathstreamTaskExecutionError as error:
            LOG.error('The proccess to update the remote S3 file has failed. Reason: %s', str(error))
            return UNCOMPLETED, str(error)

        ExternalEnrollment.objects.bulk_update(users_enrollments_qs, ['meta'])  # pylint: disable=no-member
        return COMPLETED, 'execute_upload completed'

    def _get_enrollment_data(self, data):  # pylint: disable=arguments-differ
        """
        Returns a string with the data required to be treated as a log.
        String format: 'course_key,email,username,first_name,last_name,date_time,status'
        """
        user, _ = get_user(email=data.get('user_email'))
        return (
            '{course_key},{email},{username},{fullname},'
            '{first_name},{last_name},{date_time},{status}\n'.format(
                course_key=data.get('course_id'),
                email=data.get('user_email'),
                username=user.username,
                fullname=user.profile.name,
                first_name=user.first_name,
                last_name=user.last_name,
                date_time=datetime.utcnow(),
                status=str(data.get('is_active')).lower(),
            )
        )

    def _post_enrollment(self, data, course_settings=None):
        """
        Save enrollment data in ExternalEnrollment model.
        """
        LOG.info('Calling enrollment for [%s] with data: %s', self.__str__(), data)
        LOG.info('Calling enrollment for [%s] with course settings: %s', self.__str__(), course_settings)

        log_details = {
            'data': str(data),
            'course_advanced_settings': course_settings,
        }

        try:
            enrollment, created = ExternalEnrollment.objects.get_or_create(  # pylint: disable=no-member
                controller_name=str(self),
                course_shell_id=data.get('course_id'),
                email=data.get('user_email'),
            )
        except IntegrityError:
            error_msg = 'Failed to complete enrollment, course_id and user_email can\'t be None.'
            log_details['status'] = error_msg

            LOG.error(error_msg)
            EnrollmentRequestLog.objects.create(  # pylint: disable=no-member
                request_type=str(self),
                details=log_details,
            )
        else:
            enrollment.meta = [] if created else enrollment.meta
            enrollment_data = self._get_enrollment_data(data)

            enrollment.meta.append(
                {
                    'enrollment_data_formated': enrollment_data,
                    'is_uploaded': False,
                },
            )
            enrollment.save()
            LOG.info(
                'Saving External enrollment object for [%s] -- ExternalEnrollment.id = %s -- Enrollment data = [%s]',
                self.__str__(),
                enrollment.id,
                enrollment_data,
            )

            log_details['status'] = 'success'
            log_details['payload'] = enrollment_data

            EnrollmentRequestLog.objects.create(  # pylint: disable=no-member
                request_type=str(self),
                details=log_details,
            )

    def _get_enrollment_headers(self):
        pass

    def _get_enrollment_url(self, course_settings):
        pass
