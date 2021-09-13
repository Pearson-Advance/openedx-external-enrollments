"""Tests PathstreamExternalEnrollment class file"""
import logging

import ddt
from django.db.utils import IntegrityError
from django.test import TestCase
from mock import Mock, patch
from opaque_keys.edx.keys import CourseKey
from testfixtures import LogCapture

from openedx_external_enrollments.external_enrollments.pathstream_external_enrollment import (
    PathstreamExternalEnrollment,
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
        enrollment_data = 'course-v1:test+CS102+2019_T3,test@email,,,2021-06-28 16:40:31.456900,true\n'
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
