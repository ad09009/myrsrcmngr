# Generated by Django 4.1.3 on 2022-12-30 03:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0043_alter_resourcegroups_subnet'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='resourcegroups',
            name='ip_addresses',
        ),
    ]
