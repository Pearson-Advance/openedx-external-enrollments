# Generated by Django 2.2.13 on 2021-06-28 12:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('openedx_external_enrollments', '0003_externalenrollment'),
    ]

    operations = [
        migrations.CreateModel(
            name='PathstreamEnrollment',
            fields=[
                ('externalenrollment_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='openedx_external_enrollments.ExternalEnrollment')),
                ('is_uploaded', models.BooleanField(default=False)),
            ],
            bases=('openedx_external_enrollments.externalenrollment',),
        ),
    ]
