"""Backend for course settings module."""
import logging
import time

from cms.djangoapps.models.settings.course_metadata import CourseMetadata
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from openedx_external_enrollments.models import OtherCourseSettings
from xmodule.modulestore.django import modulestore

LOG = logging.getLogger(__name__)


def update_course_settings(*args, **kwargs):  # pylint: disable=unused-argument
    """
    Updates external_course_id and external_platform from a course overview.
    This function is called from edx-platform once advance course settings is successfully saved.
    """
    try:
        other_course_settings = kwargs.get('other_course_settings', {})

        OtherCourseSettings.objects.update_or_create(
            course_overview=CourseOverview.get_from_id(kwargs.get('course_key')),
            defaults={
                'external_course_id': other_course_settings.get('external_course_run_id', ''),
                'external_platform': other_course_settings.get('external_platform_target', ''),
            },
        )
    except Exception as error:  # pylint: disable=broad-except
        LOG.error('Failed to update course_settings in the backend. Reason: %s', str(error))


def migrate_course_settings(*args, **kwargs):  # pylint: disable=unused-argument
    """
    Migrates all course settings to OtherCourseSettings table in edxapp database.
    delay_seconds -> sleep time in seconds.
    group_length -> number of courses to be migrated by groups.
    """
    migrated_courses = []

    try:
        group_counter = 0

        for course in modulestore().get_courses():
            group_counter += 1
            course_overview = CourseOverview.get_from_id(course.id)
            other_course_settings = CourseMetadata.fetch(course).get('other_course_settings', {}).get('value', {})

            # Only save or update courses that have other_course_settings configurations.
            if other_course_settings and other_course_settings.get('external_course_run_id'):
                migrated_courses.append(str(course_overview.id))
                OtherCourseSettings.objects.update_or_create(
                    course_overview=course_overview,
                    defaults={
                        'external_course_id': other_course_settings.get('external_course_run_id', ''),
                        'external_platform': other_course_settings.get('external_platform_target', ''),
                    },
                )

            # Sleeps in every group_length reach to avoid database from crashing.
            if group_counter % kwargs.get('group_length') == 0:
                print('Waiting for %s seconds...' % kwargs.get('delay_seconds'))
                time.sleep(kwargs.get('delay_seconds'))

        print('=' * 80)
        print('=' * 30 + '> Migration group')
        print('Total number of courses migrated or updated: %s\n' % len(migrated_courses))
        print('\n'.join(migrated_courses))
        print('=' * 80)
    except Exception as error:  # pylint: disable=broad-except
        print('=' * 80)
        print('This command should be run via cms. Example:\'python manage.py cms migrate_other_course_settings 5 6\'.')
        print('ERROR: %s' % error)
