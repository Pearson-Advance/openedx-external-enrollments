"""ICCExternalEnrollment class tests file."""
from django.conf import settings
from django.test import TestCase
from mock import Mock, patch

from openedx_external_enrollments.external_enrollments.icc_external_enrollment import ICCExternalEnrollment


class ICCExternalEnrollmentTest(TestCase):
    """Test class for ICCExternalEnrollment class."""

    def setUp(self):
        """Set test instance."""
        self.base = ICCExternalEnrollment()

    @patch.object(ICCExternalEnrollment, '_get_icc_user')
    def test_get_enrollment_data_with_user_not_found(self, get_icc_user_mock):
        """Testing _get_enrollment_data method with not found user."""
        data = {
            'course_mode': 'verified',
            'user_email': 'michael@example.com',
        }
        course_settings = {
            'external_course_run_id': '33',
            'external_enrollment_mode_override': 'verified',
        }
        get_icc_user_mock.return_value = None

        self.assertEqual(
            self.base._get_enrollment_data(data, course_settings),  # pylint: disable=protected-access
            {},
        )

    @patch.object(ICCExternalEnrollment, '_get_icc_user')
    def test_get_enrollment_data_with_user_found(self, get_icc_user_mock):
        """Testing _get_enrollment_data method with user found."""
        data = {
            'course_mode': 'verified',
            'user_email': 'michael@example.com',
        }
        course_settings = {
            'external_course_run_id': '33',
            'external_enrollment_mode_override': 'verified',
        }
        get_icc_user_mock.return_value = {
            'id': '14',
            'username': 'michael',
        }
        expected_data = {
            'wstoken': settings.ICC_API_TOKEN,
            'wsfunction': settings.ICC_ENROLLMENT_API_FUNCTION,
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
        expected_url = settings.ICC_BASE_URL
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

    @patch('openedx_external_enrollments.external_enrollments.icc_external_enrollment.configuration_helpers')
    def test_get_random_string(self, configuration_helpers_mock):
        """
        Testing _get_random_string method.
        """
        USERNAME_SUFFIX_LENGTH = 5
        configuration_helpers_mock.get_value.return_value = 'setting_value'

        self.assertEqual(
            len(self.base._get_random_string(USERNAME_SUFFIX_LENGTH)),  # pylint: disable=protected-access
            USERNAME_SUFFIX_LENGTH,
        )
        self.assertEqual(
            self.base._get_random_string(8),  # pylint: disable=protected-access
            'setting_value',
        )

    def test_get_found_icc_user_from_xml_response(self):
        """
        Testing user found in get_icc_user_from_xml_response method.
        """
        not_found_user_xml_response = '''<?xml version="1.0" encoding="UTF-8" ?>
        <RESPONSE>
            <SINGLE>
                <KEY name="users">
                    <MULTIPLE></MULTIPLE>
                </KEY>
                <KEY name="warnings">
                    <MULTIPLE></MULTIPLE>
                </KEY>
            </SINGLE>
        </RESPONSE>'''
        response = Mock()
        response.content = not_found_user_xml_response

        self.assertEqual(
            self.base._get_icc_user_from_xml_response(response, 'get_user'),  # pylint: disable=protected-access
            {},
        )

    def test_get_not_found_icc_user_from_xml_response(self):
        """
        Testing not user found in get_icc_user_from_xml_response method.
        """
        found_user_xml_response = '''<?xml version="1.0" encoding="UTF-8" ?>
        <RESPONSE>
            <SINGLE>
                <KEY name="users">
                    <MULTIPLE>
                        <SINGLE>
                            <KEY name="id">
                                <VALUE>1002</VALUE>
                            </KEY>
                            <KEY name="username">
                                <VALUE>michael</VALUE>
                            </KEY>
                            <KEY name="firstname">
                                <VALUE>Kineo Impact</VALUE>
                            </KEY>
                            <KEY name="lastname">
                                <VALUE>Webservice</VALUE>
                            </KEY>
                            <KEY name="fullname">
                                <VALUE>Kineo Impact Webservice</VALUE>
                            </KEY>
                            <KEY name="email">
                                <VALUE>webservice@demo.ninelanterns.com.au</VALUE>
                            </KEY>
                            <KEY name="address">
                                <VALUE null="null"/>
                            </KEY>
                            <KEY name="phone1">
                                <VALUE null="null"/>
                            </KEY>
                            <KEY name="phone2">
                                <VALUE null="null"/>
                            </KEY>
                            <KEY name="icq">
                                <VALUE null="null"/>
                            </KEY>
                            <KEY name="skype">
                                <VALUE null="null"/>
                            </KEY>
                            <KEY name="yahoo">
                                <VALUE null="null"/>
                            </KEY>
                            <KEY name="aim">
                                <VALUE null="null"/>
                            </KEY>
                            <KEY name="msn">
                                <VALUE null="null"/>
                            </KEY>
                            <KEY name="department">
                                <VALUE></VALUE>
                            </KEY>
                            <KEY name="institution">
                                <VALUE null="null"/>
                            </KEY>
                            <KEY name="idnumber">
                                <VALUE null="null"/>
                            </KEY>
                            <KEY name="interests">
                                <VALUE null="null"/>
                            </KEY>
                            <KEY name="firstaccess">
                                <VALUE>0</VALUE>
                            </KEY>
                            <KEY name="lastaccess">
                                <VALUE>0</VALUE>
                            </KEY>
                            <KEY name="auth">
                                <VALUE>manual</VALUE>
                            </KEY>
                            <KEY name="suspended">
                                <VALUE>0</VALUE>
                            </KEY>
                            <KEY name="confirmed">
                                <VALUE>1</VALUE>
                            </KEY>
                            <KEY name="lang">
                                <VALUE>en</VALUE>
                            </KEY>
                            <KEY name="calendartype">
                                <VALUE null="null"/>
                            </KEY>
                            <KEY name="theme">
                                <VALUE></VALUE>
                            </KEY>
                            <KEY name="timezone">
                                <VALUE>99</VALUE>
                            </KEY>
                            <KEY name="mailformat">
                                <VALUE>1</VALUE>
                            </KEY>
                            <KEY name="description">
                                <VALUE null="null"/>
                            </KEY>
                            <KEY name="descriptionformat">
                                <VALUE null="null"/>
                            </KEY>
                            <KEY name="city">
                                <VALUE null="null"/>
                            </KEY>
                            <KEY name="url">
                                <VALUE null="null"/>
                            </KEY>
                            <KEY name="country">
                                <VALUE>AU</VALUE>
                            </KEY>
                            <KEY name="profileimageurlsmall">
                                <VALUE>https://secure.gravatar.com/avatar/0e7b4c51e402f2d669dd0145c92025fc?s=35&amp;d=mm</VALUE>
                            </KEY>
                            <KEY name="profileimageurl">
                                <VALUE>https://secure.gravatar.com/avatar/0e7b4c51e402f2d669dd0145c92025fc?s=100&amp;d=mm</VALUE>
                            </KEY>
                            <KEY name="customfields">
                                <MULTIPLE></MULTIPLE>
                            </KEY>
                            <KEY name="preferences">
                                <MULTIPLE></MULTIPLE>
                            </KEY>
                        </SINGLE>
                    </MULTIPLE>
                </KEY>
                <KEY name="warnings">
                    <MULTIPLE></MULTIPLE>
                </KEY>
            </SINGLE>
        </RESPONSE>'''
        response = Mock()
        response.content = found_user_xml_response
        expected_icc_user = {
            'id': '1002',
            'username': 'michael',
        }

        self.assertEqual(
            self.base._get_icc_user_from_xml_response(response, 'get_user'),  # pylint: disable=protected-access
            expected_icc_user,
        )

    @patch.object(ICCExternalEnrollment, '_create_icc_user')
    def test_validate_icc_user(self, create_icc_user_mock):
        """
        Testing _validate_icc_user method.
        """
        create_icc_user_mock.return_value = {
            'id': '1002',
            'username': 'michael',
        }
        expected_icc_user = create_icc_user_mock.return_value

        self.assertEqual(
            self.base._validate_icc_user({}, {}),  # pylint: disable=protected-access
            expected_icc_user,
        )
        create_icc_user_mock.assert_called_once_with({}, False)

    @patch('openedx_external_enrollments.external_enrollments.icc_external_enrollment.get_user')
    @patch('openedx_external_enrollments.external_enrollments.icc_external_enrollment.requests.post')
    @patch('openedx_external_enrollments.external_enrollments.icc_external_enrollment.configuration_helpers')
    @patch.object(ICCExternalEnrollment, '_get_random_string')
    def test_create_icc_user(self, get_random_string_mock, configuration_helpers_mock, mock_post, get_user_mock):
        """
        Testing _create_icc_user method.
        """
        data = {
            'user_email': 'test-email',
        }
        user_mock = Mock()
        user_mock.username = 'user-test-username'
        user_mock.email = 'user-test-email'
        user_mock.first_name = 'user-test-firstname'
        user_mock.last_name = 'user-test-lastname'
        get_user_mock.return_value = (user_mock, Mock())
        get_random_string_mock.return_value = 'test-password'
        configuration_helpers_mock.get_value.return_value = 'test-auth-method'
        mock_post.return_value.content = '''<?xml version="1.0" encoding="UTF-8" ?>
        <RESPONSE>
            <MULTIPLE>
                <SINGLE>
                    <KEY name="id">
                        <VALUE>1223</VALUE>
                    </KEY>
                    <KEY name="username">
                        <VALUE>testuser</VALUE>
                    </KEY>
                </SINGLE>
            </MULTIPLE>
        </RESPONSE>'''
        expected_icc_user = {
            'id': '1223',
            'username': 'testuser',
        }

        self.assertEqual(
            self.base._create_icc_user(data, False),  # pylint: disable=protected-access
            expected_icc_user,
        )
        get_random_string_mock.assert_called_once()
        get_user_mock.assert_called_once_with(email=data.get('user_email'))

    @patch('openedx_external_enrollments.external_enrollments.icc_external_enrollment.get_user')
    @patch('openedx_external_enrollments.external_enrollments.icc_external_enrollment.requests.post')
    @patch('openedx_external_enrollments.external_enrollments.icc_external_enrollment.configuration_helpers')
    @patch.object(ICCExternalEnrollment, '_get_random_string')
    def test_create_icc_user_fail(self, get_random_string_mock, configuration_helpers_mock, mock_post, get_user_mock):
        """
        Testing fail _create_icc_user method.
        """
        data = {
            'user_email': 'test-email',
        }
        user_mock = Mock()
        user_mock.username = 'user-test-username'
        user_mock.email = 'user-test-email'
        user_mock.first_name = 'user-test-firstname'
        user_mock.last_name = 'user-test-lastname'
        get_user_mock.return_value = (user_mock, Mock())
        get_random_string_mock.return_value = 'test-password'
        configuration_helpers_mock.get_value.return_value = 'test-auth-method'
        mock_post.side_effect = Exception('Test')

        self.assertEqual(
            self.base._create_icc_user(data, False),  # pylint: disable=protected-access
            {},
        )
