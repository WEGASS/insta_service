# Generated by Django 3.2.8 on 2022-02-23 00:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_igaccount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='igaccount',
            name='last_use',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
