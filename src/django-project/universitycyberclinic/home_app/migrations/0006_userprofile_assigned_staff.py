# Generated by Django 5.1.5 on 2025-04-16 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home_app', '0005_appointment_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='assigned_staff',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
