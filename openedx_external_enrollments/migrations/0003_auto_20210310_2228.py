# Generated by Django 2.2.16 on 2021-03-10 22:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('openedx_external_enrollments', '0002_othercoursesettings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='othercoursesettings',
            name='external_course_id',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
