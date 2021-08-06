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
            aws_secret_access_key=secret_access_key,
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
                (module, 'INFO', log),
            )

        self.base.client.download_file.assert_called_with(
            s3_bucket,
            s3_file,
            s3_file,
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
                    'Error': {
                        'Code': code,
                        'Message': message,
                    },
                },
                operation,
            ),
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
                (module, 'ERROR', log),
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
                (module, 'INFO', log),
            )

        self.base.client.upload_file.assert_called_with(
            s3_file,
            s3_bucket,
            s3_file,
        )
        self.assertEqual(result, True)

    def test_upload_file_error(self):
        """When connection is forbidden or conection can not be
        established, the boto3.client('s3').upload_file will raise
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
                        'Message': message,
                    },
                },
                operation,
            ),
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
                (module, 'ERROR', log),
            )

        self.assertEqual(result, False)

    def test_upload_file_init_s3_not_called(self):
        """_upload_file must raise an S3NotInitialized when called without
        calling _init_s3 before."""
        self.assertRaises(
            S3NotInitialized,
            self.base._upload_file,  # pylint: disable=protected-access
        )

    def test_update_file(self):
        """_update_file should append data to the downloaded file.
        """
        s3_file = 'test.log'
        data = [
            '31,prueba@hola.com,2021-06-05 01:39:43.657639+00:00,true\n',
            '32,prueba2@hola.com,2021-06-05 01:40:43.657639+00:00,true\n',
        ]
        result = []

        open(s3_file, 'x')

        self.base._update_file(data)  # pylint: disable=protected-access

        with open(s3_file) as f:
            result = f.readlines()

        os.remove(s3_file)

        self.assertEqual(data, result)

    @patch('openedx_external_enrollments.external_enrollments.pathstream_external_enrollment.os.path.exists')
    def test_update_non_existing_file(self, mock_os_exists):
        """_update_file should log an error when it does not find the file."""
        data = []
        log = 'File does not exist or _download_file has not been called'
        mock_os_exists.return_value = False
        open_mock = mock_open()

        with LogCapture(level=logging.ERROR) as log_capture:
            with patch('builtins.open', open_mock):
                self.base._update_file(data)  # pylint: disable=protected-access

            log_capture.check(
                (module, 'ERROR', log)
            )

        open_mock.assert_not_called()

    @patch('openedx_external_enrollments.external_enrollments.pathstream_external_enrollment.os.path.exists')
    def test_update_file_append(self, mock_os_exists):
        """open must be called with the append parametes."""
        data = []
        open_operation = 'a'
        s3_file = 'test.log'
        mock_os_exists.return_value = True
        open_mock = mock_open()

        with patch('builtins.open', open_mock):
            self.base._update_file(data)  # pylint: disable=protected-access

        open_mock.assert_called_once_with(s3_file, open_operation)

        handle = open_mock()
        handle.writelines.assert_called_with(data)

    @patch('openedx_external_enrollments.external_enrollments.pathstream_external_enrollment.os.path.exists')
    @patch('openedx_external_enrollments.external_enrollments.pathstream_external_enrollment.os')
    def test_delete_existing_file(self, os_mock, mock_os_exists):
        """This test validates that _delete_downloaded_file deletes an existing file."""
        s3_file = 'test.log'
        mock_os_exists.return_value = True

        self.base._delete_downloaded_file()  # pylint: disable=protected-access

        os_mock.remove.assert_called_once_with(s3_file)

    @patch('openedx_external_enrollments.external_enrollments.pathstream_external_enrollment.os.path.exists')
    def test_delete_nonexisting_file(self, mock_os_exists):
        """_delete_downloaded_file should log an error when it does not find the file."""
        log = 'File could not be deleted, File does not exist'
        mock_os_exists.return_value = False

        with LogCapture(level=logging.ERROR) as log_capture:
            self.base._delete_downloaded_file()  # pylint: disable=protected-access

            log_capture.check(
                (module, 'ERROR', log)
            )

    @patch.object(PathstreamExternalEnrollment, '_download_file')
    @patch.object(PathstreamExternalEnrollment, '_update_file')
    @patch.object(PathstreamExternalEnrollment, '_upload_file')
    @patch(
        'openedx_external_enrollments.external_enrollments.pathstream_external_enrollment.ExternalEnrollment',
        )
    def test_successful_execute_upload_with_data(self, model_mock, upload_mock, update_mock, download_mock):
        """Testing _execute_upload with data and a successfull proccess of
        downloading, updating, uploading.

        'is_uploaded' value must change from False to True.
        """
        qs = [
            Mock(
                controller_name='pathstream',
                email='test1@gmail.com',
                meta=[
                    {
                        'is_uploaded': False,
                        'enrollment_data_formated': 'test_data_1',
                    },
                    {
                        'is_uploaded': False,
                        'enrollment_data_formated': 'test_data_2',
                    },
                ]
            ),
            Mock(
                controller_name='pathstream',
                email='test2@gmail.com',
                meta=[
                    {
                        'is_uploaded': True,
                        'enrollment_data_formated': 'test_data_3',
                    },
                    {
                        'is_uploaded': False,
                        'enrollment_data_formated': 'test_data_4',
                    },
                ]
            ),
        ]
        model_mock.objects.filter.return_value = qs
        download_mock.return_value = True
        update_mock.return_value = True
        upload_mock.return_value = True

        result = self.base.execute_upload()

        update_mock.assert_called_with(
            [
                'test_data_1',
                'test_data_2',
                'test_data_4',
            ],
        )
        model_mock.objects.bulk_update.assert_called_with(qs, ['meta'])
        self.assertEqual(qs[0].meta[0]['is_uploaded'], True)
        self.assertEqual(qs[0].meta[1]['is_uploaded'], True)
        self.assertEqual(qs[1].meta[1]['is_uploaded'], True)
        self.assertEqual(result, True)

    @patch.object(PathstreamExternalEnrollment, '_init_s3')
    @patch.object(PathstreamExternalEnrollment, '_delete_downloaded_file')
    @patch.object(PathstreamExternalEnrollment, '_download_file')
    @patch.object(PathstreamExternalEnrollment, '_update_file')
    @patch.object(PathstreamExternalEnrollment, '_upload_file')
    @patch(
        'openedx_external_enrollments.external_enrollments.pathstream_external_enrollment.ExternalEnrollment',
        )
    def test_successful_execute_upload_without_data(
            self, model_mock, upload_mock, update_mock, download_mock, delete_mock, init_s3_mock):
        """Testing _execute_upload without data, In this case the method
        must not call any other method.

        Does not have to update any ExternalEnrollment meta
        """
        model_mock.objects.filter.return_value = []
        log = 'There are no new enrollments to update the S3 file'

        with LogCapture(level=logging.INFO) as log_capture:
            result = self.base.execute_upload()

            log_capture.check(
                (module, 'INFO', log),
            )

        init_s3_mock.assert_not_called()
        download_mock.assert_not_called()
        update_mock.assert_not_called()
        upload_mock.assert_not_called()
        model_mock.objects.bulk_update.assert_not_called()
        delete_mock.assert_not_called()
        self.assertEqual(result, True)
