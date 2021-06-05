"""PathstreamExternalEnrollment class file."""
import logging

import datetime as dt

from requests.models import Response
import boto3
from botocore.exceptions import ClientError


from openedx_external_enrollments.edxapp_wrapper.get_site_configuration import configuration_helpers
from openedx_external_enrollments.models import EnrollmentRequestLog

LOG = logging.getLogger(__name__)


class PathstreamExternalEnrollment():
    """
    PathstreamExternalEnrollment class.
    Using Kinesis Data Firehose
    """

    def __init__(self):
        self.client = boto3.client('firehose')
        self.STREAM_NAME= configuration_helpers.get_value('STREAM_NAME', 'path')

    def __str__(self):
        return 'pathstream'

    def _get_enrollment_data(self, data, course_settings):
        """
        Returns a string with the data required to be treated as a log.
        string format: 'course_key, email, date_time, status'
        """
        time_zone = dt.timezone.utc
        date_time = dt.datetime.now(time_zone) #.strftime(%Y-%m-%d)

        enrollment_data = u'{course_key}, {email}, {date_time}, {status}\n'.format(
            course_key=course_settings.get('external_course_run_id'),
            email=data.get('user_email'),
            date_time=date_time,
            status=str(data.get('is_active')).lower(),
        )
        return enrollment_data

    def _write_enrollment_data(self, enrollment_data):
        """Write the enrollment data into the firehose delivery stream.
        """
        response = self.client.put_record(
            DeliveryStreamName=self.STREAM_NAME,
            Record={
                'Data': bytes(enrollment_data, 'utf-8')
            }
        )

        return response

        """ Exceptions to keep in mind
        Firehose.Client.exceptions.ResourceNotFoundException
        Firehose.Client.exceptions.InvalidArgumentException
        Firehose.Client.exceptions.InvalidKMSResourceException

        # if next one, back off and retry, If the exception persists,
        # it is possible that the throughput limits have been exceeded for the delivery stream.
        Firehose.Client.exceptions.ServiceUnavailableException
        LOG.error('Failed to complete enrollment. Reason: %s', str(error))
        """

    def _post_enrollment(self, data, course_settings=None):
        """
        Get and write enrollment data.
        """
        enrollment_data = self._get_enrollment_data(data, course_settings)
        LOG.info('calling enrollment for [%s] with data: %s', self.__str__(), enrollment_data)
        LOG.info('calling enrollment for [%s] with stream delivery: %s', self.__str__(), self.STREAM_NAME)
        LOG.info('calling enrollment for [%s] with course settings: %s', self.__str__(), course_settings)
        response = self._write_enrollment_data(enrollment_data)
        LOG.info('External enrollment response for [%s] -- %s', self.__str__(), response)

        log_details = {
            'response': response,
            'stream': self.STREAM_NAME,
            'course_advanced_settings': course_settings,
        }
        EnrollmentRequestLog.objects.create(  # pylint: disable=no-member
                request_type=str(self),
                details=log_details,
        )

