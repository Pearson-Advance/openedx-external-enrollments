"""SalesforceEnrollment class file."""
import datetime

from django.conf import settings
from oauthlib.oauth2 import BackendApplicationClient
from opaque_keys.edx.keys import CourseKey
from requests_oauthlib import OAuth2Session

from openedx_external_enrollments.edxapp_wrapper.get_courseware import get_course_by_id
from openedx_external_enrollments.edxapp_wrapper.get_student import CourseEnrollment, get_user
from openedx_external_enrollments.external_enrollments.base_external_enrollment import BaseExternalEnrollment
from openedx_external_enrollments.models import ProgramSalesforceEnrollment


class SalesforceEnrollment(BaseExternalEnrollment):
    """
    SalesforceEnrollment class.
    """

    def __str__(self):
        return "salesforce"

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

    def _get_enrollment_headers(self):
        token = self._get_auth_token()
        return {
            "Content-Type": "application/json",
            "Authorization": "{} {}".format(
                token.get("token_type"),
                token.get("access_token"),
            )
        }

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
                # TODO do not force logic assuming names with 2 words
                first_name, last_name = openedx_profile.name.split(" ", 1)
                user["FirstName"] = first_name.strip(" ")
                user["LastName"] = last_name.strip(" ")
                user["Email"] = email
            except Exception:  # pylint: disable=broad-except
                pass

        return user

    def _get_salesforce_data(self, data):
        """

        :param data:
        :return:
        """
        salesforce_data = {}
        order_lines = data.get("supported_lines")
        if order_lines:
            try:
                salesforce_data.update(self._get_program_of_interest_data(data, order_lines))
                salesforce_data["Order_Number"] = data.get("number")
                salesforce_data["Purchase_Type"] = "Program" if data.get("program") else "Course"
                salesforce_data["PaymentAmount"] = data.get("paid_amount")
                salesforce_data["Amount_Currency"] = data.get("currency")
            except Exception:  # pylint: disable=broad-except
                pass

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
                single_course = order_lines[0]
                course = self._get_course(single_course.get("course_id"))
                program_of_interest = course.other_course_settings.get("salesforce_data")
                program_of_interest["Drupal_ID"] = "enrollment+course+{}+{}".format(
                    openedx_user.username,
                    request_time.strftime("%Y-%m-%d-%H:%M:%S"),
                )

            program_of_interest["utm_params"] = data.get(
                "utm_source",
                program_of_interest.get("utm_params", "Open edX API"),
            )
            program_of_interest["Secondary_Source"] = data.get(
                "utm_campaign",
                program_of_interest.get("Secondary_Source", ""),
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
        courses = []
        for line in order_lines:
            try:
                course_id = line.get("course_id")
                course = self._get_course(course_id)
                salesforce_settings = course.other_course_settings.get("salesforce_data")
                course_data = dict()
                course_data["CourseName"] = salesforce_settings.get("Program_Name") or course.display_name
                course_data["CourseID"] = course_id
                course_data["CourseRunID"] = self._get_salesforce_course_id(course, course_id)
                course_data["CourseStartDate"] = self._get_course_start_date(course, line.get("user_email"), course_id)
                course_data["CourseEndDate"] = course.end.strftime("%Y-%m-%d")
            except Exception:  # pylint: disable=broad-except
                pass
            else:
                courses.append(course_data)

        return courses

    def _get_salesforce_course_id(self, course, internal_id):
        """
        Returns either an external course id or internal.
        """
        if self._is_external_course(course):
            return course.other_course_settings.get("external_course_run_id")

        return internal_id

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
            "utm_params",
            "Secondary_Source",
            "Drupal_ID",
            "Order_Number",
            "Purchase_Type",
            "PaymentAmount",
            "Amount_Currency",
            "Course_Data",
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
        for unwanted_key in unwanted:
            del payload["enrollment"][unwanted_key]

        return payload

    def _get_enrollment_url(self, course_settings):
        """
        """
        token = self._get_auth_token()
        return "{}/{}".format(token.get('instance_url'), settings.SALESFORCE_ENROLLMENT_API_PATH)
