# Generated by Django 5.1.3 on 2024-11-13 19:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LogEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serialno', models.IntegerField()),
                ('version', models.IntegerField()),
                ('account_id', models.BigIntegerField()),
                ('instance_id', models.CharField(max_length=255)),
                ('srcaddr', models.GenericIPAddressField()),
                ('dstaddr', models.GenericIPAddressField()),
                ('srcport', models.IntegerField()),
                ('dstport', models.IntegerField()),
                ('protocol', models.IntegerField()),
                ('packets', models.IntegerField()),
                ('bytes', models.IntegerField()),
                ('starttime', models.BigIntegerField()),
                ('endtime', models.BigIntegerField()),
                ('action', models.CharField(max_length=50)),
                ('log_status', models.CharField(max_length=50)),
            ],
        ),
    ]
