# Generated by Django 3.2.20 on 2023-09-20 20:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bp', '0027_alter_orgalog_last_updated'),
    ]

    operations = [
        migrations.AddField(
            model_name='orgalog',
            name='edited',
            field=models.BooleanField(blank=True, default=False, help_text='Wurde der Orga-Log bearbeitet?', verbose_name='Bearbeitet'),
        ),
        migrations.AlterField(
            model_name='orgalog',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
