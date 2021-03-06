"""Openedx external enrollments task file."""
from celery import task

from openedx_external_enrollments.external_enrollments.salesforce_external_enrollment import SalesforceEnrollment


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
