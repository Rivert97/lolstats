# Generated by Django 3.2.9 on 2022-06-29 01:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('summoners', '0007_gamerecord_kda'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='summonerstats',
            name='meankda',
        ),
        migrations.RemoveField(
            model_name='summonerstats',
            name='winrate',
        ),
        migrations.RemoveField(
            model_name='summonerstats',
            name='winstreak',
        ),
    ]
