"""Tests MITHzInstanceExternalEnrollment class file."""
from urllib.parse import quote_plus

from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from mock import Mock, patch

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
        expected_data = {
            'user_email': 'test_user@email.com',
            'course_id': 'course-id',
            'user_id': quote_plus('setting_value|setting_value|test_user@email.com'),
        }
        data = {'user_email': 'test_user@email.com', 'course_id': 'course-id'}
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

    @patch(
        'openedx_external_enrollments.external_enrollments.'
        'mit_hz_external_enrollment.MITHzInstanceExternalEnrollment._check_user_subscription'
    )
    def test_get_course_home_url(self, check_user_subscription_mock):
        """
        Test _get_course_home_url method.
        """
        course_settings = {
            'external_course_target': 'external-course-target',
        }
        check_user_subscription_mock.return_value = None

        result = self.base._get_course_home_url(course_settings, {})  # pylint: disable=protected-access

        check_user_subscription_mock.assert_called_once()
        self.assertEqual(result, course_settings.get('external_course_target'))

    @patch('openedx_external_enrollments.external_enrollments.mit_hz_external_enrollment.ExternalEnrollment')
    @patch(
        'openedx_external_enrollments.external_enrollments.'
        'mit_hz_external_enrollment.MITHzInstanceExternalEnrollment._check_user'
    )
    def test_check_user_subscription_with_existing_enrollment(self, check_user_mock, model_mock):
        """
        Test _check_user_subscription method with existing enrollment object.
        """
        data = {
            'course_id': 'course_id',
            'user_email': 'user_email',
        }
        enrollment_mock = Mock()
        enrollment_mock.save.return_value = None
        model_mock.objects.get.return_value = enrollment_mock
        check_user_mock.return_value = {}

        self.base._check_user_subscription(data)  # pylint: disable=protected-access

        model_mock.objects.get.assert_called_once_with(
            controller_name='mit_hz',
            course_shell=data.get('course_id'),
            email=data.get('user_email'),
            meta={},
        )
        check_user_mock.assert_called_once_with('setting_value%7Csetting_value%7Cuser_email')
        enrollment_mock.save.assert_called_once()

    @patch('openedx_external_enrollments.external_enrollments.mit_hz_external_enrollment.ExternalEnrollment')
    @patch(
        'openedx_external_enrollments.external_enrollments.'
        'mit_hz_external_enrollment.MITHzInstanceExternalEnrollment._check_user'
    )
    def test_check_user_subscription_with_non_existing_enrollment(self, check_user_mock, model_mock):
        """
        Test _check_user_subscription method with a non existing enrollment object.
        """
        data = {
            'course_id': 'course_id',
            'user_email': 'user_email',
        }
        model_mock.objects.get.side_effect = ObjectDoesNotExist

        self.base._check_user_subscription(data)  # pylint: disable=protected-access

        model_mock.objects.get.assert_called_once_with(
            controller_name='mit_hz',
            course_shell=data.get('course_id'),
            email=data.get('user_email'),
            meta={},
        )
        check_user_mock.assert_not_called()

    @patch('openedx_external_enrollments.external_enrollments.base_external_enrollment.requests.post')
    @patch('openedx_external_enrollments.external_enrollments.mit_hz_external_enrollment.ExternalEnrollment')
    def test_execute_post_failed(self, model_mock, post_mock):
        """
        Test _execute_post method when the post response is unsuccessful.
        """
        json_data = {
            'course_id': 'course-id',
            'user_email': 'user-email',
        }
        mock_response = Mock(ok=False)
        mock_response.json.return_value = {
            'message': 'User not found.',
        }
        post_mock.return_value = mock_response
        model_mock.objects.update_or_create.return_value = None

        result = self.base._execute_post('url', json_data=json_data)  # pylint: disable=protected-access

        self.assertEqual(result, mock_response)
        post_mock.assert_called_once_with(
            data=None,
            headers=None,
            json={'course_id': json_data.get('course_id'), 'user_email': json_data.get('user_email')},
            url='url',
        )
        model_mock.objects.update_or_create.assert_called_once_with(
            controller_name='mit_hz',
            course_shell_id=json_data.get('course_id'),
            defaults={'meta': {}},
            email=json_data.get('user_email'),
        )
        model_mock.objects.filter.assert_not_called()
        model_mock.objects.update.assert_not_called()

    @patch('openedx_external_enrollments.external_enrollments.base_external_enrollment.requests.post')
    @patch('openedx_external_enrollments.external_enrollments.mit_hz_external_enrollment.ExternalEnrollment')
    def test_execute_post_succeeded(self, model_mock, post_mock):
        """
        Test _execute_post method when the post response is successful.
        """
        json_data = {
            'course_id': 'course-id',
            'user_email': 'user-email',
        }
        mock_response = Mock(ok=True)
        mock_response.json.return_value = {
            'user': {'data': 'data'},
        }
        post_mock.return_value = mock_response
        queryset_mock = Mock()
        queryset_mock.update.return_value = None
        model_mock.objects.filter.return_value = queryset_mock

        result = self.base._execute_post('url', json_data=json_data)  # pylint: disable=protected-access

        self.assertEqual(result, mock_response)
        post_mock.assert_called_once_with(
            data=None,
            headers=None,
            json={'course_id': json_data.get('course_id'), 'user_email': json_data.get('user_email')},
            url='url',
        )
        model_mock.objects.update_or_create.assert_called_once_with(
            controller_name='mit_hz',
            course_shell_id=json_data.get('course_id'),
            defaults={'meta': {'data': 'data'}},
            email=json_data.get('user_email'),
        )
        model_mock.objects.filter.assert_called_once_with(
            controller_name='mit_hz',
            email=json_data.get('user_email'),
        )
        queryset_mock.update.assert_called_once_with(meta={'data': 'data'})
