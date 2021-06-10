"""Tests SalesforceEnrollment class file."""
from django.test import TestCase
from mock import Mock, patch

from openedx_external_enrollments.signal_receivers import update_external_enrollment


class UpdateExternalEnrollmentTest(TestCase):
    """Test class for update_external_enrollment method."""

    @patch('openedx_external_enrollments.signal_receivers.get_course_mode')
    @patch('openedx_external_enrollments.signal_receivers.get_course_by_id')
    @patch('openedx_external_enrollments.signal_receivers.configuration_helpers')
    def test_update_enrollments(self, configuration_helpers_mock, get_course_by_id_mock, get_course_mode_mock):
        """Testing update_external_enrollments method."""
        instance = Mock()
        instance.is_active = True
        instance.mode = 'test-mode'
        instance.user.email = 'test-email'
        instance.user.profile.name = 'name'
        instance.course_id = 'test-course-id'
        get_course_by_id_mock.return_value = 'test-course'
        configuration_helpers_mock.get_value.return_value = False
        data = {
            'user_email': instance.user.email,
            'course_mode': instance.mode,
            'is_active': True,
            'course_id': instance.course_id,
            'name': instance.user.profile.name,
        }
        course_mode_mock = Mock()
        course_mode_mock.VERIFIED = 'test-mode'
        get_course_mode_mock.return_value = course_mode_mock

        with patch('openedx_external_enrollments.signal_receivers.execute_external_enrollment') as execute_mock:
            update_external_enrollment('fake-sender', course_enrollment=instance)

            get_course_by_id_mock.assert_not_called()
            execute_mock.assert_not_called()

            configuration_helpers_mock.get_value.return_value = False

            update_external_enrollment('fake-sender', course_enrollment=instance)

            get_course_by_id_mock.assert_not_called()
            execute_mock.assert_not_called()

            configuration_helpers_mock.get_value.return_value = True

            update_external_enrollment('fake-sender', course_enrollment=instance)

            get_course_by_id_mock.assert_called_once_with(instance.course_id)
            execute_mock.assert_called_once_with(
                data=data,
                course='test-course',
            )

            data['is_active'] = True
            instance.is_active = True

            update_external_enrollment('fake-sender', course_enrollment=instance)
            execute_mock.assert_called_with(
                data=data,
                course='test-course',
            )


class DeleteExternalEnrollmentTest(TestCase):
    """Test class for delete_external_enrollment method."""

    @patch('openedx_external_enrollments.signal_receivers.get_course_mode')
    @patch('openedx_external_enrollments.signal_receivers.get_course_by_id')
    @patch('openedx_external_enrollments.signal_receivers.configuration_helpers')
    def test_delete_enrollments(self, configuration_helpers_mock, get_course_by_id_mock, get_course_mode_mock):
        """Testing delete_external_enrollments method."""
        instance = Mock()
        instance.is_active = False
        instance.mode = 'test-mode'
        instance.user.email = 'test-email'
        instance.course_id = 'test-course-id'
        instance.user.profile.name = 'name'
        get_course_by_id_mock.return_value = 'test-course'
        configuration_helpers_mock.get_value.return_value = False
        data = {
            'user_email': instance.user.email,
            'course_mode': instance.mode,
            'is_active': False,
            'course_id': instance.course_id,
            'name': instance.user.profile.name,
        }
        course_mode_mock = Mock()
        course_mode_mock.VERIFIED = 'test-mode'
        get_course_mode_mock.return_value = course_mode_mock

        with patch('openedx_external_enrollments.signal_receivers.execute_external_enrollment') as execute_mock:
            update_external_enrollment('fake-sender', course_enrollment=instance)

            get_course_by_id_mock.assert_not_called()
            execute_mock.assert_not_called()

            configuration_helpers_mock.get_value.return_value = True

            update_external_enrollment('fake-sender', course_enrollment=instance)

            get_course_by_id_mock.assert_called_once_with(instance.course_id)
            execute_mock.assert_called_once_with(
                data=data,
                course='test-course',
            )
