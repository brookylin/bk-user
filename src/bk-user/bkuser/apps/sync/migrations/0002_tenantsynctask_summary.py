# Generated by Django 3.2.20 on 2024-04-30 06:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sync', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenantsynctask',
            name='summary',
            field=models.JSONField(default=dict, verbose_name='任务总结'),
        ),
    ]