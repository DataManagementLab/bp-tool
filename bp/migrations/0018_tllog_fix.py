# Generated by Django 3.2.13 on 2022-09-09 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bp', '0017_timekeeping'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tllog',
            name='good_log',
            field=models.BooleanField(blank=True, default=None, null=True, verbose_name='Gutes Log?'),
        ),
    ]
