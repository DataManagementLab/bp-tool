# Generated by Django 3.2.20 on 2023-09-14 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bp', '0025_project_short_title'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orgalog',
            name='current_problems',
        ),
        migrations.RemoveField(
            model_name='orgalog',
            name='status',
        ),
        migrations.AddField(
            model_name='orgalog',
            name='last_updated',
            field=models.DateTimeField(blank=True, default=None),
        ),
    ]
