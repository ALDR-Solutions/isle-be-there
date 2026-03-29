<template>
  <div class="bg-slate-50 min-h-screen">
    <PageHeader title="Manage Your Listings">
      <template #actions>
        <button
          type="button"
          class="inline-flex items-center gap-2 rounded-2xl bg-cyan-400 px-6 py-3 text-sm font-semibold text-slate-950 transition hover:-translate-y-0.5 hover:bg-cyan-300"
          @click="openCreateModal"
        >
          Add Listing
        </button>
      </template>
    </PageHeader>

    <div class="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8 space-y-8">
      <div class="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <SurfaceCard v-for="card in statsCards" :key="card.label">
          <p class="text-sm font-medium text-slate-500">{{ card.label }}</p>
          <p class="mt-2 text-3xl font-bold" :class="card.valueClass">{{ card.value }}</p>
        </SurfaceCard>
      </div>

      <div class="flex flex-wrap gap-2">
        <button
          v-for="tab in tabs"
          :key="tab.value"
          type="button"
          class="rounded-2xl px-5 py-2.5 text-sm font-semibold transition"
          :class="activeTab === tab.value ? 'bg-slate-900 text-white shadow-sm' : 'border border-slate-200 bg-white text-slate-600 hover:border-slate-300 hover:text-slate-900'"
          @click="activeTab = tab.value"
        >
          {{ tab.label }}
        </button>
      </div>

      <LoadingSpinner v-if="dashboardLoading" />

      <InlineAlert v-else-if="dashboardError" :message="dashboardError.message" />

      <PageStatus
        v-else-if="filteredListings.length === 0"
        title="No listings found"
        :description="activeTab === 'all' ? 'Click Add Listing to create your first listing.' : 'No listings with this status yet.'"
        icon="[]"
      />

      <div v-else class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <BusinessListingCard
          v-for="item in filteredListings"
          :key="item.id"
          :listing="item"
          :business-types="businessTypes"
          @edit="openEditModal"
          @archive="openArchiveModal"
          @unarchive="handleUnarchive"
        />
      </div>
    </div>

    <BusinessListingFormDialog
      v-model="showFormModal"
      :listing="editingListing"
      :business-types="businessTypes"
      :submitting="formSubmitting"
      @save="handleSaveListing"
    />

    <ConfirmDialog
      v-model="showArchiveModal"
      eyebrow="Listing status"
      title="Archive this listing?"
      :description="archiveTarget ? `${archiveTarget.title} will be hidden from active browsing.` : ''"
      confirm-label="Archive"
      loading-label="Archiving..."
      :loading="archiveSubmitting"
      @confirm="confirmArchive"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import BusinessListingCard from '@/features/business/BusinessListingCard.vue'
import BusinessListingFormDialog from '@/features/business/BusinessListingFormDialog.vue'
import { useBusinessListings } from '@/features/business/useBusinessListings'
import ConfirmDialog from '@/components/ui/ConfirmDialog.vue'
import InlineAlert from '@/components/ui/InlineAlert.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import PageHeader from '@/components/ui/PageHeader.vue'
import PageStatus from '@/components/ui/PageStatus.vue'
import SurfaceCard from '@/components/ui/SurfaceCard.vue'
import { useToastStore } from '@/stores/toast'

const toastStore = useToastStore()
const {
  activeTab,
  archiveListing,
  businessTypes,
  dashboardState,
  filteredListings,
  loadDashboard,
  saveListing,
  stats,
  tabs,
  unarchiveListing,
} = useBusinessListings()
const { error: dashboardError, loading: dashboardLoading } = dashboardState

const showFormModal = ref(false)
const editingListing = ref(null)
const formSubmitting = ref(false)

const showArchiveModal = ref(false)
const archiveTarget = ref(null)
const archiveSubmitting = ref(false)

const statsCards = computed(() => [
  { label: 'Total Listings', value: stats.value.total, valueClass: 'text-slate-900' },
  { label: 'Active', value: stats.value.active, valueClass: 'text-cyan-600' },
  { label: 'Pending Approval', value: stats.value.pending, valueClass: 'text-amber-500' },
  { label: 'Inactive', value: stats.value.inactive, valueClass: 'text-slate-400' },
])

onMounted(() => {
  loadDashboard().catch(() => {})
})

function openCreateModal() {
  editingListing.value = null
  showFormModal.value = true
}

function openEditModal(listing) {
  editingListing.value = listing
  showFormModal.value = true
}

async function handleSaveListing(payload) {
  formSubmitting.value = true

  try {
    await saveListing(editingListing.value?.id, payload)
    toastStore.show(editingListing.value ? 'Listing updated successfully.' : 'Listing created successfully.', 'success')
    showFormModal.value = false
    editingListing.value = null
  } catch (error) {
    toastStore.show(error.message || 'Failed to save listing.', 'error')
  } finally {
    formSubmitting.value = false
  }
}

function openArchiveModal(listing) {
  archiveTarget.value = listing
  showArchiveModal.value = true
}

async function confirmArchive() {
  if (!archiveTarget.value) return

  archiveSubmitting.value = true

  try {
    await archiveListing(archiveTarget.value)
    toastStore.show('Listing archived.', 'success')
    showArchiveModal.value = false
    archiveTarget.value = null
  } catch (error) {
    toastStore.show(error.message || 'Failed to archive listing.', 'error')
  } finally {
    archiveSubmitting.value = false
  }
}

async function handleUnarchive(listing) {
  try {
    await unarchiveListing(listing)
    toastStore.show('Listing restored.', 'success')
  } catch (error) {
    toastStore.show(error.message || 'Failed to restore listing.', 'error')
  }
}
</script>
