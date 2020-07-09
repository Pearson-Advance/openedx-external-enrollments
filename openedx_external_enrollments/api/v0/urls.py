"""
openedx_proversity_reports  API URL Configuration
"""
from django.conf.urls import url

from . import views

REPORT_NAME_PATTERN = r'(?P<report_name>(generate)+[a-z-]+)'

urlpatterns = [
    url(
        r'^external-enrollment$',
        views.ExternalEnrollment.as_view(),
        name='external-enrollment',
    ),
    url(
        r'^salesforce-enrollment$',
        views.SalesforceEnrollmentView.as_view(),
        name='salesforce-enrollment',
    ),
    url(
        r'^enrollment$',
        views.CoreEnrollmentListView.as_view(),
        name='shell-enrollment',
    ),
]
