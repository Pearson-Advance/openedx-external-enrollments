"""Tests PathstreamExternalEnrollment class file"""
import io
import logging

import boto3
import botocore
import ddt
from botocore.exceptions import ClientError
from django.db.utils import IntegrityError
from django.test import TestCase
from mock import MagicMock, Mock, call, patch
from opaque_keys.edx.keys import CourseKey
from testfixtures import LogCapture

from openedx_external_enrollments.external_enrollments.pathstream_external_enrollment import (
    PathstreamExternalEnrollment,
    PathstreamTaskExecutionError,
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
        self.assertEqual(self.base.__str__(), 'pathstream')

    @patch('openedx_external_enrollments.external_enrollments.pathstream_external_enrollment.boto3', spec=boto3)
    def test_init_s3_all_settings_setup(self, boto3_mock):
        """
        _init_s3 must be called with all parameters
        """
        access_key_id = 'access_key'
        secret_access_key = 'secret_access_key'
        boto3_mock.client.return_value = Mock(spec=botocore.client.BaseClient)

        self.base._init_s3()  # pylint: disable=protected-access

        boto3_mock.client.assert_called_with(
            's3',
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
        )
        self.assertIsInstance(self.base.client, botocore.client.BaseClient)

    def test_download_file(self):
        """
        _download_file must return the downloaded content from the S3 file if called with all parameters and the
        s3 connection is established.
        """
        s3_file = 'test.log'
        s3_bucket = 'test'
        expected_file_content = 'file_content_test'
        self.base.client = Mock(spec=boto3.client('s3'))
        self.base.client.get_object.return_value = {
            'Body': io.StringIO(expected_file_content),
            'ResponseMetadata': {
                'HTTPStatusCode': 200,
            },
        }
        log = 'File content [{}] was downloaded from S3 for [{}]'.format(s3_file, self.base.__str__())

        with LogCapture(level=logging.INFO) as log_capture:
            file_content = self.base._download_file()  # pylint: disable=protected-access

            log_capture.check(
                (self.module, 'INFO', log),
            )

        self.base.client.get_object.assert_called_with(
            Bucket=s3_bucket,
            Key=s3_file,
        )
        self.assertEqual(file_content, expected_file_content)

    def test_download_file_error(self):
        """If no connection, credentials or wrong parameter values
        _download_file should handle ClientError and raise PathstreamTaskExecutionError."""
        code = '400'
        message = 'Failed'
        operation = 'get_object'
        clienterror_msg = 'An error occurred ({}) when calling the {} operation: {}'.format(
            code,
            operation,
            message,
        )
        self.base.client = Mock(spec=boto3.client('s3'))
        self.base.client.get_object.side_effect = ClientError(
            {
                'Error': {
                    'Code': code,
                    'Message': message,
                },
            },
            operation,
        )

        with self.assertRaisesMessage(PathstreamTaskExecutionError, clienterror_msg):
            self.base._download_file()  # pylint: disable=protected-access

    def test_prepare_new_content(self):
        """This test validates that _prepare_new_content accomplish
        its task of sorting and encoding."""
        enrollment_data_1 = 'course_T1,username,fullname,fname,lname,1@mail,2021-06-29 16:50:00.456900,true\n'
        enrollment_data_2 = 'course_T2,username,fullname,fname,lname,2@mail,2021-06-29 16:51:00.456900,true\n'
        enrollment_data_3 = 'course_T2,username,fullname,fname,lname,2@mail,2021-06-29 16:52:00.456900,false\n'
        enrollment_data_4 = 'course_T1,username,fullname,fname,lname,1@mail,2021-06-29 16:53:00.456900,false\n'
        content = [
            enrollment_data_1,
            enrollment_data_4,
            enrollment_data_2,
            enrollment_data_3,
        ]
        expected_result = (
            enrollment_data_1.encode() +
            enrollment_data_2.encode() +
            enrollment_data_3.encode() +
            enrollment_data_4.encode()
        )

        result = self.base._prepare_new_content(content)  # pylint: disable=protected-access

        self.assertEqual(result, expected_result)

    def test_prepare_new_content_error(self):
        """This test validates that _prepare_new_content raises
        PathstreamTaskExecutionError when called with invalid data.
        The 'content' variable will raise an Index error, after applying
        the split function to it and accessing to a non existing index."""
        content = [
            'course_T1,username,fullname,fname,lname,1@mail,2021-06-29 16:53:00.456900,false\n',
            'invalid_data\n',
        ]
        error_tuple = (
            '_prepare_new_content',
            'An enrollment data is invalid. Reason: {} \nNew data: {}'.format('list index out of range', content),
        )

        with self.assertRaisesMessage(PathstreamTaskExecutionError, str(error_tuple)):
            self.base._prepare_new_content(content)  # pylint: disable=protected-access

    @patch('openedx_external_enrollments.external_enrollments.pathstream_external_enrollment.base64')
    @patch('openedx_external_enrollments.external_enrollments.pathstream_external_enrollment.hashlib')
    def test_upload_file(self, mock_hash, mock_base64):
        """This test validates that _upload file calls the method to update
        the S3 file with the right parameters."""
        s3_file = 'test.log'
        s3_bucket = 'test'
        self.base.client = Mock(spec=boto3.client('s3'))
        response = {
            'ResponseMetadata': {
                'HTTPStatusCode': 200,
            },
        }
        self.base.client.put_object.return_value = response
        content = b'content'
        content_md5 = 'mgNkuembtIDdJeHwKEyFVQ=='
        hash_md5 = b'\x9a\x03d\xb9\xe9\x9b\xb4\x80\xdd%\xe1\xf0(L\x85U'
        mock_hash.md5.return_value.digest.return_value = hash_md5
        mock_base64.b64encode.return_value.decode.return_value = content_md5
        log = 'File [{}] was uploaded to S3 for [{}], response: [{}]'.format(s3_file, self.base.__str__(), response)

        with LogCapture(level=logging.INFO) as log_capture:
            self.base._upload_file(content)  # pylint: disable=protected-access

            log_capture.check(
                (self.module, 'INFO', log),
            )

        self.base.client.put_object.assert_called_once_with(
            Bucket=s3_bucket,
            Key=s3_file,
            Body=content,
            ContentMD5=content_md5,
        )
        mock_hash.md5.assert_called_once_with(content)
        mock_hash.md5().digest.assert_called_once()
        mock_base64.b64encode.assert_called_once_with(hash_md5)

    @ddt.data(None, b'', 'string', [], {})
    def test_upload_file_with_wrong_file_content(self, content):
        """When _upload_file is called without the content parameter or its value
        is empty, it must raise an PathstreamTaskExecutionError."""
        self.base.client = Mock(spec=boto3.client('s3'))
        error_tuple = ('_upload_file', 'Can\'t upload a file with empty content or invalid content type.')

        with self.assertRaisesMessage(PathstreamTaskExecutionError, str(error_tuple)):
            self.base._upload_file(content)  # pylint: disable=protected-access

        self.base.client.put_object.assert_not_called()

    def test_upload_file_error(self):
        """When connection is forbidden or conection can not be
        established, the boto3.client('s3').put_object will raise
        a ClientError and _upload_file must also raise PathstreamTaskExecutionError.
        """
        code = '400'
        message = 'Failed'
        operation = 'put_object'
        clienterror_msg = 'An error occurred ({}) when calling the {} operation: {}'.format(
            code,
            operation,
            message,
        )
        self.base.client = Mock(spec=boto3.client('s3'))
        self.base.client.put_object.side_effect = ClientError(
            {
                'Error': {
                    'Code': code,
                    'Message': message,
                },
            },
            operation,
        )

        with self.assertRaisesMessage(PathstreamTaskExecutionError, clienterror_msg):
            self.base._upload_file(b'content')  # pylint: disable=protected-access

    @patch.object(PathstreamExternalEnrollment, '_init_s3')
    @patch.object(PathstreamExternalEnrollment, '_download_file')
    @patch.object(PathstreamExternalEnrollment, '_prepare_new_content')
    @patch.object(PathstreamExternalEnrollment, '_upload_file')
    @patch(
        'openedx_external_enrollments.external_enrollments.pathstream_external_enrollment.ExternalEnrollment',
        )
    def test_successful_execute_upload_with_data(
            self, model_mock, upload_mock, prepare_mock, download_mock, init_s3_mock):
        """Testing _execute_upload with data and a successfull proccess of
        downloading, updating, uploading.

        'is_uploaded' value must change from False to True.
        """
        self.base.client = Mock(spec=boto3.client('s3'))
        enrollment_data1 = 'course1,email,username,fullname,fname,lname,2021-07-09 16:53:41.492901,true\n'
        enrollment_data2 = 'course1,email,username,fullname,fname,lname,2021-07-20 16:53:41.492901,false\n'
        enrollment_data3 = 'course1,email,username,fullname,fname,lname,2021-07-01 16:53:41.492901,true\n'
        enrollment_data4 = 'course1,email,username,fullname,fname,lname,2021-07-10 16:53:41.492901,false\n'
        qs = [
            Mock(
                controller_name='pathstream',
                email='test1@gmail.com',
                meta=[
                    {
                        'is_uploaded': False,
                        'enrollment_data_formated': enrollment_data1,
                    },
                    {
                        'is_uploaded': False,
                        'enrollment_data_formated': enrollment_data2,
                    },
                ],
            ),
            Mock(
                controller_name='pathstream',
                email='test2@gmail.com',
                meta=[
                    {
                        'is_uploaded': True,
                        'enrollment_data_formated': enrollment_data3,
                    },
                    {
                        'is_uploaded': False,
                        'enrollment_data_formated': enrollment_data4,
                    },
                ],
            ),
        ]
        model_mock.objects.filter.return_value = qs
        file_content = b'course,email,username,fullname,fname,lname,2021-07-08 10:50:41.492901,true\n'
        download_mock.return_value = file_content
        new_content = enrollment_data1.encode() + enrollment_data4.encode() + enrollment_data2.encode()
        prepare_mock.return_value = new_content
        new_file_content = file_content + new_content

        result = self.base.execute_upload()

        model_mock.objects.filter.assert_called_with(
            controller_name='pathstream',
            meta__icontains='"is_uploaded":false',
        )
        init_s3_mock.assert_called_once()
        download_mock.assert_called_once()
        prepare_mock.assert_called_once_with(
            [
                enrollment_data1,
                enrollment_data2,
                enrollment_data4,
            ],
        )
        upload_mock.assert_called_once_with(new_file_content)
        model_mock.objects.bulk_update.assert_called_with(qs, ['meta'])
        self.assertEqual(qs[0].meta[0]['is_uploaded'], True)
        self.assertEqual(qs[0].meta[1]['is_uploaded'], True)
        self.assertEqual(qs[1].meta[1]['is_uploaded'], True)
        self.assertEqual(result[0], True)
        self.assertEqual(result[1], 'execute_upload completed')

    @patch.object(PathstreamExternalEnrollment, '_init_s3')
    @patch.object(PathstreamExternalEnrollment, '_download_file')
    @patch.object(PathstreamExternalEnrollment, '_prepare_new_content')
    @patch.object(PathstreamExternalEnrollment, '_upload_file')
    @patch(
        'openedx_external_enrollments.external_enrollments.pathstream_external_enrollment.ExternalEnrollment',
        )
    def test_successful_execute_upload_without_data(
            self, model_mock, upload_mock, prepare_mock, download_mock, init_s3_mock):
        """Testing _execute_upload without data, In this case the method
        must not call any other method.

        Does not have to update any ExternalEnrollment meta
        """
        model_mock.objects.filter.return_value = []
        log = 'There are no new enrollments to update the S3 file.'

        with LogCapture(level=logging.INFO) as log_capture:
            result = self.base.execute_upload()

            log_capture.check(
                (self.module, 'INFO', log),
            )

        init_s3_mock.assert_not_called()
        download_mock.assert_not_called()
        prepare_mock.assert_not_called()
        upload_mock.assert_not_called()
        model_mock.objects.bulk_update.assert_not_called()
        self.assertEqual(result[0], True)
        self.assertEqual(result[1], 'execute_upload completed')

    @patch.object(PathstreamExternalEnrollment, '_init_s3')
    @patch.object(PathstreamExternalEnrollment, '_download_file')
    @patch.object(PathstreamExternalEnrollment, '_prepare_new_content')
    @patch.object(PathstreamExternalEnrollment, '_upload_file')
    @patch(
        'openedx_external_enrollments.external_enrollments.pathstream_external_enrollment.ExternalEnrollment',
        )
    def test_failed_execute_upload(self, model_mock, upload_mock, prepare_mock, download_mock, init_s3_mock):
        """When any of the methods related to S3 file management fails, it must raise an PathstreamTaskExecutionError
        which should be capture by _execute_upload in order to log the error."""
        self.base.client = Mock(spec=boto3.client('s3'))
        model_mock.objects.filter.return_value = [
            Mock(
                controller_name='pathstream',
                email='test1@gmail.com',
                meta=[
                    {
                        'is_uploaded': False,
                        'enrollment_data_formated': 'course,email,uname,fullname,,,2021-07-09 16:53:41.492901,true\n',
                    },
                ],
            ),
        ]
        error_operation_msg = ('_download_file', 'error.')
        log = 'The proccess to update the remote S3 file has failed. Reason: ' + str(error_operation_msg)
        download_mock.side_effect = PathstreamTaskExecutionError(error_operation_msg[0], error_operation_msg[1])

        with LogCapture(level=logging.ERROR) as log_capture:
            result = self.base.execute_upload()

            log_capture.check(
                (self.module, 'ERROR', log),
            )

        init_s3_mock.assert_called()
        prepare_mock.assert_not_called()
        upload_mock.assert_not_called()
        model_mock.objects.bulk_update.assert_not_called()
        self.assertEqual(result[0], False)
        self.assertEqual(result[1], str(error_operation_msg))

    @patch.object(PathstreamExternalEnrollment, '_init_s3')
    @patch.object(PathstreamExternalEnrollment, '_download_file')
    @patch.object(PathstreamExternalEnrollment, '_prepare_new_content')
    @patch.object(PathstreamExternalEnrollment, '_upload_file')
    @patch(
        'openedx_external_enrollments.external_enrollments.pathstream_external_enrollment.ExternalEnrollment',
        )
    def test_execute_upload_init_s3_failed(
            self, model_mock, upload_mock, prepare_mock, download_mock, init_s3_mock):
        """This test checks that if _init_s3 is called but it does not define self.client as a BaseClient instance,
        then execute_upload must log an error and return the tuple (False, "error_message")."""
        model_mock.objects.filter.return_value = [
            Mock(
                controller_name='pathstream',
                email='test1@gmail.com',
                meta=[
                    {
                        'is_uploaded': False,
                        'enrollment_data_formated': 'course,email,uname,fullname,,,2021-07-09 16:53:41.492901,true\n',
                    },
                ],
            ),
        ]
        log = '_init_s3 has not been called yet or failed.'

        with LogCapture(level=logging.ERROR) as log_capture:
            result = self.base.execute_upload()

            log_capture.check(
                (self.module, 'ERROR', log),
            )

        init_s3_mock.assert_called()
        self.assertEqual(result[0], False)
        self.assertEqual(result[1], log)
        prepare_mock.assert_not_called()
        upload_mock.assert_not_called()
        download_mock.assert_not_called()
        model_mock.objects.bulk_update.assert_not_called()

    @patch.object(PathstreamExternalEnrollment, '_init_s3')
    @patch.object(PathstreamExternalEnrollment, '_download_file')
    @patch.object(PathstreamExternalEnrollment, '_prepare_new_content')
    @patch.object(PathstreamExternalEnrollment, '_upload_file')
    @patch(
        'openedx_external_enrollments.external_enrollments.pathstream_external_enrollment.ExternalEnrollment',
        )
    def test_execute_upload_calling_methods_in_order(
            self, model_mock, upload_mock, prepare_mock, download_mock, init_s3_mock):
        """This test validates that execute_upload calls the following methods strictly in this order:
            1. _init_s3
            2. _download_file
            3. _prepare_new_content
            4. _upload_file
            5. ExternalEnrollment.objects.bulk_update
        """
        self.base.client = Mock(spec=boto3.client('s3'))
        file_content = b'filecontent\n'
        new_content = b'course1,email,uname,fullname,,,2021-07-09 16:53:41.492901,true\n'
        download_mock.return_value = file_content
        prepare_mock.return_value = new_content
        parent_mock = MagicMock()  # Used to record calls.
        parent_mock.attach_mock(init_s3_mock, 'init_s3_mock')
        parent_mock.attach_mock(download_mock, 'download_mock')
        parent_mock.attach_mock(prepare_mock, 'prepare_mock')
        parent_mock.attach_mock(upload_mock, 'upload_mock')
        parent_mock.attach_mock(model_mock.objects.bulk_update, 'bulk_update')
        record = Mock(
            controller_name='pathstream',
            email='test1@gmail.com',
            meta=[
                {
                    'is_uploaded': False,
                    'enrollment_data_formated': 'course1,email,uname,fullname,,,2021-07-09 16:53:41.492901,true\n',
                },
            ],
        )
        model_mock.objects.filter.return_value = [record]
        expected_order_calls = [
            call.init_s3_mock(),
            call.download_mock(),
            call.prepare_mock(['course1,email,uname,fullname,,,2021-07-09 16:53:41.492901,true\n']),
            call.upload_mock(file_content + new_content),
            call.bulk_update([record], ['meta']),
        ]

        self.base.execute_upload()

        self.assertEqual(parent_mock.mock_calls, expected_order_calls)

    @patch('openedx_external_enrollments.external_enrollments.pathstream_external_enrollment.get_user')
    @patch('openedx_external_enrollments.external_enrollments.pathstream_external_enrollment.datetime')
    def test_get_enrollment_data(self, datetime_mock, get_user_mock):
        """Testing _get_enrollment_data method."""
        data = {
            'user_email': self.user_email,
            'is_active': True,
            'course_id': self.course_id,
        }
        user = Mock()
        user.first_name = 'fname'
        user.last_name = 'lname'
        user.username = 'uname'
        user.profile.name = 'fullname'
        get_user_mock.return_value = (user, '')
        datetime_mock.utcnow.return_value = '2021-06-28 16:40:31.456900'
        expected_data = (
            'course-v1:test+CS102+2019_T3,test@email,uname,fullname,fname,lname,'
            '2021-06-28 16:40:31.456900,true\n'
        )

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
        enrollment_data = 'course,test@email,uname,fullname,,,2021-06-28 16:40:31.456900,true\n'
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
        log3 = (
            'Saving External enrollment object for [{}] -- ExternalEnrollment.id = {} '
            '-- Enrollment data = [{}]'.format(
                self.base.__str__(),
                external_enrollment_object.id,
                enrollment_data,
            )
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
                'enrollment_data_formated': 'course,t@email,uname,fullname,,,2021-06-28 16:40:31.4569,true\n',
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
        unenrollment_data = 'course,t@email,uname,fullname,,,2021-06-29 16:50:31.456900,false\n'
        get_enrollment_data_mock.return_value = unenrollment_data
        meta_expected = initial_meta.copy()
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
        log = 'Failed to complete enrollment, course_id and user_email can\'t be None.'
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

    def test_is_enrollment_duplicated_with_duplicated_data(self):
        """This test validates that _is_ enrollment duplicated returns True if there is data
        meeting the requirements to be considered a duplicate enrollment."""
        enrollment_data1 = 'course1,email,username,fullname,,,2021-07-09 16:53:41.492901,true\n'
        enrollment_data2 = 'course1,email,username,fullname,,,2021-07-20 16:53:41.492901,false\n'
        user_enrollments = Mock(
            meta=[
                {
                    'is_uploaded': False,
                    'enrollment_data_formated': enrollment_data1,
                },
                {
                    'is_uploaded': False,
                    'enrollment_data_formated': enrollment_data2,
                },
            ],
        )
        new_enrollment_data = 'course1,email,username,fullname,,,2021-07-20 16:53:42.492901,false\n'

        result = self.base._is_enrollment_duplicated(  # pylint: disable=protected-access
            user_enrollments.meta,
            new_enrollment_data
        )

        self.assertEqual(result, True)

    def test_is_enrollment_duplicated_without_duplicated_data_case_1(self):
        """This test validates that _is_ enrollment duplicated returns False if there is no data
        meeting the requirements to be considered a duplicate enrollment."""
        enrollment_data1 = 'course1,email,username,fullname,,,2021-07-09 16:53:41.492901,true\n'
        enrollment_data2 = 'course1,email,username,fullname,,,2021-07-20 16:53:41.492901,false\n'
        user_enrollments = Mock(
            meta=[
                {
                    'is_uploaded': True,
                    'enrollment_data_formated': enrollment_data1,
                },
                {
                    'is_uploaded': True,
                    'enrollment_data_formated': enrollment_data2,
                },
            ],
        )
        new_enrollment_data = 'course1,email,username,fullname,,,2021-07-20 16:53:42.492901,false\n'

        result = self.base._is_enrollment_duplicated(  # pylint: disable=protected-access
            user_enrollments.meta,
            new_enrollment_data
        )

        self.assertEqual(result, False)

    def test_is_enrollment_duplicated_without_duplicated_data_case_2(self):
        """This test validates that _is_enrollment_duplicated returns False if there is no data meeting the
        requirements to be considered a duplicate enrollment."""
        enrollment_data1 = 'course1,email,username,fullname,,,2021-07-09 16:53:41.492901,true\n'
        enrollment_data2 = 'course1,email,username,fullname,,,2021-07-20 16:53:41.492901,false\n'
        user_enrollments = Mock(
            meta=[
                {
                    'is_uploaded': False,
                    'enrollment_data_formated': enrollment_data1,
                },
                {
                    'is_uploaded': False,
                    'enrollment_data_formated': enrollment_data2,
                },
            ],
        )
        new_enrollment_data = 'course1,email,username,fullname,,,2021-07-21 16:53:42.492901,true\n'

        result = self.base._is_enrollment_duplicated(user_enrollments.meta, new_enrollment_data)

        self.assertEqual(result, False)
