# Generated by Django 4.1.3 on 2022-12-23 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0033_alter_hosts_reports_belonging_to'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hosts',
            name='reports_belonging_to',
            field=models.ManyToManyField(blank=True, related_name='related_hosts', to='website.reports'),
        ),
    ]