"""
Script for exporting all courses from Mongo to a othercoursesettings table in edxapp database.
"""
from django.core.management.base import BaseCommand

from openedx_external_enrollments.edxapp_wrapper.get_course_settings import migrate_course_settings


class Command(BaseCommand):
    """
    Migrate all courses via django command.
    Required command arguments:
        delay_seconds(first int argument) -> sleep time in seconds.
        group_length(second int argument) -> courses group length to iterate.
    Example:  'python manage.py cms migrate_other_course_settings -ds 2 -gl 2'.
    """
    help = """Export all courses from mongo to migrate into OtherCourseSettings table.
    Example: \'python manage.py cms migrate_other_course_settings -ds 30 -gl 10\'.
    """
    DEFAULT_DELAY_SECONDS = 60  # arbitrary, should be adjusted if it is found to be inadequate.
    DEFAULT_GROUP_LENGTH = 20  # arbitrary, should be adjusted if it is found to be inadequate.

    def add_arguments(self, parser):
        """
        Required command arguments:
        delay_seconds -> sleep time in seconds.
        group_length -> courses group length to iterate.
        """
        parser.add_argument(
            '-ds', '--delay_seconds',
            type=int,
            help='Sleep time in seconds.',
            default=self.DEFAULT_DELAY_SECONDS,
        )
        parser.add_argument(
            '-gl', '--group_length',
            type=int,
            help='Courses group length to iterate.',
            default=self.DEFAULT_GROUP_LENGTH,
        )

    def handle(self, *args, **options):  # pylint: disable=unused-argument
        """
        Execute the command.
        This function calls migrate_course_settings from backends.
        """
        migrate_course_settings(
            delay_seconds=options.get('delay_seconds'),
            group_length=options.get('group_length'),
        )
