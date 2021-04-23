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
