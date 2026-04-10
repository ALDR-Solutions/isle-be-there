<template>
  <div class="bg-slate-50 min-h-screen">
    <div class="bg-white border-b border-slate-200">
      <div class="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <p class="text-sm font-semibold uppercase tracking-[0.28em] text-cyan-600">
          Admin Panel
        </p>
        <h1 class="mt-3 text-3xl font-bold text-slate-900 sm:text-4xl">
          Content &amp; Account Management
        </h1>
      </div>
    </div>

    <div class="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8 space-y-8">
      <div
        v-if="loading"
        class="rounded-3xl border border-slate-200 bg-white px-6 py-16 text-center shadow-sm"
      >
        <svg
          class="mx-auto h-8 w-8 animate-spin text-cyan-500"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            class="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            stroke-width="4"
          />
          <path
            class="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
          />
        </svg>
        <p class="mt-4 text-sm text-slate-500">Loading admin data...</p>
      </div>

      <div
        v-else-if="loadError"
        class="rounded-3xl border border-red-200 bg-white px-6 py-8 text-center shadow-sm"
      >
        <p class="text-sm font-semibold text-red-600">{{ loadError }}</p>
        <button
          @click="loadAdminData"
          class="mt-4 rounded-2xl bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800"
        >
          Retry
        </button>
      </div>

      <template v-else>
      <div class="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <p class="text-sm font-medium text-slate-500">Total Businesses</p>
          <p class="mt-2 text-3xl font-bold text-slate-900">{{ stats.totalBusinesses }}</p>
        </div>
        <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <p class="text-sm font-medium text-slate-500">Pending Businesses</p>
          <p class="mt-2 text-3xl font-bold text-amber-500">{{ stats.pendingBusinesses }}</p>
        </div>
        <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <p class="text-sm font-medium text-slate-500">Total Listings</p>
          <p class="mt-2 text-3xl font-bold text-slate-900">{{ stats.totalListings }}</p>
        </div>
        <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <p class="text-sm font-medium text-slate-500">Pending Listings</p>
          <p class="mt-2 text-3xl font-bold text-amber-500">{{ stats.pendingListings }}</p>
        </div>
      </div>

      <div class="flex gap-2">
        <button
          @click="mainTab = 'businesses'"
          class="rounded-2xl px-6 py-2.5 text-sm font-semibold transition"
          :class="mainTab === 'businesses'
            ? 'bg-slate-900 text-white shadow-sm'
            : 'border border-slate-200 bg-white text-slate-600 hover:border-slate-300 hover:text-slate-900'"
        >
          Businesses
        </button>
        <button
          @click="mainTab = 'listings'"
          class="rounded-2xl px-6 py-2.5 text-sm font-semibold transition"
          :class="mainTab === 'listings'
            ? 'bg-slate-900 text-white shadow-sm'
            : 'border border-slate-200 bg-white text-slate-600 hover:border-slate-300 hover:text-slate-900'"
        >
          Listings
        </button>
      </div>

      <div class="flex flex-wrap gap-2">
        <button
          v-for="tab in filterTabs"
          :key="tab.value"
          @click="filterTab = tab.value"
          class="rounded-2xl px-5 py-2 text-sm font-semibold transition"
          :class="filterTab === tab.value
            ? 'bg-cyan-500 text-slate-950 shadow-sm'
            : 'border border-slate-200 bg-white text-slate-600 hover:border-slate-300 hover:text-slate-900'"
        >
          {{ tab.label }}
        </button>
      </div>

      <template v-if="mainTab === 'businesses'">
        <div
          v-if="filteredBusinesses.length === 0"
          class="rounded-3xl border border-slate-200 bg-white px-6 py-20 text-center shadow-sm"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="mx-auto h-12 w-12 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          <p class="mt-4 text-base font-medium text-slate-500">No businesses found.</p>
          <p class="mt-1 text-sm text-slate-400">No business accounts with this status yet.</p>
        </div>

        <div v-else class="space-y-4">
          <div
            v-for="biz in filteredBusinesses"
            :key="biz.id"
            class="flex flex-col gap-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm sm:flex-row sm:items-center sm:justify-between"
          >
            <div class="flex items-center gap-4">
              <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-slate-100 text-lg font-bold text-slate-500">
                {{ (biz.business_name || '?').charAt(0).toUpperCase() }}
              </div>
              <div>
                <div class="flex items-center gap-2">
                  <p class="text-base font-bold text-slate-900">{{ biz.business_name }}</p>
                  <span
                    class="rounded-xl px-2.5 py-0.5 text-xs font-semibold"
                    :class="statusBadgeClass(biz.status)"
                  >
                    {{ statusLabel(biz.status) }}
                  </span>
                </div>
                <p class="mt-0.5 text-sm text-slate-500">{{ biz.business_email || 'No email set' }}</p>
                <p class="mt-0.5 text-xs text-slate-400">Registered {{ formatDate(biz.created_at) }}</p>
              </div>
            </div>

            <div class="flex shrink-0 gap-2">
              <button
                v-if="biz.status !== 'approved'"
                @click="openConfirmModal('approve', 'business', biz)"
                :disabled="decisionSubmitting"
                class="rounded-2xl bg-emerald-500 px-5 py-2 text-sm font-semibold text-white transition hover:-translate-y-0.5 hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:translate-y-0"
              >
                Approve
              </button>
              <span
                v-if="biz.status === 'approved'"
                class="rounded-2xl border border-slate-100 px-5 py-2 text-sm font-semibold text-slate-400"
              >
                Approved
              </span>
            </div>
          </div>
        </div>
      </template>

      <template v-if="mainTab === 'listings'">
        <div
          v-if="filteredListings.length === 0"
          class="rounded-3xl border border-slate-200 bg-white px-6 py-20 text-center shadow-sm"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="mx-auto h-12 w-12 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
          <p class="mt-4 text-base font-medium text-slate-500">No listings found.</p>
          <p class="mt-1 text-sm text-slate-400">No submissions with this status yet.</p>
        </div>

        <div v-else class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          <div
            v-for="listing in filteredListings"
            :key="listing.id"
            class="group overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm transition hover:-translate-y-1 hover:shadow-md"
          >
            <div class="relative h-48 bg-slate-100 overflow-hidden">
              <img
                v-if="listing.image_urls && listing.image_urls.length > 0"
                :src="listing.image_urls[0]"
                :alt="listing.title"
                class="h-full w-full object-cover transition duration-500 group-hover:scale-105"
              />
              <div v-else class="flex h-full w-full items-center justify-center text-slate-300">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-14 w-14" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <div class="absolute top-3 left-3">
                <span
                  class="rounded-xl px-3 py-1 text-xs font-semibold"
                  :class="statusBadgeClass(listing.status)"
                >
                  {{ statusLabel(listing.status) }}
                </span>
              </div>
              <div class="absolute top-3 right-3">
                <span class="rounded-xl bg-slate-900/70 px-3 py-1 text-xs font-semibold text-white backdrop-blur-sm">
                  {{ listing.business_type_name || 'Listing' }}
                </span>
              </div>
            </div>

            <div class="p-6">
              <h3 class="text-base font-bold text-slate-900 leading-snug">{{ listing.title }}</h3>
              <p class="mt-1 flex items-center gap-1 text-sm text-slate-500">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 shrink-0 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                {{ [listing.address?.city, listing.address?.country].filter(Boolean).join(', ') || 'No location set' }}
              </p>
              <p class="mt-1 text-xs text-slate-400">
                Submitted by <span class="font-semibold text-slate-600">{{ businessNameById[listing.business_id] || 'Unknown business' }}</span> &middot; {{ formatDate(listing.created_at) }}
              </p>
              <p class="mt-2 text-sm text-slate-500 line-clamp-2">{{ listing.description }}</p>

              <div class="mt-4 flex gap-2 border-t border-slate-100 pt-4">
                <button
                  v-if="listing.status !== 'approved'"
                  @click="openConfirmModal('approve', 'listing', listing)"
                  :disabled="decisionSubmitting"
                  class="flex-1 rounded-2xl bg-emerald-500 py-2 text-sm font-semibold text-white transition hover:-translate-y-0.5 hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:translate-y-0"
                >
                  Approve
                </button>
                <button
                  v-if="listing.status !== 'rejected'"
                  @click="openConfirmModal('reject', 'listing', listing)"
                  :disabled="decisionSubmitting"
                  class="flex-1 rounded-2xl border border-red-100 py-2 text-sm font-semibold text-red-500 transition hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  Reject
                </button>
                <span
                  v-if="listing.status === 'approved'"
                  class="flex-1 py-2 text-center text-sm font-semibold text-slate-400"
                >
                  Approved
                </span>
              </div>
            </div>
          </div>
        </div>
      </template>
      </template>

    </div>

    <div
      v-if="showConfirmModal"
      class="fixed inset-0 z-50 flex items-center justify-center px-4"
      @click.self="!decisionSubmitting && (showConfirmModal = false)"
    >
      <div class="absolute inset-0 bg-slate-950/50 backdrop-blur-sm"></div>
      <div class="relative w-full max-w-md rounded-3xl border border-slate-200 bg-white p-8 shadow-2xl">
        <div class="flex items-start gap-4">
          <div
            class="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl"
            :class="confirmAction === 'approve' ? 'bg-emerald-50' : 'bg-red-50'"
          >
            <svg v-if="confirmAction === 'approve'" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <div>
            <h3 class="text-lg font-bold text-slate-900">
              {{ confirmAction === 'approve' ? 'Approve' : 'Reject' }}
              {{ confirmType === 'business' ? 'Business' : 'Listing' }}?
            </h3>
            <p class="mt-2 text-sm leading-6 text-slate-600">
              <span class="font-semibold text-slate-800">{{ confirmTargetLabel }}</span>
              will be marked as
              <span :class="confirmAction === 'approve' ? 'text-emerald-600 font-semibold' : 'text-red-600 font-semibold'">
                {{ confirmAction === 'approve' ? 'approved' : 'rejected' }}
              </span>
              and the system will update its status accordingly.
            </p>
          </div>
        </div>
        <div class="mt-6 flex gap-3">
          <button
            @click="showConfirmModal = false"
            :disabled="decisionSubmitting"
            class="flex-1 rounded-2xl border border-slate-200 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
          >
            Cancel
          </button>
          <button
            @click="confirmDecision"
            :disabled="decisionSubmitting"
            class="flex-1 rounded-2xl py-3 text-sm font-semibold text-white transition hover:-translate-y-0.5"
            :class="confirmAction === 'approve'
              ? 'bg-emerald-500 hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:translate-y-0'
              : 'bg-red-500 hover:bg-red-400 disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:translate-y-0'"
          >
            {{ decisionSubmitting ? 'Processing...' : (confirmAction === 'approve' ? 'Approve' : 'Reject') }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { businessesAPI, listingsAPI } from '../services/api'
import { useToastStore } from '../stores/toast'

const toastStore = useToastStore()
const loading = ref(true)
const loadError = ref('')
const decisionSubmitting = ref(false)

const businesses = ref([])
const listings = ref([])

const mainTab = ref('businesses')
const filterTab = ref('all')

const filterTabs = computed(() => {
    const baseTabs = [
        { label: 'All', value: 'all' },
        { label: 'Pending', value: 'pending' },
        { label: 'Approved', value: 'approved' },
    ]

    if (mainTab.value === 'listings') {
        baseTabs.push({ label: 'Rejected', value: 'rejected' })
    }

    return baseTabs
})

const businessNameById = computed(() =>
  Object.fromEntries(
    businesses.value.map((business) => [business.id, business.business_name]),
  ),
)

const confirmTargetLabel = computed(
  () =>
    confirmTarget.value?.title ||
    confirmTarget.value?.business_name ||
    confirmTarget.value?.name ||
    confirmTarget.value?.username ||
    'this item',
)

const filteredBusinesses = computed(() => {
    if(filterTab.value === 'all') return businesses.value
    return businesses.value.filter(b => b.status === filterTab.value)
})

const filteredListings = computed(() => {
    if (filterTab.value === 'all') return listings.value
    return listings.value.filter(l => l.status === filterTab.value)
})

const stats = computed(() => ({
    totalBusinesses: businesses.value.length,
    pendingBusinesses: businesses.value.filter(b => b.status === 'pending').length,
    totalListings: listings.value.length,
    pendingListings: listings.value.filter(l => l.status === 'pending').length, 
}))

function statusLabel(status) {
    if (status === 'approved') return 'Approved'
    if (status === 'pending') return 'Pending'
    if (status === 'rejected') return 'Rejected'
    return status
}

function statusBadgeClass(status) {
    if (status === 'approved') return 'bg-emerald-500 text-white'
    if (status === 'pending') return 'bg-amber-400 text-slate-900'
    if (status === 'rejected') return 'bg-red-500 text-white'
    return 'bg-slate-300 text-slate-900'
}

const showConfirmModal = ref(false)
const confirmAction = ref('') 
const confirmType = ref('')
const confirmTarget = ref(null)

function openConfirmModal(action, type, target){
    if (decisionSubmitting.value) return
    confirmAction.value = action
    confirmType.value = type
    confirmTarget.value = target
    showConfirmModal.value = true
}

function formatDate(value) {
    if (!value) return 'Unknown date'
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) return 'Unknown date'
    return new Intl.DateTimeFormat('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
    }).format(date)
}

function normalizeBusinessStatus(business) {
    return {
        ...business,
        status: business.is_verified ? 'approved' : 'pending',
    }
}

async function loadAdminData() {
    loading.value = true
    loadError.value = ''
    try {
        const [businessesResponse, listingsResponse] = await Promise.all([
            businessesAPI.getAll({ limit: 100 }),
            listingsAPI.getAll({ limit: 100 }),
        ])

        businesses.value = (businessesResponse.data ?? []).map(normalizeBusinessStatus)
        listings.value = listingsResponse.data ?? []
    } catch (error) {
        loadError.value = 'Failed to load admin data.'
        toastStore.show('Failed to load admin data.', 'error')
    } finally {
        loading.value = false
    }
}

async function confirmDecision() {
    if (!confirmTarget.value || decisionSubmitting.value) return
    decisionSubmitting.value = true

    try {
        if (confirmType.value === 'business') {
            if (confirmAction.value !== 'approve') {
                throw new Error('Business rejection is not supported by the current backend.')
            }

            const response = await businessesAPI.update(confirmTarget.value.id, {
                is_verified: true,
            })
            const updatedBusiness = normalizeBusinessStatus(response.data)
            const index = businesses.value.findIndex((item) => item.id === updatedBusiness.id)
            if (index !== -1) {
                businesses.value[index] = updatedBusiness
            }
            toastStore.show('Business approved.', 'success')
        } else {
            const nextStatus = confirmAction.value === 'approve' ? 'approved' : 'rejected'
            const response = await listingsAPI.update(confirmTarget.value.id, {
                status: nextStatus,
            })
            const index = listings.value.findIndex((item) => item.id === response.data.id)
            if (index !== -1) {
                listings.value[index] = response.data
            }
            toastStore.show(`Listing ${nextStatus}.`, 'success')
        }

        showConfirmModal.value = false
        confirmTarget.value = null
    } catch (error) {
        toastStore.show(
            error.response?.data?.detail || error.message || 'Failed to update status.',
            'error',
        )
    } finally {
        decisionSubmitting.value = false
    }
}

onMounted(() => {
    loadAdminData()
})

watch(mainTab, () => {
    if (!filterTabs.value.some((tab) => tab.value === filterTab.value)) {
        filterTab.value = 'all'
    }
})
</script>
