# Generated by Django 2.2.13 on 2021-06-15 20:13

from django.db import migrations, models
import jsonfield.encoder
import jsonfield.fields
import opaque_keys.edx.django.models


class Migration(migrations.Migration):

    dependencies = [
        ('openedx_external_enrollments', '0002_othercoursesettings'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalEnrollment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('controller_name', models.CharField(max_length=50)),
                ('course_shell_id', opaque_keys.edx.django.models.CourseKeyField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('meta', jsonfield.fields.JSONField(blank=True, dump_kwargs={'cls': jsonfield.encoder.JSONEncoder, 'separators': (',', ':')}, load_kwargs={})),
            ],
        ),
    ]
