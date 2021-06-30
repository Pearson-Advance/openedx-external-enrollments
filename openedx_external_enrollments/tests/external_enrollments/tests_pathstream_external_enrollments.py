"""Tests PathstreamExternalEnrollment class file"""
import logging
import os

import boto3
from botocore.exceptions import ClientError
from django.test import TestCase
from mock import Mock, mock_open, patch
from testfixtures import LogCapture

from openedx_external_enrollments.external_enrollments.pathstream_external_enrollment import (
    PathstreamExternalEnrollment,
    S3NotInitialized,
)

module = 'openedx_external_enrollments.external_enrollments.pathstream_external_enrollment'


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

    @patch('openedx_external_enrollments.external_enrollments.pathstream_external_enrollment.datetime')
    def test_get_enrollment_data(self, datetime_mock):
        """Testing _get_enrollment_data method."""
        course_settings = {
            'external_course_run_id': '31',
        }
        data = {
            'user_email': 'javier12@gmail',
            'is_active': True,
        }
        datetime_mock.utcnow.return_value.strftime.return_value = '2021-06-28 16:40:31.456900'

        expected_data = '31,javier12@gmail,2021-06-28 16:40:31.456900,true\n'

        result = self.base._get_enrollment_data(data, course_settings)  # pylint: disable=protected-access

        self.assertEqual(
            expected_data,
            result,
        )

    @patch('openedx_external_enrollments.external_enrollments.pathstream_external_enrollment.boto3', spec=boto3)
    def test_init_s3_all_settings_setup(self, boto3_mock):
        """
        _init_s3 must be called with all parameters
        """
        access_key_id = 'access_key'
        secret_access_key = 'secret_access_key'

        self.base._init_s3()  # pylint: disable=protected-access

        boto3_mock.client.assert_called_with(
            's3',
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key
        )

    def test_download_file(self):
        """
        _download_file must return True and download a file if called with all parameters, and
        s3 connection is established.
        """
        s3_file = 'test.log'
        s3_bucket = 'test'
        self.base.client = Mock(spec=boto3.client('s3'))
        log = 'File [{}] was downloaded from S3 for [{}]'.format(s3_file, self.base.__str__())

        with LogCapture(level=logging.INFO) as log_capture:
            result = self.base._download_file()  # pylint: disable=protected-access
            log_capture.check(
                (module, 'INFO', log)
            )

        self.base.client.download_file.assert_called_with(
            s3_bucket,
            s3_file,
            s3_file
        )
        self.assertEqual(result, True)

    def test_download_file_error(self):
        """If no connection or credentials _download_file should
        handle ClientError and return False.
        """
        code = '400'
        message = 'Failed'
        operation = 'download_file'
        attrs = {
            'download_file.side_effect': ClientError(
                    {
                        'Error':
                        {
                            'Code': code,
                            'Message': message
                        }
                    },
                    operation
                    )
        }
        clienterror_msg = 'An error occurred ({}) when calling the {} operation: {}'.format(
            code,
            operation,
            message,
        )
        self.base.client = Mock(spec=boto3.client('s3'), **attrs)
        log = 'Failed to download the file to S3. Reason: {}'.format(clienterror_msg)

        with LogCapture(level=logging.ERROR) as log_capture:
            result = self.base._download_file()  # pylint: disable=protected-access
            log_capture.check(
                (module, 'ERROR', log)
            )

        self.assertEqual(result, False)

    def test_download_file_init_s3_not_called(self):
        """_download_file must raise an S3NotInitialized when called without
        calling _init_s3 before."""

        self.assertRaises(
            S3NotInitialized,
            self.base._download_file,  # pylint: disable=protected-access
        )

    def test_upload_file(self):
        """_upload file must return true if the file was uploaded"""
        s3_file = 'test.log'
        s3_bucket = 'test'

        self.base.client = Mock(spec=boto3.client('s3'))
        log = 'File [{}] was uploaded to S3 for [{}]'.format(s3_file, self.base.__str__())

        with LogCapture(level=logging.INFO) as log_capture:
            result = self.base._upload_file()  # pylint: disable=protected-access
            log_capture.check(
                (module, 'INFO', log)
            )

        self.base.client.upload_file.assert_called_with(
            s3_file,
            s3_bucket,
            s3_file
        )
        self.assertEqual(result, True)

    def test_upload_file_error(self):
        """When connection is forbidden or conection can not be
        established the boto3.client('s3').upload_file will raise
        a ClientError and _upload_file must return False.
        """
        code = '400'
        message = 'Failed'
        operation = 'upload_file'
        attrs = {
            'upload_file.side_effect': ClientError(
                {
                    'Error':
                    {
                        'Code': code,
                        'Message': message
                    }
                },
                operation
            )
        }
        clienterror_msg = 'An error occurred ({}) when calling the {} operation: {}'.format(
            code,
            operation,
            message,
        )
        self.base.client = Mock(spec=boto3.client('s3'), **attrs)
        log = 'Failed to upload the file to S3. Reason: {}'.format(clienterror_msg)

        with LogCapture(level=logging.ERROR) as log_capture:
            result = self.base._upload_file()  # pylint: disable=protected-access
            log_capture.check(
                (module, 'ERROR', log)
            )

        self.assertEqual(result, False)

    def test_upload_file_init_s3_not_called(self):
        """_upload_file must raise an S3NotInitialized when called without
        calling _init_s3 before."""

        self.assertRaises(
            S3NotInitialized,
            self.base._upload_file,  # pylint: disable=protected-access
        )

    def test_update_file_non_existing(self):
        """If the file does not exits, _update_file will log an error. """
        data = []
        log = 'File does not exist or _download_file has not been called'
        self.base._delete_downloaded_file()  # pylint: disable=protected-access

        with LogCapture(level=logging.ERROR) as log_capture:
            self.base._update_file(data)  # pylint: disable=protected-access
            log_capture.check(
                (module, 'ERROR', log)
            )

    def test_update_file(self):
        """_update_file should append data to the downloaded file.
        """
        s3_file = 'test.log'
        open(s3_file, 'x')

        data = [
            '31,prueba@hola.com,2021-06-05 01:39:43.657639+00:00,true\n',
            '32,prueba2@hola.com,2021-06-05 01:40:43.657639+00:00,true\n',
        ]

        self.base._update_file(data)  # pylint: disable=protected-access

        result = []
        with open(s3_file) as f:
            result = f.readlines()
        os.remove(s3_file)

        self.assertEqual(data, result)

    @patch('openedx_external_enrollments.external_enrollments.pathstream_external_enrollment.os.path.exists')
    def test_update_file_does_not_exist(self, mock_os_exists):
        """_update_file should log an error when it does not find the file."""
        data = []
        log = 'File does not exist or _download_file has not been called'
        mock_os_exists.return_value = False

        with LogCapture(level=logging.ERROR) as log_capture:
            self.base._update_file(data)  # pylint: disable=protected-access
            log_capture.check(
                (module, 'ERROR', log)
            )

    @patch('openedx_external_enrollments.external_enrollments.pathstream_external_enrollment.os.path.exists')
    @patch('builtins.open', new_callable=mock_open())
    def test_update_file_append(self, open_mock, mock_os_exists):
        """open must be called with the write parametes."""
        data = []
        open_operation = 'a'
        s3_file = 'test.log'
        mock_os_exists.return_value = True

        self.base._update_file(data)  # pylint: disable=protected-access

        open_mock.assert_called_once_with(s3_file, open_operation)

    @patch('openedx_external_enrollments.external_enrollments.pathstream_external_enrollment.os.path.exists')
    @patch('openedx_external_enrollments.external_enrollments.pathstream_external_enrollment.os')
    def test_delete_existing_file(self, os_mock, mock_os_exists):
        """Deletes an existing file."""
        s3_file = 'test.log'
        mock_os_exists.return_value = True

        self.base._delete_downloaded_file()  # pylint: disable=protected-access

        os_mock.remove.assert_called_once_with(s3_file)
