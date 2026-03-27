<template>
  <div class="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <div class="mb-8">
      <p class="text-sm font-semibold uppercase tracking-[0.25em] text-slate-500">Business</p>
      <h1 class="mt-2 text-3xl font-bold text-slate-900">Business Profile</h1>
      <p class="mt-1 text-sm text-slate-500">Manage your business information and details.</p>
    </div>

    <div v-if="loading" class="flex justify-center py-20">
      <svg class="h-8 w-8 animate-spin text-cyan-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
      </svg>
    </div>

    <template v-else-if="business">
      <div class="bg-white rounded-3xl border border-slate-200 shadow-sm p-8 space-y-6">
        <div class="flex items-center gap-5">
          <div v-if="business.logo_url" class="h-16 w-16 rounded-2xl overflow-hidden border border-slate-200">
            <img :src="business.logo_url" alt="Business logo" class="h-full w-full object-cover" />
          </div>
          <div v-else class="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan-400 to-emerald-400 text-xl font-bold text-white select-none">
            {{ businessInitials }}
          </div>
          <div>
            <p class="font-semibold text-slate-900">{{ business.business_name }}</p>
            <p class="text-sm text-slate-500">{{ business.business_email || 'No email set' }}</p>
            <span
              v-if="business.is_verified"
              class="mt-1 inline-block rounded-full bg-emerald-100 px-2.5 py-0.5 text-xs font-medium text-emerald-700"
            >Verified</span>
            <span
              v-else
              class="mt-1 inline-block rounded-full bg-amber-100 px-2.5 py-0.5 text-xs font-medium text-amber-700"
            >Pending Verification</span>
          </div>
        </div>

        <hr class="border-slate-100" />

        <form class="space-y-5" @submit.prevent="promptSave">
          <div>
            <label class="mb-1.5 block text-sm font-medium text-slate-700">Business Name</label>
            <input
              v-model="form.business_name"
              type="text"
              :disabled="!editing"
              class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100 disabled:cursor-default disabled:text-slate-500"
            />
          </div>

          <div>
            <label class="mb-1.5 block text-sm font-medium text-slate-700">Description</label>
            <textarea
              v-model="form.description"
              rows="3"
              :disabled="!editing"
              class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100 disabled:cursor-default disabled:text-slate-500 resize-none"
            />
          </div>

          <div class="grid gap-4 sm:grid-cols-2">
            <div>
              <label class="mb-1.5 block text-sm font-medium text-slate-700">Business Email</label>
              <input
                v-model="form.business_email"
                type="email"
                :disabled="!editing"
                class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100 disabled:cursor-default disabled:text-slate-500"
              />
            </div>
            <div>
              <label class="mb-1.5 block text-sm font-medium text-slate-700">Phone</label>
              <input
                v-model="form.phone"
                type="tel"
                :disabled="!editing"
                class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100 disabled:cursor-default disabled:text-slate-500"
              />
            </div>
          </div>

          <div>
            <label class="mb-1.5 block text-sm font-medium text-slate-700">Address</label>
            <input
              v-model="form.address"
              type="text"
              :disabled="!editing"
              class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100 disabled:cursor-default disabled:text-slate-500"
            />
          </div>

          <div>
            <label class="mb-1.5 block text-sm font-medium text-slate-700">Website</label>
            <input
              v-model="form.website"
              type="url"
              :disabled="!editing"
              placeholder="https://"
              class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100 disabled:cursor-default disabled:text-slate-500"
            />
          </div>

          <div>
            <label class="mb-1.5 block text-sm font-medium text-slate-700">Logo URL</label>
            <input
              v-model="form.logo_url"
              type="url"
              :disabled="!editing"
              placeholder="https://"
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
              <button
                type="button"
                @click="$router.push('/business')"
                class="rounded-xl border border-slate-200 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
              >
                Back to Dashboard
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
    </template>

    <div v-else class="rounded-3xl border border-slate-200 bg-white p-12 text-center">
      <p class="text-slate-500">No business profile found.</p>
    </div>

    <div
      v-if="showSaveModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm"
    >
      <div class="mx-4 w-full max-w-md rounded-3xl bg-white p-8 shadow-2xl">
        <h3 class="text-lg font-bold text-slate-900">Save Changes?</h3>
        <p class="mt-2 text-sm text-slate-500">Are you sure you want to update your business profile?</p>
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
  </div>
</template>

<script setup>
import {ref, computed, onMounted} from 'vue';
import {useToastStore} from '../stores/toast';
import {businessesAPI} from '../services/api';

const toastStore = useToastStore();

const loading = ref(true);
const business = ref(null);
const editing = ref(false);
const saving = ref(false);
const showSaveModal = ref(false);
const formError = ref('');

const form = ref({
    business_name: '',
    description: '',
    business_email: '',
    phone: '',
    address: '',
    website: '',
    logo_url: '',
});

const businessInitials = computed(() => {
    const name = business.value?.business_name || '';
    return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2) || '?';
});

onMounted(async () => {
    try {
        const { data } = await businessesAPI.getMe();
        business.value = data;
        resetForm();
    } catch (err) {
        if (err.response?.status !== 404) {
        toastStore.show('Failed to load business profile.', 'error');
        }
    } finally {
        loading.value = false;
    }
});

function resetForm() {
  form.value = {
    business_name: business.value?.business_name ?? '',
    description: business.value?.description ?? '',
    business_email: business.value?.business_email ?? '',
    phone: business.value?.phone ?? '',
    address: business.value?.address ?? '',
    website: business.value?.website ?? '',
    logo_url: business.value?.logo_url ?? '',
  };
}

function startEditing(){
    editing.value = true;
    formError.value = '';
}

function cancelEditing() {
    editing.value = false;
    formError.value = '';
    resetForm();
}

function promptSave(){
    formError.value = '';
    if (!form.value.business_name?.trim()) {
        formError.value = 'Business name is required.';
        return;
    }
    showSaveModal.value = true;
}

async function confirmSave() {
  saving.value = true;
  try {
    const { data } = await businessesAPI.update(business.value.id, form.value);
    business.value = data;
    resetForm();
    editing.value = false;
    showSaveModal.value = false;
    toastStore.show('Business profile updated successfully.', 'success');
  } catch (err) {
    showSaveModal.value = false;
    formError.value = err.response?.data?.detail || 'Failed to update business profile.';
    toastStore.show('Failed to update business profile.', 'error');
  } finally {
    saving.value = false;
  }
}

</script>

