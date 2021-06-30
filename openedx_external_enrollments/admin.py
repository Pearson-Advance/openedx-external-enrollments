"""
Django admin page
"""
from django.contrib import admin

from openedx_external_enrollments.models import (
    EnrollmentRequestLog,
    ExternalEnrollment,
    OtherCourseSettings,
    PathstreamEnrollment,
    ProgramSalesforceEnrollment,
)


class ReadOnlyAdminMixin:
    """
    Mixin class to make a model read only on Django admin.
    """

    def has_add_permission(self, request):  # pylint: disable=unused-argument
        """Method that handles add permissions."""
        return False

    def has_change_permission(self, request, obj=None):  # pylint: disable=unused-argument
        """Method that handles change permissions."""
        return False

    def has_delete_permission(self, request, obj=None):  # pylint: disable=unused-argument
        """Method that handles delete permissions."""
        return False


@admin.register(ProgramSalesforceEnrollment)
class ProgramSalesforceEnrollmentAdmin(admin.ModelAdmin):
    """
    Program salesforce enrollment model admin.
    """
    list_display = [
        'bundle_id',
    ]

    search_fields = ('bundle_id', 'meta',)


@admin.register(EnrollmentRequestLog)
class EnrollmentRequestLogAdmin(admin.ModelAdmin):
    """
    Enrollment request model admin.
    """
    list_display = [
        'request_type',
        'created_at',
        'updated_at',
    ]

    search_fields = ('request_type', 'details',)


@admin.register(OtherCourseSettings)
class OtherCourseSettingsAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """
    OtherCourseSettings model admin.
    """
    list_display = [
        'course_id',
        'external_course_id',
        'external_platform',
    ]

    search_fields = ('course__id', 'external_course_id', 'external_platform')


@admin.register(ExternalEnrollment)
class ExternalEnrollmentAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """
    OtherCourseSettings model admin.
    """
    list_display = [
        'controller_name',
        'course_shell_id',
        'email',
        'meta',
    ]

    search_fields = ('controller_name', 'course_shell__id', 'email')


@admin.register(PathstreamEnrollment)
class PathstreamEnrollmentAdmin(admin.ModelAdmin):
    """
    PathstreamEnrollment model admin.
    """
    list_display = [
        'controller_name',
        'course_shell_id',
        'email',
        'meta',
        'is_uploaded',
    ]

    search_fields = ('controller_name', 'course_shell__id', 'email', 'is_uploaded')
