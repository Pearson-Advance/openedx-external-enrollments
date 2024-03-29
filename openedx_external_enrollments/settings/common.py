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


def plugin_settings(settings):  # pylint: disable=R0915
    """
    Set of plugin settings used by the Open Edx platform.
    More info: https://github.com/edx/edx-platform/blob/master/openedx/core/djangoapps/plugins/README.rst
    """
    settings.OEE_COURSEWARE_BACKEND = 'openedx_external_enrollments.edxapp_wrapper.backends.courseware_i_v1'
    settings.OEE_COURSE_BACKEND = 'openedx_external_enrollments.edxapp_wrapper.backends.course_module_j_v1'
    settings.OEE_EDX_REST_FRAMEWORK_EXTENSIONS = \
        'openedx_external_enrollments.edxapp_wrapper.backends.edx_rest_framework_extensions_i_v1'
    settings.OEE_OPENEDX_PERMISSIONS = 'openedx_external_enrollments.edxapp_wrapper.backends.openedx_permissions_i_v1'
    settings.OEE_OPENEDX_AUTH = 'openedx_external_enrollments.edxapp_wrapper.backends.openedx_authentication_j_v1'
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
    settings.SALESFORCE_ENROLLMENT_BASIC_AUTH_USER = ""
    settings.SALESFORCE_ENROLLMENT_BASIC_AUTH_PASSWORD = ""
    settings.SALESFORCE_INSTANCE_URL = "https://api-us-c.pgi.pearsondev.tech"
    settings.SALESFORCE_ENROLLMENT_API_PATH = "pa-edx/lead"
    settings.DROPBOX_API_ARG_DOWNLOAD = '{"path":"%s"}'
    settings.DROPBOX_API_DOWNLOAD_URL = "/files/download"
    settings.DROPBOX_API_ARG_UPLOAD = '{"path":"%s","mode":{".tag":"overwrite"}}'
    settings.DROPBOX_API_UPLOAD_URL = "/files/upload"
    settings.DROPBOX_DATE_FORMAT = "%m-%d-%Y %H:%M:%S"
    settings.ICC_API_TOKEN = "icc-api-token"
    settings.ICC_BASE_URL = "https://icchas11.stage.kineoplatforms.net/webservice/rest/server.php"
    settings.ICC_ENROLLMENT_API_FUNCTION = "enrol_manual_enrol_users"
    settings.ICC_GET_USER_API_FUNCTION = "core_user_get_users"
    settings.ICC_CREATE_USER_API_FUNCTION = "core_user_create_users"
    settings.ICC_LEARNER_ROLE_ID = "5"
    settings.ICC_HASH_LENGTH = 10
    settings.ICC_AUTH_METHOD = "saml2"
    settings.OEE_COURSE_SETTINGS_MODULE = "openedx_external_enrollments.edxapp_wrapper.backends.course_settings_j_v1"
    settings.OEE_UPDATE_COURSE_SETTINGS = \
        "openedx_external_enrollments.edxapp_wrapper.get_course_settings.update_course_settings"
    settings.MIT_HZ_API_URL = "https://mit-horizon-staging.herokuapp.com"
    settings.MIT_HZ_LOGIN_PATH = "/partner_api/login"
    settings.MIT_HZ_GET_USER_PATH = "/partner_api/pearson/user?user_id="
    settings.MIT_HZ_REFRESH_PATH = "/partner_api/pearson/refresh_user"
    settings.MIT_HZ_ID = "mit-hz-id"
    settings.MIT_HZ_SECRET = "mit-hz-secret"
    settings.OEE_VIPER_MUTATIONS_API_KEY = 'viper-mutations-api-key'
    settings.OEE_VIPER_API_URL = 'https://vip-demo-api.virtual-academies.com/holistic'
    settings.OEE_VIPER_IDP = 'okta'
    settings.OEE_PATHSTREAM_S3_FILE = 'pathstream_external_enrollments.log'
    settings.OEE_PATHSTREAM_S3_BUCKET = 'remoteloggerpathstream'
    settings.OOE_PATHSTREAM_S3_ACCESS_KEY = 'access_key'
    settings.OOE_PATHSTREAM_S3_SECRET_KEY = 'secret_access_key'
    settings.OOE_PATHSTREAM_S3_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
