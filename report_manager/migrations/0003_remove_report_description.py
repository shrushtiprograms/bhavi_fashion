# Generated by Django 5.2 on 2025-04-26 09:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('report_manager', '0002_report_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='report',
            name='description',
        ),
    ]
