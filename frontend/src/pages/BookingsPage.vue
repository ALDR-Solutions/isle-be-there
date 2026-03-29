<template>
  <div class="bg-slate-50 min-h-screen">
    <PageHeader
      eyebrow="Travel Plans"
      title="My Bookings"
      description="Review upcoming plans and manage pending reservations in one place."
    />

    <div class="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <LoadingSpinner v-if="loading" />

      <InlineAlert v-else-if="error" :message="error.message" />

      <PageStatus
        v-else-if="isEmpty"
        title="No bookings yet"
        description="Once you book a listing, it will appear here."
        icon="[]"
      >
        <template #actions>
          <router-link
            to="/listings"
            class="inline-flex items-center justify-center rounded-2xl bg-slate-900 px-6 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
          >
            Browse Listings
          </router-link>
        </template>
      </PageStatus>

      <div v-else class="space-y-4">
        <SurfaceCard
          v-for="booking in data"
          :key="booking.id"
          class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between"
        >
          <div>
            <h3 class="text-lg font-semibold text-slate-900">Booking #{{ booking.id }}</h3>
            <p class="mt-1 text-sm text-slate-500">Service ID: {{ booking.service_id }}</p>
            <p class="mt-4 text-sm text-slate-500">Booking time</p>
            <p class="font-medium text-slate-900">{{ formatDateTime(booking.booking_time) }}</p>
          </div>

          <div class="flex flex-col items-start gap-3 sm:items-end">
            <StatusBadge :label="toStatusLabel(booking.status)" :tone="toStatusTone(booking.status)" />
            <button
              v-if="booking.status === 'pending'"
              type="button"
              class="rounded-xl border border-red-200 bg-red-50 px-4 py-2 text-sm font-semibold text-red-700 transition hover:bg-red-100"
              @click="openCancelDialog(booking)"
            >
              Cancel booking
            </button>
          </div>
        </SurfaceCard>
      </div>
    </div>

    <ConfirmDialog
      v-model="showCancelDialog"
      eyebrow="Confirm action"
      title="Cancel this booking?"
      description="This will cancel the selected pending booking."
      confirm-label="Cancel booking"
      loading-label="Cancelling..."
      :loading="cancelling"
      @confirm="confirmCancel"
    />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import ConfirmDialog from '@/components/ui/ConfirmDialog.vue'
import InlineAlert from '@/components/ui/InlineAlert.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import PageHeader from '@/components/ui/PageHeader.vue'
import PageStatus from '@/components/ui/PageStatus.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import SurfaceCard from '@/components/ui/SurfaceCard.vue'
import { useAsyncData } from '@/composables/useAsyncData'
import { bookingsService } from '@/services/bookingsService'
import { useToastStore } from '@/stores/toast'
import { formatDateTime } from '@/utils/formatters'

const toastStore = useToastStore()
const state = useAsyncData(({ signal }) => bookingsService.getAll({}, { signal }), {
  initialData: [],
})
const { data, error, isEmpty, loading } = state

const showCancelDialog = ref(false)
const bookingToCancel = ref(null)
const cancelling = ref(false)

onMounted(() => {
  state.load().catch(() => {})
})

function toStatusLabel(status) {
  if (status === 'confirmed') return 'Confirmed'
  if (status === 'pending') return 'Pending'
  if (status === 'completed') return 'Completed'
  if (status === 'cancelled') return 'Cancelled'
  return status
}

function toStatusTone(status) {
  if (status === 'confirmed') return 'success'
  if (status === 'pending') return 'warning'
  if (status === 'completed') return 'info'
  if (status === 'cancelled') return 'danger'
  return 'neutral'
}

function openCancelDialog(booking) {
  bookingToCancel.value = booking
  showCancelDialog.value = true
}

async function confirmCancel() {
  if (!bookingToCancel.value) return

  cancelling.value = true

  try {
    await bookingsService.cancel(bookingToCancel.value.id)
    await state.refresh()
    toastStore.show('Booking cancelled.', 'success')
    showCancelDialog.value = false
    bookingToCancel.value = null
  } catch (error) {
    toastStore.show(error.message || 'Unable to cancel booking.', 'error')
  } finally {
    cancelling.value = false
  }
}
</script>
