"""Tests factory file."""
from ddt import data, ddt, unpack
from django.test import TestCase
from mock import patch

from openedx_external_enrollments.external_enrollments.edx_enterprise_external_enrollment import (
    EdxEnterpriseExternalEnrollment,
)
from openedx_external_enrollments.external_enrollments.edx_instance_external_enrollment import (
    EdxInstanceExternalEnrollment,
)
from openedx_external_enrollments.external_enrollments.greenfig_external_enrollment import (
    GreenfigInstanceExternalEnrollment,
)
from openedx_external_enrollments.external_enrollments.icc_external_enrollment import ICCExternalEnrollment
from openedx_external_enrollments.external_enrollments.mit_hz_external_enrollment import MITHzInstanceExternalEnrollment
from openedx_external_enrollments.external_enrollments.pathstream_external_enrollment import (
    PathstreamExternalEnrollment,
)
from openedx_external_enrollments.factory import ExternalEnrollmentFactory


@ddt
class ExternalEnrollmentFactoryTest(TestCase):
    """Test class for ExternalEnrollmentFactory class."""

    @patch('openedx_external_enrollments.external_enrollments.mit_hz_external_enrollment.configuration_helpers')
    @patch('openedx_external_enrollments.external_enrollments.greenfig_external_enrollment.configuration_helpers')
    @data(
        ('edX', EdxEnterpriseExternalEnrollment),
        ('openedX', EdxInstanceExternalEnrollment),
        ('icc', ICCExternalEnrollment),
        ('greenfig', GreenfigInstanceExternalEnrollment),
        ('mit_hz', MITHzInstanceExternalEnrollment),
        ('pathstream', PathstreamExternalEnrollment),
    )
    @unpack
    def test_get_enrollment_controller(self, controller, instance, greenfig_configuration_helpers_mock,
                                       mit_hz_configuration_helpers_mock):
        """Testing _get_enrollment_controller method."""
        greenfig_configuration_helpers_mock.get_value.return_value = 'settings-value'
        mit_hz_configuration_helpers_mock.get_value.return_value = 'settings-value'

        self.assertTrue(
            isinstance(
                ExternalEnrollmentFactory.get_enrollment_controller(controller),
                instance,
            )
        )
