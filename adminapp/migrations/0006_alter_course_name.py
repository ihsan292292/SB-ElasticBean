# Generated by Django 5.0.4 on 2024-04-22 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0005_alter_course_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='name',
            field=models.CharField(max_length=150),
        ),
    ]