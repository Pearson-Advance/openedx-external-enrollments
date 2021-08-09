"""Openedx external enrollments task file."""
<<<<<<< HEAD
from celery import task
from rest_framework import status
=======
import logging
<<<<<<< HEAD
from datetime import timedelta
>>>>>>> Add S3 management to Pathstream.
=======
>>>>>>> Update logic and what methods return.

from celery import task

from openedx_external_enrollments.external_enrollments.pathstream_external_enrollment import (
    PathstreamExternalEnrollment,
)
from openedx_external_enrollments.external_enrollments.salesforce_external_enrollment import SalesforceEnrollment
<<<<<<< HEAD
from openedx_external_enrollments.external_enrollments.viper_external_enrollment import ViperExternalEnrollment
=======

COUNT_DOWN_RETRY = 10 * 60
LOG = logging.getLogger(__name__)
>>>>>>> Add S3 management to Pathstream.


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


<<<<<<< HEAD
<<<<<<< HEAD
@task(bind=True, default_retry_delay=5*60)  # pylint: disable=not-callable
def refresh_viper_api_keys(self, *args, **kwargs):  # pylint: disable=unused-argument
=======
@periodic_task(bind=True, run_every=timedelta(days=1), default_retry_delay=COUNT_DOWN_RETRY)
def pathstream_periodic_task(self):
>>>>>>> Add S3 management to Pathstream.
    """
    Task that handles Viper's API keys expiration time refresh request.
    """
<<<<<<< HEAD
    result_message, status_code = ViperExternalEnrollment()._refresh_api_keys()  # pylint: disable=protected-access
    if status_code != status.HTTP_200_OK:
        raise self.retry(exc=Exception(result_message))

    return {'message': result_message}
=======
    try:
        enrollment_controller = PathstreamExternalEnrollment()
    except Exception as error:  # pylint: disable=broad-except
        LOG.error('Failed to instantiate PathstreamExternalEnrollment. Reason: %s', str(error))
        self.retry(exc=error)
    else:
        is_completed = enrollment_controller.execute_upload()
        if not is_completed:
            self.retry(exc=Exception('execute_upload not completed'))
>>>>>>> Add S3 management to Pathstream.
=======
@task(bind=True, default_retry_delay=5*60)  # pylint: disable=not-callable
def run_pathstream_task(self):
    """
    Executes the _execute_upload method of the Pathstream controller in order to update the remote
    S3 file.
    """
    completed, message = PathstreamExternalEnrollment().execute_upload()
    if not completed:
        raise self.retry(exc=Exception(message))

    return {'messge': message}
>>>>>>> Update logic and what methods return.
