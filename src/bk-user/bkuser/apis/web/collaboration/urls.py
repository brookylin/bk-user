# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.
from django.urls import path

from . import views

urlpatterns = [
    # ----------------------------- 分享方 -----------------------------
    # 本租户分享给其他租户的协同策略 / 新建协同策略（分享）给其他租户
    path(
        "to-strategies/",
        views.CollaborationToStrategyListCreateApi.as_view(),
        name="collaboration.to-strategy.list_create",
    ),
    # 编辑 / 删除协同策略（分享方）
    path(
        "to-strategies/<str:id>/",
        views.CollaborationToStrategyUpdateDestroyApi.as_view(),
        name="collaboration.to-strategy.update_destroy",
    ),
    # 更新协同策略状态（分享方）
    path(
        "to-strategies/<str:id>/source-status/",
        views.CollaborationToStrategySourceStatusUpdateApi.as_view(),
        name="collaboration.to-strategy.source-status.update",
    ),
    # 目标租户列表（目标租户可能是不可见的，则需要通过过滤的方式）
    path(
        "target-tenants/",
        views.CollaborationTargetTenantListApi.as_view(),
        name="collaboration.target_tenant.list",
    ),
    # ----------------------------- 接受方 -----------------------------
    # 其他租户分享给本租户的协同策略
    path(
        "from-strategies/",
        views.CollaborationFromStrategyListApi.as_view(),
        name="collaboration.from-strategy.list",
    ),
    # 获取源租户用户自定义字段（接受方）
    path(
        "from-strategies/<str:id>/source-tenant-custom-fields/",
        views.CollaborationStrategySourceTenantCustomFieldListApi.as_view(),
        name="collaboration.from-strategy.source-tenant-custom-fields.list",
    ),
    # 更新协同策略（接受方）
    path(
        "from-strategies/<str:id>/",
        views.CollaborationFromStrategyUpdateApi.as_view(),
        name="collaboration.from-strategy.update",
    ),
    # 确认协同策略（接受方）
    path(
        "from-strategies/<str:id>/operations/confirm/",
        views.CollaborationFromStrategyConfirmApi.as_view(),
        name="collaboration.from-strategy.confirm",
    ),
    # 更新协同策略状态（接受方）
    path(
        "from-strategies/<str:id>/target-status/",
        views.CollaborationFromStrategyTargetStatusUpdateApi.as_view(),
        name="collaboration.from-strategy.target-status.update",
    ),
    # 协同数据更新记录
    path(
        "sync-records/",
        views.CollaborationSyncRecordListApi.as_view(),
        name="collaboration.sync-record.list",
    ),
    # 协同数据更新记录详情
    path(
        "sync-records/<str:id>/",
        views.CollaborationSyncRecordRetrieveApi.as_view(),
        name="collaboration.sync-record.retrieve",
    ),
]
