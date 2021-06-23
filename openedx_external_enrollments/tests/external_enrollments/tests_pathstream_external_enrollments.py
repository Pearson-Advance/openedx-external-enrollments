

from datetime import datetime

from django.test import TestCase
from mock import Mock, patch
import boto3
from moto import mock_s3


from openedx_external_enrollments.external_enrollments.pathstream_external_enrollment import PathstreamExternalEnrollment
from openedx_external_enrollments.models import EnrollmentRequestLog


def mocked_datetime():
    """retunrs mocked datetime."""
    return datetime(year=2021, month=10, day=12, hour=13, minute=10, second=2)

class PathstreamExternalEnrollmentTest(TestCase):
    """Test class for PathstreamExternalEnrollment."""

    def setUp(self):
        """Set test database."""
        self.base = PathstreamExternalEnrollment()

    def test_str(self):
        """
        PathstreamExternalEnrollment overrides the __str__ method,
        this test that the method __str__ returns the right value.
        """
        self.assertEqual(
            'pathstream',
            self.base.__str__(),
        )

    def test_get_enrollment_data(self):
        """Testing _get_enrollment_data method."""
        course_settings = {
            'external_course_run_id': '31',
        }
        data = {
            'user_email': 'javier12@gmail',
            'is_active': True,
        }
        expected_data = {
            'course_key':'31',
            'email':'javier12@gmail',
            'status':'true',
        }

        result = self.base._get_enrollment_data(data, course_settings)  # pylint: disable=protected-access

        self.assertEqual(
            expected_data,
            result,
        )

    @patch('openedx_external_enrollments.external_enrollments.pathstream_external_enrollment.dt')
    def test_get_format_data(self, model_mock):

        enrollment_data = {
            'course_key':'31',
            'email':'javier12@gmail.com',
            'status':'true',
        }
        created_datetime = datetime(year=2021, month=10, day=12, hour=13, minute=10, second=2)

        expected_result = '31,javier12@gmail.com,2021-10-12 13:10:02.000000,true\n'
        result = self.base._get_format_data(enrollment_data, created_datetime)

        self.assertEqual(expected_result, result)

    @mock_s3
    def test_init_s3(self):
        """
        pass
        """
        conn = boto3.resource('s3', region_name='us-east-1') #, region_name='us-east-1'
        # We need to create the bucket since this is all in Moto's 'virtual' AWS account
        conn.create_bucket(Bucket='mybucket')

        self.base._init_s3()