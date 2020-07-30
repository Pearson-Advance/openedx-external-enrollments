"""Tests EdxInstanceExternalEnrollment class file."""
from django.test import TestCase
from mock import Mock, patch

from openedx_external_enrollments.external_enrollments.greenfig_external_enrollment import (
    GreenfigInstanceExternalEnrollment,
)


class GreenfigInstanceExternalEnrollmentTest(TestCase):
    """Test class for GreenfigInstanceExternalEnrollment."""

    @patch('openedx_external_enrollments.external_enrollments.greenfig_external_enrollment.configuration_helpers')
    def setUp(self, configuration_helpers_mock):
        """setUp."""
        configuration_helpers_mock.get_value.return_value = 'setting_value'
        self.base = GreenfigInstanceExternalEnrollment()

    @patch('openedx_external_enrollments.external_enrollments.greenfig_external_enrollment.get_user')
    @patch('openedx_external_enrollments.external_enrollments.greenfig_external_enrollment.GreenfigInstanceExternalEnrollment._get_course_list')
    @patch('openedx_external_enrollments.external_enrollments.greenfig_external_enrollment.datetime')
    def test_get_enrollment_data_enroll(self, datetime_now_mock, _get_course_list_mock, get_user_mock):
        """Test _get_enrollment_data method."""
        data = {
            'user_email': 'test@email.com',
        }
        course_settings = {
            'external_course_run_id': 'test_course_run_id',
        }
        expected_data = u'08-04-2020 10:50:34, user_test_name, email, course, true\n'
        expected_data += u'08-04-2020 10:50:34, fullname_test, test@email.com, test_course_run_id, true\n'

        user = Mock()
        user.username = 'test-username'
        user.email = 'test@email.com'
        user.profile.name = 'fullname_test'
        get_user_mock.return_value = (user, '')
        datetime_now_mock.now.strftime = Mock(return_value='08-04-2020 10:50:34')

        dropbox_response = Mock()
        dropbox_response.text = u'08-04-2020 10:50:34, user_test_name, email, course, true\n'
        _get_course_list_mock.return_value = dropbox_response

        self.assertEqual(
            self.base._get_enrollment_data(data, course_settings),  # pylint: disable=protected-access
            expected_data,
        )

    def test_get_enrollment_url_default_settings(self):
        """Test _get_enrollment_url method with default settings."""
        expected_url = 'setting_value/files/upload'
        course_settings = 'not used'

        self.assertEqual(
            expected_url,
            self.base._get_enrollment_url(course_settings),  # pylint: disable=protected-access
        )

    def test_get_enrollment_headers(self):
        """Test _get_enrollment_headers method with default settings."""
        expected_headers = {
            "Authorization": "Bearer {token}".format(token='setting_value'),
            "Content-Type": "application/octet-stream",
            "Dropbox-API-Arg": "{\"path\":\"%s\",\"mode\":{\".tag\":\"overwrite\"}}" % 'setting_value'
        }

        self.assertEqual(self.base._get_enrollment_headers(), expected_headers)  # pylint: disable=protected-access

    def test_str(self):
        """
        GreenfigInstanceExternalEnrollment overrides the __str__ method,
        this test that the method __str__ returns the right value.
        """
        self.assertEqual(
            'greenfig',
            self.base.__str__(),
        )
