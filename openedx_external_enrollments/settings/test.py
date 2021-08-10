"""
Test Django settings for openedx_external_enrollments project.
"""

from __future__ import unicode_literals

from .common import *  # pylint: disable=wildcard-import

# Disables migrations due to OtherCourseSettings table migration depends on an edx-platform migration file.
MIGRATION_MODULES = {
    'openedx_external_enrollments': None,
}
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    },
}

INSTALLED_APPS += ['openedx_external_enrollments']

OEE_COURSEWARE_BACKEND = 'openedx_external_enrollments.tests.tests_backends'
OEE_COURSE_BACKEND = 'openedx_external_enrollments.tests.tests_backends'
OEE_EDX_REST_FRAMEWORK_EXTENSIONS = 'openedx_external_enrollments.tests.tests_backends'
OEE_OPENEDX_PERMISSIONS = 'openedx_external_enrollments.tests.tests_backends'
OEE_OPENEDX_AUTH = 'openedx_external_enrollments.tests.tests_backends'
OEE_SITE_CONFIGURATION_BACKEND = 'openedx_external_enrollments.tests.tests_backends'
OEE_STUDENT_BACKEND = 'openedx_external_enrollments.tests.tests_backends'

EDX_API_KEY = 'edx-text-api-key'
EDX_ENTERPRISE_API_CLIENT_ID = 'edx-test-api-client-id'
EDX_ENTERPRISE_API_CLIENT_SECRET = 'edx-test-api-client-secret'
EDX_ENTERPRISE_API_TOKEN_URL = 'edx-test-api-token'
EDX_ENTERPRISE_API_CUSTOMER_UUID = 'edx-test-api-customer-uuid'
EDX_ENTERPRISE_API_BASE_URL = 'edx-test-api-base-url'

SALESFORCE_API_CLIENT_ID = 'salesforce-test-api-client-id'
SALESFORCE_API_CLIENT_SECRET = 'salesforce-test-api-client-secret'
SALESFORCE_API_PASSWORD = 'salesforce-test-password'
SALESFORCE_API_USERNAME = 'salesforce-test-username'
SALESFORCE_API_TOKEN_URL = 'salesforce-test-api-token'
SALESFORCE_ENROLLMENT_API_PATH = 'salesforce-enrollment-api-path'
SALESFORCE_INSTANCE_URL = "salesforce-instance-url"
SALESFORCE_ENABLE_AUTHENTICATION = True

DROPBOX_API_ARG_DOWNLOAD = '%s-download'
DROPBOX_API_DOWNLOAD_URL = 'dropbox-tets-api-download-url'
DROPBOX_API_ARG_UPLOAD = '%s-upload'
DROPBOX_API_UPLOAD_URL = 'dropbox-tets-api-upload-url'
DROPBOX_DATE_FORMAT = '%m-%d-%Y %H:%M:%S'

MIT_HZ_API_URL = 'root-url'
MIT_HZ_LOGIN_PATH = '/partner_api/login'
MIT_HZ_GET_USER_PATH = '/partner_api/pearson/user?user_id='
MIT_HZ_REFRESH_PATH = '/partner_api/pearson/refresh_user'
MIT_HZ_ID = 'login-id'
MIT_HZ_SECRET = 'secret-key'

ICC_CREATE_USER_API_FUNCTION = 'icc-create-user-api-function'
ICC_ENROLLMENT_API_FUNCTION = 'icc-enrollment-api-function'
ICC_API_TOKEN = 'icc-api-token'
ICC_LEARNER_ROLE_ID = '5'
ICC_BASE_URL = "icc-base-url"
ICC_HASH_LENGTH = 10
ICC_AUTH_METHOD = "test-auth-method"

OEE_VIPER_IDP = 'okta'
OEE_VIPER_MUTATIONS_API_KEY = 'viper-mutations-api-key'
OEE_VIPER_API_URL = 'https://viper-api-url'

OEE_PATHSTREAM_S3_FILE = 'test.log'
OEE_PATHSTREAM_S3_BUCKET = 'test'
OOE_PATHSTREAM_S3_ACCESS_KEY = 'access_key'
OOE_PATHSTREAM_S3_SECRET_KEY = 'secret_access_key'
