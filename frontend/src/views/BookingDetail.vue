<template>
  <div class="bg-slate-50 min-h-screen">
    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center py-20">
      <svg class="h-8 w-8 animate-spin text-cyan-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
      </svg>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="flex min-h-screen items-center justify-center px-4">
      <div class="rounded-3xl border border-red-200 bg-white px-12 py-16 text-center shadow-sm">
        <p class="text-base font-medium text-red-600">{{ error }}</p>
        <router-link
          to="/bookings"
          class="mt-6 inline-block rounded-2xl bg-slate-900 px-6 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
        >
          Back to Bookings
        </router-link>
      </div>
    </div>

    <!-- Not Found State -->
    <div v-else-if="!booking" class="flex min-h-screen items-center justify-center px-4">
      <div class="rounded-3xl border border-slate-200 bg-white px-12 py-16 text-center shadow-sm">
        <p class="text-base font-medium text-slate-500">Booking not found.</p>
        <router-link
          to="/bookings"
          class="mt-6 inline-block rounded-2xl bg-slate-900 px-6 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
        >
          Back to Bookings
        </router-link>
      </div>
    </div>

    <!-- Booking Detail Content -->
    <div v-else>
      <!-- Header Section -->
      <div class="bg-white border-b border-slate-200">
        <div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <div class="flex items-center gap-4">
            <router-link
              to="/bookings"
              class="inline-flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
              Back
            </router-link>
          </div>

          <div class="mt-6 flex items-start justify-between gap-4">
            <div>
              <p class="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">
                {{ isRestaurantBooking ? 'Reservation' : 'Booking' }}
              </p>
              <h1 class="mt-2 text-2xl font-bold text-slate-900">
                Reference No.: #{{ booking.id }}
              </h1>
            </div>
            <span
              class="rounded-full px-4 py-2 text-sm font-semibold"
              :class="statusClasses(booking.status)"
            >
              {{ statusLabel(booking.status) }}
            </span>
          </div>
        </div>
      </div>

      <!-- Main Content -->
      <div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 gap-8 lg:grid-cols-3">
          <!-- Booking Details Section -->
          <div class="lg:col-span-2 space-y-6">
            <!-- Listing Info -->
            <div class="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">
              <div class="border-b border-slate-100 bg-slate-50 px-6 py-4">
                <h2 class="font-bold text-slate-950">Listing Details</h2>
              </div>
              <div class="p-6">
                <div class="space-y-4">
                  <div>
                    <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                      Listing
                    </p>
                    <p class="mt-1 text-sm font-medium text-slate-700">
                      {{ booking.listing_name }}
                    </p>
                  </div>

                  <div>
                    <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                      Service
                    </p>
                    <p class="mt-1 text-sm font-medium text-slate-700">
                      {{ booking.service_name }}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Booking Information -->
            <div class="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">
              <div class="border-b border-slate-100 bg-slate-50 px-6 py-4">
                <h2 class="font-bold text-slate-950">Booking Information</h2>
              </div>
              <div class="p-6">
                <div class="space-y-4">
                  <div>
                    <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                      Booked On
                    </p>
                    <p class="mt-1 text-sm font-medium text-slate-700">
                      {{ formatDate(booking.created_at) }}
                    </p>
                  </div>

                  <div>
                    <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                      Name On Booking
                    </p>
                    <p class="mt-1 text-sm font-medium text-slate-700">
                      {{ booking.bookers_name }}
                    </p>
                  </div>

                  <div v-if="booking.status === 'approved' || booking.status === 'completed'">
                    <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                      Paid On
                    </p>
                    <p class="mt-1 text-sm font-medium text-slate-700">
                      {{ formatDate(booking.paid_at) }}
                    </p>
                  </div>

                  <div>
                    <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                      Booking Time
                    </p>
                    <p class="mt-1 text-sm font-medium text-slate-700">
                      From: {{ formatDate(booking.booking_from_time) }}
                    </p>
                    <p class="mt-1 text-sm font-medium text-slate-700">
                      To: {{ formatDate(booking.booking_to_time) }}
                    </p>
                  </div>

                  <div>
                    <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                      {{ isHotelBooking ? 'Number of Rooms' : 'Amount of People' }}
                    </p>
                    <p class="mt-1 text-sm font-medium text-slate-700">
                      {{ booking.amount_of_people }}
                    </p>
                  </div>

                  <div v-if="booking.special_requests">
                    <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                      Special Requests
                    </p>
                    <p class="mt-1 text-sm font-medium text-slate-700">
                      {{ booking.special_requests }}
                    </p>
                  </div>

                  <div v-if="shouldShowCancellationReason(booking)">
                    <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                      Cancellation Reason
                    </p>
                    <div class="mt-2 rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3">
                      <p class="text-sm font-medium text-rose-700">
                        {{ booking.cancellation_reason }}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Payment Section for Pending Bookings -->
            <div
              v-if="normalizedStatus(booking.status) === 'pending' && !isRestaurantBooking"
              class="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm"
            >
              <div class="border-b border-slate-100 bg-slate-50 px-6 py-4">
                <h2 class="font-bold text-slate-950">Payment</h2>
              </div>
              <div class="p-6">
                <component
                  v-if="PaymentFormComponent"
                  :is="PaymentFormComponent"
                  :booking-id="booking.id"
                  :client-secret="clientSecret"
                  @payment-success="handlePaymentSuccess"
                  @payment-error="handlePaymentError"
                />
                <div v-else class="rounded-2xl border border-slate-200 bg-slate-50 p-6 text-center">
                  <p class="text-sm text-slate-500">Payment form is loading...</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Price Summary Sidebar -->
          <div class="lg:col-span-1">
            <div class="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm sticky top-8">
              <div class="border-b border-slate-100 bg-slate-50 px-6 py-4">
                <h2 class="font-bold text-slate-950">
                  {{ isRestaurantBooking ? 'Spend Estimate' : 'Price Summary' }}
                </h2>
              </div>
              <div class="p-6 space-y-4">
                <div v-if="booking.base_price !== undefined" class="flex justify-between text-sm">
                  <span class="text-slate-600">
                    {{ isRestaurantBooking ? 'Average spend' : 'Base Price' }}
                  </span>
                  <span class="font-medium text-slate-900">${{ Number(booking.base_price).toFixed(2) }}</span>
                </div>

                <div v-if="booking.service_fee_amount !== undefined && !isRestaurantBooking" class="flex justify-between text-sm">
                  <span class="text-slate-600">Service Fee</span>
                  <span class="font-medium text-slate-900">${{ Number(booking.service_fee_amount).toFixed(2) }}</span>
                </div>

                <div v-if="booking.discount_amount" class="flex justify-between text-sm">
                  <span class="text-slate-600">Discount</span>
                  <span class="font-medium text-emerald-600">-${{ Number(booking.discount_amount).toFixed(2) }}</span>
                </div>

                <div v-if="booking.status === 'cancelled' && booking.has_refund" class="flex justify-between text-sm">
                  <div>
                    <span class="text-emerald-600">Refunded</span>
                    <span v-if="booking.refund_date" class="ml-2 text-xs text-slate-400">
                      {{ new Date(booking.refund_date).toLocaleDateString() }}
                    </span>
                  </div>
                  <span class="font-medium text-emerald-700">-${{ Number(booking.final_price ?? 0).toFixed(2) }}</span>
                </div>

                <div class="border-t border-slate-200 pt-4">
                  <div class="flex justify-between">
                    <span class="font-semibold text-slate-900">
                      {{ isRestaurantBooking ? 'Estimated total' : 'Total' }}
                    </span>
                    <span class="font-bold text-lg text-slate-900">${{ Number(displayTotal).toFixed(2) }}</span>
                  </div>
                  <p v-if="isRestaurantBooking" class="mt-2 text-xs leading-5 text-slate-500">
                    This reservation does not require payment in Isle Be There. The amount shown is an average spend estimate only.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, shallowRef } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { bookingsAPI } from '../services/api'
import { useToastStore } from '../stores/toast'

const route = useRoute()
const router = useRouter()
const toastStore = useToastStore()

const booking = ref(null)
const loading = ref(true)
const error = ref('')
const clientSecret = ref('')

const isRestaurantBooking = computed(() => booking.value?.listing_business_type_name === 'Restaurant')
const isHotelBooking = computed(() => booking.value?.listing_business_type_name === 'Hotel')
const displayTotal = computed(() => {
  if (!booking.value) return 0
  if (isRestaurantBooking.value) {
    return Number(booking.value.base_price ?? 0)
  }
  return Number(
    booking.value.final_price
      ?? (booking.value.base_price + (booking.value.service_fee_amount || 0) - (booking.value.discount_amount || 0))
  )
})

// PaymentForm component - loaded dynamically
const PaymentFormComponent = shallowRef(null)

async function loadPaymentFormComponent() {
  try {
    const module = await import('../components/PaymentForm.vue')
    PaymentFormComponent.value = module.default
  } catch (e) {
    PaymentFormComponent.value = null
  }
}

async function fetchBooking() {
  loading.value = true
  error.value = ''

  try {
    const response = await bookingsAPI.getById(route.params.id)
    booking.value = response.data

    // Fetch client secret if booking is pending and payment is required
    if (normalizedStatus(booking.value.status) === 'pending' && !isRestaurantBooking.value) {
      await loadPaymentFormComponent()
    } else {
      PaymentFormComponent.value = null
    }
  } catch (err) {
    if (err.response?.status === 404) {
      booking.value = null
    } else {
      error.value = 'Failed to load booking details.'
    }
  } finally {
    loading.value = false
  }
}

function formatDate(date) {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}

function normalizedStatus(status) {
  return typeof status === 'string' ? status : status?.value
}

function statusLabel(status) {
  const value = normalizedStatus(status)
  if (value === 'pending') return 'Pending'
  if (value === 'approved') return 'Approved'
  if (value === 'cancelled') {
    if (booking.value?.has_refund) return 'Refunded'
    return 'Cancelled'
  }
  if (value === 'completed') return 'Completed'
  return value || 'Unknown'
}

function statusClasses(status) {
  const value = normalizedStatus(status)
  if (value === 'pending') return 'bg-amber-100 text-amber-800'
  if (value === 'approved') return 'bg-emerald-100 text-emerald-800'
  if (value === 'cancelled') {
    if (booking.value?.has_refund) return 'bg-green-100 text-green-800'
    return 'bg-red-100 text-red-800'
  }
  if (value === 'completed') return 'bg-cyan-100 text-cyan-800'
  return 'bg-slate-100 text-slate-700'
}

function shouldShowCancellationReason(currentBooking) {
  return (
    normalizedStatus(currentBooking?.status) === 'cancelled'
    && currentBooking?.cancelled_by_role
    && currentBooking.cancelled_by_role !== 'guest'
    && typeof currentBooking.cancellation_reason === 'string'
    && currentBooking.cancellation_reason.trim().length > 0
  )
}

async function handlePaymentSuccess() {
  toastStore.show('Payment successful! Your booking is now confirmed.', 'success')

  // Fetch all bookings to find the next pending one from the same itinerary
  try {
    const response = await bookingsAPI.getAll()
    const allBookings = response.data || []

    // Current booking's itinerary_id (from the freshly loaded booking)
    const currentItineraryId = booking.value?.itinerary_id

    // Find pending bookings from the same itinerary (excluding current one)
    const currentId = booking.value?.id
    let nextPendingBooking = null

    for (const b of allBookings) {
      if (
        b.id !== currentId &&
        normalizedStatus(b.status) === 'pending' &&
        b.itinerary_id === currentItineraryId
      ) {
        nextPendingBooking = b
        break
      }
    }

    if (nextPendingBooking) {
      // Navigate to the next pending booking from the same itinerary
      window.location.href = `/bookings/${nextPendingBooking.id}`
    } else {
      // No more pending bookings in this itinerary, navigate to bookings list
      window.location.href = '/bookings'
    }
  } catch (err) {
    // On error, reload current page
    window.location.reload()
  }
}

function handlePaymentError(message) {
  toastStore.show(message || 'Payment failed. Please try again.', 'error')
}

onMounted(() => {
  fetchBooking()
})
</script>
