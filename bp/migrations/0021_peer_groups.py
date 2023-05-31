# Generated by Django 3.2.16 on 2022-11-17 18:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bp', '0020_add_more_grades'),
    ]

    operations = [
        migrations.CreateModel(
            name='PeerGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nr', models.PositiveSmallIntegerField(verbose_name='Nummer')),
                ('bp', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bp.bp', verbose_name='Zugehöriges BP')),
            ],
            options={
                'verbose_name': 'Peergruppe',
                'verbose_name_plural': 'Peergruppen',
                'ordering': ['bp', 'nr'],
                'unique_together': {('bp', 'nr')},
            },
        ),
        migrations.AddField(
            model_name='project',
            name='peer_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='projects', to='bp.peergroup', verbose_name='Peer Group'),
        ),
    ]