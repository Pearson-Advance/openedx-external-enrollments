"""ICCExternalEnrollment class tests file."""
from django.test import TestCase
from mock import Mock, patch

from openedx_external_enrollments.external_enrollments.icc_external_enrollment import ICCExternalEnrollment


class ICCExternalEnrollmentTest(TestCase):
    """Test class for ICCExternalEnrollment class."""

    def setUp(self):
        """Set test instance."""
        self.base = ICCExternalEnrollment()

    @patch('openedx_external_enrollments.external_enrollments.icc_external_enrollment.get_user')
    def test_get_enrollment_data(self, get_user_mock):
        """Testing _get_enrollment_data method."""
        data = {
            'course_mode': 'verified',
            'user_email': 'michael@example.com',
        }
        course_settings = {
            'external_course_run_id': '33',
            'external_enrollment_mode_override': 'verified',
        }
        user = Mock()
        user.username = 'michael'
        user.email = 'michael@example.com'
        user.id = 14
        get_user_mock.return_value = (user, '')
        expected_data = {
            'wstoken': 'michael',
            'wsfunction': 'verified',
            'enrolments[0][roleid]': '5',
            'enrolments[0][userid]': '14',
            'enrolments[0][courseid]': '33',
        }

        self.assertEqual(
            self.base._get_enrollment_data(data, course_settings),  # pylint: disable=protected-access
            expected_data,
        )

    def test_get_enrollment_headers(self):
        """Testing _get_enrollment_headers method."""
        expected_headers = None

        self.assertEqual(self.base._get_enrollment_headers(), expected_headers)  # pylint: disable=protected-access

    def test_get_enrollment_url(self):
        """Testing _get_enrollment_url method."""
        expected_url = 'https://icchas11.stage.kineoplatforms.net/webservice/rest/server.php'
        course_settings = {}

        self.assertEqual(
            self.base._get_enrollment_url(course_settings),  # pylint: disable=protected-access
            expected_url,
        )

    def test_str(self):
        """
        ICCExternalEnrollment overrides the __str__ method,
        this test that the method __str__ returns the right value.
        """
        self.assertEqual(
            self.base.__str__(),
            'ICC',
        )
