"""
This file contains the views for openedx-external-enrollments API.
"""
import logging

from django.http import JsonResponse
from opaque_keys.edx.keys import CourseKey
from rest_framework import status
from rest_framework.views import APIView

from openedx_external_enrollments.edxapp_wrapper.get_courseware import get_course_by_id
from openedx_external_enrollments.edxapp_wrapper.get_edx_rest_framework_extensions import get_jwt_authentication
from openedx_external_enrollments.edxapp_wrapper.get_openedx_authentication import get_oauth2_authentication
from openedx_external_enrollments.edxapp_wrapper.get_openedx_permissions import get_api_key_permission
from openedx_external_enrollments.edxapp_wrapper.get_site_configuration import configuration_helpers
from openedx_external_enrollments.external_enrollments.salesforce_external_enrollment import SalesforceEnrollment
from openedx_external_enrollments.factory import ExternalEnrollmentFactory
from openedx_external_enrollments.tasks import generate_salesforce_enrollment

LOG = logging.getLogger(__name__)


class ExternalEnrollment(APIView):
    """
    ExternalEnrollment APIView.
    """

    authentication_classes = [
        get_jwt_authentication(),
        get_oauth2_authentication(),
    ]
    permission_classes = [
        get_api_key_permission(),
    ]

    def post(self, request):
        """
        View to execute the external enrollment.
        """
        response = {}
        course = self._get_course(request.data.get("course_id"))

        if not course:
            return JsonResponse(
                {"error": "Invalid operation: course not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Getting the corresponding enrollment controller
            enrollment_controller = ExternalEnrollmentFactory.get_enrollment_controller(
                course.other_course_settings.get("external_platform_target")
            )
        except Exception:  # pylint: disable=broad-except
            LOG.info('Course [%s] not configured as external', request.data.get("course_id"))
            return JsonResponse(
                {"info": "Course {} not configured as external".format(request.data.get("course_id"))},
                status=status.HTTP_200_OK,
            )
        else:
            # Now, let's try to execute the enrollment
            response, request_status = enrollment_controller._post_enrollment(  # pylint: disable=protected-access
                request.data,
                course.other_course_settings,
            )

        return JsonResponse(response, status=request_status, safe=False)

    @staticmethod
    def _get_course(course_id):
        """
        Return a course object.
        """
        if not course_id:
            return None

        course_key = CourseKey.from_string(course_id)
        course = get_course_by_id(course_key)
        return course


class SalesforceEnrollmentView(APIView):
    """
    SalesforceEnrollmentView APIView.
    """
    CONTROLLER_DISABLED_MESSAGE = "Salesforce enrollment controller not enabled for this site."

    authentication_classes = [
        get_jwt_authentication(),
        get_oauth2_authentication(),
    ]
    permission_classes = [
        get_api_key_permission(),
    ]

    def post(self, request):
        """
        View to execute enrollments in salesforce.
        """
        try:
            # Getting the corresponding enrollment controller
            salesforce_controller = SalesforceEnrollment()
        except Exception:  # pylint: disable=broad-except
            LOG.info("Can't instantiate Salesforce enrollment controller")
            return JsonResponse(
                {"info": "Can't instantiate Salesforce enrollment controller"},
                status=status.HTTP_200_OK,
            )
        else:
            if str(salesforce_controller) not in configuration_helpers.get_value("VALID_EXTERNAL_TARGETS", []):
                LOG.info(self.CONTROLLER_DISABLED_MESSAGE)
                return JsonResponse(
                    {"info": self.CONTROLLER_DISABLED_MESSAGE},
                    status=status.HTTP_200_OK,
                )

            # Now, let's try to call the asynchronous enrollment
            generate_salesforce_enrollment.delay(
                request.data
            )
            return JsonResponse(
                {"info": "Salesforce enrollment request sent..."},
                status=status.HTTP_200_OK,
            )
