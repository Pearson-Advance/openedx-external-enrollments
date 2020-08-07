"""
Test Django settings for openedx_external_enrollments project.
"""

from __future__ import unicode_literals

from .common import *  # pylint: disable=wildcard-import

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    },
}

INSTALLED_APPS += ['openedx_external_enrollments']

OEE_COURSEWARE_BACKEND = 'openedx_external_enrollments.tests.tests_backends'
OEE_EDX_REST_FRAMEWORK_EXTENSIONS = 'openedx_external_enrollments.tests.tests_backends'
OEE_OPENEDX_PERMISSIONS = 'openedx_external_enrollments.tests.tests_backends'
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

DROPBOX_API_ARG_DOWNLOAD = '%s-download'
DROPBOX_API_DOWNLOAD_URL = 'dropbox-tets-api-download-url'
DROPBOX_API_ARG_UPLOAD = '%s-upload'
DROPBOX_API_UPLOAD_URL = 'dropbox-tets-api-upload-url'
DROPBOX_DATE_FORMAT = '%m-%d-%Y %H:%M:%S'
