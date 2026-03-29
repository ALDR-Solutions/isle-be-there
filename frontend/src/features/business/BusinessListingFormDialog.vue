<template>
  <BaseDialog
    :model-value="modelValue"
    :title="listing ? 'Edit Listing' : 'Add Listing'"
    :description="listing ? 'Update your listing details and media.' : 'Create a new listing for travelers to discover.'"
    eyebrow="Listing editor"
    max-width="lg"
    @update:modelValue="$emit('update:modelValue', $event)"
  >
    <form class="space-y-5" @submit.prevent="submit">
      <div class="grid gap-4 sm:grid-cols-2">
        <FormField label="Listing Title" required :error="errors.title">
          <input v-model="values.title" type="text" class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100" />
        </FormField>
        <FormField label="Business Type" required :error="errors.business_type">
          <select v-model="values.business_type" class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100">
            <option value="">Select a type</option>
            <option v-for="type in businessTypes" :key="type.id" :value="type.id">{{ type.name }}</option>
          </select>
        </FormField>
      </div>

      <FormField label="Description" required :error="errors.description">
        <textarea v-model="values.description" rows="4" class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100" />
      </FormField>

      <div class="grid gap-4 sm:grid-cols-2">
        <FormField label="Base Price" required :error="errors.base_price">
          <input v-model="values.base_price" type="number" min="0" step="0.01" class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100" />
        </FormField>
        <FormField label="Phone Number">
          <input v-model="values.phone_number" type="text" class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100" />
        </FormField>
      </div>

      <div class="grid gap-4 sm:grid-cols-2">
        <FormField label="Street">
          <input v-model="values.street" type="text" class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100" />
        </FormField>
        <FormField label="City" required :error="errors.city">
          <input v-model="values.city" type="text" class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100" />
        </FormField>
      </div>

      <div class="grid gap-4 sm:grid-cols-3">
        <FormField label="State">
          <input v-model="values.state" type="text" class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100" />
        </FormField>
        <FormField label="Postal Code">
          <input v-model="values.postal_code" type="text" class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100" />
        </FormField>
        <FormField label="Country / Island" required :error="errors.country">
          <input v-model="values.country" type="text" class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100" />
        </FormField>
      </div>

      <FormField label="Email Address">
        <input v-model="values.email_address" type="email" class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100" />
      </FormField>

      <div>
        <div class="mb-2 flex items-center justify-between gap-3">
          <label class="text-sm font-medium text-slate-700">Listing Images</label>
          <span v-if="uploadingCount > 0" class="text-xs font-semibold text-cyan-600">Uploading {{ uploadingCount }}...</span>
        </div>

        <div
          class="rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-5 text-center"
          :class="isDragging ? 'border-cyan-400 bg-cyan-50' : ''"
          @dragenter.prevent="isDragging = true"
          @dragover.prevent
          @dragleave.prevent="isDragging = false"
          @drop.prevent="onDrop"
        >
          <p class="text-sm text-slate-500">Drop image files here or</p>
          <button
            type="button"
            class="mt-3 rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
            @click="fileInputRef?.click()"
          >
            Choose Files
          </button>
          <input ref="fileInputRef" type="file" multiple accept="image/*" class="hidden" @change="onFileChange" />
        </div>

        <div v-if="values.image_urls.length" class="mt-4 grid grid-cols-2 gap-4 sm:grid-cols-3">
          <div v-for="(imageUrl, index) in values.image_urls" :key="imageUrl" class="relative overflow-hidden rounded-2xl border border-slate-200 bg-slate-100">
            <img :src="imageUrl" alt="" class="h-28 w-full object-cover" />
            <button
              type="button"
              class="absolute right-2 top-2 rounded-full bg-slate-900/80 px-2 py-1 text-xs font-semibold text-white"
              @click="removeImage(index)"
            >
              Remove
            </button>
          </div>
        </div>
      </div>

      <InlineAlert v-if="submitError" :message="submitError" />
    </form>

    <template #footer>
      <div class="flex gap-3">
        <button
          type="button"
          class="flex-1 rounded-2xl border border-slate-200 bg-white py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
          @click="$emit('update:modelValue', false)"
        >
          Cancel
        </button>
        <button
          type="button"
          class="flex-1 rounded-2xl bg-slate-900 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:opacity-60"
          :disabled="submitting"
          @click="submit"
        >
          {{ submitting ? 'Saving...' : listing ? 'Save Changes' : 'Create Listing' }}
        </button>
      </div>
    </template>
  </BaseDialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import BaseDialog from '@/components/ui/BaseDialog.vue'
import FormField from '@/components/ui/FormField.vue'
import InlineAlert from '@/components/ui/InlineAlert.vue'
import { useForm } from '@/composables/useForm'
import { uploadService } from '@/services/uploadService'
import { useToastStore } from '@/stores/toast'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  listing: {
    type: Object,
    default: null,
  },
  businessTypes: {
    type: Array,
    default: () => [],
  },
  submitting: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue', 'save'])
const toastStore = useToastStore()

const fileInputRef = ref(null)
const isDragging = ref(false)
const uploadingCount = ref(0)

function createBlankForm() {
  return {
    title: '',
    business_type: '',
    description: '',
    base_price: '',
    street: '',
    city: '',
    state: '',
    postal_code: '',
    country: '',
    phone_number: '',
    email_address: '',
    image_urls: [],
  }
}

const form = useForm(createBlankForm())
const { errors, submitError, values } = form

watch(
  () => props.modelValue,
  (isOpen) => {
    if (isOpen) {
      form.reset(props.listing ? mapListingToForm(props.listing) : createBlankForm())
    }
  }
)

function mapListingToForm(listing) {
  return {
    title: listing.title ?? '',
    business_type: listing.business_type ?? '',
    description: listing.description ?? '',
    base_price: listing.base_price ?? '',
    street: listing.address?.street ?? '',
    city: listing.address?.city ?? '',
    state: listing.address?.state ?? '',
    postal_code: listing.address?.postal_code ?? '',
    country: listing.address?.country ?? '',
    phone_number: listing.phone_number ?? '',
    email_address: listing.email_address ?? '',
    image_urls: listing.image_urls?.length ? [...listing.image_urls] : [],
  }
}

function validate() {
  const errors = {}

  if (!form.values.value.title?.trim()) errors.title = 'Listing title is required.'
  if (!form.values.value.business_type) errors.business_type = 'Please select a business type.'
  if (!form.values.value.description?.trim()) errors.description = 'Description is required.'
  if (!form.values.value.base_price || Number(form.values.value.base_price) <= 0) errors.base_price = 'Please enter a valid price.'
  if (!form.values.value.city?.trim()) errors.city = 'City is required.'
  if (!form.values.value.country?.trim()) errors.country = 'Country / Island is required.'

  form.setErrors(errors)
  return Object.keys(errors).length === 0
}

async function uploadFiles(files) {
  for (const file of files) {
    if (!file.type.startsWith('image/')) continue

    uploadingCount.value += 1
    try {
      const result = await uploadService.uploadImage(file)
      form.values.value.image_urls.push(result.url)
    } catch (error) {
      toastStore.show(error.message || 'Image upload failed.', 'error')
    } finally {
      uploadingCount.value -= 1
    }
  }
}

function onFileChange(event) {
  uploadFiles(Array.from(event.target.files || []))
  event.target.value = ''
}

function onDrop(event) {
  isDragging.value = false
  uploadFiles(Array.from(event.dataTransfer.files || []))
}

function removeImage(index) {
  form.values.value.image_urls.splice(index, 1)
}

function submit() {
  form.clearErrors()
  if (!validate()) return

  emit('save', {
    title: form.values.value.title.trim(),
    business_type: form.values.value.business_type,
    description: form.values.value.description.trim(),
    base_price: Number(form.values.value.base_price),
    address: {
      street: form.values.value.street.trim() || null,
      city: form.values.value.city.trim(),
      state: form.values.value.state.trim() || null,
      postal_code: form.values.value.postal_code.trim() || null,
      country: form.values.value.country.trim(),
    },
    phone_number: form.values.value.phone_number.trim() || null,
    email_address: form.values.value.email_address.trim() || null,
    image_urls: form.values.value.image_urls,
  })
}
</script>
