"""
Api URLs.
"""
from django.conf.urls import include, url

app_name = 'api'
urlpatterns = [  # pylint: disable=invalid-name
    url(r'v0/', include(('openedx_external_enrollments.api.v0.urls', app_name), namespace='v0')),
]
