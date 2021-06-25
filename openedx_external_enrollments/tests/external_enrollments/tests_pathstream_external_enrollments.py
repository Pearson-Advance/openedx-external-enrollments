

from datetime import datetime
import os

import boto3
from botocore.exceptions import ClientError
from django.test import TestCase
from mock import Mock, patch, mock_open


from openedx_external_enrollments.external_enrollments.pathstream_external_enrollment import (
    PathstreamExternalEnrollment,
    S3NotInitialized,
)
from openedx_external_enrollments.models import EnrollmentRequestLog


class PathstreamExternalEnrollmentTest(TestCase):
    """Test class for PathstreamExternalEnrollment."""

    def setUp(self):
        """Set test database."""
        self.base = PathstreamExternalEnrollment()

    def test_str(self):
        """
        PathstreamExternalEnrollment overrides the __str__ method,
        this test that the method __str__ returns the right value.
        """
        self.assertEqual(
            'pathstream',
            self.base.__str__(),
        )

    def test_get_enrollment_data(self):
        """Testing _get_enrollment_data method."""
        course_settings = {
            'external_course_run_id': '31',
        }
        data = {
            'user_email': 'javier12@gmail',
            'is_active': True,
        }
        expected_data = {
            'course_key':'31',
            'email':'javier12@gmail',
            'status':'true',
        }

        result = self.base._get_enrollment_data(data, course_settings)  # pylint: disable=protected-access

        self.assertEqual(
            expected_data,
            result,
        )

    def test_get_format_data(self):

        enrollment_data = {
            'course_key':'31',
            'email':'javier12@gmail.com',
            'status':'true',
        }
        created_datetime = datetime(year=2021, month=10, day=12, hour=13, minute=10, second=2)

        expected_result = '31,javier12@gmail.com,2021-10-12 13:10:02.000000,true\n'
        result = self.base._get_format_data(enrollment_data, created_datetime)

        self.assertEqual(expected_result, result)


    @patch('openedx_external_enrollments.external_enrollments.pathstream_external_enrollment.boto3', spec=boto3)
    def test_init_s3_all_settings_setup(self, boto3_mock):
        """
        _init_s3 must be called with all parameters
        """
        s3_file = 'test.log'
        s3_bucket = 'test'

        self.base._init_s3()

        boto3_mock.client.assert_called_with(
            's3',
            aws_access_key_id='access_key',
            aws_secret_access_key='secret_access_key'
        )
        self.assertEqual(self.base.S3_FILE, s3_file)
        self.assertEqual(self.base.S3_BUCKET, s3_bucket)

    # def test_download_file_before_calling_init_s3(self):
    #     self.assertRaises(S3NotInitialized, self.base._download_file())

    def test_download_file(self):
        """
        _download_file must be called with all parameters
        """
        s3_file = 'test.log'
        s3_bucket = 'test'

        client_mock = Mock(spec=boto3.client('s3'))
        self.base._download_file(client_mock)

        client_mock.download_file.assert_called_with(
            s3_bucket,
            s3_file,
            s3_file
        )

    def test_upload_file(self):
        s3_file = 'test.log'
        s3_bucket = 'test'

        client_mock = Mock(spec=boto3.client('s3'))
        self.base._upload_file(client_mock)

        client_mock.upload_file.assert_called_with(
            s3_file,
            s3_bucket,
            s3_file
        )

    @patch('builtins.open', new_callable=mock_open())
    def test_update_file(self, mock_open):

        s3_file = 'test.log'

        data = [
            '31,prueba@hola.com,2021-06-05 01:39:43.657639+00:00,true\n',
            '32,prueba2@hola.com,2021-06-05 01:40:43.657639+00:00,true\n',
        ]

        self.base._update_file(data)

        # print(mock_open.mock_calls)
        # print(mock_open.return_value)
        # handle = mock_open()
        # self.assertEqual(open(s3_file).read(), data)
        # handle.writelines.assert_called_once_with(data)
        mock_open.assert_called_once_with(s3_file, 'a')

    @patch('openedx_external_enrollments.external_enrollments.pathstream_external_enrollment.os', spec=os)
    def test_delete_nonexisting_file(self, os_mock):

        s3_file = 'test.log'

        self.base._delete_downloaded_file()

        os_mock.remove.assert_called_once_with(s3_file)


