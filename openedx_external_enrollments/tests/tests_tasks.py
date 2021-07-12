"""Tests for openedx_external_enrollments.tasks file."""
import unittest

from mock import patch

from openedx_external_enrollments.tasks import refresh_viper_api_keys


class TestViperTasks(unittest.TestCase):
    """Test class for viper related tasks."""

    @patch('openedx_external_enrollments.tasks.refresh_viper_api_keys.retry')
    @patch('openedx_external_enrollments.external_enrollments.viper_external_enrollment.ViperExternalEnrollment._refresh_api_keys')  # noqa: disable=E501 pylint: disable=C0301
    def test_refresh_viper_api_keys_with_200_status_code(
            self,
            refresh_api_keys_mock,
            refresh_viper_api_keys_task_retry_mock,
    ):
        """
        Test the refresh_viper_api_keys method and its result message.
        """
        refresh_api_keys_mock.return_value = 'success-result-message', 200
        expected_result = {'message': 'success-result-message'}

        result = refresh_viper_api_keys()  # pylint: disable=no-value-for-parameter

        refresh_viper_api_keys_task_retry_mock.assert_not_called()
        refresh_api_keys_mock.assert_called_once()
        self.assertEqual(result, expected_result)

    @patch('openedx_external_enrollments.tasks.refresh_viper_api_keys.retry')
    @patch('openedx_external_enrollments.external_enrollments.viper_external_enrollment.ViperExternalEnrollment._refresh_api_keys')  # noqa: disable=E501 pylint: disable=C0301
    def test_refresh_viper_api_keys_with_400_status_code(
            self,
            refresh_api_keys_mock,
            refresh_viper_api_keys_task_retry_mock,
    ):
        """
        Test the refresh_viper_api_keys method and its result message.
        """
        refresh_api_keys_mock.return_value = 'fail-result-message', 400
        expected_result = {'message': 'fail-result-message'}

        with self.assertRaises(Exception):
            result = refresh_viper_api_keys()  # pylint: disable=no-value-for-parameter

            self.assertEqual(result, expected_result)

        refresh_api_keys_mock.assert_called_once()
        refresh_viper_api_keys_task_retry_mock.assert_called_once()
