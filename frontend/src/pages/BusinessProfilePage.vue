<template>
  <div class="bg-slate-50 min-h-screen">
    <PageHeader
      eyebrow="Business"
      title="Business Profile"
      description="Manage your business information and details."
    />

    <div class="mx-auto max-w-2xl px-4 py-12 sm:px-6 lg:px-8">
      <LoadingSpinner v-if="loading" />

      <InlineAlert v-else-if="error" :message="error.message" />

      <PageStatus
        v-else-if="!business"
        title="No business profile found"
        description="Create your business record first to start managing listings."
        icon="[]"
      />

      <SurfaceCard v-else padding="lg">
        <div class="flex items-center gap-5">
          <div v-if="business.logo_url" class="h-16 w-16 overflow-hidden rounded-2xl border border-slate-200">
            <img :src="business.logo_url" alt="Business logo" class="h-full w-full object-cover" />
          </div>
          <div v-else class="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan-400 to-emerald-400 text-xl font-bold text-white select-none">
            {{ businessInitials }}
          </div>
          <div>
            <p class="font-semibold text-slate-900">{{ business.business_name }}</p>
            <p class="text-sm text-slate-500">{{ business.business_email || 'No email set' }}</p>
            <span
              class="mt-1 inline-block rounded-full px-2.5 py-0.5 text-xs font-medium"
              :class="business.is_verified ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'"
            >
              {{ business.is_verified ? 'Verified' : 'Pending Verification' }}
            </span>
          </div>
        </div>

        <hr class="my-6 border-slate-100" />

        <form class="space-y-5" @submit.prevent="promptSave">
          <FormField label="Business Name" required :error="errors.business_name">
            <input
              v-model="values.business_name"
              type="text"
              :disabled="!editing"
              class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100 disabled:text-slate-500"
            />
          </FormField>

          <FormField label="Description" :error="errors.description">
            <textarea
              v-model="values.description"
              rows="3"
              :disabled="!editing"
              class="w-full resize-none rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100 disabled:text-slate-500"
            />
          </FormField>

          <div class="grid gap-4 sm:grid-cols-2">
            <FormField label="Business Email" :error="errors.business_email">
              <input
                v-model="values.business_email"
                type="email"
                :disabled="!editing"
                class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100 disabled:text-slate-500"
              />
            </FormField>

            <FormField label="Phone" :error="errors.phone">
              <input
                v-model="values.phone"
                type="tel"
                :disabled="!editing"
                class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100 disabled:text-slate-500"
              />
            </FormField>
          </div>

          <FormField label="Address" :error="errors.address">
            <input
              v-model="values.address"
              type="text"
              :disabled="!editing"
              class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100 disabled:text-slate-500"
            />
          </FormField>

          <FormField label="Website" :error="errors.website">
            <input
              v-model="values.website"
              type="url"
              :disabled="!editing"
              placeholder="https://"
              class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100 disabled:text-slate-500"
            />
          </FormField>

          <FormField label="Logo URL" :error="errors.logo_url">
            <input
              v-model="values.logo_url"
              type="url"
              :disabled="!editing"
              placeholder="https://"
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
              <router-link
                to="/business"
                class="rounded-xl border border-slate-200 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
              >
                Back to Dashboard
              </router-link>
            </template>
            <template v-else>
              <button
                type="submit"
                class="rounded-xl bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:opacity-60"
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
    </div>

    <ConfirmDialog
      v-model="showSaveDialog"
      eyebrow="Business profile"
      title="Save business profile changes?"
      description="Your business details will be updated immediately."
      confirm-label="Confirm"
      loading-label="Saving..."
      tone="success"
      :loading="isSubmitting"
      @confirm="confirmSave"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import ConfirmDialog from '@/components/ui/ConfirmDialog.vue'
import FormField from '@/components/ui/FormField.vue'
import InlineAlert from '@/components/ui/InlineAlert.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import PageHeader from '@/components/ui/PageHeader.vue'
import PageStatus from '@/components/ui/PageStatus.vue'
import SurfaceCard from '@/components/ui/SurfaceCard.vue'
import { useAsyncData } from '@/composables/useAsyncData'
import { useForm } from '@/composables/useForm'
import { businessesService } from '@/services/businessesService'
import { useToastStore } from '@/stores/toast'

const toastStore = useToastStore()
const editing = ref(false)
const showSaveDialog = ref(false)

const state = useAsyncData(({ signal }) => businessesService.getMe({ signal }), {
  initialData: null,
})
const { error, loading } = state

const form = useForm({
  business_name: '',
  description: '',
  business_email: '',
  phone: '',
  address: '',
  website: '',
  logo_url: '',
})
const { errors, isSubmitting, submitError, values } = form

const business = computed(() => state.data.value)
const businessInitials = computed(() => {
  const name = business.value?.business_name || ''
  return name.split(' ').map((word) => word[0]).join('').toUpperCase().slice(0, 2) || '?'
})

function syncForm() {
  form.reset({
    business_name: business.value?.business_name ?? '',
    description: business.value?.description ?? '',
    business_email: business.value?.business_email ?? '',
    phone: business.value?.phone ?? '',
    address: business.value?.address ?? '',
    website: business.value?.website ?? '',
    logo_url: business.value?.logo_url ?? '',
  })
}

onMounted(async () => {
  await state.load().catch(() => {})
  syncForm()
})

function cancelEditing() {
  editing.value = false
  form.clearErrors()
  syncForm()
}

function validate() {
  const errors = {}
  if (!form.values.value.business_name?.trim()) {
    errors.business_name = 'Business name is required.'
  }
  form.setErrors(errors)
  return Object.keys(errors).length === 0
}

function promptSave() {
  form.clearErrors()
  if (!validate()) return
  showSaveDialog.value = true
}

async function confirmSave() {
  if (!business.value) return
  form.isSubmitting.value = true

  try {
    state.data.value = await businessesService.update(business.value.id, form.values.value)
    syncForm()
    editing.value = false
    showSaveDialog.value = false
    toastStore.show('Business profile updated successfully.', 'success')
  } catch (error) {
    form.submitError.value = error.message || 'Failed to update business profile.'
    toastStore.show(form.submitError.value, 'error')
  } finally {
    form.isSubmitting.value = false
  }
}
</script>
