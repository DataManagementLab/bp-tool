# Generated by Django 3.2.13 on 2022-07-15 12:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bp', '0016_auto_20220714_1621'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='ag_grade',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='valid_grade', to='bp.aggrade', verbose_name='Derzeit gültige Bewertung'),
        ),
    ]