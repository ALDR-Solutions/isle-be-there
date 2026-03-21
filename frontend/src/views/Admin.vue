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
                {{ biz.username.charAt(0).toUpperCase() }}
              </div>
              <div>
                <div class="flex items-center gap-2">
                  <p class="text-base font-bold text-slate-900">{{ biz.username }}</p>
                  <span
                    class="rounded-xl px-2.5 py-0.5 text-xs font-semibold"
                    :class="statusBadgeClass(biz.status)"
                  >
                    {{ statusLabel(biz.status) }}
                  </span>
                </div>
                <p class="mt-0.5 text-sm text-slate-500">{{ biz.email }}</p>
                <p class="mt-0.5 text-xs text-slate-400">Registered {{ biz.registeredAt }}</p>
              </div>
            </div>

            <div class="flex shrink-0 gap-2">
              <button
                v-if="biz.status !== 'approved'"
                @click="openConfirmModal('approve', 'business', biz)"
                class="rounded-2xl bg-emerald-500 px-5 py-2 text-sm font-semibold text-white transition hover:-translate-y-0.5 hover:bg-emerald-400"
              >
                Approve
              </button>
              <button
                v-if="biz.status !== 'rejected'"
                @click="openConfirmModal('reject', 'business', biz)"
                class="rounded-2xl border border-red-100 px-5 py-2 text-sm font-semibold text-red-500 transition hover:bg-red-50"
              >
                Reject
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
                v-if="listing.images && listing.images.length > 0"
                :src="listing.images[0]"
                :alt="listing.name"
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
                  {{ listing.category }}
                </span>
              </div>
            </div>

            <div class="p-6">
              <h3 class="text-base font-bold text-slate-900 leading-snug">{{ listing.name }}</h3>
              <p class="mt-1 flex items-center gap-1 text-sm text-slate-500">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 shrink-0 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                {{ listing.city }}, {{ listing.country }}
              </p>
              <p class="mt-1 text-xs text-slate-400">
                Submitted by <span class="font-semibold text-slate-600">{{ listing.businessName }}</span> &middot; {{ listing.submittedAt }}
              </p>
              <p class="mt-2 text-sm text-slate-500 line-clamp-2">{{ listing.description }}</p>

              <div class="mt-4 flex gap-2 border-t border-slate-100 pt-4">
                <button
                  v-if="listing.status !== 'approved'"
                  @click="openConfirmModal('approve', 'listing', listing)"
                  class="flex-1 rounded-2xl bg-emerald-500 py-2 text-sm font-semibold text-white transition hover:-translate-y-0.5 hover:bg-emerald-400"
                >
                  Approve
                </button>
                <button
                  v-if="listing.status !== 'rejected'"
                  @click="openConfirmModal('reject', 'listing', listing)"
                  class="flex-1 rounded-2xl border border-red-100 py-2 text-sm font-semibold text-red-500 transition hover:bg-red-50"
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

    </div>

    <div
      v-if="showConfirmModal"
      class="fixed inset-0 z-50 flex items-center justify-center px-4"
      @click.self="showConfirmModal = false"
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
              <span class="font-semibold text-slate-800">{{ confirmTarget?.name || confirmTarget?.username }}</span>
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
            class="flex-1 rounded-2xl border border-slate-200 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
          >
            Cancel
          </button>
          <button
            @click="confirmDecision"
            class="flex-1 rounded-2xl py-3 text-sm font-semibold text-white transition hover:-translate-y-0.5"
            :class="confirmAction === 'approve' ? 'bg-emerald-500 hover:bg-emerald-400' : 'bg-red-500 hover:bg-red-400'"
          >
            {{ confirmAction === 'approve' ? 'Approve' : 'Reject' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'


const businesses = ref([
  {
    id: 1,
    username: 'sunsetresorts',
    email: 'contact@sunsetresorts.com',
    registeredAt: 'Mar 10, 2026',
    status: 'pending',
  },
  {
    id: 2,
    username: 'coraldivers',
    email: 'info@coraldivers.lc',
    registeredAt: 'Mar 12, 2026',
    status: 'approved',
  },
  {
    id: 3,
    username: 'spicegarden',
    email: 'hello@spicegarden.gd',
    registeredAt: 'Mar 15, 2026',
    status: 'rejected',
  },
])

const listings = ref([
  {
    id: 1,
    name: 'Sunset Bay Resort',
    category: 'Hotel',
    description: 'A stunning luxury resort perched above the turquoise bay with panoramic ocean views.',
    city: 'Bridgetown',
    country: 'Barbados',
    businessName: 'sunsetresorts',
    submittedAt: 'Mar 10, 2026',
    images: [],
    status: 'pending',
  },
  {
    id: 2,
    name: 'Coral Reef Diving Tour',
    category: 'Tour',
    description: 'Guided snorkelling and diving experience through the vibrant coral reefs of St. Lucia.',
    city: 'Castries',
    country: 'St. Lucia',
    businessName: 'coraldivers',
    submittedAt: 'Mar 12, 2026',
    images: [],
    status: 'approved',
  },
  {
    id: 3,
    name: 'Spice Garden Restaurant',
    category: 'Restaurant',
    description: 'Farm-to-table dining featuring authentic Grenadian spices and fresh seafood.',
    city: "St. George's",
    country: 'Grenada',
    businessName: 'spicegarden',
    submittedAt: 'Mar 15, 2026',
    images: [],
    status: 'rejected',
  },
])

const mainTab = ref('businesses')
const filterTab = ref('all')

const filterTabs = [
    { label: 'All', value: 'all' },
    { label: 'Pending', value: 'pending' },
    { label: 'Approved', value: 'approved' },
    { label: 'Rejected', value: 'rejected' },
]

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
    confirmAction.value = action
    confirmType.value = type
    confirmTarget.value = target
    showConfirmModal.value = true
}

function confirmDecision() {
    const collection = confirmType.value === 'business' ? businesses : listings
    const index = collection.value.findIndex(item => item.id === confirmTarget.value.id)
    if (index !== -1) {
        collection.value[index] = {
            ...collection.value[index],
            status: confirmAction.value === 'approve' ? 'approved' : 'rejected',

        }
    }
    showConfirmModal.value = false
    confirmTarget.value = null
}
</script>
