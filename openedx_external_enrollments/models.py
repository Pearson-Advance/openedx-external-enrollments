"""
Model module
"""
from django.db import models
from jsonfield.fields import JSONField

from opaque_keys.edx.django.models import CourseKeyField


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
    course_id = CourseKeyField(db_index=True, primary_key=True, max_length=255)
    external_course_id = models.CharField(max_length=255, null=True, blank=True)
    external_platform = models.CharField(max_length=255, null=True, blank=True)
    other_course_settings = JSONField(null=True, blank=True)

    class Meta(object):
        """
        Model meta class.
        """
        app_label = "openedx_external_enrollments"
        verbose_name_plural = "Other course settings"

    def __str__(self):
        return str(self.course_id)
