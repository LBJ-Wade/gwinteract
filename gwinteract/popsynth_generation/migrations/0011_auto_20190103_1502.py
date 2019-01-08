# Generated by Django 2.1.4 on 2019-01-03 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('popsynth_generation', '0010_auto_20190103_1451'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newpopsynthmodel',
            name='galaxy_component',
            field=models.CharField(choices=[('ThinDisk', 'ThinDisk'), ('Bulge', 'Bulge'), ('ThickDisk', 'ThickDisk'), ('DeltaBurst', 'DeltaBurst'), ('FIRE', 'FIRE')], max_length=20),
        ),
        migrations.AlterField(
            model_name='newpopsynthmodel',
            name='initial_samp',
            field=models.CharField(choices=[('independent', 'independent'), ('multidim', 'multidim')], max_length=20),
        ),
    ]