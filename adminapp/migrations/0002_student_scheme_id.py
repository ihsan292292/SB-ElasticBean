# Generated by Django 5.0.3 on 2024-03-28 09:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='scheme_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='adminapp.scheme'),
            preserve_default=False,
        ),
    ]
