# Generated by Django 3.1.5 on 2021-10-21 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bp', '0007_tl_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='tllog',
            name='text',
            field=models.TextField(default='EMPTY'),
            preserve_default=False,
        ),
    ]
