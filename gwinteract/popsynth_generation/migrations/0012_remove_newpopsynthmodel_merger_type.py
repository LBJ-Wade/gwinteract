# Generated by Django 2.1.4 on 2019-04-03 16:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('popsynth_generation', '0011_auto_20190403_1109'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='newpopsynthmodel',
            name='merger_type',
        ),
    ]
