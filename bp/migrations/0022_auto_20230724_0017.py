# Generated by Django 3.2.18 on 2023-07-23 22:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bp', '0021_peer_groups'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tllog',
            name='good_log',
        ),
        migrations.AddField(
            model_name='tllog',
            name='rating',
            field=models.SmallIntegerField(choices=[(1, '1 Star(s)'), (2, '2 Star(s)'), (3, '3 Star(s)'), (4, '4 Star(s)'), (5, '5 Star(s)')], null=True, verbose_name='Bewertung'),
        ),
        migrations.AlterUniqueTogether(
            name='student',
            unique_together={('moodle_id',)},
        ),
    ]
