"""
Common Django settings for openedx_external_enrollments project.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

from __future__ import unicode_literals

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'secret-key'


# Application definition

INSTALLED_APPS = []

ROOT_URLCONF = 'openedx_external_enrollments.urls'


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_TZ = True


def plugin_settings(settings):
    """
    Set of plugin settings used by the Open Edx platform.
    More info: https://github.com/edx/edx-platform/blob/master/openedx/core/djangoapps/plugins/README.rst
    """
    settings.OEE_COURSEWARE_BACKEND = 'openedx_external_enrollments.edxapp_wrapper.backends.courseware_i_v1'
    settings.OEE_EDX_REST_FRAMEWORK_EXTENSIONS = \
        'openedx_external_enrollments.edxapp_wrapper.backends.edx_rest_framework_extensions_i_v1'
    settings.OEE_OPENEDX_PERMISSIONS = 'openedx_external_enrollments.edxapp_wrapper.backends.openedx_permissions_i_v1'
    settings.OEE_COURSE_HOME_MODULE = 'openedx_external_enrollments.edxapp_wrapper.backends.course_home_i_v1'
    settings.OEE_COURSE_HOME_CALCULATOR = \
        'openedx_external_enrollments.edxapp_wrapper.get_course_home.calculate_course_home'
    settings.OEE_SITE_CONFIGURATION_BACKEND = \
        'openedx_external_enrollments.edxapp_wrapper.backends.site_configuration_module_i_v1'
    settings.OEE_STUDENT_BACKEND = 'openedx_external_enrollments.edxapp_wrapper.backends.student_i_v1'
    settings.EDX_ENTERPRISE_API_CLIENT_ID = "client-id"
    settings.EDX_ENTERPRISE_API_CLIENT_SECRET = "client-secret"
    settings.EDX_ENTERPRISE_API_TOKEN_URL = "https://api.edx.org/oauth2/v1/access_token"
    settings.EDX_ENTERPRISE_API_BASE_URL = "https://api.edx.org/enterprise/v1"
    settings.EDX_ENTERPRISE_API_CUSTOMER_UUID = "customer-id"
    settings.EDX_ENTERPRISE_API_CATALOG_UUID = "catalog-id"
    settings.SALESFORCE_API_TOKEN_URL = "salesforce-api-url"
    settings.SALESFORCE_API_CLIENT_ID = "salesforce-client-id"
    settings.SALESFORCE_API_CLIENT_SECRET = "salesforce-client-secret"
    settings.SALESFORCE_API_USERNAME = "salesforce-username"
    settings.SALESFORCE_API_PASSWORD = "salesforce-password"
    settings.SALESFORCE_ENABLE_AUTHENTICATION = False
    settings.SALESFORCE_INSTANCE_URL =  "https://api-us-c.pgi.pearsondev.tech"
    settings.SALESFORCE_ENROLLMENT_API_PATH = "pa-edx/lead"
    settings.DROPBOX_API_ARG_DOWNLOAD = '{"path":"%s"}'
    settings.DROPBOX_API_DOWNLOAD_URL = "/files/download"
    settings.DROPBOX_API_ARG_UPLOAD = '{"path":"%s","mode":{".tag":"overwrite"}}'
    settings.DROPBOX_API_UPLOAD_URL = "/files/upload"
    settings.DROPBOX_DATE_FORMAT = "%m-%d-%Y %H:%M:%S"
