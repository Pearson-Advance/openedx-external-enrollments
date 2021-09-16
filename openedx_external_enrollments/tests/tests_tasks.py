"""Tests for openedx_external_enrollments.tasks file."""
import unittest

from mock import patch

from openedx_external_enrollments.external_enrollments.pathstream_external_enrollment import (
    PathstreamTaskExecutionError,
)
from openedx_external_enrollments.tasks import refresh_viper_api_keys, run_pathstream_task


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


class TestPathstreamTask(unittest.TestCase):
    """Test class for Pathstream tasks."""

    @patch('openedx_external_enrollments.tasks.run_pathstream_task.retry')
    @patch(
        'openedx_external_enrollments.external_enrollments.pathstream_external_enrollment'
        '.PathstreamExternalEnrollment.execute_upload'
    )
    def test_run_pathstream_task_completed(self, execute_upload_mock, run_pathstream_task_retry_mock):
        """
        This test checks the execution of run_pathstream_task when PathstreamExternalEnrollment.execute_upload
        returns a successful response.
        """
        execute_upload_mock.return_value = True, 'execute_upload completed'
        expected_result = {'message': 'execute_upload completed'}

        result = run_pathstream_task()  # pylint: disable=no-value-for-parameter

        execute_upload_mock.assert_called_once()
        run_pathstream_task_retry_mock.assert_not_called()
        self.assertEqual(result, expected_result)

    @patch('openedx_external_enrollments.tasks.run_pathstream_task.retry')
    @patch(
        'openedx_external_enrollments.external_enrollments.pathstream_external_enrollment'
        '.PathstreamExternalEnrollment.execute_upload'
    )
    def test_run_pathstream_task_not_completed(self, execute_upload_mock, mock_retry):
        """
        This test checks the execution of run_pathstream_task when PathstreamExternalEnrollment.execute_upload
        returns a failed response. Therefore, this test validates that PathstreamTaskExecutionError is raised.
        """
        error_msg = 'test-ExecutionError-message'
        execute_upload_mock.return_value = False, error_msg
        mock_retry.return_value = PathstreamTaskExecutionError(error_msg)

        with self.assertRaises(PathstreamTaskExecutionError):
            run_pathstream_task()  # pylint: disable=no-value-for-parameter

        execute_upload_mock.assert_called_once()
        mock_retry.assert_called_once()
