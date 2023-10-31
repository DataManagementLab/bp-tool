# Generated by Django 3.2.20 on 2023-10-23 03:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bp', '0029_bp_last_reminded'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bp',
            name='last_reminded',
        ),
        migrations.AddField(
            model_name='project',
            name='last_reminded',
            field=models.DateField(blank=True, null=True, verbose_name='Datum der letzten Erinnerung, einen Log zu senden'),
        ),
    ]
