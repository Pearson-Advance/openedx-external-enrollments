"""Tests EdxInstanceExternalEnrollment class file."""
from django.conf import settings
from django.test import TestCase
from mock import Mock, patch

from openedx_external_enrollments.external_enrollments.greenfig_external_enrollment import (
    GreenfigInstanceExternalEnrollment,
)


class GreenfigInstanceExternalEnrollmentTest(TestCase):
    """Test class for GreenfigInstanceExternalEnrollment."""

    @patch('openedx_external_enrollments.external_enrollments.greenfig_external_enrollment.configuration_helpers')
    def setUp(self, configuration_helpers_mock):  # pylint: disable=arguments-differ
        """setUp."""
        configuration_helpers_mock.get_value.return_value = 'setting_value'
        self.base = GreenfigInstanceExternalEnrollment()

    @patch('openedx_external_enrollments.external_enrollments.greenfig_external_enrollment.get_user')
    @patch('openedx_external_enrollments.external_enrollments.greenfig_external_enrollment.GreenfigInstanceExternalEnrollment._get_course_list')  # noqa pylint: disable=I0021, C0301
    @patch('openedx_external_enrollments.external_enrollments.greenfig_external_enrollment.datetime')
    def test_get_enrollment_data(self, datetime_now_mock, _get_course_list_mock, get_user_mock):
        """Test _get_enrollment_data method."""
        data = {
            'user_email': 'test@email.com',
            'is_active': True,
        }
        course_settings = {
            'external_course_run_id': 'course_id+10',
        }
        expected_data = u'08-04-2020 10:50:34, John Doe, John, Doe, johndoe@email.com, course_id+10, true\n'
        expected_data += u'08-04-2020 10:50:34, Mary Brown, Mary, Brown, marybrown@email.com, course_id+10, true\n'
        user = Mock()
        user.first_name = 'Mary'
        user.last_name = 'Brown'
        user.email = 'marybrown@email.com'
        user.profile.name = 'Mary Brown'
        get_user_mock.return_value = (user, '')
        datetime_now_mock.now.return_value.strftime.return_value = '08-04-2020 10:50:34'
        dropbox_response = Mock()
        dropbox_response.text = u'08-04-2020 10:50:34, John Doe, John, Doe, johndoe@email.com, course_id+10, true\n'
        _get_course_list_mock.return_value = dropbox_response

        self.assertEqual(
            self.base._get_enrollment_data(data, course_settings),  # pylint: disable=protected-access
            expected_data,
        )

    def test_get_enrollment_url_default_settings(self):
        """Test _get_enrollment_url method with default settings."""
        expected_url = 'setting_valuedropbox-tets-api-upload-url'
        course_settings = 'not used'

        self.assertEqual(
            expected_url,
            self.base._get_enrollment_url(course_settings),  # pylint: disable=protected-access
        )

    def test_get_enrollment_headers(self):
        """Test _get_enrollment_headers method with default settings."""
        expected_headers = {
            'Authorization': 'Bearer {token}'.format(token='setting_value'),
            'Content-Type': 'application/octet-stream',
            'Dropbox-API-Arg': settings.DROPBOX_API_ARG_UPLOAD % 'setting_value',
        }
        self.assertEqual(self.base._get_enrollment_headers(), expected_headers)  # pylint: disable=protected-access

    def test_get_download_headers(self):
        """Test _get_download_headers method with default settings."""
        expected_headers = {
            'Authorization': 'Bearer {token}'.format(token='setting_value'),
            'Dropbox-API-Arg': settings.DROPBOX_API_ARG_DOWNLOAD % 'setting_value',
        }
        self.assertEqual(self.base._get_download_headers(), expected_headers)  # pylint: disable=protected-access

    @patch('openedx_external_enrollments.external_enrollments.greenfig_external_enrollment.requests.post')
    def test_execute_post(self, mock_post):
        """Testing _execute_post method."""
        url = 'test_url'
        data = 'data'
        headers = 'headers'
        json_data = 'json_data'

        self.base._execute_post(  # pylint: disable=protected-access
            url=url,
            data=data,
            headers=headers,
            json_data=json_data,
        )

        mock_post.assert_called_with(
            url=url,
            data=json_data,
            headers=headers,
        )

    def test_str(self):
        """
        GreenfigInstanceExternalEnrollment overrides the __str__ method,
        this test that the method __str__ returns the right value.
        """
        self.assertEqual(
            'greenfig',
            self.base.__str__(),
        )
