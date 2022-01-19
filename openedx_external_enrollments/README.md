# openedx_external_enrollments

Principal directory that contains code relating to the openedx_external_enrollments.

## Directorys

- api: This Application Programming Interface (api) has the views of the Features of this plugin and their respective URLs.

- edx_wrapper: This directory contains modules with the functionality of the edx-platform once the platform backends have been imported with absolute paths.

- external_enrollments:

|Module                            |Functionality                                                          |
|----------------------------------|-----------------------------------------------------------------------|
|base_external_enrollment          | Module with the base class for all external enrollments where _get_enrollment_headers, _get_enrollment_data, _get_enrollment_url are defined in other modules to execute _post_enrollment from base_external_enrollment.|
|edx_enterprise_external_enrollment| This module contains EdxEnterpriseExternalEnrollment class to get enrollments from edX enterprise, executing a signal.|                                                        |edx_instance_external_enrollment  | This module contains EdxInstanceExternalEnrollment class.|
|greenfig_external_enrollment      | This module contains GreenfigInstanceExternalEnrollment class with the functionality regarding dropbox, executing a signal.|
|icc_external_enrollment           | This module contains ICCExternalEnrollment class with the functionality to enroll users in ICC, executing a signal.| 
|mit_hz_external_enrollment        | This module contains MITHzInstanceExternalEnrollment class with the functionality to enroll users in MITHz, executing a signal.|
|pathstream_external_enrollment    | This module contains PathstreamExternalEnrollment class with the functionality to enroll users in Pathstream, executing a signal.|
|salesforce_external_enrollment    | This module contains SalesforceEnrollment class. Unlike the other OEE integrations, it runs from ecommerce and asynchronously executing a task from tasks module.|
|viper_external_enrollment         | This module contains ViperExternalEnrollment class with the functionality to enroll users in viper, executing a signal.|

- management: This directory contains modules related with the manage of the plugin. For example, Migrate all courses via django command.

- migrations: This directory contains modules related with the the different migrations that have been made.

- settings: This directory contains modules with all the settings used by the Open Edx platform and AWS Django settings for openedx_external_enrollments project.

- Tests: This directory contains all tests realated with openedx_external_enrollments.

## Modules

- admin: This module contains everything related to the Django admin page.

- apps: In this module is the App configuration for openedx_external_enrollments.

- factory: This module contains a class to define enrollment controller.

- models: This model contains classes to persist the features of the plugin.

- signal_receivers: Signals from the platform are received in this module to execute some functionality.

- tasks: In this module are the different tasks related to celery

- urls: This module contains the openedx_external_enrollments URL Configuration. more information: https://docs.djangoproject.com/en/1.11/topics/http/urls/
