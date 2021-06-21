"""Openedx external enrollments task file."""
import datetime as dt
import time

from celery import task, decorators

from openedx_external_enrollments.external_enrollments.pathstream_external_enrollment import (
    PathstreamExternalEnrollment,
)
from openedx_external_enrollments.external_enrollments.salesforce_external_enrollment import SalesforceEnrollment
from openedx_external_enrollments.models import EnrollmentRequestLog


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

@task() #@decorators.periodic_task(run_every=dt.timedelta(days=1))
def pathstream_periodic_task():
    """
    Executes the _execute_upload method of the Pathstream controller.
    """
    try:
        enrollment_controller = PathstreamExternalEnrollment()
    except Exception:  # pylint: disable=broad-except
        pass
    else:
        enrollment_controller._execute_upload()

@task()
def upload_data(start=0, end=100):
    """Create data to test"""
    for i in range(start, end):
        time.sleep(0.05)

        enrollment = EnrollmentRequestLog(request_type='pathstream')
        enrollment.save()

        date_time = enrollment.created_at.strftime("%Y-%m-%d %H:%M:%S.%f")

        details = {'course_advanced_settings': {
                'external_course_run_id': '31',
                'external_course_target': 'https://www.youtube.com/watch?v=2fhBvH_-tNM',
                'external_platform_target': 'pathstream'
                },
                'enrollment_data': '31,javier{}@gmail.com,{},true\n'.format(i, date_time)
            }

        enrollment.details = details
        enrollment.save()
