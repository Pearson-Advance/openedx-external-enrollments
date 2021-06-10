"""
Model module
"""
from django.db import models
from jsonfield.fields import JSONField
from opaque_keys.edx.django.models import CourseKeyField

from openedx_external_enrollments.edxapp_wrapper.course_module import get_course_overview


class ProgramSalesforceEnrollment(models.Model):
    """
    Model to persist salesforce enrollment course / program configurations.
    """

    bundle_id = models.CharField(max_length=48, unique=True)
    meta = JSONField(null=False, blank=True)

    class Meta:
        """
        Model meta class.
        """
        app_label = "openedx_external_enrollments"

    def __unicode__(self):
        return self.bundle_id


class EnrollmentRequestLog(models.Model):
    """
    Model to persist enrollment requests.
    """

    request_type = models.CharField(max_length=10)
    details = JSONField(null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Model meta class.
        """
        app_label = "openedx_external_enrollments"


class OtherCourseSettings(models.Model):
    """
    Model to persist other course settings.
    """
    course = models.ForeignKey(get_course_overview(), on_delete=models.CASCADE, related_name='course_settings')
    external_course_id = models.CharField(max_length=255, null=True, blank=True)
    external_platform = models.CharField(max_length=255, null=True, blank=True)
    other_course_settings = JSONField(null=True, blank=True)

    class Meta:
        """
        Model meta class.
        """
        app_label = "openedx_external_enrollments"
        verbose_name_plural = "Other course settings"

    def __str__(self):
        return str(self.course)


class ExternalEnrollment(models.Model):
    """
    Model to persist external enrollments.
    This model is thought for special cases where enrollments have invitation links for example and this will
    help to retrieve the course URL when the learner will try to access the course content.

    Fields:
        meta: stores the relevant data from the enrollment. e.g:
            {
                'course_id': 'external-course-id',
                'class_id': 'external-class-id',
                'course_url': 'external-course-launch-target',
            }
    """
    controller_name = models.CharField(max_length=50)
    course_shell_id = CourseKeyField(max_length=255)
    email = models.EmailField()
    meta = JSONField(null=False, blank=True)

    class Meta:
        """
        Model meta class.
        """
        app_label = "openedx_external_enrollments"
