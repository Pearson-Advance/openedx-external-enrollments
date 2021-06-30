"""Openedx external enrollments factory file."""
import logging

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
from openedx_external_enrollments.external_enrollments.viper_external_enrollment import ViperExternalEnrollment

LOG = logging.getLogger(__name__)


class ExternalEnrollmentFactory():
    """Class to define the right controller."""

    @classmethod
    def get_enrollment_controller(cls, controller):
        """
        Return the an instance of the enrollment controller.
        """
        if controller.lower() == 'openedx':
            return EdxInstanceExternalEnrollment()
        elif controller.lower() == 'greenfig':
            return GreenfigInstanceExternalEnrollment()
        elif controller.lower() == 'edx':
            return EdxEnterpriseExternalEnrollment()
        elif controller.lower() == 'icc':
            return ICCExternalEnrollment()
        elif controller.lower() == 'mit_hz':
            return MITHzInstanceExternalEnrollment()
        elif controller.lower() == 'viper':
            return ViperExternalEnrollment()
        elif controller.lower() == 'pathstream':
            return PathstreamExternalEnrollment()
        else:
            LOG.error(
                'The external enrollment controller [%s] is not available',
                controller,
            )
            raise NotImplementedError('external enrollment controller not implemented')
