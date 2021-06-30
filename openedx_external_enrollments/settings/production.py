"""
Production Django settings for openedx_external_enrollments project.
"""

from __future__ import unicode_literals


def plugin_settings(settings):
    """
    Set of plugin settings used by the Open Edx platform.
    More info: https://github.com/edx/edx-platform/blob/master/openedx/core/djangoapps/plugins/README.rst
    """
    settings.EDX_ENTERPRISE_API_CLIENT_ID = getattr(settings, 'ENV_TOKENS', {}).get(
        'EDX_ENTERPRISE_API_CLIENT_ID',
        settings.EDX_ENTERPRISE_API_CLIENT_ID,
    )
    settings.EDX_ENTERPRISE_API_CLIENT_SECRET = getattr(settings, 'ENV_TOKENS', {}).get(
        'EDX_ENTERPRISE_API_CLIENT_SECRET',
        settings.EDX_ENTERPRISE_API_CLIENT_SECRET,
    )
    settings.EDX_ENTERPRISE_API_CUSTOMER_UUID = getattr(settings, 'ENV_TOKENS', {}).get(
        'EDX_ENTERPRISE_API_CUSTOMER_UUID',
        settings.EDX_ENTERPRISE_API_CUSTOMER_UUID,
    )
    settings.EDX_ENTERPRISE_API_CATALOG_UUID = getattr(settings, 'ENV_TOKENS', {}).get(
        'EDX_ENTERPRISE_API_CATALOG_UUID',
        settings.EDX_ENTERPRISE_API_CATALOG_UUID,
    )
    settings.SALESFORCE_API_TOKEN_URL = getattr(settings, 'ENV_TOKENS', {}).get(
        'SALESFORCE_API_TOKEN_URL',
        settings.SALESFORCE_API_TOKEN_URL,
    )
    settings.SALESFORCE_API_CLIENT_ID = getattr(settings, 'ENV_TOKENS', {}).get(
        'SALESFORCE_API_CLIENT_ID',
        settings.SALESFORCE_API_CLIENT_ID,
    )
    settings.SALESFORCE_API_CLIENT_SECRET = getattr(settings, 'ENV_TOKENS', {}).get(
        'SALESFORCE_API_CLIENT_SECRET',
        settings.SALESFORCE_API_CLIENT_SECRET,
    )
    settings.SALESFORCE_ENROLLMENT_API_PATH = getattr(settings, 'ENV_TOKENS', {}).get(
        'SALESFORCE_ENROLLMENT_API_PATH',
        settings.SALESFORCE_ENROLLMENT_API_PATH,
    )
    settings.SALESFORCE_ENABLE_AUTHENTICATION = getattr(settings, 'ENV_TOKENS', {}).get(
        'SALESFORCE_ENABLE_AUTHENTICATION',
        settings.SALESFORCE_ENABLE_AUTHENTICATION,
    )
    settings.SALESFORCE_ENROLLMENT_BASIC_AUTH_USER = getattr(settings, 'ENV_TOKENS', {}).get(
        'SALESFORCE_ENROLLMENT_BASIC_AUTH_USER',
        settings.SALESFORCE_ENROLLMENT_BASIC_AUTH_USER,
    )
    settings.SALESFORCE_ENROLLMENT_BASIC_AUTH_PASSWORD = getattr(settings, 'ENV_TOKENS', {}).get(
        'SALESFORCE_ENROLLMENT_BASIC_AUTH_PASSWORD',
        settings.SALESFORCE_ENROLLMENT_BASIC_AUTH_PASSWORD,
    )
    settings.SALESFORCE_INSTANCE_URL = getattr(settings, 'ENV_TOKENS', {}).get(
        'SALESFORCE_INSTANCE_URL',
        settings.SALESFORCE_INSTANCE_URL,
    )
    settings.SALESFORCE_API_USERNAME = getattr(settings, 'ENV_TOKENS', {}).get(
        'SALESFORCE_API_USERNAME',
        settings.SALESFORCE_API_USERNAME,
    )
    settings.SALESFORCE_API_PASSWORD = getattr(settings, 'ENV_TOKENS', {}).get(
        'SALESFORCE_API_PASSWORD',
        settings.SALESFORCE_API_PASSWORD,
    )
    settings.DROPBOX_API_ARG_DOWNLOAD = getattr(settings, 'ENV_TOKENS', {}).get(
        'DROPBOX_API_ARG_DOWNLOAD',
        settings.DROPBOX_API_ARG_DOWNLOAD,
    )
    settings.DROPBOX_API_ARG_UPLOAD = getattr(settings, 'ENV_TOKENS', {}).get(
        'DROPBOX_API_ARG_UPLOAD',
        settings.DROPBOX_API_ARG_UPLOAD,
    )
    settings.DROPBOX_API_DOWNLOAD_URL = getattr(settings, 'ENV_TOKENS', {}).get(
        'DROPBOX_API_DOWNLOAD_URL',
        settings.DROPBOX_API_DOWNLOAD_URL,
    )
    settings.DROPBOX_API_UPLOAD_URL = getattr(settings, 'ENV_TOKENS', {}).get(
        'DROPBOX_API_UPLOAD_URL',
        settings.DROPBOX_API_UPLOAD_URL,
    )
    settings.DROPBOX_DATE_FORMAT = getattr(settings, 'ENV_TOKENS', {}).get(
        'DROPBOX_DATE_FORMAT',
        settings.DROPBOX_DATE_FORMAT,
    )
    settings.ICC_API_TOKEN = getattr(settings, 'ENV_TOKENS', {}).get(
        'ICC_API_TOKEN',
        settings.ICC_API_TOKEN,
    )
    settings.ICC_BASE_URL = getattr(settings, 'ENV_TOKENS', {}).get(
        'ICC_BASE_URL',
        settings.ICC_BASE_URL,
    )
    settings.ICC_ENROLLMENT_API_FUNCTION = getattr(settings, 'ENV_TOKENS', {}).get(
        'ICC_ENROLLMENT_API_FUNCTION',
        settings.ICC_ENROLLMENT_API_FUNCTION,
    )
    settings.ICC_GET_USER_API_FUNCTION = getattr(settings, 'ENV_TOKENS', {}).get(
        'ICC_GET_USER_API_FUNCTION',
        settings.ICC_GET_USER_API_FUNCTION,
    )
    settings.ICC_CREATE_USER_API_FUNCTION = getattr(settings, 'ENV_TOKENS', {}).get(
        'ICC_CREATE_USER_API_FUNCTION',
        settings.ICC_CREATE_USER_API_FUNCTION,
    )
    settings.ICC_LEARNER_ROLE_ID = getattr(settings, 'ENV_TOKENS', {}).get(
        'ICC_LEARNER_ROLE_ID',
        settings.ICC_LEARNER_ROLE_ID,
    )
    settings.ICC_HASH_LENGTH = getattr(settings, 'ENV_TOKENS', {}).get(
        'ICC_HASH_LENGTH',
        settings.ICC_HASH_LENGTH,
    )
    settings.MIT_HZ_API_URL = getattr(settings, 'ENV_TOKENS', {}).get(
        'MIT_HZ_API_URL',
        settings.MIT_HZ_API_URL,
    )
    settings.MIT_HZ_LOGIN_PATH = getattr(settings, 'ENV_TOKENS', {}).get(
        'MIT_HZ_LOGIN_PATH',
        settings.MIT_HZ_LOGIN_PATH,
    )
    settings.MIT_HZ_REFRESH_PATH = getattr(settings, 'ENV_TOKENS', {}).get(
        'MIT_HZ_REFRESH_PATH',
        settings.MIT_HZ_REFRESH_PATH,
    )
    settings.MIT_HZ_GET_USER_PATH = getattr(settings, 'ENV_TOKENS', {}).get(
        'MIT_HZ_GET_USER_PATH',
        settings.MIT_HZ_GET_USER_PATH,
    )
    settings.MIT_HZ_ID = getattr(settings, 'ENV_TOKENS', {}).get(
        'MIT_HZ_ID',
        settings.MIT_HZ_ID,
    )
    settings.MIT_HZ_SECRET = getattr(settings, 'ENV_TOKENS', {}).get(
        'MIT_HZ_SECRET',
        settings.MIT_HZ_SECRET,
    )
    settings.OEE_VIPER_MUTATIONS_API_KEY = getattr(settings, 'ENV_TOKENS', {}).get(
        'OEE_VIPER_MUTATIONS_API_KEY',
        settings.OEE_VIPER_MUTATIONS_API_KEY,
    )
    settings.OEE_VIPER_API_URL = getattr(settings, 'ENV_TOKENS', {}).get(
        'OEE_VIPER_API_URL',
        settings.OEE_VIPER_API_URL,
    )
    settings.OEE_VIPER_IDP = getattr(settings, 'ENV_TOKENS', {}).get(
        'OEE_VIPER_IDP',
        settings.OEE_VIPER_IDP,
    )
    settings.OEE_PATHSTREAM_S3_FILE = getattr(settings, 'ENV_TOKENS', {}).get(
        'OEE_PATHSTREAM_S3_FILE',
        settings.OEE_PATHSTREAM_S3_FILE,
    )
    settings.OEE_PATHSTREAM_S3_BUCKET = getattr(settings, 'ENV_TOKENS', {}).get(
        'OEE_PATHSTREAM_S3_BUCKET',
        settings.OEE_PATHSTREAM_S3_BUCKET,
    )
    settings.OOE_PATHSTREAM_S3_ACCESS_KEY = getattr(settings, 'ENV_TOKENS', {}).get(
        'OOE_PATHSTREAM_S3_ACCESS_KEY',
        settings.OOE_PATHSTREAM_S3_ACCESS_KEY,
    )
    settings.OOE_PATHSTREAM_S3_SECRET_KEY = getattr(settings, 'ENV_TOKENS', {}).get(
        'OOE_PATHSTREAM_S3_SECRET_KEY',
        settings.OOE_PATHSTREAM_S3_SECRET_KEY,
    )
