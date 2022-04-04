# Generated by Django 3.2.11 on 2022-01-21 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0003_userinfo'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='nickname',
            field=models.CharField(default=None, max_length=32, verbose_name='姓名'),
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='name',
            field=models.CharField(max_length=32, verbose_name='用户名'),
        ),
    ]
