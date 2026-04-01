<template>
  <div class="bg-slate-50 min-h-screen">

    <!-- Loading -->
    <div v-if="businessStore.loading" class="flex min-h-screen items-center justify-center">
      <svg class="h-8 w-8 animate-spin text-cyan-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
      </svg>
    </div>

    <!-- No listings yet -->
    <div v-else-if="businessStore.listings.length === 0" class="flex min-h-screen flex-col items-center justify-center px-4 text-center">
      <div class="flex h-16 w-16 items-center justify-center rounded-3xl bg-slate-100">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
      </div>
      <h2 class="mt-6 text-2xl font-bold text-slate-900">No listings yet</h2>
      <p class="mt-2 max-w-sm text-sm text-slate-500">Add your first listing to start managing your property on Isle Be There.</p>
      <button
        @click="openCreateModal"
        class="mt-8 inline-flex items-center gap-2 rounded-2xl bg-cyan-400 px-6 py-3 text-sm font-semibold text-slate-950 transition hover:-translate-y-0.5 hover:bg-cyan-300"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4" />
        </svg>
        Add your first listing
      </button>
    </div>

    <!-- Per-listing view -->
    <template v-else>

      <!-- Header -->
      <div class="bg-white border-b border-slate-200">
        <div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <p class="text-xs font-semibold uppercase tracking-[0.28em] text-cyan-600">
            {{ businessStore.business?.name || 'Your Business' }}
          </p>
          <div class="mt-2 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div class="flex flex-wrap items-center gap-3">
              <span
                class="rounded-xl px-3 py-1 text-xs font-semibold"
                :class="statusBadgeClass(businessStore.activeListing?.status)"
              >
                {{ statusLabel(businessStore.activeListing?.status) }}
              </span>
              <h1 class="text-2xl font-bold text-slate-900 sm:text-3xl">
                {{ businessStore.activeListing?.title }}
              </h1>
            </div>
            <div class="flex shrink-0 gap-2">
              <button
                v-if="businessStore.activeListing?.status !== 'inactive'"
                @click="openEditModal(businessStore.activeListing)"
                class="inline-flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:bg-slate-50"
              >
                Edit Listing
              </button>
              <button
                v-if="businessStore.activeListing?.status !== 'inactive'"
                @click="openArchiveModal(businessStore.activeListing)"
                class="inline-flex items-center gap-2 rounded-2xl border border-red-100 px-5 py-2.5 text-sm font-semibold text-red-500 transition hover:bg-red-50"
              >
                Archive
              </button>
              <button
                v-if="businessStore.activeListing?.status === 'inactive'"
                @click="unarchiveListing(businessStore.activeListing)"
                class="inline-flex items-center gap-2 rounded-2xl border border-emerald-100 px-5 py-2.5 text-sm font-semibold text-emerald-600 transition hover:bg-emerald-50"
              >
                Restore Listing
              </button>
            </div>
          </div>
          <p v-if="businessStore.activeListing?.address" class="mt-2 flex items-center gap-1.5 text-sm text-slate-500">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 shrink-0 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a2 2 0 01-2.828 0l-4.243-4.243a8 8 0 1111.314 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            {{ [businessStore.activeListing?.address?.city, businessStore.activeListing?.address?.country].filter(Boolean).join(', ') }}
          </p>
        </div>
      </div>

      <div class="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8 space-y-8">

        <!-- Stats -->
        <div class="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <p class="text-sm font-medium text-slate-500">Total Services</p>
            <p class="mt-2 text-3xl font-bold text-slate-900">0</p>
            <p class="mt-1 text-xs text-slate-400">Coming soon</p>
          </div>
          <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <p class="text-sm font-medium text-slate-500">Active Services</p>
            <p class="mt-2 text-3xl font-bold text-cyan-600">0</p>
            <p class="mt-1 text-xs text-slate-400">Coming soon</p>
          </div>
          <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <p class="text-sm font-medium text-slate-500">Reviews</p>
            <p class="mt-2 text-3xl font-bold text-slate-900">{{ businessStore.activeListing?.review_count ?? 0 }}</p>
          </div>
          <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <p class="text-sm font-medium text-slate-500">Avg Rating</p>
            <p class="mt-2 text-3xl font-bold text-amber-500">
              {{ businessStore.activeListing?.avg_rating ? businessStore.activeListing.avg_rating.toFixed(1) : '—' }}
            </p>
          </div>
        </div>

        <!-- Services -->
        <div>
          <div class="mb-6 flex items-center justify-between">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.28em] text-cyan-600">Listing</p>
              <h2 class="mt-1 text-xl font-bold text-slate-900">Services</h2>
            </div>
            <button
              disabled
              title="Service management coming soon"
              class="inline-flex cursor-not-allowed items-center gap-2 rounded-2xl bg-slate-100 px-5 py-2.5 text-sm font-semibold text-slate-400"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4" />
              </svg>
              Add Service
            </button>
          </div>

          <div class="rounded-3xl border-2 border-dashed border-slate-200 bg-white px-6 py-20 text-center">
            <div class="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-100">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <p class="mt-4 text-base font-semibold text-slate-700">No services yet</p>
            <p class="mt-1.5 text-sm text-slate-400">Services for this listing will appear here once the feature is available.</p>
          </div>
        </div>

      </div>
    </template>

    <!-- Create / Edit Modal -->
    <div
      v-if="showFormModal"
      class="fixed inset-0 z-50 flex items-center justify-center px-4"
      @click.self="closeFormModal"
    >
      <div class="absolute inset-0 bg-slate-950/50 backdrop-blur-sm"></div>
      <div class="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-3xl border border-slate-200 bg-white shadow-2xl no-scrollbar">

        <div class="sticky top-0 z-10 flex items-center justify-between border-b border-slate-100 bg-white px-8 py-6">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.28em] text-cyan-600">
              {{ isEditing ? 'Edit Listing' : 'New Listing' }}
            </p>
            <h2 class="mt-1 text-xl font-bold text-slate-900">
              {{ isEditing ? 'Update your listing details' : 'Create a new listing' }}
            </h2>
          </div>
          <button
            @click="closeFormModal"
            class="flex h-9 w-9 items-center justify-center rounded-2xl border border-slate-200 text-slate-500 transition hover:bg-slate-50"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form @submit.prevent="submitForm" class="px-8 py-6 space-y-5">

          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-1.5">Listing Title <span class="text-red-500">*</span></label>
            <input v-model="form.title" type="text" placeholder="e.g. Sunset Bay Resort"
              class="w-full rounded-2xl border px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition"
              :class="formErrors.title ? 'border-red-300 bg-red-50 focus:border-red-400' : 'border-slate-200 bg-white focus:border-cyan-400'" />
            <p v-if="formErrors.title" class="mt-1.5 text-xs text-red-500">{{ formErrors.title }}</p>
          </div>

          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-1.5">Business Type <span class="text-red-500">*</span></label>
            <div v-if="businessTypes.length" class="grid grid-cols-2 gap-3 sm:grid-cols-4">
              <button
                v-for="type in businessTypes" :key="type.id" type="button"
                @click="form.business_type = type.id"
                class="flex flex-col items-center gap-2 rounded-2xl border py-3.5 text-xs font-semibold transition"
                :class="form.business_type === type.id ? 'border-cyan-400 bg-cyan-50 text-cyan-700' : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300'"
              >{{ type.name }}</button>
            </div>
            <p v-else class="text-sm text-slate-400">Loading types...</p>
            <p v-if="formErrors.business_type" class="mt-1.5 text-xs text-red-500">{{ formErrors.business_type }}</p>
          </div>

          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-1.5">Description <span class="text-red-500">*</span></label>
            <textarea v-model="form.description" rows="3" placeholder="Describe what makes this listing special..."
              class="w-full rounded-2xl border px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition resize-none"
              :class="formErrors.description ? 'border-red-300 bg-red-50 focus:border-red-400' : 'border-slate-200 bg-white focus:border-cyan-400'"></textarea>
            <p v-if="formErrors.description" class="mt-1.5 text-xs text-red-500">{{ formErrors.description }}</p>
          </div>

          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-1.5">Base Price (USD) <span class="text-red-500">*</span></label>
            <div class="relative">
              <span class="absolute left-4 top-1/2 -translate-y-1/2 text-sm font-semibold text-slate-400">$</span>
              <input v-model="form.base_price" type="number" min="0" step="0.01" placeholder="0.00"
                class="w-full rounded-2xl border pl-8 pr-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition"
                :class="formErrors.base_price ? 'border-red-300 bg-red-50 focus:border-red-400' : 'border-slate-200 bg-white focus:border-cyan-400'" />
            </div>
            <p v-if="formErrors.base_price" class="mt-1.5 text-xs text-red-500">{{ formErrors.base_price }}</p>
          </div>

          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-1.5">Street Address</label>
            <input v-model="form.street" type="text" placeholder="e.g. 12 Bay Street"
              class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400" />
          </div>

          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-1.5">City <span class="text-red-500">*</span></label>
              <input v-model="form.city" type="text" placeholder="e.g. Bridgetown"
                class="w-full rounded-2xl border px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition"
                :class="formErrors.city ? 'border-red-300 bg-red-50 focus:border-red-400' : 'border-slate-200 bg-white focus:border-cyan-400'" />
              <p v-if="formErrors.city" class="mt-1.5 text-xs text-red-500">{{ formErrors.city }}</p>
            </div>
            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-1.5">State / Parish</label>
              <input v-model="form.state" type="text" placeholder="e.g. Saint Michael"
                class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400" />
            </div>
          </div>

          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-1.5">Postal Code</label>
              <input v-model="form.postal_code" type="text" placeholder="e.g. BB11000"
                class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400" />
            </div>
            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-1.5">Country / Island <span class="text-red-500">*</span></label>
              <input v-model="form.country" type="text" placeholder="e.g. Barbados"
                class="w-full rounded-2xl border px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition"
                :class="formErrors.country ? 'border-red-300 bg-red-50 focus:border-red-400' : 'border-slate-200 bg-white focus:border-cyan-400'" />
              <p v-if="formErrors.country" class="mt-1.5 text-xs text-red-500">{{ formErrors.country }}</p>
            </div>
          </div>

          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-1.5">Phone Number</label>
              <input v-model="form.phone_number" type="tel" placeholder="e.g. +1 246 555 0100"
                class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400" />
            </div>
            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-1.5">Email Address</label>
              <input v-model="form.email_address" type="email" placeholder="e.g. contact@resort.com"
                class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400" />
            </div>
          </div>

          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-1.5">Images</label>
            <div
              class="relative flex flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 py-10 text-center transition cursor-pointer"
              :class="isDragging ? 'border-cyan-400 bg-cyan-50' : 'border-slate-200 bg-slate-50 hover:border-slate-300 hover:bg-white'"
              @dragover.prevent="isDragging = true"
              @dragleave.prevent="isDragging = false"
              @drop.prevent="onDrop"
              @click="fileInputRef.click()"
            >
              <input ref="fileInputRef" type="file" accept="image/*" multiple class="hidden" @change="onFileChange" />
              <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-slate-300 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <p class="text-sm font-semibold text-slate-600">Drag & drop images here</p>
              <p class="mt-1 text-xs text-slate-400">or click to browse files</p>
              <p v-if="uploadingCount > 0" class="mt-2 text-xs font-semibold text-cyan-600">
                Uploading {{ uploadingCount }} file{{ uploadingCount > 1 ? 's' : '' }}...
              </p>
            </div>
            <div v-if="form.image_urls.filter(u => u).length" class="mt-3 grid grid-cols-3 gap-3 sm:grid-cols-4">
              <div
                v-for="(url, index) in form.image_urls.filter(u => u)" :key="url"
                class="relative group aspect-square overflow-hidden rounded-2xl border border-slate-200 bg-slate-100"
              >
                <img :src="url" class="h-full w-full object-cover" />
                <button type="button" @click.stop="removeImage(index)"
                  class="absolute top-1.5 right-1.5 flex h-6 w-6 items-center justify-center rounded-full bg-slate-900/70 text-white opacity-0 transition group-hover:opacity-100">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <div class="rounded-2xl border border-amber-100 bg-amber-50 px-5 py-4">
            <div class="flex items-start gap-3">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 shrink-0 text-amber-500 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p class="text-sm text-amber-700">
                <span class="font-semibold">Requires approval.</span>
                {{ isEditing ? 'Edits will be reviewed before the listing updates publicly.' : 'New listings are marked as Pending Approval until reviewed by a moderator.' }}
              </p>
            </div>
          </div>

          <p v-if="formErrors.submit" class="text-sm text-red-500 text-center">{{ formErrors.submit }}</p>

          <div class="flex gap-3 pt-2">
            <button type="button" @click="closeFormModal"
              class="flex-1 rounded-2xl border border-slate-200 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50">
              Cancel
            </button>
            <button type="submit" :disabled="formSubmitting"
              class="flex-1 rounded-2xl bg-slate-900 py-3 text-sm font-semibold text-white transition hover:-translate-y-0.5 hover:bg-slate-800 disabled:opacity-50">
              {{ formSubmitting ? 'Saving...' : isEditing ? 'Save Changes' : 'Create Listing' }}
            </button>
          </div>

        </form>
      </div>
    </div>

    <!-- Archive Modal -->
    <div
      v-if="showArchiveModal"
      class="fixed inset-0 z-50 flex items-center justify-center px-4"
      @click.self="showArchiveModal = false"
    >
      <div class="absolute inset-0 bg-slate-950/50 backdrop-blur-sm"></div>
      <div class="relative w-full max-w-md rounded-3xl border border-slate-200 bg-white p-8 shadow-2xl">
        <div class="flex items-start gap-4">
          <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-red-50">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8l1 12a2 2 0 002 2h8a2 2 0 002-2L19 8M10 12v4M14 12v4" />
            </svg>
          </div>
          <div>
            <h3 class="text-lg font-bold text-slate-900">Archive Listing?</h3>
            <p class="mt-2 text-sm leading-6 text-slate-600">
              <span class="font-semibold text-slate-800">{{ listingToArchive?.title }}</span> will be hidden from visitors. You can restore it at any time.
            </p>
          </div>
        </div>
        <div class="mt-6 flex gap-3">
          <button @click="showArchiveModal = false"
            class="flex-1 rounded-2xl border border-slate-200 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50">
            Cancel
          </button>
          <button @click="confirmArchive" :disabled="archiveSubmitting"
            class="flex-1 rounded-2xl bg-red-500 py-3 text-sm font-semibold text-white transition hover:-translate-y-0.5 hover:bg-red-400 disabled:opacity-50">
            {{ archiveSubmitting ? 'Archiving...' : 'Archive' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { businessesAPI, listingsAPI, uploadsAPI } from '../services/api'
import { useToastStore } from '../stores/toast'
import { useBusinessStore } from '../stores/business'

const toastStore = useToastStore()
const businessStore = useBusinessStore()
const businessTypes = ref([])

onMounted(() => {
  fetchBusinessTypes()
})

watch(() => businessStore.showCreateModal, (val) => {
  if (val) {
    openCreateModal()
    businessStore.showCreateModal = false
  }
})

async function fetchBusinessTypes() {
  try {
    const response = await businessesAPI.getTypes()
    businessTypes.value = response.data
  } catch (error) {
    console.error('Error fetching business types:', error)
  }
}

function statusLabel(status) {
  if (status === 'active') return 'Active'
  if (status === 'pending') return 'Pending Approval'
  if (status === 'inactive') return 'Archived'
  return status ?? ''
}

function statusBadgeClass(status) {
  if (status === 'active') return 'bg-emerald-500 text-white'
  if (status === 'pending') return 'bg-amber-400 text-slate-900'
  if (status === 'inactive') return 'bg-slate-500 text-white'
  return 'bg-slate-300 text-slate-900'
}

const showFormModal = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const formSubmitting = ref(false)

const blankForm = () => ({
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
})

const form = ref(blankForm())
const formErrors = ref({})

function openCreateModal() {
  isEditing.value = false
  editingId.value = null
  form.value = blankForm()
  formErrors.value = {}
  showFormModal.value = true
}

function openEditModal(item) {
  isEditing.value = true
  editingId.value = item.id
  form.value = {
    title: item.title ?? '',
    business_type: item.business_type ?? '',
    description: item.description ?? '',
    base_price: item.base_price ?? '',
    street: item.address?.street ?? '',
    city: item.address?.city ?? '',
    state: item.address?.state ?? '',
    postal_code: item.address?.postal_code ?? '',
    country: item.address?.country ?? '',
    phone_number: item.phone_number ?? '',
    email_address: item.email_address ?? '',
    image_urls: item.image_urls?.length ? [...item.image_urls] : [],
  }
  formErrors.value = {}
  showFormModal.value = true
}

function closeFormModal() {
  showFormModal.value = false
}

const fileInputRef = ref(null)
const isDragging = ref(false)
const uploadingCount = ref(0)

async function uploadFiles(files) {
  for (const file of files) {
    if (!file.type.startsWith('image/')) continue
    uploadingCount.value++
    try {
      const formData = new FormData()
      formData.append('file', file)
      const res = await uploadsAPI.uploadImage(formData)
      form.value.image_urls.push(res.data.url)
    } catch (e) {
      toastStore.show('Failed to upload an image.', 'error')
    } finally {
      uploadingCount.value--
    }
  }
}

function onFileChange(e) {
  uploadFiles(Array.from(e.target.files))
  e.target.value = ''
}

function onDrop(e) {
  isDragging.value = false
  uploadFiles(Array.from(e.dataTransfer.files))
}

function removeImage(index) {
  form.value.image_urls.splice(index, 1)
}

function validateForm() {
  const errors = {}
  if (!form.value.title.trim()) errors.title = 'Listing title is required.'
  if (!form.value.business_type) errors.business_type = 'Please select a business type.'
  if (!form.value.description.trim()) errors.description = 'Description is required.'
  if (!form.value.base_price || Number(form.value.base_price) <= 0) errors.base_price = 'Please enter a valid price.'
  if (!form.value.city.trim()) errors.city = 'City is required.'
  if (!form.value.country.trim()) errors.country = 'Country / Island is required.'
  formErrors.value = errors
  return Object.keys(errors).length === 0
}

async function submitForm() {
  if (!validateForm()) return
  formSubmitting.value = true
  const payload = {
    title: form.value.title.trim(),
    business_type: form.value.business_type,
    description: form.value.description.trim(),
    base_price: Number(form.value.base_price),
    address: {
      street: form.value.street.trim() || null,
      city: form.value.city.trim(),
      state: form.value.state.trim() || null,
      postal_code: form.value.postal_code.trim() || null,
      country: form.value.country.trim(),
    },
    phone_number: form.value.phone_number.trim() || null,
    email_address: form.value.email_address.trim() || null,
    image_urls: form.value.image_urls,
  }
  try {
    if (isEditing.value) {
      const response = await listingsAPI.update(editingId.value, payload)
      businessStore.updateListing(response.data)
      toastStore.show('Listing updated successfully.', 'success')
    } else {
      const response = await listingsAPI.create(payload)
      businessStore.addListing(response.data)
      toastStore.show('Listing created successfully.', 'success')
    }
    closeFormModal()
  } catch (e) {
    formErrors.value.submit = e.response?.data?.detail || 'Failed to save listing. Please try again.'
    toastStore.show('Failed to save listing.', 'error')
  } finally {
    formSubmitting.value = false
  }
}

const showArchiveModal = ref(false)
const listingToArchive = ref(null)
const archiveSubmitting = ref(false)

function openArchiveModal(item) {
  listingToArchive.value = item
  showArchiveModal.value = true
}

async function confirmArchive() {
  if (!listingToArchive.value) return
  archiveSubmitting.value = true
  try {
    await listingsAPI.update(listingToArchive.value.id, { status: 'inactive' })
    businessStore.updateListing({ ...listingToArchive.value, status: 'inactive' })
    const next = businessStore.listings.find(l => l.id !== listingToArchive.value.id && l.status !== 'inactive')
    if (next) businessStore.setActiveListing(next.id)
    showArchiveModal.value = false
    listingToArchive.value = null
    toastStore.show('Listing archived.', 'success')
  } catch (e) {
    toastStore.show('Failed to archive listing.', 'error')
  } finally {
    archiveSubmitting.value = false
  }
}

async function unarchiveListing(item) {
  try {
    await listingsAPI.update(item.id, { status: 'active' })
    businessStore.updateListing({ ...item, status: 'active' })
    toastStore.show('Listing restored.', 'success')
  } catch (e) {
    toastStore.show('Failed to restore listing.', 'error')
  }
}
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
</style>
