# Generated by Django 4.1.3 on 2022-11-19 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0008_alter_scans_scantemplate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scans',
            name='ScanTemplate',
            field=models.CharField(choices=[('-oX -vvv --stats-every 1s --top-ports 100 -T2', 'Pirmais variants'), ('--stats-every 1s --top-ports 100 -T3', 'Otrais variants'), ('--stats-every 1s --top-ports 100 -T4', 'Tresais variants')], max_length=80),
        ),
    ]