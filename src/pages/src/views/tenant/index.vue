<template>
  <div
    v-bkloading="{ loading: state.tableLoading, zIndex: 9 }"
    :class="['group-details-wrapper user-scroll-y relative', { 'has-alert': userStore.showAlert }]">
    <div class="main-content">
      <div class="content-search">
        <div class="content-search-left">
          <bk-button v-if="isCreateTenant" class="mr-[24px]" theme="primary" @click="handleClick('add')">
            <i class="user-icon icon-add-2 mr8" />
            {{ $t('新建租户') }}
          </bk-button>
        </div>
        <bk-input
          class="content-search-input"
          v-model="search"
          :placeholder="$t('搜索租户名')"
          type="search"
          clearable
        />
      </div>
      <bk-table
        class="content-table"
        :data="tableSearchData"
        :border="['outer']"
        :max-height="tableMaxHeight"
        show-overflow-tooltip
        @column-sort="columnSort">
        <template #empty>
          <Empty
            :is-data-empty="state.isTableDataEmpty"
            :is-search-empty="state.isEmptySearch"
            :is-data-error="state.isTableDataError"
            @handle-empty="search = ''"
            @handle-update="fetchTenantsList"
          />
        </template>
        <bk-table-column
          prop="name"
          :label="$t('租户名')">
          <template #default="{ row, index }">
            <div class="item-name">
              <img v-if="row.logo" class="img-logo" :src="row.logo" />
              <span v-else class="span-logo" :style="`background-color: ${LOGO_COLOR[index]}`">
                {{ logoConvert(row.name) }}
              </span>
              <bk-button
                text
                theme="primary"
                @click="handleClick('view', row)"
              >
                {{ row.name }}
              </bk-button>
              <img v-if="row.new" class="icon-new" src="@/images/new.svg" alt="">
            </div>
          </template>
        </bk-table-column>
        <bk-table-column prop="id" :label="$t('租户ID')"></bk-table-column>
        <bk-table-column prop="status" :label="$t('租户状态')" :filter="{ list: statusFilters }">
          <template #default="{ row }">
            <div>
              <img :src="tenantStatus[row.status]?.icon" class="status-icon" />
              <span>{{ tenantStatus[row.status]?.text }}</span>
            </div>
          </template>
        </bk-table-column>
        <bk-table-column prop="created_at" :label="$t('创建时间')" />
        <bk-table-column :label="$t('操作')">
          <template #default="{ row }">
            <div class="flex items-center">
              <span
                v-bk-tooltips="{
                  content: $t('admin只能进入默认租户'),
                  distance: 20,
                  disabled: userStore.user?.tenant_id === row.id,
                }">
                <bk-button
                  text
                  theme="primary"
                  style="margin-right: 8px;"
                  :disabled="userStore.user?.tenant_id !== row.id"
                  @click="handleClickEnter"
                >
                  {{ $t('进入') }}
                </bk-button>
              </span>
              <bk-button
                text
                theme="primary"
                style="margin-right: 8px;"
                @click="handleClick('edit', row)"
              >
                {{ $t('编辑') }}
              </bk-button>
              <bk-popover
                class="dot-menu"
                placement="bottom-start"
                theme="light"
                ext-cls="operate-popover"
                :arrow="false">
                <i class="user-icon icon-more"></i>
                <template #content>
                  <ul class="dot-menu-list">
                    <li class="dot-menu-item" @click="handleClickDisable(row)">
                      {{ row.status === 'enabled' ? $t('停用') : $t('启用') }}
                    </li>
                    <li
                      class="dot-menu-item"
                      v-bk-tooltips="{
                        content: $t('需要先停用租户才能删除'),
                        disabled: row.status !== 'enabled',
                      }"
                      @click="handleClickDelete(row)">
                      <span :class="{ 'delete-disable': row.status === 'enabled' }">
                        {{ $t('删除') }}
                      </span>
                    </li>
                    <li class="dot-menu-item" @click="resetAdminPassword(row)">
                      {{ $t('重置管理员密码') }}
                    </li>
                  </ul>
                </template>
              </bk-popover>
            </div>
          </template>
        </bk-table-column>
      </bk-table>
    </div>
    <!-- 编辑/预览 -->
    <bk-sideslider
      :class="[{ 'details-edit-wrapper': !isView }]"
      :width="640"
      :is-show="detailsConfig.isShow"
      :title="detailsConfig.title"
      :before-close="handleBeforeClose"
      render-directive="if"
      quick-close
      transfer
    >
      <template #header>
        <div class="flex items-center justify-between w-[100%] pr-[16px]">
          <span>{{ detailsConfig.title }}</span>
          <div v-if="isView">
            <bk-button
              outline
              theme="primary"
              @click="handleClick('edit', state.tenantsData)"
            >{{ $t('编辑') }}</bk-button
            >
          </div>
        </div>
      </template>
      <template #default>
        <ViewDetails v-if="isView" :tenants-data="state.tenantsData" />
        <OperationDetails
          v-else
          :type="detailsConfig.type"
          :tenants-data="state.tenantsData"
          :is-email="isEmail"
          @handle-cancel-edit="handleCancelEdit"
          @update-tenants-list="updateTenantsList"
        />
      </template>
    </bk-sideslider>
    <!-- 重置管理员密码 -->
    <bk-dialog
      :width="640"
      :is-show="adminPasswordConfig.isShow"
      :title="adminPasswordConfig.title"
      :is-loading="adminPasswordConfig.isLoading"
      :theme="'primary'"
      :quick-close="false"
      @closed="closedPassword"
      @confirm="confirmPassword"
    >
      <bk-form
        class="operation-content"
        ref="formRef"
        form-type="vertical"
        :model="adminPasswordData"
        :rules="rules">
        <bk-form-item :label="$t('用户名')" required>
          <bk-input
            :model-value="adminPasswordConfig.username"
            disabled
          />
        </bk-form-item>
        <bk-form-item :label="$t('密码')" property="fixed_password" required>
          <div class="flex justify-between">
            <passwordInput
              v-model="adminPasswordData.fixed_password"
              @change="changePassword"
              @input="inputPassword" />
            <bk-button
              outline
              theme="primary"
              :class="['ml-[8px]', { 'min-w-[88px]': $i18n.locale === 'zh-cn' }]"
              @click="handleRandomPassword">
              {{ $t('随机生成') }}
            </bk-button>
          </div>
        </bk-form-item>
        <bk-form-item :label="$t('通知方式')">
          <div class="mb-[18px]">
            <bk-checkbox v-model="smsValue" @change="changeSms">{{ $t('短信') }}</bk-checkbox>
            <PhoneInput
              :form-data="adminPasswordData"
              :tel-error="telError"
              :required="smsValue"
              @change-country-code="changeCountryCode"
              @change-tel-error="changeTelError" />
          </div>
          <div>
            <bk-checkbox v-model="emailValue" @change="changeEmail">{{ $t('邮箱') }}</bk-checkbox>
            <div>
              <bk-input
                :class="{ 'input-error': emailError }"
                v-model="adminPasswordData.email"
                @blur="emailBlur"
                @input="handleInput" />
              <p class="error" v-show="emailError">{{ $t('请输入正确的邮箱地址') }}</p>
            </div>
          </div>
        </bk-form-item>
      </bk-form>
    </bk-dialog>
    <!-- 创建租户成功弹窗 -->
    <bk-dialog
      class="tenant-success"
      v-model:is-show="isShowDialog"
      quick-close
      width="560px"
    >
      <div>
        <div class="text-center">
          <i class="user-icon icon-duihao-2 text-[44px] text-[#2dcb56]"></i>
          <p class="text-[20px] my-[8px]">{{$t('创建租户成功')}}</p>
        </div>
        <div
          v-if="!dialogData.isShowItem"
          class="mb-[16px] text-[14px] text-[#63656e] flex justify-center items-center">
          <div>
            <div v-if="dialogData.emailNotification">
              {{$t('登录方式已通过')}}
              <span class="text-[red]">{{dialogData.emailNotification}}</span>
              {{$t('发送给')}}
              <span class="text-[#313238]">{{ dialogData.email}}</span>
            </div>
            <div v-if="dialogData.smsNotification">
              {{$t('登录方式已通过')}}
              <span class="text-[red]">{{dialogData.smsNotification}}</span>
              {{$t('发送给')}}
              <span class="text-[#313238] text-[13px]">{{dialogData.phone}}</span>
            </div>
          </div>
        </div>
        <div>
          <div class="bg-[#F5F7FA]" ref="dialogRef">
            <LabelContent :label="$t('租户名称')">{{ dialogData.name }}</LabelContent>
            <LabelContent :label="$t('租户ID')">{{ dialogData.id }}</LabelContent>
            <LabelContent v-if="dialogData.isShowItem" :label="$t('访问地址')" class="access-url">
              <a :href="dialogData.accessUrl" target="_blank">{{dialogData.accessUrl}}</a>
            </LabelContent>
            <LabelContent v-if="dialogData.isShowItem" :label="$t('用户名')">admin</LabelContent>
            <LabelContent v-if="dialogData.isShowItem" :label="$t('登录密码')">
              {{ dialogData.fixed_password }}
            </LabelContent>
          </div>
        </div>
      </div>
      <template #footer>
        <bk-button
          theme="primary"
          class="w-[64px] mr-[8px] center"
          @click="copyContent"
        >
          {{ $t('复制') }}
        </bk-button>
      </template>
    </bk-dialog>
    <footer class="footer">
      <p class="text-[#3A84FF]" v-dompurify-html="contact"></p>
      <p class="text-[#63656E]">{{ copyright }}</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { bkTooltips as vBkTooltips, InfoBox, Message } from 'bkui-vue';
import { computed, inject, nextTick, onMounted, reactive, ref, watch } from 'vue';

import OperationDetails from './OperationDetails.vue';
import ViewDetails from './ViewDetails.vue';

import LabelContent from '@/components/layouts/LabelContent.vue';
import passwordInput from '@/components/passwordInput.vue';
import PhoneInput from '@/components/phoneInput.vue';
import Empty from '@/components/SearchEmpty.vue';
import { useAdminPassword, useInfoBoxContent, useTableMaxHeight, useValidate } from '@/hooks';
import {
  currentUser,
  deleteTenants,
  getTenantDetails,
  getTenants,
  getTenantsBuiltinManager,
  getTenantsRelatedResource,
  putBuiltinManager,
  putTenantsStatus,
} from '@/http';
import { t } from '@/language/index';
import router from '@/router';
import { platformConfig, useMainViewStore, useUser } from '@/store';
import { copy, LOGO_COLOR, logoConvert, tenantStatus } from '@/utils';

const userStore = useUser();
const store = useMainViewStore();
const  platformConfigData = platformConfig();
const contact = computed(() => platformConfigData.i18n.footerInfoHTML);
const copyright = computed(() => platformConfigData.footerCopyrightContent);
store.customBreadcrumbs = false;
const isCreateTenant = window.ENABLE_CREATE_TENANT !== 'False';

const validate = useValidate();
const tableMaxHeight = useTableMaxHeight(202);
const editLeaveBefore = inject('editLeaveBefore');
const search = ref('');
const state = reactive({
  list: [],
  tableLoading: true,
  // 搜索结果为空
  isEmptySearch: false,
  // 表格请求出错
  isTableDataError: false,
  // 表格请求结果为空
  isTableDataEmpty: false,
  // 租户详情数据
  tenantsData: {
    name: '',
    id: '',
    logo: '',
    status: 'enabled',
    fixed_password: '',
    notification_methods: ['email'],
    email: '',
    phone: '',
    phone_country_code: '86',
  },
});
const detailsConfig = reactive({
  isShow: false,
  title: '',
  type: '',
});
const enumData = {
  view: {
    title: t('租户详情'),
    type: 'view',
  },
  add: {
    title: t('新建租户'),
    type: 'add',
  },
  edit: {
    title: t('编辑租户'),
    type: 'edit',
  },
};

watch(
  () => detailsConfig.isShow,
  () => {
    if (!detailsConfig.isShow) {
      nextTick(() => {
        state.tenantsData = {
          name: '',
          id: '',
          logo: '',
          status: 'enabled',
          fixed_password: '',
          notification_methods: ['email'],
          email: '',
          phone: '',
          phone_country_code: '86',
        };
      });
    }
  },
);

const isView = computed(() => detailsConfig.type === 'view');
const currentTenantId = ref('');

const statusFilters = [
  { text: t('已启用'), value: 'enabled' },
  { text: t('未启用'), value: 'disabled' },
];

const handleClick = async (type: string, item?: any) => {
  if (type !== 'add') {
    const res = await getTenantDetails(item.id);
    state.tenantsData = res.data;
    currentTenantId.value = item.id;
  }
  detailsConfig.title = enumData[type].title;
  detailsConfig.type = enumData[type].type;
  detailsConfig.isShow = true;
};

const inputPassword = (val) => {
  adminPasswordData.value.fixed_password = val;
};

const handleCancelEdit = async () => {
  window.changeInput = false;
  if (detailsConfig.type === 'add') {
    detailsConfig.isShow = false;
  } else {
    const res = await getTenantDetails(currentTenantId.value);
    state.tenantsData = res.data;
    detailsConfig.type = 'view';
    detailsConfig.title = t('租户详情');
    window.changeInput = false;
  }
};

onMounted(() => {
  currentUser()
    .then((res) => {
      if (res.data.role === 'tenant_manager') {
        router.push({ name: 'organization' });
      } else {
        fetchTenantsList();
      }
    })
    .catch(() => {
      Message(t('获取用户信息失败，请检查后再试'));
    });
});

// 新建租户状态 id
const isCreated = ref(false);
const newId = ref('');

const getRows = () => document.getElementsByClassName('hover-highlight')[0].getElementsByTagName('td');

watch(() => search.value, (val) => {
  if (val) {
    isCreated.value = false;
    newId.value = '';
    const rows = getRows();
    for (const i of rows) {
      i.style.background = '#fff';
    }
    state.list = state.list.sort((a, b) => a.name.localeCompare(b.name, 'zh-Hans-CN'));
  }
});

// 获取租户列表
const fetchTenantsList = () => {
  search.value = '';
  state.tableLoading = true;
  state.isTableDataEmpty = false;
  state.isEmptySearch = false;
  state.isTableDataError = false;
  getTenants()
    .then((res: any) => {
      if (res.data.length === 0) {
        state.isTableDataEmpty = true;
      }

      const newDate = new Date().getTime(); // 当前时间
      res.data.forEach((item) => {
        const createdDate = new Date(item.created_at).getTime();
        // 相差天数
        item.new = Math.floor((newDate - createdDate) / (24 * 3600 * 1000)) <= 1;
      });

      if (isCreated.value) {
        state.list = res.data.map((item) => {
          item.add = item.id === newId.value;
          return item;
        }).sort((a, b) => !a.add - !b.add);

        const rows = getRows();
        for (const i of rows) {
          i.style.background = '#F2FCF5';
        }
      } else {
        state.list = res.data.sort((a, b) => a.name.localeCompare(b.name, 'zh-Hans-CN'));
      }
      state.tableLoading = false;
    })
    .catch(() => {
      state.isTableDataError = true;
      state.tableLoading = false;
    });
};

// 搜索租户列表
const tableSearchData = computed(() => state.list.filter(item => !search.value || item.name.includes(search.value)));

watch(() => search.value, (val) => {
  state.isEmptySearch = val && !tableSearchData.value.length;
});

const dialogData = ref({});
const isShowDialog = ref(false);

// 更新租户列表
const updateTenantsList = (type: string, formData: any) => {
  detailsConfig.isShow = false;
  window.changeInput = false;
  isCreated.value = type === 'add';
  newId.value = formData?.id;
  fetchTenantsList();
  if (isCreated.value) {
    Object.assign(dialogData.value, {
      ...formData,
      isShowItem: formData.notification_methods?.length === 0,
      emailNotification: formData.notification_methods?.includes('email') ? t('邮箱') : '',
      smsNotification: formData.notification_methods?.includes('sms') ? t('短信') : '',
      accessUrl: location.origin,
    });
    isShowDialog.value = true;
  } else {
    Message({
      theme: 'success',
      message: t('租户更新成功'),
    });
  }
};

const dialogRef = ref();
const getDialogContentText = () => {
  const text = dialogRef.value.innerText;
  const lines = text.split('\n');
  const processedLines = lines.map((line, index) => ((index % 2 === 0) ? line.trim() : `${line.trim()}\n`));
  return processedLines.join('');
};

const copyContent = () => {
  const container = getDialogContentText();
  copy(container);
  isShowDialog.value = false;
};

const handleBeforeClose = async () => {
  let enableLeave = true;
  if (window.changeInput) {
    enableLeave = await editLeaveBefore();
    detailsConfig.isShow = !enableLeave;
  } else {
    detailsConfig.isShow = false;
  }
  if (!enableLeave) {
    return Promise.resolve(enableLeave);
  }
};

const columnSort = () => {
  if (isCreated.value) {
    isCreated.value = false;
    newId.value = '';
    const rows = getRows();
    for (const i of rows) {
      i.style.background = '#fff';
    }
  }
};

const handleClickEnter = () => {
  router.push({ name: 'organization' });
};

// 停用租户
const handleClickDisable = (item) => {
  const isEnabled = item.status === 'enabled';
  const title = isEnabled ? `${t('确定停用租户')}：${item.name}？` : `${t('确定启用租户')}：${item.name}？`;
  const subTitle = isEnabled ? t('停用期间，该租户下的用户将无法登录系统') : t('启用后，该租户下的用户可以重新登录系统');
  const successMessage = isEnabled ? t('租户停用成功') : t('租户启用成功');
  InfoBox({
    width: 400,
    title,
    subTitle,
    confirmText: t('确定'),
    onConfirm: () => {
      putTenantsStatus(item.id).then(() => {
        Message({ theme: 'success', message: successMessage });
        fetchTenantsList();
      })
        .catch((error) => {
          console.warn(error);
        });
    },
  });
};

// 删除租户
const handleClickDelete = async (item) => {
  if (item.status === 'enabled') return;
  try {
    const res = await getTenantsRelatedResource(item.id);
    const { subContent } = useInfoBoxContent(res.data, 'tenant');
    InfoBox({
      width: 600,
      title: t('确定删除当前租户？'),
      subTitle: subContent,
      onConfirm: () => {
        deleteTenants(item.id).then(() => {
          Message({ theme: 'success', message: t('租户删除成功') });
          fetchTenantsList();
        })
          .catch((error) => {
            console.error(error);
          });
      },
    });
  } catch (e) {
    console.warn(e);
  }
};

// 重置管理员密码
const adminPasswordConfig = reactive({
  isShow: false,
  title: t('重置管理员密码'),
  id: '',
  username: '',
  isLoading: false,
});

const adminPasswordData = ref({
  fixed_password: '',
  notification_methods: ['email'],
  email: '',
  phone: '',
  phone_country_code: '86',
});
const formRef = ref();

const rules = {
  fixed_password: [validate.required],
};

watch(() => adminPasswordData.value.notification_methods, (val) => {
  if (val.length === 1) {
    if (val[0] === 'email') {
      adminPasswordData.value.phone = '';
      adminPasswordData.value.phone_country_code = '86';
      telError.value = false;
    } else if (val[0] === 'sms') {
      adminPasswordData.value.email = '';
      emailError.value = false;
    }
  }
});

const resetAdminPassword = async (item) => {
  try {
    const res = await getTenantsBuiltinManager(item.id);
    adminPasswordConfig.id = item.id;
    adminPasswordConfig.username = res.data.username;
    adminPasswordConfig.isShow = true;
  } catch (e) {
    console.warn(e);
  }
};

const confirmPassword = async () => {
  try {
    if (emailValue.value) handleBlur();
    if (smsValue.value && !adminPasswordData.value.phone) changeTelError(true);
    await formRef.value.validate();
    if (emailValue.value && emailError.value) return;
    if (telError.value) return;

    adminPasswordConfig.isLoading = true;
    adminPasswordData.value.notification_methods = [];
    if (emailValue.value) adminPasswordData.value.notification_methods.push('email');
    if (smsValue.value) adminPasswordData.value.notification_methods.push('sms');
    await putBuiltinManager(adminPasswordConfig.id, adminPasswordData.value);
    adminPasswordConfig.isShow = false;
    Message({ theme: 'success', message: t('重置密码成功') });
    resetAdminPasswordData();
  } catch (e) {
    console.warn(e);
  } finally {
    adminPasswordConfig.isLoading = false;
  }
};

const closedPassword = () => {
  adminPasswordConfig.isShow = false;
  emailError.value = false;
  telError.value = false;
  resetAdminPasswordData();
};

const resetAdminPasswordData = () => {
  Object.assign(adminPasswordData.value, {
    fixed_password: '',
    notification_methods: ['email'],
    email: '',
    phone: '',
    phone_country_code: '86',
  });
};

const {
  changePassword,
  handleRandomPassword,
  emailError,
  telError,
  isEmail,
  handleBlur,
  handleInput,
  changeCountryCode,
  changeTelError,
} = useAdminPassword(adminPasswordData.value);

const emailValue = ref(true);
const smsValue = ref(false);

const changeSms = () => {
  telError.value = smsValue.value ? telError.value : false;
};
const changeEmail = () => {
  emailError.value = emailValue.value ? emailError.value : false;
};
const emailBlur = () => {
  emailValue.value && handleBlur();
};
</script>

<style lang="less">
.operate-popover {
  padding: 5px 0 !important;
}

.details-edit-wrapper {
  .bk-modal-content {
    height: calc(100vh - 52px) !important;
    background: #f5f7fa !important;
  }
}
</style>

<style lang="less" scoped>
.has-alert {
  height: calc(100vh - 92px) !important;
}

.group-details-wrapper {
  width: 100%;
  height: calc(100vh - 52px);
  padding: 24px 144px;

  .main-content {
    .content-search {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;

      .content-search-left {
        display: flex;
        align-items: center;

        .switcher-text {
          margin-left: 12px;
          font-size: 14px;
          color: #313238;
        }
      }

      .content-search-input {
        width: 400px;
      }
    }

    :deep(.bk-table) {
      .item-name {
        display: flex;
        align-items: center;
        height: 42px;
        line-height: 42px;

        .icon-new {
          width: 26px;
          margin-left: 8px;
        }
      }

      .status-icon {
        display: inline-block;
        width: 16px;
        height: 16px;
        margin-right: 5px;
        color: #999;
        vertical-align: middle
      }
    }
  }
}

.error {
  position: absolute;
  left: 0;
  padding-top: 4px;
  font-size: 12px;
  line-height: 1;
  color: #ea3636;
  text-align: left;
  animation: form-error-appear-animation 0.15s;
}

.input-error {
  border-color: #ea3636 !important;
}

.dot-menu {
  display: inline-block;
  vertical-align: middle;
}

.icon-more {
  display: block;
  width: 30px;
  height: 30px;
  margin-top: 3px;
  font-size: 0;
  line-height: 30px;
  color: #979ba5;
  text-align: center;
  cursor: pointer;
  border-radius: 50%;

  &::before {
    display: inline-block;
    width: 3px;
    height: 3px;
    background-color: currentcolor;
    border-radius: 50%;
    content: "";
    box-shadow: 0 -4px 0 currentcolor, 0 4px 0 currentcolor;
  }

  &:hover {
    color: #3a84ff;
    background-color: #ebecf0;
  }
}

.dot-menu-list {
  min-width: 50px;
  margin: 0;
  list-style: none;

  .dot-menu-item {
    padding: 0 10px;
    font-size: 12px;
    line-height: 26px;
    cursor: pointer;

    &:hover {
      color: #3a84ff;
      background-color: #eaf3ff;
    }

    .delete-disable {
      color: #c4c6cc;
      cursor: not-allowed;
    }
  }
}

.item-name {
  display: flex;
  align-items: center;
  height: 42px;
  line-height: 42px;

  .icon-new {
    width: 26px;
    margin-left: 8px;
  }
}

.tenant-success {
  :deep(.bk-dialog-footer) {
    padding: 0 24px 24px;
    text-align: center !important;
    background-color: #fff;
    border-top:#fff;
  }

  :deep(.bk-dialog-content) {
    margin-top: 0;
  }

  :deep(.bk-dialog-header) {
    padding: 0;
  }
}

:deep(.access-url) {
  .label-value {
    color: #3A84FF !important;
  }
}

.footer {
  position: absolute;
  bottom: 0;
  width: calc(100% - 288px);
  padding: 2% 0;
  font-size: 12px;
  line-height: 20px;
  text-align: center;
}
</style>
