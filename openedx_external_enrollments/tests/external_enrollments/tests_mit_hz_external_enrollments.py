"""Tests MITHzInstanceExternalEnrollment class file."""
from urllib.parse import quote_plus

from django.test import TestCase
from mock import patch

from openedx_external_enrollments.external_enrollments.mit_hz_external_enrollment import MITHzInstanceExternalEnrollment


class MITHzInstanceExternalEnrollmentTest(TestCase):
    """Test class for MITHzInstanceExternalEnrollment."""

    @patch('openedx_external_enrollments.external_enrollments.mit_hz_external_enrollment.configuration_helpers')
    def setUp(self, configuration_helpers_mock):  # pylint: disable=arguments-differ
        """setUp."""
        configuration_helpers_mock.get_value.return_value = 'setting_value'
        self.base = MITHzInstanceExternalEnrollment()

    def test_str(self):
        """
        MITHzInstanceExternalEnrollment overrides the __str__ method,
        this test that the method __str__ returns the right value.
        """
        self.assertEqual(
            'mit_hz',
            self.base.__str__(),
        )

    @patch('openedx_external_enrollments.external_enrollments.mit_hz_external_enrollment.MITHzInstanceExternalEnrollment._get_bearer_token')  # noqa pylint: disable=I0021, C0301
    def test_get_enrollment_headers(self, _get_bearer_token_mock):
        """
        Test _get_enrollment_headers method.
        """
        expected_data = {'Authorization': 'Bearer token', 'Content-Type': 'application/json'}
        _get_bearer_token_mock.return_value = 'token'

        self.assertDictEqual(
            self.base._get_enrollment_headers(),  # pylint: disable=protected-access
            expected_data,
        )

    @patch('openedx_external_enrollments.external_enrollments.mit_hz_external_enrollment.MITHzInstanceExternalEnrollment._check_user')  # noqa pylint: disable=I0021, C0301
    def test_get_enrollment_data(self, _check_user_mock):
        """
        Test _get_enrollment_data method.
        """
        expected_data = {'user_id': quote_plus('setting_value|setting_value|test_user@email.com')}
        data = {'user_email': 'test_user@email.com'}
        course_settings = {}
        _check_user_mock.return_value = True

        self.assertDictEqual(
            self.base._get_enrollment_data(data, course_settings),  # pylint: disable=protected-access
            expected_data,
        )

    def test_get_enrollment_url(self):
        """
        Test test_get_enrollment_url method.
        """
        course_settings = {}
        expected_data = 'root-url/partner_api/pearson/refresh_user'

        self.assertEqual(
            self.base._get_enrollment_url(course_settings),  # pylint: disable=protected-access
            expected_data,
        )

    def test_get_user_id(self):
        """
        Test test_get_user_id method.
        """
        email = 'johndoe@email.com'
        expected_data = quote_plus('setting_value|setting_value|johndoe@email.com')

        self.assertEqual(
            self.base._get_user_id(email),  # pylint: disable=protected-access
            expected_data,
        )
