# Generated by Django 5.0.3 on 2024-03-29 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Testimonal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(upload_to='testimonals')),
                ('name', models.CharField(max_length=50)),
                ('designation', models.CharField(max_length=50)),
                ('message', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='home',
            name='about',
            field=models.TextField(default='We are making skilled students for future'),
        ),
    ]