# Generated by Django 2.1.4 on 2019-03-26 22:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('popsynth_generation', '0009_auto_20190326_1715'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newpopsynthmodel',
            name='ecsn_mlow',
            field=models.FloatField(default=1.6),
        ),
    ]