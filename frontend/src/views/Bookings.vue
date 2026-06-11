<template>
  <div class="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
    <div class="mb-8">
      <p
        class="text-sm font-semibold uppercase tracking-[0.25em] text-slate-500"
      >
        Trips
      </p>
      <h1 class="mt-2 text-3xl font-bold text-slate-900">My Bookings</h1>
      <p class="mt-2 text-sm text-slate-500">
        Track upcoming reservations and manage pending bookings.
      </p>
      <router-link
        to="/calendar"
        class="mt-4 inline-flex w-full items-center justify-center rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 sm:w-auto"
      >
        Open Calendar
      </router-link>
    </div>

    <div
      v-if="error"
      class="mb-6 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
    >
      {{ error }}
    </div>

    <!-- Status Tabs -->
    <div v-if="!loading && bookings.length > 0" class="mb-6">
      <div class="sm:hidden">
        <nav class="-mx-1 flex gap-2 overflow-x-auto px-1 pb-1">
          <button
            v-for="tab in statusTabs"
            :key="tab.value"
            @click="activeTab = tab.value"
            :class="[
              'shrink-0 rounded-full border px-4 py-2.5 text-sm font-semibold transition-colors',
              activeTab === tab.value
                ? 'border-cyan-600 bg-cyan-50 text-cyan-700 shadow-sm'
                : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300 hover:text-slate-800'
            ]"
          >
            {{ tab.label }}
            <span
              class="ml-2 rounded-full px-2 py-0.5 text-xs"
              :class="activeTab === tab.value ? 'bg-cyan-100 text-cyan-700' : tab.count > 0 ? 'bg-slate-100 text-slate-600' : 'bg-slate-50 text-slate-400'"
            >
              {{ tab.count }}
            </span>
          </button>
        </nav>
      </div>

      <div class="hidden border-b border-slate-200 sm:block">
        <nav class="flex gap-6">
          <button
            v-for="tab in statusTabs"
            :key="tab.value"
            @click="activeTab = tab.value"
            :class="[
              'pb-3 text-sm font-medium transition-colors',
              activeTab === tab.value
                ? 'border-b-2 border-cyan-600 text-cyan-600'
                : 'text-slate-500 hover:text-slate-700'
            ]"
          >
            {{ tab.label }}
            <span class="ml-2 rounded-full px-2 py-0.5 text-xs" :class="tab.count > 0 ? 'bg-slate-100 text-slate-600' : 'bg-slate-50 text-slate-400'">
              {{ tab.count }}
            </span>
          </button>
        </nav>
      </div>
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
      v-else-if="filteredBookings.length === 0"
      class="rounded-3xl border border-slate-200 bg-white px-6 py-20 text-center shadow-sm"
    >
      <div
        class="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-slate-100 text-slate-400"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-8 w-8"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="1.5"
            d="M8 7V3m8 4V3m-9 8h10m-11 9h12a2 2 0 002-2V7a2 2 0 00-2-2H6a2 2 0 00-2 2v11a2 2 0 002 2z"
          />
        </svg>
      </div>
      <h2 class="mt-5 text-lg font-bold text-slate-900">
                {{ activeTab === 'all' ? 'No bookings yet' : `No ${activeTab} bookings` }}
              </h2>
              <p class="mt-2 text-sm text-slate-500">
                {{ activeTab === 'all' ? 'When you book a listing, it will appear here for easy reference.' : `You have no ${activeTab} bookings at the moment.` }}
              </p>
              <router-link
                v-if="activeTab === 'all'"
                to="/listings"
                class="mt-6 inline-flex items-center justify-center rounded-2xl bg-slate-900 px-6 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
              >
                Browse Listings
              </router-link>
    </div>

    <div v-else class="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
      <article
        v-for="booking in filteredBookings"
        :key="booking.id"
        class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6"
      >
        <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div class="min-w-0">
            <p
              class="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400"
            >
              Booking
            </p>
            <h2 class="mt-2 break-all text-lg font-bold text-slate-900 sm:text-xl">
              Ref #{{ booking.id }}
            </h2>
          </div>
          <span
            class="self-start rounded-full px-3 py-1 text-xs font-semibold"
            :class="statusClasses(booking.status, booking.has_refund)"
          >
            {{ statusLabel(booking.status, booking.has_refund) }}
          </span>
        </div>

        <div class="mt-5 rounded-2xl bg-slate-50 p-4">
          <div class="space-y-1">
            <p
              class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400"
            >
              Listing
            </p>
            <p class="mt-1 text-sm font-medium text-slate-700">
              {{ booking.listing_name }}
            </p>
          </div>
        </div>

        <div class="mt-4 rounded-2xl bg-slate-50 p-4">
          <div class="grid gap-4 sm:grid-cols-2">
            <div>
              <p
                class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400"
              >
                Service
              </p>
              <p class="mt-1 text-sm font-medium text-slate-700">
                {{ booking.service_name }}
              </p>
            </div>

            <div>
              <p
                class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400"
              >
                Booker
              </p>
              <p class="mt-1 text-sm font-medium text-slate-700">
                {{ booking.bookers_name }}
              </p>
            </div>
          </div>

          <div class="mt-4 space-y-4">
            <div>
              <p
                class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400"
              >
                Booking Time
              </p>
              <div class="mt-2 space-y-2 text-sm font-medium text-slate-700">
                <p><span class="text-slate-500">From:</span> {{ formatDate(booking.booking_from_time) }}</p>
                <p><span class="text-slate-500">To:</span> {{ formatDate(booking.booking_to_time) }}</p>
              </div>
            </div>

            <div>
              <p
                class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400"
              >
                Guests
              </p>
              <p class="mt-1 text-sm font-medium text-slate-700">
                {{ booking.amount_of_people }}
              </p>
            </div>
          </div>
        </div>

        <div class="mt-5 border-t border-slate-100 pt-4">
          <p class="text-sm leading-6 text-slate-500">
            {{ bookingStatusMessage(booking) }}
          </p>

          <div
            v-if="shouldShowCancellationReason(booking)"
            class="mt-4 rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3"
          >
            <p class="text-xs font-semibold uppercase tracking-[0.18em] text-rose-500">
              Cancellation Reason
            </p>
            <p class="mt-2 text-sm text-rose-700">
              {{ booking.cancellation_reason }}
            </p>
          </div>

          <div class="mt-4 flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center">
            <router-link
              :to="'/bookings/' + booking.id"
              class="inline-flex w-full items-center justify-center rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 sm:w-auto"
            >
              {{ normalizedStatus(booking.status) === 'pending' ? 'Pay Now' : 'View Details' }}
            </router-link>

            <button
              v-if="normalizedStatus(booking.status) === 'pending' || normalizedStatus(booking.status) === 'approved'"
              @click="bookingToCancel = booking"
              class="inline-flex w-full items-center justify-center rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-semibold text-red-700 transition hover:bg-red-100 sm:w-auto"
            >
              Cancel
            </button>

            <template v-else-if="normalizedStatus(booking.status) === 'cancelled' && !booking.has_refund">
              <div
                v-if="confirmingDelete === booking.id"
                class="rounded-2xl border border-slate-200 bg-slate-50 p-3"
              >
                <p class="text-sm font-medium text-slate-600">Delete this booking?</p>
                <div class="mt-3 grid gap-2 sm:grid-cols-2">
                  <button
                    @click="deleteBooking(booking.id)"
                    :disabled="deleting"
                    class="rounded-2xl bg-red-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-red-700 disabled:opacity-50"
                  >
                    Yes, Delete
                  </button>
                  <button
                    @click="confirmingDelete = null"
                    class="rounded-2xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
                  >
                    Keep It
                  </button>
                </div>
              </div>

              <button
                v-else
                @click="confirmingDelete = booking.id"
                class="inline-flex w-full items-center justify-center rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm font-semibold text-slate-600 transition hover:bg-slate-50 sm:w-auto"
              >
                Delete
              </button>
            </template>

            <div
              v-else-if="normalizedStatus(booking.status) === 'cancelled' && booking.has_refund"
              class="rounded-2xl border border-emerald-100 bg-emerald-50 px-4 py-3 text-sm font-medium text-emerald-700"
            >
              Refunded bookings stay in your history.
            </div>
          </div>
        </div>
      </article>
    </div>

    <div
      v-if="bookingToCancel"
      class="fixed inset-0 z-50 flex items-center justify-center px-4"
      @click.self="bookingToCancel = null"
    >
      <div class="absolute inset-0 bg-slate-950/50 backdrop-blur-sm"></div>
      <div
        class="relative w-full max-w-md rounded-3xl border border-slate-200 bg-white p-6 shadow-2xl sm:p-8"
      >
        <div class="flex items-start gap-4">
          <div
            class="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-red-50"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-6 w-6 text-red-500"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </div>
          <div>
            <h3 class="text-lg font-bold text-slate-900">Cancel booking?</h3>
            <p class="mt-2 text-sm leading-6 text-slate-600">
              Booking #{{ bookingToCancel.id }} will be cancelled. A full refund will be issued to your original payment method.
            </p>
          </div>
        </div>

        <div class="mt-6 flex flex-col gap-3 sm:flex-row">
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
            {{ cancelling ? "Cancelling..." : "Cancel Booking" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { bookingsAPI } from "../services/api";
import { useToastStore } from "../stores/toast";

const toastStore = useToastStore();

const bookings = ref([]);
const loading = ref(true);
const cancelling = ref(false);
const bookingToCancel = ref(null);
const confirmingDelete = ref(null);
const deleting = ref(false);
const error = ref("");
const activeTab = ref("all");

const statusTabs = computed(() => [
  { label: "All", value: "all", count: bookings.value.length },
  { label: "Pending", value: "pending", count: bookings.value.filter(b => normalizedStatus(b.status) === "pending").length },
  { label: "Approved", value: "approved", count: bookings.value.filter(b => normalizedStatus(b.status) === "approved").length },
  { label: "Completed", value: "completed", count: bookings.value.filter(b => normalizedStatus(b.status) === "completed").length },
  { label: "Cancelled", value: "cancelled", count: bookings.value.filter(b => normalizedStatus(b.status) === "cancelled" && !b.has_refund).length },
  { label: "Refunded", value: "refunded", count: bookings.value.filter(b => normalizedStatus(b.status) === "cancelled" && b.has_refund).length },
]);

const filteredBookings = computed(() => {
  if (activeTab.value === "all") return bookings.value;
  if (activeTab.value === "cancelled") {
    return bookings.value.filter(b => normalizedStatus(b.status) === "cancelled" && !b.has_refund);
  }
  if (activeTab.value === "refunded") {
    return bookings.value.filter(b => normalizedStatus(b.status) === "cancelled" && b.has_refund);
  }
  return bookings.value.filter(b => normalizedStatus(b.status) === activeTab.value);
});

async function fetchBookings() {
  loading.value = true;
  error.value = "";

  try {
    const response = await bookingsAPI.getAll();
    bookings.value = response.data;
  } catch (err) {
    error.value = "Failed to load bookings.";
  } finally {
    loading.value = false;
  }
}

async function confirmCancelBooking() {
  if (!bookingToCancel.value) {
    return;
  }

  cancelling.value = true;

  try {
    await bookingsAPI.cancel(bookingToCancel.value.id);
    toastStore.show("Booking cancelled successfully.", "success");
    bookingToCancel.value = null;
    await fetchBookings();
  } catch (err) {
    error.value = "Failed to cancel booking.";
    toastStore.show("Failed to cancel booking.", "error");
  } finally {
    cancelling.value = false;
  }
}

async function deleteBooking(id) {
  deleting.value = true;
  confirmingDelete.value = null;

  try {
    await bookingsAPI.delete(id);
    bookings.value = bookings.value.filter((b) => b.id !== id);
    toastStore.show("Booking deleted successfully.", "success");
  } catch (err) {
    const message = err.response?.data?.detail || "Failed to delete booking.";
    toastStore.show(message, "error");
  } finally {
    deleting.value = false;
  }
}

function formatDate(date) {
  return new Date(date).toLocaleString();
}

function statusLabel(status, hasRefund = false) {
  const value = normalizedStatus(status);
  if (value === "pending") return "Pending";
  if (value === "approved") return "Approved";
  if (value === "cancelled") {
    if (hasRefund) return "Refunded";
    return "Cancelled";
  }
  if (value === "completed") return "Completed";
  return value || "Unknown";
}

function statusClasses(status, hasRefund = false) {
  const value = normalizedStatus(status);
  if (value === "pending") return "bg-amber-100 text-amber-800";
  if (value === "approved") return "bg-emerald-100 text-emerald-800";
  if (value === "cancelled") {
    if (hasRefund) return "bg-green-100 text-green-800";
    return "bg-red-100 text-red-800";
  }
  if (value === "completed") return "bg-cyan-100 text-cyan-800";
  return "bg-slate-100 text-slate-700";
}

function bookingStatusMessage(booking) {
  const value = normalizedStatus(booking.status);
  if (value === "pending") {
    return "This booking is still awaiting confirmation.";
  }
  if (value === "cancelled") {
    if (booking.cancelled_by_role === "guest") {
      return booking.has_refund
        ? "You cancelled this booking and received a refund."
        : "You cancelled this booking.";
    }
    if (booking.cancelled_by_role) {
      return booking.has_refund
        ? "This booking was cancelled by the business and refunded."
        : "This booking was cancelled by the business.";
    }
    return booking.has_refund
      ? "This booking was cancelled and refunded."
      : "This booking has been cancelled.";
  }
  return "Your booking status is up to date.";
}

function shouldShowCancellationReason(booking) {
  return (
    normalizedStatus(booking?.status) === "cancelled"
    && booking?.cancelled_by_role
    && booking.cancelled_by_role !== "guest"
    && typeof booking.cancellation_reason === "string"
    && booking.cancellation_reason.trim().length > 0
  );
}

function normalizedStatus(status) {
  return typeof status === "string" ? status : status?.value;
}

onMounted(() => {
  fetchBookings();
});
</script>
