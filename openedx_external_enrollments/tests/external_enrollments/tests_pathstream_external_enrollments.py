"""Tests PathstreamExternalEnrollment class file"""
import logging
import os

import boto3
import ddt
from botocore.exceptions import ClientError
from django.db.utils import IntegrityError
from django.test import TestCase
from mock import Mock, mock_open, patch
from opaque_keys.edx.keys import CourseKey
from testfixtures import LogCapture

from openedx_external_enrollments.external_enrollments.pathstream_external_enrollment import (
    ExecutionError,
    PathstreamExternalEnrollment,
    S3NotInitialized,
)


@ddt.ddt
class PathstreamExternalEnrollmentTest(TestCase):
    """Test class for PathstreamExternalEnrollment."""

    def setUp(self):
        """Set test instance."""
        self.base = PathstreamExternalEnrollment()
        self.module = 'openedx_external_enrollments.external_enrollments.pathstream_external_enrollment'
        self.course_id = CourseKey.from_string('course-v1:test+CS102+2019_T3')
        self.user_email = 'test@email'

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
        _download_file must download a file if called with all parameters, and
        s3 connection is established.
        """
        s3_file = 'test.log'
        s3_bucket = 'test'
        self.base.client = Mock(spec=boto3.client('s3'))
        log = 'File [{}] was downloaded from S3 for [{}]'.format(s3_file, self.base.__str__())

        with LogCapture(level=logging.INFO) as log_capture:
            self.base._download_file()  # pylint: disable=protected-access

            log_capture.check(
                (self.module, 'INFO', log),
            )

        self.base.client.download_file.assert_called_with(
            s3_bucket,
            s3_file,
            s3_file,
        )

    def test_download_file_error(self):
        """If no connection or credentials _download_file should
        handle ClientError and raise ExecutionError.
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
            with self.assertRaises(ExecutionError):
                self.base._download_file()  # pylint: disable=protected-access

            log_capture.check(
                (self.module, 'ERROR', log),
            )

    def test_download_file_init_s3_not_called(self):
        """_download_file must raise an S3NotInitialized when called without
        calling _init_s3 before."""
        self.assertRaises(
            S3NotInitialized,
            self.base._download_file,  # pylint: disable=protected-access
        )

    def test_upload_file(self):
        """This test validates that _upload file calls the method to update
        the S3 file with the right parameters."""
        s3_file = 'test.log'
        s3_bucket = 'test'
        self.base.client = Mock(spec=boto3.client('s3'))
        log = 'File [{}] was uploaded to S3 for [{}]'.format(s3_file, self.base.__str__())

        with LogCapture(level=logging.INFO) as log_capture:
            self.base._upload_file()  # pylint: disable=protected-access

            log_capture.check(
                (self.module, 'INFO', log),
            )

        self.base.client.upload_file.assert_called_with(
            s3_file,
            s3_bucket,
            s3_file,
        )

    def test_upload_file_error(self):
        """When connection is forbidden or conection can not be
        established, the boto3.client('s3').upload_file will raise
        a ClientError and _upload_file must also raise ExecutionError.
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
            with self.assertRaises(ExecutionError):
                self.base._upload_file()  # pylint: disable=protected-access

            log_capture.check(
                (self.module, 'ERROR', log),
            )

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
                with self.assertRaises(ExecutionError):
                    self.base._update_file(data)  # pylint: disable=protected-access

            log_capture.check(
                (self.module, 'ERROR', log)
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
            with self.assertRaises(ExecutionError):
                self.base._delete_downloaded_file()  # pylint: disable=protected-access

            log_capture.check(
                (self.module, 'ERROR', log)
            )

    @patch.object(PathstreamExternalEnrollment, '_init_s3')
    @patch.object(PathstreamExternalEnrollment, '_delete_downloaded_file')
    @patch.object(PathstreamExternalEnrollment, '_download_file')
    @patch.object(PathstreamExternalEnrollment, '_update_file')
    @patch.object(PathstreamExternalEnrollment, '_upload_file')
    @patch(
        'openedx_external_enrollments.external_enrollments.pathstream_external_enrollment.ExternalEnrollment',
        )
    def test_successful_execute_upload_with_data(
            self, model_mock, upload_mock, update_mock, download_mock, delete_mock, init_s3_mock):
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

        result = self.base.execute_upload()

        init_s3_mock.assert_called_once()
        download_mock.assert_called_once()
        update_mock.assert_called_with(
            [
                'test_data_1',
                'test_data_2',
                'test_data_4',
            ],
        )
        upload_mock.assert_called_once()
        model_mock.objects.bulk_update.assert_called_with(qs, ['meta'])
        delete_mock.assert_called_once()
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
                (self.module, 'INFO', log),
            )

        init_s3_mock.assert_not_called()
        download_mock.assert_not_called()
        update_mock.assert_not_called()
        upload_mock.assert_not_called()
        model_mock.objects.bulk_update.assert_not_called()
        delete_mock.assert_not_called()
        self.assertEqual(result, True)
        self.assertEqual(self.base.__str__(), 'pathstream')

    @patch('openedx_external_enrollments.external_enrollments.pathstream_external_enrollment.datetime')
    def test_get_enrollment_data(self, datetime_mock):
        """Testing _get_enrollment_data method."""
        data = {
            'user_email': self.user_email,
            'is_active': True,
            'course_id': self.course_id,
        }
        datetime_mock.utcnow.return_value = '2021-06-28 16:40:31.456900'
        expected_data = 'course-v1:test+CS102+2019_T3,test@email,2021-06-28 16:40:31.456900,true\n'

        result = self.base._get_enrollment_data(data)  # pylint: disable=protected-access

        self.assertEqual(result, expected_data)

    @patch(
        'openedx_external_enrollments.external_enrollments.pathstream_external_enrollment.ExternalEnrollment')
    @patch(
        'openedx_external_enrollments.external_enrollments.'
        'pathstream_external_enrollment.PathstreamExternalEnrollment._get_enrollment_data'
    )
    def test_post_enrollment_new_enrollment(self, get_enrollment_data_mock, model_mock):
        """This test validates _post_enrollment method for a new enrollment."""
        data = {
            'user_email': self.user_email,
            'is_active': True,
            'course_id': self.course_id,
        }
        enrollment_data = 'course-v1:test+CS102+2019_T3,test@email,2021-06-28 16:40:31.456900,true\n'
        get_enrollment_data_mock.return_value = enrollment_data
        meta_expected = [
            {
                'enrollment_data_formated': enrollment_data,
                'is_uploaded': False,
            },
        ]
        external_enrollment_object = Mock()
        external_enrollment_object.id = 1
        model_mock.objects.get_or_create.return_value = (external_enrollment_object, True)
        log1 = 'Calling enrollment for [{}] with data: {}'.format(self.base.__str__(), data)
        log2 = 'Calling enrollment for [{}] with course settings: {}'.format(self.base.__str__(), None)
        log3 = 'Saving External enrollment object for [{}] -- ExternalEnrollment.id = {}'.format(
            self.base.__str__(),
            external_enrollment_object.id,
        )

        with LogCapture(level=logging.INFO) as log_capture:
            self.base._post_enrollment(data)  # pylint: disable=protected-access

            log_capture.check(
                (self.module, 'INFO', log1),
                (self.module, 'INFO', log2),
                (self.module, 'INFO', log3),
            )

        get_enrollment_data_mock.assert_called_once_with(data)
        model_mock.objects.get_or_create.assert_called_with(
            controller_name='pathstream',
            course_shell_id=self.course_id,
            email=self.user_email,
        )
        external_enrollment_object.save.assert_called_once()
        self.assertListEqual(external_enrollment_object.meta, meta_expected)

    @patch('openedx_external_enrollments.external_enrollments.pathstream_external_enrollment.ExternalEnrollment')
    @patch(
        'openedx_external_enrollments.external_enrollments.'
        'pathstream_external_enrollment.PathstreamExternalEnrollment._get_enrollment_data'
    )
    def test_post_enrollment_update_enrollment(self, get_enrollment_data_mock, model_mock):
        """This test validates _post_enrollment method when an unenrollment event
        is triggered for user and course, which have been used to create the initial
        ExternalEnrollment object."""
        initial_meta = [
            {
                'enrollment_data_formated': 'course-v1:test+CS102+2019_T3,t@email,2021-06-28 16:40:31.4569,true\n',
                'is_uploaded': False,
            },
        ]
        external_enrollment_object = Mock()
        external_enrollment_object.meta = initial_meta
        model_mock.objects.get_or_create.return_value = (external_enrollment_object, False)
        data = {
            'user_email': self.user_email,
            'is_active': False,
            'course_id': self.course_id,
        }
        unenrollment_data = 'course-v1:test+CS102+2019_T3,t@email,2021-06-29 16:50:31.456900,false\n'
        get_enrollment_data_mock.return_value = unenrollment_data
        meta_expected = initial_meta
        meta_expected.append(
            {
                'enrollment_data_formated': unenrollment_data,
                'is_uploaded': False,
            },
        )

        self.base._post_enrollment(data)  # pylint: disable=protected-access

        external_enrollment_object.save.assert_called_once()
        self.assertListEqual(external_enrollment_object.meta, meta_expected)

    @patch('openedx_external_enrollments.external_enrollments.pathstream_external_enrollment.ExternalEnrollment')
    @patch(
        'openedx_external_enrollments.external_enrollments.pathstream_external_enrollment.'
        'PathstreamExternalEnrollment._get_enrollment_data')
    @ddt.data(
        {
            'course_id': 1,
            'user_email': None,
        },
        {
            'course_id': None,
            'user_email': 'test@email',
        },
        {},
    )
    def test_post_enrollment_with_missing_data(self, data, get_enrollment_mock, model_mock):
        """This test validates the _post_enrollment execution for missing data.
        For instance, if email or course_id are not in data, this will raise an IntegrityError as
        email and course_id can't be None."""
        log = 'Failed to complete enrollment, course_id and user_email can\'t be None'
        model_mock.objects.get_or_create.side_effect = IntegrityError

        with LogCapture(level=logging.ERROR) as log_capture:
            self.base._post_enrollment(data)  # pylint: disable=protected-access

            log_capture.check(
                (self.module, 'ERROR', log),
            )

        get_enrollment_mock.assert_not_called()
        model_mock.objects.get_or_create.assert_called_with(
            controller_name=self.base.__str__(),
            course_shell_id=data.get('course_id'),
            email=data.get('user_email'),
        )
