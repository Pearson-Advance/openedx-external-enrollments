"""Openedx external enrollments task file."""
from celery import task
from rest_framework import status

from openedx_external_enrollments.external_enrollments.pathstream_external_enrollment import (
    PathstreamExternalEnrollment,
    PathstreamTaskExecutionError,
)
from openedx_external_enrollments.external_enrollments.salesforce_external_enrollment import SalesforceEnrollment
from openedx_external_enrollments.external_enrollments.viper_external_enrollment import ViperExternalEnrollment


@task(default_retry_delay=5, max_retries=5)  # pylint: disable=not-callable
def generate_salesforce_enrollment(data, *args, **kwargs):  # pylint: disable=unused-argument
    """
    Handles the enrollment process at Salesforce.
    Args:
        data: request data
    """

    try:
        # Getting the corresponding enrollment controller
        enrollment_controller = SalesforceEnrollment()
    except Exception:  # pylint: disable=broad-except
        pass
    else:
        # Calling the controller enrollment method
        enrollment_controller._post_enrollment(data)  # pylint: disable=protected-access


@task(bind=True, default_retry_delay=5*60)  # pylint: disable=not-callable
def refresh_viper_api_keys(self, *args, **kwargs):  # pylint: disable=unused-argument
    """
    Task that handles Viper's API keys expiration time refresh request.
    """
    result_message, status_code = ViperExternalEnrollment()._refresh_api_keys()  # pylint: disable=protected-access
    if status_code != status.HTTP_200_OK:
        raise self.retry(exc=Exception(result_message))

    return {'message': result_message}


@task(bind=True, default_retry_delay=5*60)  # pylint: disable=not-callable
def run_pathstream_task(self):
    """
    Executes the _execute_upload method of the Pathstream controller in order to update the remote
    S3 file.
    """
    is_completed, message = PathstreamExternalEnrollment().execute_upload()

    if not is_completed:
        raise self.retry(exc=PathstreamTaskExecutionError(message))

    return {'message': message}
