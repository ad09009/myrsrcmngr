# Generated by Django 4.1.3 on 2022-11-20 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0015_alter_reports_full_cmndline'),
    ]

    operations = [
        migrations.AddField(
            model_name='hosts',
            name='is_added',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hosts',
            name='is_removed',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='services',
            name='is_added',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
