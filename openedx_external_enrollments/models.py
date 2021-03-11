"""
Model module
"""
from django.db import models
from jsonfield.fields import JSONField

from openedx.core.djangoapps.content.course_overviews.models import CourseOverview


class ProgramSalesforceEnrollment(models.Model):
    """
    Model to persist salesforce enrollment course / program configurations.
    """

    bundle_id = models.CharField(max_length=48, unique=True)
    meta = JSONField(null=False, blank=True)

    class Meta(object):
        """
        Model meta class.
        """
        app_label = "openedx_external_enrollments"

    def __unicode__(self):
        return self.bundle_id


class EnrollmentRequestLog(models.Model):
    """
    Model to persist enrollment requests
    """

    request_type = models.CharField(max_length=10)
    details = JSONField(null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(object):
        """
        Model meta class.
        """
        app_label = "openedx_external_enrollments"


class OtherCourseSettings(models.Model):
    """
    Model to persist other course settings.
    """

    course_overview = models.OneToOneField(
        CourseOverview,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    external_course_id = models.CharField(max_length=50, null=False, blank=True)
    external_platform = models.CharField(max_length=20, null=False, blank=True)

    class Meta(object):
        """
        Model meta class.
        """
        app_label = "openedx_external_enrollments"

    def __str__(self):
        return str(course_overview.id)
