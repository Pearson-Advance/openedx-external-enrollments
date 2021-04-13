"""This file contains all the necessary backend in a test scenario."""
from mock import Mock


class ApiKeyHeaderPermissionIsAuthenticated():
    """Test class for openedx.core.lib.api.permissions.ApiKeyHeaderPermissionIsAuthenticated"""


class JwtAuthentication():
    """Test class for edx_rest_framework_extensions.auth.jwt.authentication.JwtAuthentication"""


class OAuth2Authentication():
    """Test class for openedx.core.lib.api.authentication.OAuth2Authentication."""


def get_course_enrollment_backend():
    """Test get_course_enrollment_backend method."""


def get_configuration_helpers():
    """Test get_configuration_helpers method."""


def get_course_mode():
    """Test get_course_mode method."""


def get_enrollment_track_updated_signal():
    """Test get_enrollment_track_updated_signal method."""
    return Mock()


def get_unenroll_done_signal():
    """Test get_unenroll_done_signal method."""
    return Mock()
