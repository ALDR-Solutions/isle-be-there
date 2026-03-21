<template>
  <div class="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <div class="mb-8">
      <p class="text-sm font-semibold uppercase tracking-[0.25em] text-slate-500">Account</p>
      <h1 class="mt-2 text-3xl font-bold text-slate-900">My Profile</h1>
      <p class="mt-1 text-sm text-slate-500">Manage your personal information and account settings.</p>
    </div>

    <div class="bg-white rounded-3xl border border-slate-200 shadow-sm p-8 space-y-6">
      <div class="flex items-center gap-5">
        <div class="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan-400 to-emerald-400 text-xl font-bold text-white select-none">
          {{ initials }}
        </div>
        <div>
          <p class="font-semibold text-slate-900">{{ user?.first_name }} {{ user?.last_name }}</p>
          <p class="text-sm text-slate-500">{{ user?.email }}</p>
          <span
            v-if="user?.is_business"
            class="mt-1 inline-block rounded-full bg-cyan-100 px-2.5 py-0.5 text-xs font-medium text-cyan-700"
          >Business Account</span>
          <span
            v-else
            class="mt-1 inline-block rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-600"
          >Personal Account</span>
        </div>
      </div>

      <hr class="border-slate-100" />

      <form class="space-y-5" @submit.prevent="promptSave">
        <div class="grid gap-4 sm:grid-cols-2">
          <div>
            <label class="mb-1.5 block text-sm font-medium text-slate-700">First name</label>
            <input
              v-model="form.first_name"
              type="text"
              :disabled="!editing"
              class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100 disabled:cursor-default disabled:text-slate-500"
            />
          </div>
          <div>
            <label class="mb-1.5 block text-sm font-medium text-slate-700">Last name</label>
            <input
              v-model="form.last_name"
              type="text"
              :disabled="!editing"
              class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100 disabled:cursor-default disabled:text-slate-500"
            />
          </div>
        </div>

        <div>
          <label class="mb-1.5 block text-sm font-medium text-slate-700">Username</label>
          <input
            v-model="form.username"
            type="text"
            :disabled="!editing"
            class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100 disabled:cursor-default disabled:text-slate-500"
          />
        </div>

        <div>
          <label class="mb-1.5 block text-sm font-medium text-slate-700">Email</label>
          <input
            v-model="form.email"
            type="email"
            :disabled="!editing"
            class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100 disabled:cursor-default disabled:text-slate-500"
          />
        </div>

        <div
          v-if="formError"
          class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
        >
          {{ formError }}
        </div>

        <div class="flex gap-3 pt-1">
          <template v-if="!editing">
            <button
              type="button"
              @click="startEditing"
              class="rounded-xl bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800"
            >
              Edit Profile
            </button>
          </template>
          <template v-else>
            <button
              type="submit"
              :disabled="saving"
              class="rounded-xl bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {{ saving ? 'Saving...' : 'Save Changes' }}
            </button>
            <button
              type="button"
              @click="cancelEditing"
              class="rounded-xl border border-slate-200 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
            >
              Cancel
            </button>
          </template>
        </div>
      </form>
    </div>

    <div class="mt-6 rounded-3xl border border-red-200 bg-white p-8">
      <h2 class="text-base font-semibold text-red-700">Danger Zone</h2>
      <p class="mt-1 text-sm text-slate-500">
        Disabling your account will log you out immediately. An administrator will need to reactivate it.
      </p>
      <button
        type="button"
        @click="showDisableModal = true"
        class="mt-4 rounded-xl border border-red-300 bg-red-50 px-5 py-2.5 text-sm font-semibold text-red-700 transition hover:bg-red-100"
      >
        Disable Account
      </button>
    </div>

    <div
      v-if="showSaveModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm"
    >
      <div class="mx-4 w-full max-w-md rounded-3xl bg-white p-8 shadow-2xl">
        <h3 class="text-lg font-bold text-slate-900">Save Changes?</h3>
        <p class="mt-2 text-sm text-slate-500">Are you sure you want to update your profile details?</p>
        <div class="mt-6 flex gap-3">
          <button
            @click="confirmSave"
            :disabled="saving"
            class="flex-1 rounded-xl bg-slate-900 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:opacity-60"
          >
            {{ saving ? 'Saving...' : 'Confirm' }}
          </button>
          <button
            @click="showSaveModal = false"
            class="flex-1 rounded-xl border border-slate-200 bg-white py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>

    <div
      v-if="showDisableModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm"
    >
      <div class="mx-4 w-full max-w-md rounded-3xl bg-white p-8 shadow-2xl">
        <h3 class="text-lg font-bold text-slate-900">Disable Account?</h3>
        <p class="mt-2 text-sm text-slate-500">
          This will deactivate your account and log you out immediately. You won't be able to sign in until an administrator reactivates your account.
        </p>
        <div class="mt-6 flex gap-3">
          <button
            @click="confirmDisable"
            :disabled="disabling"
            class="flex-1 rounded-xl bg-red-600 py-2.5 text-sm font-semibold text-white transition hover:bg-red-700 disabled:opacity-60"
          >
            {{ disabling ? 'Disabling...' : 'Disable Account' }}
          </button>
          <button
            @click="showDisableModal = false"
            class="flex-1 rounded-xl border border-slate-200 bg-white py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter} from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useToastStore } from '../stores/toast';
import { profileAPI, authAPI } from '../services/api';

const router = useRouter();
const authStore = useAuthStore();
const toastStore = useToastStore();

const user = computed(() => authStore.user);

const editing = ref(false);
const saving = ref(false);
const disabling = ref(false);
const showSaveModal = ref(false);
const showDisableModal = ref(false);
const formError = ref('');

const form = ref({
  first_name: '',
  last_name: '',
  username: '',
  email: '',
});

const initials = computed(() => {
  const f = user.value?.first_name?.[0] ?? '';
  const l = user.value?.last_name?.[0] ?? '';
  return (f + l).toUpperCase() || user.value?.username?.[0]?.toUpperCase() || '?';

});

onMounted(() => {
  form.value = {
    first_name: user.value?.first_name ?? '',
    last_name: user.value?.last_name ?? '',
    username: user.value?.username ?? '',
    email: user.value?.email ?? '',
  };
});

function startEditing() {
  editing.value = true;
  formError.value = '';
}

function cancelEditing() {
  editing.value = false;
  formError.value = '';
  form.value = {
    first_name: user.value?.first_name ?? '',
    last_name: user.value?.last_name ?? '',
    username: user.value?.username ?? '',
    email: user.value?.email ?? '',
  };
}

function promptSave() {
  formError.value = '';
  if(!form.value.first_name || !form.value.last_name){
    formError.value = 'First name and last name are required';
    return;
  }
  showSaveModal.value = true;
}

async function confirmSave() {
  saving.value = true;
  try {
    await profileAPI.update(form.value);
    await authStore.fetchUser();
    editing.value = false;
    showSaveModal.value = false;
    toastStore.show('Profile updated successfully.', 'success');
  }catch (err) {
    showSaveModal.value = false;
    formError.value = err.response?.data?.detail || 'Failed to update profile.';
    toastStore.show('Failed to update profile.', 'error');
  }finally {
    saving.value = false;
  }
}

async function confirmDisable() {
  disabling.value = true;
  try{
    await authAPI.disableAccount();
    authStore.logout();
    toastStore.show('Your account has been disabled.', 'success');
    router.push('/');
  }catch (err){
    showDisableModal.value = false;
    toastStore.show('Failed to disable account.', 'error');
  }finally{
    disabling.value = false;
  }
  
}
</script>
