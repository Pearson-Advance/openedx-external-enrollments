"""
This file contains the views for openedx-external-enrollments API.
"""
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from opaque_keys.edx.keys import CourseKey
from rest_framework import status
from rest_framework_oauth.authentication import OAuth2Authentication
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from enrollment.views import EnrollmentListView
from openedx_external_enrollments.edxapp_wrapper.get_courseware import get_course_by_id
from openedx_external_enrollments.edxapp_wrapper.get_edx_rest_framework_extensions import get_jwt_authentication
from openedx_external_enrollments.edxapp_wrapper.get_openedx_permissions import get_api_key_permission
from openedx_external_enrollments.edxapp_wrapper.get_student import get_user
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
        OAuth2Authentication,
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

    authentication_classes = [
        get_jwt_authentication(),
        OAuth2Authentication,
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
            SalesforceEnrollment()
        except Exception:  # pylint: disable=broad-except
            LOG.info("Can't instantiate Salesforce enrollment controller")
            return JsonResponse(
                {"info": "Can't instantiate Salesforce enrollment controller"},
                status=status.HTTP_200_OK,
            )
        else:
            # Now, let's try to call the asynchronous enrollment
            generate_salesforce_enrollment.delay(
                request.data
            )
            return JsonResponse(
                {"info": "Salesforce enrollment request sent..."},
                status=status.HTTP_200_OK,
                safe=False,
            )


class CoreEnrollmentListView(EnrollmentListView):
    """
    Extending EnrollmentListView

    data = {
        'user_email': 'address@example.org',
        'username': 'Username',
        'password': 'P4ssW0rd',
        'fullname': 'Full Name',
        'activate': True,
        'is_active': True,
        'course_mode': 'audit',
        'course_id': 'course_id_pattern',
    }

    """

    parser_classes = [JSONParser]

    def post(self, request):
        """
        Wrapper for EnrollmentListView post method in order to allow
        user_email parameter.
        """
        if 'user_email' in request.data:
            email = request.data.get('user_email')

            try:
                user, _ = get_user(email=email)
            except ObjectDoesNotExist:
                user = self._create_edxapp_user(request.data)

            request.data.update({
                'user': user.username,
                'mode': request.data.get('course_mode'),
                'course_details': {'course_id': request.data.get('course_id')},
            })

        return super(CoreEnrollmentListView, self).post(request)

    def _create_edxapp_user(self, data):
        from django.db import transaction
        from student.forms import AccountCreationForm
        from student.helpers import do_create_account

        form_data = {
            'username': data.get('username'),
            'email': data.get('user_email'),
            'password': data.get('password'),
            'name': data.get('fullname'),
        }
        # Go ahead and create the new user
        with transaction.atomic():
            form = AccountCreationForm(
                data=form_data,
                tos_required=False,
        )
        (user, profile, registration) = do_create_account(form)

        if data.get('activate', False):
            user.is_active = True
            user.save()

        return user
