"""Tests SalesforceEnrollment class file."""
from datetime import datetime, timedelta

from django.conf import settings
from django.test import TestCase
from mock import Mock, patch
from opaque_keys.edx.keys import CourseKey

from openedx_external_enrollments.external_enrollments.salesforce_external_enrollment import (
    SalesforceEnrollment,
)
from openedx_external_enrollments.models import ProgramSalesforceEnrollment


class SalesforceEnrollmentTest(TestCase):
    """Test class for SalesforceEnrollment class."""

    def setUp(self):
        """Set test database."""
        self.base = SalesforceEnrollment()

    @patch('openedx_external_enrollments.external_enrollments.salesforce_external_enrollment.get_course_by_id')
    def test_get_course(self, get_course_by_id_mock):
        """Testing _get_course method."""
        self.assertIsNone(
            self.base._get_course(''),
        )

        course_id = 'course-v1:test+CS102+2019_T3'
        course_key = CourseKey.from_string(course_id)
        expected_course = 'test-course'
        get_course_by_id_mock.return_value = expected_course

        self.assertEqual(self.base._get_course(course_id), expected_course)
        get_course_by_id_mock.assert_called_once_with(course_key)

    def test_str(self):
        """
        SalesforceEnrollment overrides the __str__ method,
        this test that the method __str__ returns the right value.
        """
        self.assertEqual(
            'salesforce',
            self.base.__str__(),
        )

    @patch.object(SalesforceEnrollment, '_get_auth_token')
    def test_get_enrollment_headers(self, get_auth_token_mock):
        """Testing _get_enrollment_headers method."""

        get_auth_token_mock.return_value = {
            'token_type': 'test-token-type',
            'access_token': 'test-access-token',
        }
        expected_headers = {
            'Content-Type': 'application/json',
            'Authorization': 'test-token-type test-access-token',
        }
        self.assertEqual(self.base._get_enrollment_headers(), expected_headers)
        get_auth_token_mock.assert_called_once()

    @patch('openedx_external_enrollments.external_enrollments.salesforce_external_enrollment.OAuth2Session')
    @patch('openedx_external_enrollments.external_enrollments.salesforce_external_enrollment.BackendApplicationClient')
    def test_get_auth_token(self, backend_mock, oauth_session_mock):
        """Testing _get_auth_token method."""
        oauth_mock = Mock()
        oauth_mock.fetch_token.return_value = 'test-token'
        backend_mock.return_value = 'test-client'
        oauth_session_mock.return_value = oauth_mock

        request_params = {
            'client_id': settings.SALESFORCE_API_CLIENT_ID,
            'client_secret': settings.SALESFORCE_API_CLIENT_SECRET,
            'username': settings.SALESFORCE_API_USERNAME,
            'password': settings.SALESFORCE_API_PASSWORD,
            'grant_type': 'password',
        }

        self.assertEqual('test-token', self.base._get_auth_token())
        backend_mock.assert_called_once_with(**request_params)
        oauth_session_mock.assert_called_once_with(client='test-client')
        oauth_mock.fetch_token.assert_called_once_with(token_url=settings.SALESFORCE_API_TOKEN_URL)

    @patch('openedx_external_enrollments.external_enrollments.salesforce_external_enrollment.get_user')
    def test_get_openedx_user(self, get_user_mock):
        """Testing _get_openedx_user method."""
        self.assertEqual({}, self.base._get_openedx_user(data={}))

        data = {
            'supported_lines': [
                {'user_email': 'test-email'},
            ],
        }
        expected_user = {
            'FirstName': 'Peter',
            'LastName': 'Parker',
            'Email': 'test-email',
        }
        profile_mock = Mock()
        profile_mock.name = 'Peter Parker'
        get_user_mock.return_value = (Mock(), profile_mock)

        self.assertEqual(expected_user, self.base._get_openedx_user(data))
        get_user_mock.assert_called_once_with(email='test-email')

        get_user_mock.side_effect = Exception('test')
        self.assertEqual({}, self.base._get_openedx_user(data))

    @patch.object(SalesforceEnrollment, '_get_program_of_interest_data')
    def test_get_salesforce_data(self, get_program_mock):
        """Testing _get_salesforce_data method."""
        data = {
            'supported_lines': [],
            'program': False,
            'paid_amount': 100,
            'currency': 'USD',
        }

        self.assertEqual({}, self.base._get_salesforce_data(data))

        lines = [
            {'user_email': 'test-email'},
        ]
        expected_data = {
            'Purchase_Type': 'Course',
            'PaymentAmount': 100,
            'Amount_Currency': 'USD',
        }
        program_data = {
            'test-key': 'test-value',
            'test-key1': 'test-value1',
            'test-key2': 'test-value2',
        }
        data['supported_lines'] = lines
        expected_data.update(program_data)
        get_program_mock.return_value = program_data

        self.assertEqual(expected_data, self.base._get_salesforce_data(data))
        get_program_mock.assert_called_once_with(data, lines)

        data['program'] = True
        expected_data['Purchase_Type'] = 'Program'
        self.assertEqual(expected_data, self.base._get_salesforce_data(data))

        get_program_mock.side_effect = Exception('test')
        self.assertEqual({}, self.base._get_salesforce_data(data))

    @patch('openedx_external_enrollments.external_enrollments.salesforce_external_enrollment.get_user')
    @patch.object(SalesforceEnrollment, '_get_course')
    def test_get_program_of_interest_data(self, get_course_mock, get_user_mock):
        """Testing _get_program_of_interest_data method."""
        self.assertEqual({}, self.base._get_program_of_interest_data({}, []))

        lines = [
            {
                'user_email': 'test-email',
                'course_id': 'test-course-id',
            },
        ]
        data = {
            'supported_lines': lines,
            'program': {},
        }
        expected_data = {
            'Lead_Source': 'Open edX API',
            'Secondary_Source': '',
            'Tertiary_Source': '',
        }
        course_mock = Mock()
        course_mock.other_course_settings = {'salesforce_data': {}}
        get_course_mock.return_value = course_mock
        user_mock = Mock()
        user_mock.username = 'Spiderman'
        get_user_mock.return_value = (user_mock, Mock())
        expected_drupal = 'enrollment+course+{}+{}'.format(
            user_mock.username,
            datetime.utcnow().strftime('%Y-%m-%d-%H:%M'),
        )

        program_data = self.base._get_program_of_interest_data(data, lines)
        get_user_mock.assert_called_with(email='test-email')
        get_course_mock.assert_called_with('test-course-id')

        drupal_id = program_data.pop('Drupal_ID')
        self.assertEqual(expected_data, program_data)
        self.assertTrue(drupal_id.startswith(expected_drupal))

        salesforce_data = {
            'Lead_Source': 'test-lead',
            'Secondary_Source': 'test-secondary',
            'Tertiary_Source': 'test-tertiary',
        }
        expected_data.update(salesforce_data)
        course_mock.other_course_settings = {'salesforce_data': salesforce_data}

        program_data = self.base._get_program_of_interest_data(data, lines)
        drupal_id = program_data.pop('Drupal_ID')
        self.assertEqual(expected_data, program_data)

        data['program'] = {'uuid': 'test-uuid'}
        data['utm_source'] = 'test-source'
        expected_data['Lead_Source'] = data['utm_source']
        expected_drupal = 'enrollment+program+{}+{}'.format(
            user_mock.username,
            datetime.utcnow().strftime('%Y/%m/%d-%H:%M'),
        )
        ProgramSalesforceEnrollment.objects.create(bundle_id='test-uuid', meta=salesforce_data)
        program_data = self.base._get_program_of_interest_data(data, lines)
        drupal_id = program_data.pop('Drupal_ID')
        self.assertEqual(expected_data, program_data)
        self.assertTrue(drupal_id.startswith(expected_drupal))

    @patch.object(SalesforceEnrollment, '_get_salesforce_course_id')
    @patch.object(SalesforceEnrollment, '_get_course_start_date')
    @patch.object(SalesforceEnrollment, '_get_course')
    def test_get_courses_data(self, get_course_mock, get_date_mock, get_salesforce_mock):
        """Testing _get_courses_data method."""
        self.assertEqual([], self.base._get_courses_data({}, []))

        lines = [
            {
                'user_email': 'test-email',
                'course_id': 'test-course-id',
            },
        ]
        now = datetime.now()
        course_mock = Mock()
        course_mock.end = now
        course_mock.display_name = 'test-course'
        course_mock.other_course_settings = {'salesforce_data': {}}
        get_course_mock.return_value = course_mock
        get_date_mock.return_value = now
        get_salesforce_mock.return_value = 'test-salesforce'
        expected_data = {
            'CourseName': course_mock.display_name,
            'CourseCode': 'test-salesforce',
            'CourseStartDate': now,
            'CourseEndDate': now.strftime('%Y-%m-%d'),
            'CourseDuration': '0',
        }

        self.assertEqual([expected_data], self.base._get_courses_data({}, lines))
        get_course_mock.assert_called_with('test-course-id')
        get_date_mock.assert_called_with(course_mock, 'test-email', 'test-course-id')

        course_mock.other_course_settings = {
            'salesforce_data': {
                'Program_Name': 'test-program',
            },
        }
        expected_data['CourseName'] = 'test-program'

        self.assertEqual([expected_data], self.base._get_courses_data({}, lines))

        get_course_mock.side_effect = Exception('test-exception')

        self.assertEqual([], self.base._get_courses_data({}, lines))

    @patch.object(SalesforceEnrollment, '_is_external_course')
    def test_get_salesforce_course_id(self, external_course_mock):
        """Testing _get_salesforce_course_id method."""
        external_course_mock.return_value = False
        course_mock = Mock()
        course_mock.other_course_settings = {'external_course_run_id': 'test-settings-id'}

        self.assertEqual('internal-id', self.base._get_salesforce_course_id(course_mock, 'internal-id'))
        external_course_mock.assert_called_with(course_mock)

        external_course_mock.return_value = True
        self.assertEqual(
            'test-settings-id',
            self.base._get_salesforce_course_id(course_mock, 'internal-id'),
        )

    def test_is_external_course(self):
        """Testing _is_external_course method."""
        course_mock = Mock()
        course_mock.other_course_settings = {}
        self.assertFalse(self.base._is_external_course(course_mock))

        course_mock.other_course_settings = {'external_course_run_id': 'test'}
        self.assertFalse(self.base._is_external_course(course_mock))

        course_mock.other_course_settings = {'external_course_target': 'test'}
        self.assertFalse(self.base._is_external_course(course_mock))

        course_mock.other_course_settings = {
            'external_course_target': 'test',
            'external_course_run_id': 'test',
        }
        self.assertTrue(self.base._is_external_course(course_mock))

    @patch('openedx_external_enrollments.external_enrollments.salesforce_external_enrollment.get_user')
    @patch('openedx_external_enrollments.external_enrollments.salesforce_external_enrollment.CourseEnrollment')
    def test_get_course_start_date(self, enrollment_mock, get_user_mock):
        """Testing _get_course_start_date method."""
        now = datetime.now()
        course_mock = Mock()
        course_mock.start = now - timedelta(days=1)
        course_mock.self_paced = True
        user = Mock()
        get_user_mock.return_value = (user, Mock())
        course_id = 'course-v1:test+CS102+2019_T3'
        course_key = CourseKey.from_string(course_id)
        enrollment = Mock()
        enrollment.created = now
        enrollment_mock.get_enrollment.return_value = enrollment

        self.assertEqual(
            now.strftime('%Y-%m-%d'),
            self.base._get_course_start_date(course_mock, 'test-email', course_id),
        )
        enrollment_mock.get_enrollment.assert_called_with(user, course_key)

        course_mock.self_paced = False
        self.assertEqual(
            (now - timedelta(days=1)).strftime('%Y-%m-%d'),
            self.base._get_course_start_date(course_mock, 'test-email', course_id),
        )

    @patch.object(SalesforceEnrollment, '_get_salesforce_data')
    @patch.object(SalesforceEnrollment, '_get_openedx_user')
    @patch.object(SalesforceEnrollment, '_get_courses_data')
    def test_get_enrollment_data(self, get_course_mock, get_openedx_mock, get_salesforce_mock):
        """Testing _get_enrollment_data method."""
        now = datetime.now()
        lines = [
            {'user_email': 'test-email'},
        ]
        data = {
            'test': 'data',
            'supported_lines': lines,
        }
        user_data = {
            'FirstName': 'Peter',
            'LastName': 'Parker',
            'Email': 'test-email',
        }
        salesforce_data = {
            'Lead_Source': 'test-source',
            'Secondary_Source': '',
            'Tertiary_Source': '',
        }
        course_data = {
            'CourseName': 'test-course-name',
            'CourseCode': 'test-code',
            'CourseStartDate': now,
            'CourseEndDate': now.strftime('%Y-%m-%d'),
            'CourseDuration': '0',
        }
        get_openedx_mock.return_value = user_data
        get_salesforce_mock.return_value = salesforce_data
        get_course_mock.return_value = course_data

        enrollment = {}
        enrollment.update(user_data)
        enrollment.update(salesforce_data)
        enrollment['Course_Data'] = course_data
        expected_data = {
            'enrollment': enrollment,
        }
        self.assertEqual(expected_data, self.base._get_enrollment_data(data, {}))
        get_openedx_mock.assert_called_once_with(data)
        get_salesforce_mock.assert_called_once_with(data)
        get_course_mock.assert_called_once_with(data, lines)

        user_data['unwanted_key'] = 'testing'
        get_openedx_mock.return_value = user_data
        self.assertEqual(expected_data, self.base._get_enrollment_data(data, {}))

    @patch.object(SalesforceEnrollment, '_get_auth_token')
    def test_get_enrollment_url(self, get_auth_token_mock):
        """Testing _get_enrollment_url method."""
        get_auth_token_mock.return_value = {
            'token_type': 'test-token-type',
            'access_token': 'test-access-token',
            'instance_url': 'test-instance-url',
        }
        expected_url = '{}/{}'.format('test-instance-url', settings.SALESFORCE_ENROLLMENT_API_PATH)
        self.assertEqual(expected_url, self.base._get_enrollment_url({}))
        get_auth_token_mock.assert_called_once()
