<template>
  <div class="bg-slate-50 min-h-screen">
    <PageHeader
      eyebrow="Account"
      title="My Profile"
      description="Manage your personal information and account settings."
    />

    <div class="mx-auto max-w-2xl px-4 py-12 sm:px-6 lg:px-8">
      <SurfaceCard padding="lg">
        <div class="flex items-center gap-5">
          <div class="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan-400 to-emerald-400 text-xl font-bold text-white select-none">
            {{ initials }}
          </div>
          <div>
            <p class="font-semibold text-slate-900">{{ authStore.user?.first_name }} {{ authStore.user?.last_name }}</p>
            <p class="text-sm text-slate-500">{{ authStore.user?.email }}</p>
            <span
              class="mt-1 inline-block rounded-full px-2.5 py-0.5 text-xs font-medium"
              :class="authStore.user?.is_business ? 'bg-cyan-100 text-cyan-700' : 'bg-slate-100 text-slate-600'"
            >
              {{ authStore.user?.is_business ? 'Business Account' : 'Personal Account' }}
            </span>
          </div>
        </div>

        <hr class="my-6 border-slate-100" />

        <form class="space-y-5" @submit.prevent="promptSave">
          <div class="grid gap-4 sm:grid-cols-2">
            <FormField label="First name" :error="errors.first_name">
              <input
                v-model="values.first_name"
                type="text"
                :disabled="!editing"
                class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100 disabled:text-slate-500"
              />
            </FormField>
            <FormField label="Last name" :error="errors.last_name">
              <input
                v-model="values.last_name"
                type="text"
                :disabled="!editing"
                class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100 disabled:text-slate-500"
              />
            </FormField>
          </div>

          <FormField label="Username" :error="errors.username">
            <input
              v-model="values.username"
              type="text"
              :disabled="!editing"
              class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100 disabled:text-slate-500"
            />
          </FormField>

          <FormField label="Email" :error="errors.email">
            <input
              v-model="values.email"
              type="email"
              :disabled="!editing"
              class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100 disabled:text-slate-500"
            />
          </FormField>

          <InlineAlert v-if="submitError" :message="submitError" />

          <div class="flex gap-3 pt-1">
            <template v-if="!editing">
              <button
                type="button"
                class="rounded-xl bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800"
                @click="editing = true"
              >
                Edit Profile
              </button>
            </template>
            <template v-else>
              <button
                type="submit"
                class="rounded-xl bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800"
                :disabled="isSubmitting"
              >
                {{ isSubmitting ? 'Saving...' : 'Save Changes' }}
              </button>
              <button
                type="button"
                class="rounded-xl border border-slate-200 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
                @click="cancelEditing"
              >
                Cancel
              </button>
            </template>
          </div>
        </form>
      </SurfaceCard>

      <SurfaceCard class="mt-6 border-red-200" padding="lg">
        <h2 class="text-base font-semibold text-red-700">Danger Zone</h2>
        <p class="mt-1 text-sm text-slate-500">
          Disabling your account will log you out immediately. An administrator will need to reactivate it.
        </p>
        <button
          type="button"
          class="mt-4 rounded-xl border border-red-300 bg-red-50 px-5 py-2.5 text-sm font-semibold text-red-700 transition hover:bg-red-100"
          @click="showDisableDialog = true"
        >
          Disable Account
        </button>
      </SurfaceCard>
    </div>

    <ConfirmDialog
      v-model="showSaveDialog"
      eyebrow="Profile update"
      title="Save profile changes?"
      description="Your account details will be updated immediately."
      confirm-label="Confirm"
      loading-label="Saving..."
      tone="success"
      :loading="isSubmitting"
      @confirm="confirmSave"
    />

    <ConfirmDialog
      v-model="showDisableDialog"
      eyebrow="Danger zone"
      title="Disable your account?"
      description="This will deactivate your account and log you out immediately."
      confirm-label="Disable account"
      loading-label="Disabling..."
      :loading="disabling"
      @confirm="confirmDisable"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import ConfirmDialog from '@/components/ui/ConfirmDialog.vue'
import FormField from '@/components/ui/FormField.vue'
import InlineAlert from '@/components/ui/InlineAlert.vue'
import PageHeader from '@/components/ui/PageHeader.vue'
import SurfaceCard from '@/components/ui/SurfaceCard.vue'
import { useForm } from '@/composables/useForm'
import { authService } from '@/services/authService'
import { profileService } from '@/services/profileService'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'

const authStore = useAuthStore()
const toastStore = useToastStore()

const editing = ref(false)
const disabling = ref(false)
const showSaveDialog = ref(false)
const showDisableDialog = ref(false)

const form = useForm({
  first_name: '',
  last_name: '',
  username: '',
  email: '',
})
const { errors, isSubmitting, submitError, values } = form

const initials = computed(() => {
  const first = authStore.user?.first_name?.[0] || ''
  const last = authStore.user?.last_name?.[0] || ''
  return (first + last).toUpperCase() || authStore.user?.username?.[0]?.toUpperCase() || '?'
})

function syncForm() {
  form.reset({
    first_name: authStore.user?.first_name ?? '',
    last_name: authStore.user?.last_name ?? '',
    username: authStore.user?.username ?? '',
    email: authStore.user?.email ?? '',
  })
}

onMounted(async () => {
  if (!authStore.user) {
    await authStore.fetchUser()
  }

  syncForm()
})

function cancelEditing() {
  editing.value = false
  form.clearErrors()
  syncForm()
}

function validate() {
  const errors = {}

  if (!form.values.value.first_name) errors.first_name = 'First name is required.'
  if (!form.values.value.last_name) errors.last_name = 'Last name is required.'
  if (!form.values.value.email) errors.email = 'Email is required.'

  form.setErrors(errors)
  return Object.keys(errors).length === 0
}

function promptSave() {
  form.clearErrors()
  if (!validate()) return
  showSaveDialog.value = true
}

async function confirmSave() {
  form.isSubmitting.value = true

  try {
    await profileService.update(form.values.value)
    await authStore.fetchUser()
    syncForm()
    editing.value = false
    showSaveDialog.value = false
    toastStore.show('Profile updated successfully.', 'success')
  } catch (error) {
    form.submitError.value = error.message || 'Failed to update profile.'
    toastStore.show(form.submitError.value, 'error')
  } finally {
    form.isSubmitting.value = false
  }
}

async function confirmDisable() {
  disabling.value = true

  try {
    await authService.disableAccount()
    authStore.logout()
    toastStore.show('Your account has been disabled.', 'success')
    window.location.assign('/')
  } catch (error) {
    toastStore.show(error.message || 'Failed to disable account.', 'error')
  } finally {
    disabling.value = false
  }
}
</script>
