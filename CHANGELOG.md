### Version 3.11.2 - October 14, 2021
**Changes:**

  - Improve SF Integration.

### Version 3.11.1 - October 04, 2021
**Changes:**

  - Fix SF API payload according to new conditions.

### Version 3.11.0 - September 27, 2021
**Changes:**

  - Update SF API payload.

### Version 3.10.1 - September 16, 2021
**Changes:**

  - Fix the Pathstream task.

### Version 3.10.0 - September 16, 2021
**Changes:**

  - Add the S3 file management feature to Pathstream integration.

### Version 3.9.1 - September 13, 2021
**Changes:**

  - Update Pathstream data format and use EnrollmentRequestLog.

### Version 3.9.0 - September 09, 2021
**Changes:**

  - Add MIT Hz enrollment storage in ExternalEnrollment model.

### Version 3.8.2 - September 08, 2021
**Changes:**

  - Fix requirements for Python 3.5, add boto3 and botocore.

### Version 3.8.1 - August 18, 2021
**Changes:**

  - Change the CUSTOM_BUNDLE_TYPE value for SF.

### Version 3.8.0 - August 10, 2021
**Changes:**

  - Add the basic Pathstream external enrollment integration.

### Version 3.7.0 - August 05, 2021
**Changes:**

  - Edit salesforce external enrollment to handle the interim case for the SF API.

### Version 3.6.0 - July 13, 2021
**Changes:**

  - Add Viper refresk API keys task.

### Version 3.5.0 - June 18, 2021
**Changes:**

  - Add Viper external enrollment integration..
### Version 3.4.1 - June 16, 2021
**Changes:**

  - Edit salesforce external enrollment to return course run key.
### Version 3.4.0 - June 15, 2021
**Changes:**

  - Changes OtherCourseSettings table, course_id CourseKeyField to course CourseOverview FK.
### Version 3.3.0 - May 23, 2021
**Changes:**

  - Change condition to migrate and update courses in OtherCourseSettings table.
### Version 3.2.1 - May 12, 2021
**Changes:**

  - Removing relation between UTM params and source fields.
### Version 3.2.0 - Apr 23, 2021
**Changes:**

  - Replace CircleCI with GitHub Actions

### Version 3.1.1 - Apr 21, 2021
**Changes:**

  - Add MIT Horizon prod settings

### Version 3.1.0 - Apr 20, 2021
**Changes:**

  - Add tox setup to test py35 and py38.

### Version 3.0.0 - Apr 13, 2021
**Changes:**

  - Fix plugin tests and remove support for python27.

### Version 2.8.6 - Apr 12, 2021
**Changes:**

  - Fix MIT Horizon TypeError

### Version 2.8.6 - Apr 09, 2021
**Changes:**

  - Set a default value for MIT_HZ_API_URL.

### Version 2.8.5 - Apr 09, 2021
**Changes:**

  - Change Other course settings Django admin module to read-only.

### Version 2.8.4 - Apr 08, 2021
**Changes:**

  - Adds MIT Horizon Integration

### Version 2.8.3 - Apr 08, 2021
**Changes:**

  - Fix bug on Salesforce enrollment and Other course settings module name.

### Version 2.8.2 - Apr 07, 2021
**Changes:**

  - Check for all courses in the basket to get related salesforce data.

### Version 2.8.1 - Apr 05, 2021
**Changes:**

  - Fix Other course settings migrations files in order to unblock tests running.

More info: https://github.com/Pearson-Advance/openedx-external-enrollments/pull/19

### Version 2.8.0 - Mar 31, 2021
**Changes:**

  - Adds OtherCourseSettings model to Django admin panel and replaces single to double quotes in print statements.

### Version 2.7.0 - Mar 31, 2021
**Changes:**

  - Changes to OtherCourseSettings model and adds an entrypoint from cms.

### Version 2.6.0 - Mar 18, 2021
**Changes:**

  - Copy 'Other Course Settings' into LMS DB.

### Version 2.5.2 - Mar 1, 2021
**Changes:**

  - Add site configuration flag to override ICC Authentication method.

### Version 2.5.1 - Feb 25, 2021
**Changes:**

  - Uppercase username bug solved.

### Version 2.5.0 - Feb 24, 2021
**Changes:**

  - Supporting ICC integration.

### Version 2.3.0 - Oct 29, 2020
**Changes:**

  - Supporting greenfig integration.

### Version 2.2.0 - Oct 27, 2020
**Changes:**

  - Avoiding duplicated execution over signal receivers.

### Version 2.1.0 - Sep 23, 2020
**Changes:**

  - Listening only "Change Enrollment" events to forward the enrollment over the external platform.

### Version 2.0.0 - Sep 21, 2020
**Breaking changes:**

  - openedx_external_enrollments now requires Python 3.5 to run but continues to support Python 2.7 (Version 1.5.0).
