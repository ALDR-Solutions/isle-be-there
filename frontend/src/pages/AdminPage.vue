<template>
  <div class="bg-slate-50 min-h-screen">
    <PageHeader
      eyebrow="Admin Panel"
      title="Content & Account Management"
      description="Review business accounts and listing submissions from one streamlined dashboard."
    />

    <div class="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8 space-y-8">
      <div class="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <SurfaceCard v-for="item in statsCards" :key="item.label">
          <p class="text-sm font-medium text-slate-500">{{ item.label }}</p>
          <p class="mt-2 text-3xl font-bold" :class="item.valueClass">{{ item.value }}</p>
        </SurfaceCard>
      </div>

      <div class="flex gap-2">
        <button
          type="button"
          class="rounded-2xl px-6 py-2.5 text-sm font-semibold transition"
          :class="mainTab === 'businesses' ? 'bg-slate-900 text-white shadow-sm' : 'border border-slate-200 bg-white text-slate-600 hover:border-slate-300 hover:text-slate-900'"
          @click="mainTab = 'businesses'"
        >
          Businesses
        </button>
        <button
          type="button"
          class="rounded-2xl px-6 py-2.5 text-sm font-semibold transition"
          :class="mainTab === 'listings' ? 'bg-slate-900 text-white shadow-sm' : 'border border-slate-200 bg-white text-slate-600 hover:border-slate-300 hover:text-slate-900'"
          @click="mainTab = 'listings'"
        >
          Listings
        </button>
      </div>

      <div class="flex flex-wrap gap-2">
        <button
          v-for="tab in filterTabs"
          :key="tab.value"
          type="button"
          class="rounded-2xl px-5 py-2 text-sm font-semibold transition"
          :class="filterTab === tab.value ? 'bg-cyan-500 text-slate-950 shadow-sm' : 'border border-slate-200 bg-white text-slate-600 hover:border-slate-300 hover:text-slate-900'"
          @click="filterTab = tab.value"
        >
          {{ tab.label }}
        </button>
      </div>

      <div v-if="mainTab === 'businesses'" class="space-y-4">
        <PageStatus
          v-if="filteredBusinesses.length === 0"
          title="No businesses found"
          description="No business accounts match this status."
          icon="[]"
        />

        <SurfaceCard
          v-for="biz in filteredBusinesses"
          :key="biz.id"
          v-else
          class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"
        >
          <div class="flex items-center gap-4">
            <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-slate-100 text-lg font-bold text-slate-500">
              {{ biz.username.charAt(0).toUpperCase() }}
            </div>
            <div>
              <div class="flex items-center gap-2">
                <p class="text-base font-bold text-slate-900">{{ biz.username }}</p>
                <StatusBadge :label="statusLabel(biz.status)" :tone="statusTone(biz.status)" />
              </div>
              <p class="mt-0.5 text-sm text-slate-500">{{ biz.email }}</p>
              <p class="mt-0.5 text-xs text-slate-400">Registered {{ biz.registeredAt }}</p>
            </div>
          </div>

          <div class="flex shrink-0 gap-2">
            <button
              v-if="biz.status !== 'approved'"
              type="button"
              class="rounded-2xl bg-emerald-500 px-5 py-2 text-sm font-semibold text-white transition hover:bg-emerald-400"
              @click="openConfirmModal('approve', 'business', biz)"
            >
              Approve
            </button>
            <button
              v-if="biz.status !== 'rejected'"
              type="button"
              class="rounded-2xl border border-red-100 px-5 py-2 text-sm font-semibold text-red-500 transition hover:bg-red-50"
              @click="openConfirmModal('reject', 'business', biz)"
            >
              Reject
            </button>
          </div>
        </SurfaceCard>
      </div>

      <div v-else>
        <PageStatus
          v-if="filteredListings.length === 0"
          title="No listings found"
          description="No listing submissions match this status."
          icon="[]"
        />

        <div v-else class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          <SurfaceCard
            v-for="listing in filteredListings"
            :key="listing.id"
            class="overflow-hidden"
          >
            <div class="flex items-center justify-between gap-2">
              <StatusBadge :label="statusLabel(listing.status)" :tone="statusTone(listing.status)" />
              <span class="rounded-xl bg-slate-900/70 px-3 py-1 text-xs font-semibold text-white">
                {{ listing.category }}
              </span>
            </div>

            <h3 class="mt-4 text-base font-bold text-slate-900">{{ listing.name }}</h3>
            <p class="mt-1 text-sm text-slate-500">{{ listing.city }}, {{ listing.country }}</p>
            <p class="mt-1 text-xs text-slate-400">
              Submitted by <span class="font-semibold text-slate-600">{{ listing.businessName }}</span> - {{ listing.submittedAt }}
            </p>
            <p class="mt-3 text-sm text-slate-500 line-clamp-2">{{ listing.description }}</p>

            <div class="mt-4 flex gap-2 border-t border-slate-100 pt-4">
              <button
                v-if="listing.status !== 'approved'"
                type="button"
                class="flex-1 rounded-2xl bg-emerald-500 py-2 text-sm font-semibold text-white transition hover:bg-emerald-400"
                @click="openConfirmModal('approve', 'listing', listing)"
              >
                Approve
              </button>
              <button
                v-if="listing.status !== 'rejected'"
                type="button"
                class="flex-1 rounded-2xl border border-red-100 py-2 text-sm font-semibold text-red-500 transition hover:bg-red-50"
                @click="openConfirmModal('reject', 'listing', listing)"
              >
                Reject
              </button>
            </div>
          </SurfaceCard>
        </div>
      </div>
    </div>

    <ConfirmDialog
      v-model="showConfirmModal"
      eyebrow="Admin action"
      :title="`${confirmAction === 'approve' ? 'Approve' : 'Reject'} ${confirmType === 'business' ? 'business' : 'listing'}?`"
      :description="confirmDescription"
      :confirm-label="confirmAction === 'approve' ? 'Approve' : 'Reject'"
      :tone="confirmAction === 'approve' ? 'success' : 'danger'"
      @confirm="confirmDecision"
    />
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import ConfirmDialog from '@/components/ui/ConfirmDialog.vue'
import PageHeader from '@/components/ui/PageHeader.vue'
import PageStatus from '@/components/ui/PageStatus.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import SurfaceCard from '@/components/ui/SurfaceCard.vue'

const businesses = ref([
  { id: 1, username: 'sunsetresorts', email: 'contact@sunsetresorts.com', registeredAt: 'Mar 10, 2026', status: 'pending' },
  { id: 2, username: 'coraldivers', email: 'info@coraldivers.lc', registeredAt: 'Mar 12, 2026', status: 'approved' },
  { id: 3, username: 'spicegarden', email: 'hello@spicegarden.gd', registeredAt: 'Mar 15, 2026', status: 'rejected' },
])

const listings = ref([
  { id: 1, name: 'Sunset Bay Resort', category: 'Hotel', description: 'A stunning luxury resort perched above the turquoise bay with panoramic ocean views.', city: 'Bridgetown', country: 'Barbados', businessName: 'sunsetresorts', submittedAt: 'Mar 10, 2026', status: 'pending' },
  { id: 2, name: 'Coral Reef Diving Tour', category: 'Tour', description: 'Guided snorkelling and diving experience through the vibrant coral reefs of St. Lucia.', city: 'Castries', country: 'St. Lucia', businessName: 'coraldivers', submittedAt: 'Mar 12, 2026', status: 'approved' },
  { id: 3, name: 'Spice Garden Restaurant', category: 'Restaurant', description: 'Farm-to-table dining featuring authentic Grenadian spices and fresh seafood.', city: "St. George's", country: 'Grenada', businessName: 'spicegarden', submittedAt: 'Mar 15, 2026', status: 'rejected' },
])

const mainTab = ref('businesses')
const filterTab = ref('all')
const showConfirmModal = ref(false)
const confirmAction = ref('')
const confirmType = ref('')
const confirmTarget = ref(null)

const filterTabs = [
  { label: 'All', value: 'all' },
  { label: 'Pending', value: 'pending' },
  { label: 'Approved', value: 'approved' },
  { label: 'Rejected', value: 'rejected' },
]

const filteredBusinesses = computed(() => {
  if (filterTab.value === 'all') return businesses.value
  return businesses.value.filter((item) => item.status === filterTab.value)
})

const filteredListings = computed(() => {
  if (filterTab.value === 'all') return listings.value
  return listings.value.filter((item) => item.status === filterTab.value)
})

const statsCards = computed(() => [
  { label: 'Total Businesses', value: businesses.value.length, valueClass: 'text-slate-900' },
  { label: 'Pending Businesses', value: businesses.value.filter((item) => item.status === 'pending').length, valueClass: 'text-amber-500' },
  { label: 'Total Listings', value: listings.value.length, valueClass: 'text-slate-900' },
  { label: 'Pending Listings', value: listings.value.filter((item) => item.status === 'pending').length, valueClass: 'text-amber-500' },
])

const confirmDescription = computed(() => {
  const targetName = confirmTarget.value?.name || confirmTarget.value?.username || 'This item'
  const actionLabel = confirmAction.value === 'approve' ? 'approved' : 'rejected'
  return `${targetName} will be marked as ${actionLabel}.`
})

function statusLabel(status) {
  if (status === 'approved') return 'Approved'
  if (status === 'pending') return 'Pending'
  if (status === 'rejected') return 'Rejected'
  return status
}

function statusTone(status) {
  if (status === 'approved') return 'success'
  if (status === 'pending') return 'warning'
  if (status === 'rejected') return 'danger'
  return 'neutral'
}

function openConfirmModal(action, type, target) {
  confirmAction.value = action
  confirmType.value = type
  confirmTarget.value = target
  showConfirmModal.value = true
}

function confirmDecision() {
  const collection = confirmType.value === 'business' ? businesses : listings
  const index = collection.value.findIndex((item) => item.id === confirmTarget.value.id)

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
