# Generated by Django 4.1.3 on 2022-11-20 12:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0013_reports_parse_success'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reports',
            name='resourcegroups_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='website.resourcegroups'),
        ),
    ]
