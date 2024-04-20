# Generated by Django 5.0.4 on 2024-04-20 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0004_bgimages_remove_home_bgimage'),
    ]

    operations = [
        migrations.RenameField(
            model_name='home',
            old_name='title',
            new_name='qoute1',
        ),
        migrations.RenameField(
            model_name='home',
            old_name='subtitle',
            new_name='qoute2',
        ),
        migrations.AddField(
            model_name='home',
            name='by',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='home',
            name='about',
            field=models.TextField(default='skillboard education pandikkad'),
        ),
    ]
