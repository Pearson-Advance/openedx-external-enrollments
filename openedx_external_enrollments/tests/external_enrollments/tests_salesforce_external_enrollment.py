"""Tests SalesforceEnrollment class file."""
from datetime import datetime, timedelta

from django.conf import settings
from django.test import TestCase
from mock import Mock, call, patch
from opaque_keys.edx.keys import CourseKey

from openedx_external_enrollments.external_enrollments.salesforce_external_enrollment import SalesforceEnrollment
from openedx_external_enrollments.models import ProgramSalesforceEnrollment


class SalesforceEnrollmentTest(TestCase):
    """Test class for SalesforceEnrollment class."""

    def setUp(self):
        """Set test database."""
        self.base = SalesforceEnrollment()
        self.module = 'openedx_external_enrollments.external_enrollments.salesforce_external_enrollment'

    @patch('openedx_external_enrollments.external_enrollments.salesforce_external_enrollment.get_course_by_id')
    def test_get_course(self, get_course_by_id_mock):
        """Testing _get_course method."""
        self.assertIsNone(
            self.base._get_course(''),  # pylint: disable=protected-access
        )

        course_id = 'course-v1:test+CS102+2019_T3'
        course_key = CourseKey.from_string(course_id)
        expected_course = 'test-course'
        get_course_by_id_mock.return_value = expected_course

        self.assertEqual(self.base._get_course(course_id), expected_course)  # pylint: disable=protected-access
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
        self.assertEqual(self.base._get_enrollment_headers(), expected_headers)  # pylint: disable=protected-access
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

        self.assertEqual('test-token', self.base._get_auth_token())  # pylint: disable=protected-access
        backend_mock.assert_called_once_with(**request_params)
        oauth_session_mock.assert_called_once_with(client='test-client')
        oauth_mock.fetch_token.assert_called_once_with(token_url=settings.SALESFORCE_API_TOKEN_URL)

    @patch('openedx_external_enrollments.external_enrollments.salesforce_external_enrollment.get_user')
    def test_get_openedx_user(self, get_user_mock):
        """Testing _get_openedx_user method."""
        self.assertEqual({}, self.base._get_openedx_user(data={}))  # pylint: disable=protected-access

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
        user_mock = Mock()
        user_mock.first_name = 'Peter'
        user_mock.last_name = 'Parker'
        profile_mock.user = user_mock
        get_user_mock.return_value = (Mock(), profile_mock)

        self.assertEqual(self.base._get_openedx_user(data), expected_user)  # pylint: disable=protected-access
        get_user_mock.assert_called_once_with(email='test-email')

        get_user_mock.side_effect = Exception('test')
        self.assertEqual(self.base._get_openedx_user(data), {})  # pylint: disable=protected-access

    @patch.object(SalesforceEnrollment, '_get_program_of_interest_data')
    def test_get_salesforce_data(self, get_program_mock):
        """Testing _get_salesforce_data method."""
        data = {
            'supported_lines': [],
            'program': False,
            'paid_amount': 100,
            'currency': 'USD',
            'number': '123',
        }

        self.assertEqual({}, self.base._get_salesforce_data(data))  # pylint: disable=protected-access

        lines = [
            {'user_email': 'test-email'},
        ]
        expected_data = {
            'Purchase_Type': 'Course',
            'Order_Number': '123',
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

        self.assertEqual(expected_data, self.base._get_salesforce_data(data))  # pylint: disable=protected-access
        get_program_mock.assert_called_once_with(data, lines)

        data['program'] = True
        expected_data['Purchase_Type'] = 'Program'
        self.assertEqual(expected_data, self.base._get_salesforce_data(data))  # pylint: disable=protected-access

        get_program_mock.side_effect = Exception('test')
        self.assertEqual({}, self.base._get_salesforce_data(data))  # pylint: disable=protected-access

    @patch('openedx_external_enrollments.external_enrollments.salesforce_external_enrollment.get_user')
    @patch.object(SalesforceEnrollment, '_get_course')
    def test_get_program_of_interest_data(self, get_course_mock, get_user_mock):
        """Testing _get_program_of_interest_data method."""
        self.assertEqual({}, self.base._get_program_of_interest_data({}, []))  # pylint: disable=protected-access

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
            'UTM_Parameters': '',
        }
        course_mock = Mock()
        course_mock.other_course_settings = {
            'salesforce_data': {
                'Lead_Source': 'Open edX API',
            },
        }
        get_course_mock.return_value = course_mock
        user_mock = Mock()
        user_mock.username = 'Spiderman'
        get_user_mock.return_value = (user_mock, Mock())
        expected_drupal = 'enrollment+course+{}+{}'.format(
            user_mock.username,
            datetime.utcnow().strftime('%Y/%m/%d-%H:%M'),
        )

        program_data = self.base._get_program_of_interest_data(data, lines)  # pylint: disable=protected-access
        get_user_mock.assert_called_with(email='test-email')
        get_course_mock.assert_called_with('test-course-id')

        drupal_id = program_data.pop('Drupal_ID')
        self.assertEqual(expected_data, program_data)
        self.assertTrue(drupal_id.startswith(expected_drupal))

        salesforce_data = {
            'Lead_Source': 'test-lead',
            'Secondary_Source': 'test-secondary',
        }
        expected_data.update(salesforce_data)
        course_mock.other_course_settings = {'salesforce_data': salesforce_data}

        program_data = self.base._get_program_of_interest_data(data, lines)  # pylint: disable=protected-access
        drupal_id = program_data.pop('Drupal_ID')
        self.assertEqual(expected_data, program_data)

        data['program'] = {'uuid': 'test-uuid'}
        data['utm_source'] = 'test-source'
        expected_drupal = 'enrollment+program+{}+{}'.format(
            user_mock.username,
            datetime.utcnow().strftime('%Y/%m/%d-%H:%M'),
        )
        ProgramSalesforceEnrollment.objects.create(  # pylint: disable=no-member
            bundle_id='test-uuid',
            meta=salesforce_data,
        )
        program_data = self.base._get_program_of_interest_data(data, lines)  # pylint: disable=protected-access
        drupal_id = program_data.pop('Drupal_ID')
        self.assertEqual(expected_data, program_data)
        self.assertTrue(drupal_id.startswith(expected_drupal))

    @patch.object(SalesforceEnrollment, '_get_program_course_runs')
    @patch.object(SalesforceEnrollment, '_get_course_start_date')
    @patch.object(SalesforceEnrollment, '_get_course_key')
    @patch.object(SalesforceEnrollment, '_get_course')
    def test_get_courses_data_case_1(self, get_course_mock, get_course_key_mock, get_date_mock, get_runs_mock):
        """Testing _get_courses_data method for case 1 (Single course)."""
        result = self.base._get_courses_data({}, [])  # pylint: disable=protected-access

        self.assertEqual(result, [])

        lines = [
            {
                'user_email': 'test-email',
                'course_id': 'test-course-id',
            },
        ]
        now = datetime.now()
        now_date_format = now.strftime('%Y-%m-%d')
        course_mock = Mock()
        course_mock.end = now
        course_mock.display_name = 'test-course'
        course_mock.other_course_settings = {
            'salesforce_data': {
                'Institution_Hidden': 'HI',
                'Program_of_Interest': 'POI',
            },
        }
        get_runs_mock.return_value = []
        get_course_mock.return_value = course_mock
        get_course_key_mock.return_value = CourseKey.from_string('course-v1:PX+test-course-run-id+2015')
        get_date_mock.return_value = now_date_format
        expected_data = {
            'CourseName': course_mock.display_name,
            'CourseID': 'PX+test-course-run-id',
            'CourseRunID': 'test-course-id',
            'CourseStartDate': now_date_format,
            'CourseEndDate': now_date_format,
            'CourseDuration': '0',
            'Institution_Hidden': 'HI',
            'Program_of_Interest': 'POI',
        }

        result = self.base._get_courses_data({}, lines)  # pylint: disable=protected-access

        self.assertEqual(result, [expected_data])
        get_course_mock.assert_called_with('test-course-id')
        get_date_mock.assert_called_with(course_mock, 'test-email', 'test-course-id')

        course_mock.other_course_settings['salesforce_data']['Program_Name'] = 'test-program'
        expected_data['CourseName'] = 'test-program'

        result = self.base._get_courses_data({}, lines)  # pylint: disable=protected-access

        self.assertEqual(result, [expected_data])

        get_course_mock.side_effect = Exception('test-exception')

        result = self.base._get_courses_data({}, lines)  # pylint: disable=protected-access

        self.assertEqual(result, [])

    @patch.object(SalesforceEnrollment, '_get_program_of_interest_from_program')
    @patch.object(SalesforceEnrollment, '_get_program_course_runs')
    @patch.object(SalesforceEnrollment, '_get_course_start_date')
    @patch.object(SalesforceEnrollment, '_get_course_key')
    @patch.object(SalesforceEnrollment, '_get_course')
    def test_get_courses_data_case_2(
        self, get_course_mock, get_course_key_mock, get_date_mock,
        get_runs_mock, get_poi_mock
    ):
        """Testing _get_courses_data method for case 2 (1 program)."""
        course_id = 'test-course-id'
        lines = [
            {
                'user_email': 'test-email',
                'course_id': course_id,
            },
        ]
        data = {
            'program': {
                'courses': [
                    {
                        'course_runs': [
                            {'key': course_id},
                        ],
                    },
                ],
            },
        }
        now = datetime.now()
        now_date_format = now.strftime('%Y-%m-%d')
        course_mock = Mock()
        course_mock.end = now
        course_mock.display_name = 'test-course'
        course_mock.other_course_settings = {}
        get_poi_mock.return_value = {
            'Institution_Hidden': 'HI_from_program',
            'Program_of_Interest': 'POI_from_program',
        }
        get_runs_mock.return_value = [course_id]
        get_course_mock.return_value = course_mock
        get_course_key_mock.return_value = CourseKey.from_string('course-v1:PX+test-course-run-id+2015')
        get_date_mock.return_value = now_date_format
        expected_data = {
            'CourseName': course_mock.display_name,
            'CourseID': 'PX+test-course-run-id',
            'CourseRunID': course_id,
            'CourseStartDate': now_date_format,
            'CourseEndDate': now_date_format,
            'CourseDuration': '0',
            'Institution_Hidden': 'HI_from_program',
            'Program_of_Interest': 'POI_from_program',
        }

        result = self.base._get_courses_data(data, lines)  # pylint: disable=protected-access

        self.assertEqual(result, [expected_data])
        get_course_mock.assert_called_with('test-course-id')
        get_date_mock.assert_called_with(course_mock, 'test-email', course_id)

    @patch.object(SalesforceEnrollment, '_get_program_of_interest_from_program')
    @patch.object(SalesforceEnrollment, '_get_program_course_runs')
    @patch.object(SalesforceEnrollment, '_get_course_start_date')
    @patch.object(SalesforceEnrollment, '_get_course_key')
    @patch.object(SalesforceEnrollment, '_get_course')
    def test_get_courses_data_case_2_with_empty_get_program_of_interest_from_program(
        self, get_course_mock, get_course_key_mock, get_date_mock,
        get_runs_mock, get_poi_mock
    ):
        """Testing _get_courses_data method for case 2 (1 program) when _get_program_of_interest_from_program
        returns an empty dict (This is caused by a non-existing ProgramSalesforceEnrollment for the program).
        In this case the program courses must get Institution_Hidden and Program_of_Interest from their
        other_course_settings."""
        course_id = 'test-course-id'
        lines = [
            {
                'user_email': 'test-email',
                'course_id': course_id,
            },
        ]
        data = {
            'program': {
                'courses': [
                    {
                        'course_runs': [
                            {'key': course_id},
                        ],
                    },
                ],
            },
        }
        now = datetime.now()
        now_date_format = now.strftime('%Y-%m-%d')
        course_mock = Mock()
        course_mock.end = now
        course_mock.display_name = 'test-course'
        course_mock.other_course_settings = {
            'salesforce_data': {
                'Institution_Hidden': 'HI_from_course',
                'Program_of_Interest': 'POI_from_course',
            },
        }
        get_poi_mock.return_value = {}
        get_runs_mock.return_value = [course_id]
        get_course_mock.return_value = course_mock
        get_course_key_mock.return_value = CourseKey.from_string('course-v1:PX+test-course-run-id+2015')
        get_date_mock.return_value = now_date_format
        expected_data = {
            'CourseName': course_mock.display_name,
            'CourseID': 'PX+test-course-run-id',
            'CourseRunID': course_id,
            'CourseStartDate': now_date_format,
            'CourseEndDate': now_date_format,
            'CourseDuration': '0',
            'Institution_Hidden': 'HI_from_course',
            'Program_of_Interest': 'POI_from_course',
        }

        result = self.base._get_courses_data(data, lines)  # pylint: disable=protected-access

        self.assertEqual(result, [expected_data])
        get_course_mock.assert_called_with('test-course-id')
        get_date_mock.assert_called_with(course_mock, 'test-email', course_id)

    @patch.object(SalesforceEnrollment, '_get_program_of_interest_from_program')
    @patch.object(SalesforceEnrollment, '_get_program_course_runs')
    @patch.object(SalesforceEnrollment, '_get_course_start_date')
    @patch.object(SalesforceEnrollment, '_get_course_key')
    @patch.object(SalesforceEnrollment, '_get_course')
    def test_get_courses_data_case_2_with_empty_get_program_of_interest_from_program_and_no_other_course_settings(
        self, get_course_mock, get_course_key_mock, get_date_mock,
        get_runs_mock, get_poi_mock
    ):
        """Testing _get_courses_data method for case 2 (1 program) when _get_program_of_interest_from_program
        returns an empty dict (This is caused by a non-existing ProgramSalesforceEnrollment for the program),
        and other_course_settings has no SF settings. In this case the program courses must have empty values for
        Institution_Hidden and Program_of_Interest."""
        course_id = 'test-course-id'
        lines = [
            {
                'user_email': 'test-email',
                'course_id': course_id,
            },
        ]
        data = {
            'program': {
                'courses': [
                    {
                        'course_runs': [
                            {'key': course_id},
                        ],
                    },
                ],
            },
        }
        now = datetime.now()
        now_date_format = now.strftime('%Y-%m-%d')
        course_mock = Mock()
        course_mock.end = now
        course_mock.display_name = 'test-course'
        course_mock.other_course_settings = {}
        get_poi_mock.return_value = {}
        get_runs_mock.return_value = [course_id]
        get_course_mock.return_value = course_mock
        get_course_key_mock.return_value = CourseKey.from_string('course-v1:PX+test-course-run-id+2015')
        get_date_mock.return_value = now_date_format
        expected_data = {
            'CourseName': course_mock.display_name,
            'CourseID': 'PX+test-course-run-id',
            'CourseRunID': course_id,
            'CourseStartDate': now_date_format,
            'CourseEndDate': now_date_format,
            'CourseDuration': '0',
            'Institution_Hidden': '',
            'Program_of_Interest': '',
        }

        result = self.base._get_courses_data(data, lines)  # pylint: disable=protected-access

        self.assertEqual(result, [expected_data])
        get_course_mock.assert_called_with('test-course-id')
        get_date_mock.assert_called_with(course_mock, 'test-email', course_id)

    @patch.object(SalesforceEnrollment, '_get_program_of_interest_from_program')
    @patch.object(SalesforceEnrollment, '_get_program_course_runs')
    @patch.object(SalesforceEnrollment, '_get_course_start_date')
    @patch.object(SalesforceEnrollment, '_get_course_key')
    @patch.object(SalesforceEnrollment, '_get_course')
    def test_get_courses_data_case_3(
        self, get_course_mock, get_course_key_mock, get_date_mock,
        get_runs_mock, get_poi_mock
    ):
        """Testing _get_courses_data method for case 3 (1 program and 1 single course)."""
        single_course_id = 'single-course-id'
        program_course_id = 'program-course-id'
        lines = [
            {
                'user_email': 'test-email',
                'course_id': single_course_id,
            },
            {
                'user_email': 'test-email',
                'course_id': program_course_id,
            }
        ]
        data = {
            'program': {
                'courses': [
                    {
                        'course_runs': [
                            {'key': program_course_id},
                        ],
                    },
                ],
            },
        }
        now = datetime.now()
        now_date_format = now.strftime('%Y-%m-%d')
        single_course_mock = Mock()
        single_course_mock.end = now
        single_course_mock.display_name = 'single-course'
        single_course_mock.other_course_settings = {
            'salesforce_data': {
                'Institution_Hidden': 'HI_from_course',
                'Program_of_Interest': 'POI_from_course',
            },
        }
        program_course_mock = Mock()
        program_course_mock.end = now
        program_course_mock.display_name = 'program-course'
        program_course_mock.other_course_settings = {}
        get_runs_mock.return_value = [program_course_id]
        get_poi_mock.return_value = {
            'Institution_Hidden': 'HI_from_program',
            'Program_of_Interest': 'POI_from_program',
        }
        get_course_mock.side_effect = [
            single_course_mock,
            program_course_mock,
        ]
        get_course_key_mock.side_effect = [
            CourseKey.from_string('course-v1:PX+single-course-run-id+2015'),
            CourseKey.from_string('course-v1:PX+program-course-run-id+2015'),
        ]
        get_date_mock.return_value = now_date_format
        expected_data = [
            {
                'CourseName': single_course_mock.display_name,
                'CourseID': 'PX+single-course-run-id',
                'CourseRunID': single_course_id,
                'CourseStartDate': now_date_format,
                'CourseEndDate': now_date_format,
                'CourseDuration': '0',
                'Institution_Hidden': 'HI_from_course',
                'Program_of_Interest': 'POI_from_course',
            },
            {
                'CourseName': program_course_mock.display_name,
                'CourseID': 'PX+program-course-run-id',
                'CourseRunID': program_course_id,
                'CourseStartDate': now_date_format,
                'CourseEndDate': now_date_format,
                'CourseDuration': '0',
                'Institution_Hidden': 'HI_from_program',
                'Program_of_Interest': 'POI_from_program',
            },
        ]

        result = self.base._get_courses_data(data, lines)  # pylint: disable=protected-access

        self.assertEqual(result, expected_data)

    @patch.object(SalesforceEnrollment, '_get_program_course_runs')
    @patch.object(SalesforceEnrollment, '_get_course_start_date')
    @patch.object(SalesforceEnrollment, '_get_course_key')
    @patch.object(SalesforceEnrollment, '_get_course')
    def test_get_courses_data_case_4(self, get_course_mock, get_course_key_mock, get_date_mock, get_runs_mock):
        """Testing _get_courses_data method for case 4 (Single course without SF in other_course_settings).
        If the course other_course_settings has no SF settings and is not part of a program, then POI/HI should
        be empty."""
        lines = [
            {
                'user_email': 'test-email',
                'course_id': 'test-course-id',
            },
        ]
        now = datetime.now()
        now_date_format = now.strftime('%Y-%m-%d')
        course_mock = Mock()
        course_mock.end = now
        course_mock.display_name = 'test-course'
        course_mock.other_course_settings = {}
        get_runs_mock.return_value = []
        get_course_mock.return_value = course_mock
        get_course_key_mock.return_value = CourseKey.from_string('course-v1:PX+test-course-run-id+2015')
        get_date_mock.return_value = now_date_format
        expected_data = {
            'CourseName': course_mock.display_name,
            'CourseID': 'PX+test-course-run-id',
            'CourseRunID': 'test-course-id',
            'CourseStartDate': now_date_format,
            'CourseEndDate': now_date_format,
            'CourseDuration': '0',
            'Institution_Hidden': '',
            'Program_of_Interest': '',
        }

        result = self.base._get_courses_data({}, lines)  # pylint: disable=protected-access

        self.assertEqual(result, [expected_data])
        get_course_mock.assert_called_with('test-course-id')
        get_date_mock.assert_called_with(course_mock, 'test-email', 'test-course-id')

    def test_is_external_course(self):
        """Testing _is_external_course method."""
        course_mock = Mock()
        course_mock.other_course_settings = {}
        self.assertFalse(self.base._is_external_course(course_mock))  # pylint: disable=protected-access

        course_mock.other_course_settings = {'external_course_run_id': 'test'}
        self.assertFalse(self.base._is_external_course(course_mock))  # pylint: disable=protected-access

        course_mock.other_course_settings = {'external_course_target': 'test'}
        self.assertFalse(self.base._is_external_course(course_mock))  # pylint: disable=protected-access

        course_mock.other_course_settings = {
            'external_course_target': 'test',
            'external_course_run_id': 'test',
        }
        self.assertTrue(self.base._is_external_course(course_mock))  # pylint: disable=protected-access

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
            self.base._get_course_start_date(course_mock, 'test-email', course_id),  # pylint: disable=protected-access
        )
        enrollment_mock.get_enrollment.assert_called_with(user, course_key)

        course_mock.self_paced = False
        self.assertEqual(
            (now - timedelta(days=1)).strftime('%Y-%m-%d'),
            self.base._get_course_start_date(course_mock, 'test-email', course_id),  # pylint: disable=protected-access
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
            'UTM_Parameters': '',
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
        self.assertEqual(expected_data, self.base._get_enrollment_data(data, {}))  # pylint: disable=protected-access
        get_openedx_mock.assert_called_once_with(data)
        get_salesforce_mock.assert_called_once_with(data)
        get_course_mock.assert_called_once_with(data, lines)

        user_data['unwanted_key'] = 'testing'
        get_openedx_mock.return_value = user_data
        self.assertEqual(expected_data, self.base._get_enrollment_data(data, {}))  # pylint: disable=protected-access

    @patch.object(SalesforceEnrollment, '_get_auth_token')
    def test_get_enrollment_url(self, get_auth_token_mock):
        """Testing _get_enrollment_url method."""
        get_auth_token_mock.return_value = {
            'token_type': 'test-token-type',
            'access_token': 'test-access-token',
            'instance_url': 'test-instance-url',
        }
        expected_url = '{}/{}'.format('test-instance-url', settings.SALESFORCE_ENROLLMENT_API_PATH)
        self.assertEqual(expected_url, self.base._get_enrollment_url({}))  # pylint: disable=protected-access
        get_auth_token_mock.assert_called_once()

    @patch.object(SalesforceEnrollment, '_get_course')
    def test_get_program_of_interest_from_courses(self, get_course_mock):
        """This test checks that _get_program_of_interest_from_courses returns data
        from the first course with SF metadata."""
        course1_id = 'test-course1-id'
        course2_id = 'test-course2-id'
        course3_id = 'test-course3-id'
        lines = [
            {'course_id': course1_id},
            {'course_id': course2_id},
            {'course_id': course3_id},
        ]
        course1_mock = Mock()
        course1_mock.other_course_settings = {}
        course2_mock = Mock()
        course2_mock.other_course_settings = {
            'salesforce_data': {
                'key-test': 'value-course2',
            },
        }
        course3_mock = Mock()
        course3_mock.other_course_settings = {
            'salesforce_data': {
                'key-test': 'value-course3',
            },
        }
        get_course_mock.side_effect = [
            course1_mock,
            course2_mock,
            course3_mock,
        ]
        expected_data = course2_mock.other_course_settings['salesforce_data']
        calls = [call(course1_id), call(course2_id)]

        result = self.base._get_program_of_interest_from_courses(lines)  # pylint: disable=protected-access

        get_course_mock.assert_has_calls(calls)
        self.assertEqual(result, expected_data)

    @patch.object(SalesforceEnrollment, '_get_course')
    def test_get_program_of_interest_from_courses_without_sf_data(self, get_course_mock):
        """This tests checks that if there is no SF metadata from any of the courses,
        _get_program_of_interest_from_courses must return an empty dict {}."""
        course1_id = 'test-course1-id'
        lines = [
            {'course_id': course1_id},
        ]
        course1_mock = Mock()
        course1_mock.other_course_settings = {}
        get_course_mock.return_value = course1_mock

        result = self.base._get_program_of_interest_from_courses(lines)  # pylint: disable=protected-access

        get_course_mock.assert_called_with(course1_id)
        self.assertEqual(result, {})

    @patch.object(SalesforceEnrollment, '_get_salesforce_data')
    @patch.object(SalesforceEnrollment, '_get_openedx_user')
    @patch.object(SalesforceEnrollment, '_get_courses_data')
    def test_get_enrollment_data_new_version(self, get_course_mock, get_openedx_mock, get_salesforce_mock):
        """Testing _get_enrollment_data updated method."""
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
            "Institution_Hidden": "hidden_institution",
            "Type_Hidden": "type",
            "Company": "company",
            "Program_of_Interest": "Programilla - Cursillo 1",
            'Lead_Source': 'test-source',
            'Secondary_Source': '',
            'UTM_Parameters': '',
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
        expected_data['enrollment']['Course_Data'].update(
            {
                "Program_of_Interest": expected_data["enrollment"].pop("Program_of_Interest"),
                "Institution_Hiden": expected_data["enrollment"].pop("Institution_Hidden"),
            },
        )

        result = self.base._get_enrollment_data(data, {})  # pylint: disable=protected-access

        self.assertEqual(result, expected_data)
        get_openedx_mock.assert_called_once_with(data)
        get_salesforce_mock.assert_called_once_with(data)
        get_course_mock.assert_called_once_with(data, lines)

        user_data['unwanted_key'] = 'testing'
        get_openedx_mock.return_value = user_data

        result = self.base._get_enrollment_data(data, {})  # pylint: disable=protected-access

        self.assertEqual(result, expected_data)

    def test_get_program_course_runs_with_data(self):
        """This test validates _get_program_course_runs with data."""
        data = {
            'program': {
                'courses': [
                    {
                        'course_runs': [
                            {'key': 'course-test1'},
                            {'key': 'course-test2'},
                        ],
                    },
                    {
                        'course_runs': [
                            {'key': 'course-test3'},
                            {'key': 'course-test4'},
                        ],
                    },
                ],
            },
        }
        expected_result = [
            'course-test1',
            'course-test2',
            'course-test3',
            'course-test4',
        ]

        result = self.base._get_program_course_runs(data)  # pylint: disable=protected-access

        self.assertEqual(result, expected_result)

    def test_get_program_course_runs_without_program(self):
        """This test validates _get_program_course_runs when
        there is no program."""
        data = {}
        expected_result = []

        result = self.base._get_program_course_runs(data)  # pylint: disable=protected-access

        self.assertEqual(result, expected_result)

    def test_get_program_course_runs_without_courses(self):
        """This test validates _get_program_course_runs when the
        program misses courses."""
        data = {
            'program': {
                'courses': [],
            },
        }
        expected_result = []

        result = self.base._get_program_course_runs(data)  # pylint: disable=protected-access

        self.assertEqual(result, expected_result)

    def test_get_program_course_runs_without_course_runs(self):
        """This test validates _get_program_course_runs when the
        courses miss course runs."""
        data = {
            'program': {
                'courses': [
                    {'course_runs': []},
                    {'course_runs': []},
                ],
            },
        }
        expected_result = []

        result = self.base._get_program_course_runs(data)  # pylint: disable=protected-access

        self.assertEqual(result, expected_result)
