"""
Django admin page
"""
from django.contrib import admin

from openedx_external_enrollments.models import EnrollmentRequestLog, ProgramSalesforceEnrollment, OtherCourseSettings


class ProgramSalesforceEnrollmentAdmin(admin.ModelAdmin):
    """
    Program salesforce enrollment model admin.
    """
    list_display = [
        'bundle_id',
    ]

    search_fields = ('bundle_id', 'meta',)


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


class OtherCourseSettingsAdmin(admin.ModelAdmin):
    """
    OtherCourseSettings model admin.
    """
    list_display = [
        'course_id',
        'external_course_id',
        'external_platform',
    ]

    search_fields = ('course_id', 'external_course_id',)


admin.site.register(EnrollmentRequestLog, EnrollmentRequestLogAdmin)
admin.site.register(ProgramSalesforceEnrollment, ProgramSalesforceEnrollmentAdmin)
admin.site.register(OtherCourseSettings, OtherCourseSettingsAdmin)
