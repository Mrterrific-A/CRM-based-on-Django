# Generated by Django 3.0.5 on 2021-10-07 12:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128, verbose_name='一级菜单标题')),
                ('icon', models.CharField(max_length=32, verbose_name='图标')),
            ],
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=32, verbose_name='标题')),
                ('name', models.CharField(max_length=32, unique=True, verbose_name='权限的别名')),
                ('url', models.CharField(max_length=128, verbose_name='含正则的URL')),
                ('menu', models.ForeignKey(blank=True, help_text='null表示不是菜单；非null表示是二级菜单', null=True, on_delete=django.db.models.deletion.CASCADE, to='rbac.Menu', verbose_name='所属菜单')),
                ('pid', models.ForeignKey(blank=True, help_text='对于非菜单权限要选中一个可以成为菜单的权限 作默认展开', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parents', to='rbac.Permission', verbose_name='关联的权限')),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=32, verbose_name='角色名称')),
                ('permissions', models.ManyToManyField(blank=True, to='rbac.Permission', verbose_name='拥有的所有权限')),
            ],
        ),
    ]
