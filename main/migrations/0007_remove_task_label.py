# Generated by Django 3.2.8 on 2022-02-27 16:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_task_label'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='label',
        ),
    ]
