"""SalesforceEnrollment class file."""
import datetime
import logging
from urllib.parse import parse_qs, urlsplit

import requests
from django.conf import settings
from oauthlib.oauth2 import BackendApplicationClient
from opaque_keys.edx.keys import CourseKey
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session

from openedx_external_enrollments.edxapp_wrapper.get_courseware import get_course_by_id
from openedx_external_enrollments.edxapp_wrapper.get_student import CourseEnrollment, get_user
from openedx_external_enrollments.external_enrollments.base_external_enrollment import BaseExternalEnrollment
from openedx_external_enrollments.models import ProgramSalesforceEnrollment

LOG = logging.getLogger(__name__)

class SalesforceEnrollment(BaseExternalEnrollment):
    """
    SalesforceEnrollment class.
    """

    def __str__(self):
        return "salesforce"

    def _execute_post(self, url, data=None, headers=None, json_data=None):
        """
        Execute post request.
        """
        basic_auth = HTTPBasicAuth(
            settings.SALESFORCE_ENROLLMENT_BASIC_AUTH_USER,
            settings.SALESFORCE_ENROLLMENT_BASIC_AUTH_PASSWORD
        )

        response = requests.post(
            url=url,
            data=data,
            headers=headers,
            json=json_data,
            auth=basic_auth
        )
        return response

    @staticmethod
    def _decode_utm_params(utm_params):
        utm_params_dict = {key: value[0] for key, value in parse_qs(urlsplit(utm_params).path).items()}
        return utm_params_dict

    @staticmethod
    def _get_course_key(course_id):
        course_key = CourseKey.from_string(course_id)
        return course_key

    def _get_course(self, course_id):
        """
        Return a course object.
        """
        if not course_id:
            return None

        course_key = self._get_course_key(course_id)
        course = get_course_by_id(course_key)
        return course

    def _get_enrollment_headers(self):
        headers = {
            "Content-Type": "application/json"
        }

        if settings.SALESFORCE_ENABLE_AUTHENTICATION:
            token = self._get_auth_token()
            headers.update(
                {
                    "Authorization": "{} {}".format(
                        token.get("token_type"),
                        token.get("access_token"),
                    )
                }
            )

        return headers

    @staticmethod
    def _get_auth_token():
        """

        :return:
        """
        request_params = {
            'client_id': settings.SALESFORCE_API_CLIENT_ID,
            'client_secret': settings.SALESFORCE_API_CLIENT_SECRET,
            'username': settings.SALESFORCE_API_USERNAME,
            'password': settings.SALESFORCE_API_PASSWORD,
            'grant_type': 'password',
        }
        client = BackendApplicationClient(**request_params)
        oauth = OAuth2Session(client=client)
        oauth.params = request_params
        token = oauth.fetch_token(
            token_url=settings.SALESFORCE_API_TOKEN_URL,
        )

        return token

    @staticmethod
    def _get_openedx_user(data):
        """
        :param data:
        :return:
        """
        user = {}
        order_lines = data.get("supported_lines")
        if order_lines:
            try:
                email = order_lines[0].get("user_email")
                _, openedx_profile = get_user(email=email)

                user["Email"] = email
                if openedx_profile.user.first_name:
                    user["FirstName"] = openedx_profile.user.first_name
                    user["LastName"] = openedx_profile.user.last_name
                else:
                    first_name, last_name = openedx_profile.name.split(" ", 1)
                    user["FirstName"] = first_name.strip(" ")
                    user["LastName"] = last_name.strip(" ")
            except Exception:  # pylint: disable=broad-except
                pass

        return user

    def _get_salesforce_data(self, data):
        """

        :param data:
        :return:
        """
        LOG.info('Calling _get_salesforce_data for [%s] with data: %s',  self.__str__(), data)
        salesforce_data = {}
        order_lines = data.get("supported_lines")
        if order_lines:
            try:
                salesforce_data.update(self._get_program_of_interest_data(data, order_lines))
                salesforce_data["Order_Number"] = data.get("number")
                salesforce_data["Purchase_Type"] = "Program" if data.get("program") else "Course"
                salesforce_data["PaymentAmount"] = data.get("paid_amount")
                salesforce_data["Amount_Currency"] = data.get("currency")
            except Exception as error:  # pylint: disable=broad-except
                LOG.warning('Failed while filling salesforce_data. Reason: %s', str(error))

        return salesforce_data

    def _get_program_of_interest_data(self, data, order_lines):
        """

        :param data:
        :param order_lines:
        :return:
        """
        program_of_interest = {}
        program = data.get("program")
        try:
            email = order_lines[0].get("user_email")
            openedx_user, _ = get_user(email=email)
            request_time = datetime.datetime.utcnow()
            if program:
                related_program = ProgramSalesforceEnrollment.objects.get(  # pylint: disable=no-member
                    bundle_id=program.get("uuid"),
                )
                program_of_interest = related_program.meta
                program_of_interest["Drupal_ID"] = "enrollment+program+{}+{}".format(
                    openedx_user.username,
                    request_time.strftime("%Y/%m/%d-%H:%M:%S"),
                )
            else:
                for line in order_lines:
                    course = self._get_course(line.get("course_id"))
                    program_of_interest = course.other_course_settings.get("salesforce_data")
                    if program_of_interest:
                        break

                program_of_interest["Drupal_ID"] = "enrollment+course+{}+{}".format(
                    openedx_user.username,
                    request_time.strftime("%Y-%m-%d-%H:%M:%S"),
                )

            program_of_interest["Lead_Source"] = program_of_interest.get(
                "Lead_Source",
                "",
            )
            program_of_interest["UTM_Parameters"] = data.get(
                "utm_params",
                "",
            )
            program_of_interest["Secondary_Source"] = program_of_interest.get(
                "Secondary_Source",
                ""
            )
        except Exception:  # pylint: disable=broad-except
            pass

        return program_of_interest

    def _get_courses_data(self, data, order_lines):  # pylint: disable=unused-argument
        """

        :param data:
        :param order_lines:
        :return:
        """
        LOG.info('Calling _get_courses_data for [%s] with order_lines: %s',  self.__str__(), order_lines)
        courses = []
        for line in order_lines:
            try:
                course_id = line.get("course_id")
                course = self._get_course(course_id)
                course_key = self._get_course_key(course_id)
                salesforce_settings = course.other_course_settings.get("salesforce_data")
                course_data = dict()
                course_data["CourseName"] = salesforce_settings.get("Program_Name") or course.display_name
                course_data["CourseID"] = "{}+{}".format(course_key.org, course_key.course)
                course_data["CourseRunID"] = course_id
                course_data["CourseStartDate"] = self._get_course_start_date(course, line.get("user_email"), course_id)
                course_data["CourseEndDate"] = course.end.strftime("%Y-%m-%d")
                course_data["CourseDuration"] = "0"
            except Exception as error:  # pylint: disable=broad-except
                LOG.error('Failed _get_courses_data while filling course_data. Reason: %s', str(error))
            else:
                courses.append(course_data)

        return courses

    @staticmethod
    def _is_external_course(course):
        """
        True if the course was confiured as external, False otherwise.
        """

        return (
            course.other_course_settings.get("external_course_run_id") and
            course.other_course_settings.get("external_course_target")
        )

    @staticmethod
    def _get_course_start_date(course, email, course_id):
        """
        Return the course date start.
        """

        user, _ = get_user(email=email)
        course_key = CourseKey.from_string(course_id)
        enrollment = CourseEnrollment.get_enrollment(user, course_key)

        if course.self_paced:
            dates_to_check = [enrollment.created, course.start]
            student_start = max(dates_to_check)
        else:
            student_start = course.start

        return student_start.strftime("%Y-%m-%d")

    def _get_enrollment_data(self, data, course_settings):
        """
        :param data:
        :return:
        """
        valid_keys = [
            "FirstName",
            "LastName",
            "Email",
            "Institution_Hidden",
            "Program_of_Interest",
            "UTM_Parameters",
            "Secondary_Source",
            "Drupal_ID",
            "Order_Number",
            "Purchase_Type",
            "PaymentAmount",
            "Amount_Currency",
            "Course_Data",
            "Lead_Source",
            "Company",
            "Type_Hidden",
        ]
        payload = {
            "enrollment": {}
        }
        openedx_user_info = self._get_openedx_user(data)
        payload["enrollment"].update(openedx_user_info)

        salesforce_data = self._get_salesforce_data(data)
        payload["enrollment"].update(salesforce_data)

        payload["enrollment"]["Course_Data"] = self._get_courses_data(
            data,
            data.get("supported_lines"),
        )

        unwanted = set(payload["enrollment"]) - set(valid_keys)
        LOG.info('Unwanted keys when calling _get_enrollment_data: %s', unwanted)
        for unwanted_key in unwanted:
            del payload["enrollment"][unwanted_key]

        return payload

    def _get_enrollment_url(self, course_settings):
        """
        We defined the SALESFORCE_ENABLE_AUTHENTICATION option to
        have the control of this in each environment.
        """
        instance_url = settings.SALESFORCE_INSTANCE_URL

        if settings.SALESFORCE_ENABLE_AUTHENTICATION:
            token = self._get_auth_token()
            instance_url = token.get('instance_url')

        return "{}/{}".format(instance_url, settings.SALESFORCE_ENROLLMENT_API_PATH)
