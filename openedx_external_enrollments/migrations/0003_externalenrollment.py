# Generated by Django 2.2.13 on 2021-06-17 18:05

from django.db import migrations, models
import django.db.models.deletion
import jsonfield.encoder
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('course_overviews', '0022_courseoverviewtab_is_hidden'),
        ('openedx_external_enrollments', '0002_othercoursesettings'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalEnrollment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('controller_name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('meta', jsonfield.fields.JSONField(blank=True, dump_kwargs={'cls': jsonfield.encoder.JSONEncoder, 'separators': (',', ':')}, load_kwargs={})),
                ('course_shell', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='external_course_enrollment', to='course_overviews.CourseOverview')),
            ],
        ),
    ]
