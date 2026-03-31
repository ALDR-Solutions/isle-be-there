<template>
  <div class="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
    <div class="mb-8">
      <p class="text-sm font-semibold uppercase tracking-[0.25em] text-slate-500">Trips</p>
      <h1 class="mt-2 text-3xl font-bold text-slate-900">My Bookings</h1>
      <p class="mt-2 text-sm text-slate-500">Track upcoming reservations and manage pending bookings.</p>
    </div>

    <div
      v-if="error"
      class="mb-6 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
    >
      {{ error }}
    </div>

    <div v-if="loading" class="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
      <div
        v-for="n in 6"
        :key="n"
        class="animate-pulse rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
      >
        <div class="h-5 w-1/3 rounded bg-slate-200"></div>
        <div class="mt-4 h-4 w-1/2 rounded bg-slate-100"></div>
        <div class="mt-6 h-16 rounded-2xl bg-slate-100"></div>
        <div class="mt-6 flex justify-between">
          <div class="h-4 w-24 rounded bg-slate-100"></div>
          <div class="h-10 w-28 rounded-2xl bg-slate-200"></div>
        </div>
      </div>
    </div>

    <div
      v-else-if="bookings.length === 0"
      class="rounded-3xl border border-slate-200 bg-white px-6 py-20 text-center shadow-sm"
    >
      <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-slate-100 text-slate-400">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7V3m8 4V3m-9 8h10m-11 9h12a2 2 0 002-2V7a2 2 0 00-2-2H6a2 2 0 00-2 2v11a2 2 0 002 2z" />
        </svg>
      </div>
      <h2 class="mt-5 text-lg font-bold text-slate-900">No bookings yet</h2>
      <p class="mt-2 text-sm text-slate-500">
        When you book a listing, it will appear here for easy reference.
      </p>
      <router-link
        to="/listings"
        class="mt-6 inline-flex items-center justify-center rounded-2xl bg-slate-900 px-6 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
      >
        Browse Listings
      </router-link>
    </div>

    <div v-else class="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
      <article
        v-for="booking in bookings"
        :key="booking.id"
        class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
      >
        <div class="flex items-start justify-between gap-4">
          <div>
            <p class="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">Booking</p>
            <h2 class="mt-2 text-xl font-bold text-slate-900">#{{ booking.id }}</h2>
          </div>
          <span
            class="rounded-full px-3 py-1 text-xs font-semibold"
            :class="statusClasses(booking.status)"
          >
            {{ statusLabel(booking.status) }}
          </span>
        </div>

        <div class="mt-6 space-y-4 rounded-2xl bg-slate-50 p-4">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Service</p>
            <p class="mt-1 text-sm font-medium text-slate-700">Service ID: {{ booking.service_id }}</p>
          </div>

          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Booking Time</p>
            <p class="mt-1 text-sm font-medium text-slate-700">{{ formatDate(booking.booking_time) }}</p>
          </div>
        </div>

        <div class="mt-6 flex items-center justify-between gap-3">
          <p class="text-sm text-slate-500">
            {{ booking.status === 'pending' ? 'This booking is still awaiting confirmation.' : 'Your booking status is up to date.' }}
          </p>
          <button
            v-if="booking.status === 'pending'"
            @click="bookingToCancel = booking"
            class="shrink-0 rounded-2xl border border-red-200 bg-red-50 px-4 py-2 text-sm font-semibold text-red-700 transition hover:bg-red-100"
          >
            Cancel
          </button>
        </div>
      </article>
    </div>

    <div
      v-if="bookingToCancel"
      class="fixed inset-0 z-50 flex items-center justify-center px-4"
      @click.self="bookingToCancel = null"
    >
      <div class="absolute inset-0 bg-slate-950/50 backdrop-blur-sm"></div>
      <div class="relative w-full max-w-md rounded-3xl border border-slate-200 bg-white p-8 shadow-2xl">
        <div class="flex items-start gap-4">
          <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-red-50">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <div>
            <h3 class="text-lg font-bold text-slate-900">Cancel booking?</h3>
            <p class="mt-2 text-sm leading-6 text-slate-600">
              Booking #{{ bookingToCancel.id }} will be cancelled immediately.
            </p>
          </div>
        </div>

        <div class="mt-6 flex gap-3">
          <button
            @click="bookingToCancel = null"
            class="flex-1 rounded-2xl border border-slate-200 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
          >
            Keep Booking
          </button>
          <button
            @click="confirmCancelBooking"
            :disabled="cancelling"
            class="flex-1 rounded-2xl bg-red-600 py-3 text-sm font-semibold text-white transition hover:bg-red-700 disabled:opacity-60"
          >
            {{ cancelling ? 'Cancelling...' : 'Cancel Booking' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { bookingsAPI } from '../services/api'
import { useToastStore } from '../stores/toast'

const toastStore = useToastStore()

const bookings = ref([])
const loading = ref(true)
const cancelling = ref(false)
const bookingToCancel = ref(null)
const error = ref('')

async function fetchBookings() {
  loading.value = true
  error.value = ''

  try {
    const response = await bookingsAPI.getAll()
    bookings.value = response.data
  } catch (err) {
    error.value = 'Failed to load bookings.'
  } finally {
    loading.value = false
  }
}

async function confirmCancelBooking() {
  if (!bookingToCancel.value) {
    return
  }

  cancelling.value = true

  try {
    await bookingsAPI.cancel(bookingToCancel.value.id)
    toastStore.show('Booking cancelled successfully.', 'success')
    bookingToCancel.value = null
    await fetchBookings()
  } catch (err) {
    error.value = 'Failed to cancel booking.'
    toastStore.show('Failed to cancel booking.', 'error')
  } finally {
    cancelling.value = false
  }
}

function formatDate(date) {
  return new Date(date).toLocaleString()
}

function statusLabel(status) {
  if (status === 'pending') return 'Pending'
  if (status === 'confirmed') return 'Confirmed'
  if (status === 'cancelled') return 'Cancelled'
  if (status === 'completed') return 'Completed'
  return status
}

function statusClasses(status) {
  if (status === 'pending') return 'bg-amber-100 text-amber-800'
  if (status === 'confirmed') return 'bg-emerald-100 text-emerald-800'
  if (status === 'cancelled') return 'bg-red-100 text-red-800'
  if (status === 'completed') return 'bg-cyan-100 text-cyan-800'
  return 'bg-slate-100 text-slate-700'
}

onMounted(() => {
  fetchBookings()
})
</script>
