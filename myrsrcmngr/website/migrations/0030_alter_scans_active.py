# Generated by Django 4.1.3 on 2022-12-21 22:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0029_alter_scans_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scans',
            name='active',
            field=models.BooleanField(blank=True, default=False, null=True, verbose_name='Make Active'),
        ),
    ]
