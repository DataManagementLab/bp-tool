# Generated by Django 3.2.8 on 2021-11-12 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bp', '0012_tllog_minor'),
    ]

    operations = [
        migrations.AddField(
            model_name='tllog',
            name='good_log',
            field=models.NullBooleanField(default=None, verbose_name='Gutes Log?'),
        ),
        migrations.AddField(
            model_name='tllog',
            name='read',
            field=models.BooleanField(blank=True, default=False, verbose_name='Gelesen'),
        ),
    ]
