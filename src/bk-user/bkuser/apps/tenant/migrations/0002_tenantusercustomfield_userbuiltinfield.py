# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
# Generated by Django 3.2.20 on 2023-09-12 11:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserBuiltinField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=128, unique=True, verbose_name='字段名称')),
                ('display_name', models.CharField(max_length=128, verbose_name='展示用名称')),
                ('data_type', models.CharField(choices=[('string', '字符串'), ('number', '数字'), ('datetime', '日期时间'), ('enum', '枚举'), ('multi_enum', '多选枚举')], max_length=32, verbose_name='数据类型')),
                ('required', models.BooleanField(verbose_name='是否必填')),
                ('unique', models.BooleanField(verbose_name='是否唯一')),
                ('default', models.JSONField(default='', verbose_name='默认值')),
                ('options', models.JSONField(default={}, verbose_name='配置项')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TenantUserCustomField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=128, verbose_name='字段名称')),
                ('display_name', models.CharField(max_length=128, verbose_name='展示用名称')),
                ('data_type', models.CharField(choices=[('string', '字符串'), ('number', '数字'), ('datetime', '日期时间'), ('enum', '枚举'), ('multi_enum', '多选枚举')], max_length=32, verbose_name='数据类型')),
                ('required', models.BooleanField(verbose_name='是否必填')),
                ('order', models.IntegerField(default=0, verbose_name='展示顺序')),
                ('default', models.JSONField(default='', verbose_name='默认值')),
                ('options', models.JSONField(default={}, verbose_name='配置项')),
                ('tenant', models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.CASCADE, to='tenant.tenant')),
            ],
            options={
                'unique_together': {('tenant', 'name'), ('tenant', 'display_name')},
            },
        ),
    ]