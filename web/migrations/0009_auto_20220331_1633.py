# Generated by Django 3.2.11 on 2022-03-31 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0008_auto_20220304_1953'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classlist',
            name='price',
            field=models.IntegerField(verbose_name='价格'),
        ),
        migrations.AlterField(
            model_name='classlist',
            name='semester',
            field=models.IntegerField(verbose_name='班级(期)'),
        ),
    ]
