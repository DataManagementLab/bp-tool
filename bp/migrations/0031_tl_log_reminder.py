# Generated by Django 3.2.20 on 2023-10-26 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bp', '0030_auto_20231023_1123'),
    ]

    operations = [
        migrations.AddField(
            model_name='tl',
            name='log_reminder',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Anzahl Reminder für Logs'),
        ),
    ]
