"""
Course home concrete module
"""
import datetime

import pytz
import requests
from courseware.courses import get_course_by_id  # pylint: disable=import-error
from django.conf import settings
from opaque_keys.edx.keys import CourseKey
from student.models import CourseEnrollment, anonymous_id_for_user  # pylint: disable=import-error
from submissions import api as submissions_api  # pylint: disable=import-error

from openedx_external_enrollments.models import ExternalEnrollment

DAYS_IN_WEEK = 7


def calculate_course_home(course_id, user):
    """
    Calculate course home.
    """
    course_key = CourseKey.from_string(course_id)
    user_is_enrolled = CourseEnrollment.is_enrolled(user, course_key)

    if not user_is_enrolled:
        return None

    course = get_course_by_id(course_key)
    custom_course_settings = course.other_course_settings
    course_entry_points = custom_course_settings.get("course_entry_points", [])
    enrollment = CourseEnrollment.get_enrollment(user, course_key)
    custom_entry_point = _calculate_entry_point(course, course_id, course_key, course_entry_points, user, enrollment)

    if custom_entry_point:
        return custom_entry_point

    if is_external_course(course_id):
        if custom_course_settings.get('external_platform_target') == 'viper':
            return get_viper_course_target(course_key, user)
        return custom_course_settings.get("external_course_target")

    return None


def is_external_course(course_id):
    """
    Decide if the course was confiured as external or not.
    """
    course_key = CourseKey.from_string(course_id)
    course = get_course_by_id(course_key)
    custom_course_settings = course.other_course_settings

    return (
        custom_course_settings.get("external_course_run_id") and
        custom_course_settings.get("external_platform_target")
    )


def _calculate_entry_point(course, course_id, course_key, course_entry_points, user, enrollment):
    """
    Decides which entry point is currently valid for the course
    and returns its URL.
    """
    url = None

    # Calculate student start for the current course
    if course.self_paced:
        dates_to_check = [enrollment.created, course.start]
        student_start = max(dates_to_check)
    else:
        student_start = course.start

    current_entry_point = _get_current_entry_point(course_entry_points, student_start)

    if current_entry_point and not _check_entry_point_completion(current_entry_point, user, course_key, course_id):
        url = "/courses/{}/jump_to_id/{}".format(course_id, current_entry_point.get("block_id"))

    return url


def _get_current_entry_point(course_entry_points, student_start_date):
    """
    Returns a valid entry point within a list of points.
    Otherwise returns None.
    """
    entry_point = None
    difference = datetime.datetime.utcnow().replace(tzinfo=pytz.utc) - student_start_date
    days_since_course_start = difference.days

    for point in course_entry_points:
        valid_from_day = int(point.get("valid_from_week", 0)) * DAYS_IN_WEEK
        valid_through_day = int(point.get("valid_through_week", 0)) * DAYS_IN_WEEK

        if valid_from_day <= 0:
            is_current_point = 0 <= days_since_course_start <= valid_through_day
        else:
            is_current_point = valid_from_day < days_since_course_start <= valid_through_day

        if is_current_point:
            entry_point = point
            break

    return entry_point


def _check_entry_point_completion(point, user, course_key, course_id):
    """
    Checks if there is a submission entry related with the given point and course for the user.
    """
    student_item = dict(
        student_id=anonymous_id_for_user(user, course_key),
        course_id=course_id,
        item_id=point.get("block_id"),
        item_type=point.get("block_type"),
    )

    return bool(submissions_api.get_submissions(student_item))


def get_viper_course_target(course_id, user):
    """
    Return a valid external course target for Viper enrollments.
    """
    CONTROLLER_NAME = 'viper'

    try:
        enrollment = ExternalEnrollment.objects.get(  # pylint: disable=no-member
            controller_name=CONTROLLER_NAME,
            course_shell_id=course_id,
            email=user.email
        )
    except ExternalEnrollment.DoesNotExist:  # pylint: disable=no-member
        return None

    if enrollment.meta.get('is_active') and 'invitations' not in enrollment.meta.get('course_url'):
        return enrollment.meta.get('course_url')

    # Retrieve the invitation/course url through an enrollment.
    # This operation will happen until invitation link is replaced by the actual course enrollment target.
    try:
        response = requests.post(
            url=settings.OEE_VIPER_API_URL,
            headers={
                'x-api-key': settings.OEE_VIPER_MUTATIONS_API_KEY,
            },
            json={
                'action': 'createEnrolment',
                'variables': {
                    'classId': enrollment.meta.get('class_id'),
                    'courseId': enrollment.meta.get('course_id'),
                    'email': user.email,
                    'name': user.profile.name,
                    'provider': settings.OEE_VIPER_IDP,
                },
            },
        )
    except Exception:  # pylint: disable=broad-except
        # LOG
        course_url = None
    else:
        course_url = response.json().get('link')

    # Update the Viper course URL in the enrollment record in order to retrieve it directly.
    enrollment.meta['course_url'] = course_url
    enrollment.meta['is_active'] = True
    enrollment.save()

    return course_url
