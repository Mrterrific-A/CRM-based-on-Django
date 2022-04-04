# Generated by Django 3.0.5 on 2022-04-03 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0013_paymentrecord_student'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classlist',
            name='tech_teacher',
            field=models.ManyToManyField(blank=True, limit_choices_to={'depart__title__in': ['python', 'linux']}, related_name='tech_classes', to='web.UserInfo', verbose_name='任课老师'),
        ),
    ]