# Generated by Django 2.2.13 on 2021-03-23 22:29

from django.db import migrations, models
import jsonfield.encoder
import jsonfield.fields
import opaque_keys.edx.django.models


class Migration(migrations.Migration):

    dependencies = [
        ('openedx_external_enrollments', '0002_othercoursesettings'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='othercoursesettings',
            name='course_overview',
        ),
        migrations.AddField(
            model_name='othercoursesettings',
            name='course_id',
            field=opaque_keys.edx.django.models.CourseKeyField(db_index=True, default='course-v1:default+value+2021', max_length=255, primary_key=True, serialize=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='othercoursesettings',
            name='other_course_settings',
            field=jsonfield.fields.JSONField(blank=True, dump_kwargs={'cls': jsonfield.encoder.JSONEncoder, 'separators': (',', ':')}, load_kwargs={}, null=True),
        ),
        migrations.AlterField(
            model_name='othercoursesettings',
            name='external_course_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='othercoursesettings',
            name='external_platform',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
