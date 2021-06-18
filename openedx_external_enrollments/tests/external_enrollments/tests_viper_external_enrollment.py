"""ViperExternalEnrollment class tests file."""
import logging

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from mock import Mock, patch
from testfixtures import LogCapture

from openedx_external_enrollments.external_enrollments.viper_external_enrollment import ViperExternalEnrollment


class ViperExternalEnrollmentTest(TestCase):
    """Test class for ViperExternalEnrollment class."""

    def setUp(self):
        """Set test instance."""
        self.base = ViperExternalEnrollment()

    def test_get_enrollment_data(self):
        """Testing _get_enrollment_data method."""
        course_settings = {
            'external_course_class_id': 'class-id',
            'external_course_run_id': 'course-id'
        }
        data = {
            'course_id': 'course-id',
            'user_email': 'user-email',
            'user_name': 'user-name',
        }
        expected_data = {
            'action': 'createEnrolment',
            'variables': {
                'shellCourseId': data.get('course_id'),
                'classId': course_settings.get('external_course_class_id'),
                'courseId': course_settings.get('external_course_run_id'),
                'email': data.get('user_email'),
                'name': data.get('user_name'),
                'provider': settings.OEE_VIPER_IDP,
            }}

        result = self.base._get_enrollment_data(data, course_settings)  # pylint: disable=protected-access

        self.assertEqual(
            expected_data,
            result,
        )

    def test_get_enrollment_headers(self):
        """Testing _get_enrollment_headers method."""
        expected_headers = {'x-api-key': settings.OEE_VIPER_MUTATIONS_API_KEY}

        self.assertEqual(self.base._get_enrollment_headers(), expected_headers)  # pylint: disable=protected-access

    def test_get_enrollment_url(self):
        """Testing _get_enrollment_url method."""
        expected_url = settings.OEE_VIPER_API_URL

        self.assertEqual(
            self.base._get_enrollment_url({}),  # pylint: disable=protected-access
            expected_url,
        )

    def test_str(self):
        """
        ViperExternalEnrollment overrides the __str__ method,
        this test that the method __str__ returns the right value.
        """
        self.assertEqual(
            self.base.__str__(),
            'viper',
        )

    @patch('openedx_external_enrollments.external_enrollments.viper_external_enrollment.ExternalEnrollment')
    def test_get_course_home_url_with_not_found_enrollment(self, model_mock):
        """
        This test validates the get_url_home method.
        """
        model_mock.objects.get.side_effect = ObjectDoesNotExist
        result = self.base._get_course_home_url({}, data={'user': Mock()})  # pylint: disable=protected-access

        self.assertEqual(None, result)

    @patch('openedx_external_enrollments.external_enrollments.viper_external_enrollment.ExternalEnrollment')
    def test_get_course_home_url_with_active_enrollment(self, model_mock):
        """
        This test validates the get_url_home method.
        """
        enrollment_mock = Mock()
        enrollment_mock.meta = {
            'is_active': True,
            'course_url': 'course-url',
        }
        model_mock.objects.get.return_value = enrollment_mock
        result = self.base._get_course_home_url({}, data={'user': Mock()})  # pylint: disable=protected-access

        self.assertEqual(enrollment_mock.meta.get('course_url'), result)

    @patch('openedx_external_enrollments.external_enrollments.viper_external_enrollment.ExternalEnrollment')
    @patch('openedx_external_enrollments.external_enrollments.viper_external_enrollment.requests.post')
    def test_get_course_home_url_with_inactive_enrollment(self, post_mock, model_mock):
        """
        This test validates the get_url_home method with a inactive enrollment.
        """
        expected_result = {
            'link': 'link'
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_result
        post_mock.return_value = mock_response
        enrollment_mock = Mock()
        enrollment_mock.meta = {
            'is_active': False,
            'course_url': 'course-url',
            'class_id': 'class-id',
        }
        model_mock.objects.get.return_value = enrollment_mock
        model_mock.objects.save.return_value = Mock()
        result = self.base._get_course_home_url({}, data={'user': Mock()})  # pylint: disable=protected-access

        self.assertEqual(expected_result.get('link'), result)

    @patch('openedx_external_enrollments.external_enrollments.viper_external_enrollment.ExternalEnrollment')
    @patch('openedx_external_enrollments.external_enrollments.viper_external_enrollment.requests.post')
    def test_get_course_home_url_with_failed_post_enrollment(self, post_mock, model_mock):
        """
        This test validates the get_url_home method with a inactive enrollment.
        """
        module = 'openedx_external_enrollments.external_enrollments.viper_external_enrollment'
        enrollment_mock = Mock()
        enrollment_mock.meta = {
            'is_active': False,
            'course_url': 'course-url',
            'class_id': 'class-id',
        }
        model_mock.objects.get.return_value = enrollment_mock
        post_mock.side_effect = Exception('Exception reason.')

        with LogCapture(level=logging.ERROR) as log_capture:
            result = self.base._get_course_home_url({}, data={'user': Mock()})  # pylint: disable=protected-access
            log = 'Failed to complete re-enrollment. Reason: Exception reason.'
            log_capture.check((module, 'ERROR', log), )

        self.assertEqual(None, result)
