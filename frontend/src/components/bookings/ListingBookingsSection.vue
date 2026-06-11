<template>
  <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
    <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.28em] text-cyan-600">
          Reservations
        </p>
        <h2 class="mt-1 text-xl font-bold text-slate-900">Listing Bookings</h2>
        <p class="mt-2 text-sm text-slate-500">
          View the reservations attached to
          <span class="font-semibold text-slate-700">
            {{ listing?.title || "this listing" }}
          </span>
          in one place.
        </p>
      </div>
      <div class="flex flex-wrap gap-2">
        <span class="rounded-2xl bg-slate-100 px-3 py-2 text-sm font-semibold text-slate-700">
          {{ bookings.length }} total
        </span>
        <span class="rounded-2xl bg-amber-50 px-3 py-2 text-sm font-semibold text-amber-700">
          {{ pendingCount }} pending
        </span>
      </div>
    </div>

    <div
      v-if="error"
      class="mt-6 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
    >
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <span>{{ error }}</span>
        <button
          @click="fetchBookings()"
          class="inline-flex items-center justify-center rounded-2xl border border-red-200 bg-white px-4 py-2 text-sm font-semibold text-red-700 transition hover:bg-red-100"
        >
          Try Again
        </button>
      </div>
    </div>

    <div
      v-if="!loading && bookings.length > 0"
      class="mt-6 border-b border-slate-200"
    >
      <nav class="flex flex-wrap gap-5">
        <button
          v-for="tab in statusTabs"
          :key="tab.value"
          @click="activeTab = tab.value"
          :class="[
            'pb-3 text-sm font-medium transition-colors',
            activeTab === tab.value
              ? 'border-b-2 border-cyan-600 text-cyan-600'
              : 'text-slate-500 hover:text-slate-700',
          ]"
        >
          {{ tab.label }}
          <span
            class="ml-2 rounded-full px-2 py-0.5 text-xs"
            :class="tab.count > 0 ? 'bg-slate-100 text-slate-600' : 'bg-slate-50 text-slate-400'"
          >
            {{ tab.count }}
          </span>
        </button>
      </nav>
    </div>

    <div v-if="loading" class="mt-6 grid gap-6 xl:grid-cols-2">
      <div
        v-for="n in 4"
        :key="n"
        class="animate-pulse rounded-3xl border border-slate-200 bg-slate-50 p-6"
      >
        <div class="h-5 w-1/3 rounded bg-slate-200"></div>
        <div class="mt-4 h-4 w-1/2 rounded bg-slate-100"></div>
        <div class="mt-6 h-20 rounded-2xl bg-white"></div>
        <div class="mt-4 h-12 rounded-2xl bg-white"></div>
      </div>
    </div>

    <div
      v-else-if="filteredBookings.length === 0"
      class="mt-6 rounded-3xl border-2 border-dashed border-slate-200 bg-slate-50 px-6 py-16 text-center"
    >
      <div
        class="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-white text-slate-400"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-7 w-7"
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
      <h3 class="mt-5 text-lg font-bold text-slate-900">
        {{ activeTab === "all" ? "No bookings yet" : `No ${activeTab} bookings` }}
      </h3>
      <p class="mt-2 text-sm text-slate-500">
        {{
          activeTab === "all"
            ? "This listing has not received any bookings yet."
            : `There are no ${activeTab} bookings for this listing right now.`
        }}
      </p>
    </div>

    <div v-else class="mt-6 grid gap-6 xl:grid-cols-2">
      <article
        v-for="booking in filteredBookings"
        :key="booking.id"
        class="rounded-3xl border border-slate-200 bg-slate-50 p-6"
      >
        <div class="flex items-start justify-between gap-4">
          <div>
            <p class="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">
              Booking
            </p>
            <h3 class="mt-2 text-lg font-bold text-slate-900 break-all">
              Reference No.: #{{ booking.id }}
            </h3>
          </div>
          <span
            class="rounded-full px-3 py-1 text-xs font-semibold"
            :class="statusClasses(booking.status, booking.has_refund)"
          >
            {{ statusLabel(booking.status, booking.has_refund) }}
          </span>
        </div>

        <div class="mt-6 grid gap-4 rounded-2xl bg-white p-4 sm:grid-cols-2">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
              Service
            </p>
            <p class="mt-1 text-sm font-medium text-slate-700">
              {{ booking.service_name || "Not provided" }}
            </p>
          </div>
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
              Guest
            </p>
            <p class="mt-1 text-sm font-medium text-slate-700">
              {{ booking.bookers_name || "Not provided" }}
            </p>
          </div>
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
              Booking Time
            </p>
            <p class="mt-1 text-sm font-medium text-slate-700">
              {{ formatDate(booking.booking_from_time) }}
            </p>
            <p class="mt-1 text-sm text-slate-500">
              to {{ formatDate(booking.booking_to_time) }}
            </p>
          </div>
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
              Guests
            </p>
            <p class="mt-1 text-sm font-medium text-slate-700">
              {{ booking.amount_of_people }}
            </p>
          </div>
          <div v-if="booking.paid_at">
            <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
              Paid
            </p>
            <p class="mt-1 text-sm font-medium text-slate-700">
              {{ formatDate(booking.paid_at) }}
            </p>
          </div>
          <div v-if="booking.special_requests">
            <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
              Special Request
            </p>
            <p class="mt-1 text-sm font-medium text-slate-700">
              {{ booking.special_requests }}
            </p>
          </div>
        </div>

        <p class="mt-4 text-sm text-slate-500">
          {{ statusMessage(booking) }}
        </p>

        <div
          v-if="booking.cancellation_reason"
          class="mt-4 rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3"
        >
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-rose-500">
            Cancellation Reason
          </p>
          <p class="mt-2 text-sm text-rose-700">
            {{ booking.cancellation_reason }}
          </p>
        </div>

        <div v-if="canCancelBooking(booking)" class="mt-5 flex justify-end">
          <button
            type="button"
            @click="openCancelModal(booking)"
            class="inline-flex items-center justify-center rounded-2xl bg-red-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-red-700"
          >
            Cancel Booking
          </button>
        </div>
      </article>
    </div>

    <div
      v-if="bookingToCancel"
      class="fixed inset-0 z-[70] flex items-center justify-center px-4"
      @click.self="!cancelling && closeCancelModal()"
    >
      <div class="absolute inset-0 bg-slate-950/60 backdrop-blur-sm"></div>
      <div class="relative w-full max-w-xl overflow-hidden rounded-3xl border border-slate-200 bg-white text-left shadow-2xl">
        <div class="px-6 py-6 sm:px-7">
          <div class="flex items-start gap-4">
            <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-red-500/10 text-red-500">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="1.5"
                  d="M12 9v3.75m0 3.75h.007v.008H12v-.008Zm-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126Z"
                />
              </svg>
            </div>
            <div class="flex-1">
              <h3 class="text-lg font-bold text-slate-900">Cancel booking?</h3>
              <p class="mt-2 text-sm leading-6 text-slate-600">
                Booking
                <span class="font-semibold text-slate-900">#{{ bookingToCancel.id }}</span>
                will be cancelled by the business.
                {{ cancelModalDescription }}
              </p>

              <div class="mt-5">
                <label
                  for="business-booking-cancel-reason"
                  class="block text-sm font-semibold text-slate-800"
                >
                  Cancellation reason
                </label>
                <textarea
                  id="business-booking-cancel-reason"
                  v-model="cancellationReason"
                  rows="4"
                  maxlength="500"
                  placeholder="Tell the guest why this booking is being cancelled."
                  class="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-700 focus:border-red-300 focus:outline-none focus:ring-2 focus:ring-red-100"
                ></textarea>
                <div class="mt-2 flex items-center justify-between gap-3">
                  <p
                    v-if="cancelReasonError"
                    class="text-sm text-red-600"
                  >
                    {{ cancelReasonError }}
                  </p>
                  <span class="ml-auto text-xs text-slate-400">
                    {{ cancellationReason.trim().length }}/500
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="border-t border-slate-100 bg-slate-50 px-6 py-4 sm:flex sm:flex-row-reverse sm:px-7">
          <button
            type="button"
            @click="confirmCancelBooking"
            :disabled="cancelling"
            class="inline-flex w-full justify-center rounded-2xl bg-red-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-60 sm:ml-3 sm:w-auto"
          >
            {{ cancelling ? "Cancelling..." : "Cancel Booking" }}
          </button>
          <button
            type="button"
            @click="closeCancelModal"
            :disabled="cancelling"
            class="mt-3 inline-flex w-full justify-center rounded-2xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-60 sm:mt-0 sm:w-auto"
          >
            Keep Booking
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, ref, watch } from "vue";

import { bookingsAPI } from "../../services/api";
import { useToastStore } from "../../stores/toast";

const props = defineProps({
  listing: {
    type: Object,
    default: null,
  },
});

const toastStore = useToastStore();
const bookings = ref([]);
const loading = ref(false);
const error = ref("");
const activeTab = ref("all");
const bookingToCancel = ref(null);
const cancellationReason = ref("");
const cancelReasonError = ref("");
const cancelling = ref(false);

const sortedBookings = computed(() =>
  [...bookings.value].sort((a, b) => {
    const aTime = new Date(a.created_at || a.booking_from_time || 0).getTime();
    const bTime = new Date(b.created_at || b.booking_from_time || 0).getTime();
    return bTime - aTime;
  }),
);

const statusTabs = computed(() => [
  { label: "All", value: "all", count: bookings.value.length },
  {
    label: "Pending",
    value: "pending",
    count: bookings.value.filter((booking) => normalizedStatus(booking.status) === "pending").length,
  },
  {
    label: "Approved",
    value: "approved",
    count: bookings.value.filter((booking) => normalizedStatus(booking.status) === "approved").length,
  },
  {
    label: "Completed",
    value: "completed",
    count: bookings.value.filter((booking) => normalizedStatus(booking.status) === "completed").length,
  },
  {
    label: "Cancelled",
    value: "cancelled",
    count: bookings.value.filter(
      (booking) => normalizedStatus(booking.status) === "cancelled" && !booking.has_refund,
    ).length,
  },
  {
    label: "Refunded",
    value: "refunded",
    count: bookings.value.filter(
      (booking) => normalizedStatus(booking.status) === "cancelled" && booking.has_refund,
    ).length,
  },
]);

const filteredBookings = computed(() => {
  if (activeTab.value === "all") return sortedBookings.value;
  if (activeTab.value === "cancelled") {
    return sortedBookings.value.filter(
      (booking) => normalizedStatus(booking.status) === "cancelled" && !booking.has_refund,
    );
  }
  if (activeTab.value === "refunded") {
    return sortedBookings.value.filter(
      (booking) => normalizedStatus(booking.status) === "cancelled" && booking.has_refund,
    );
  }
  return sortedBookings.value.filter(
    (booking) => normalizedStatus(booking.status) === activeTab.value,
  );
});

const pendingCount = computed(
  () => bookings.value.filter((booking) => normalizedStatus(booking.status) === "pending").length,
);

const cancelModalDescription = computed(() => {
  if (!bookingToCancel.value) return "";
  if (
    normalizedStatus(bookingToCancel.value.status) === "approved"
    && bookingToCancel.value.paid_at
  ) {
    return "If payment was collected, the refund will be issued automatically.";
  }
  return "The guest will be notified that this reservation is no longer available.";
});

watch(
  () => props.listing?.id,
  (listingId) => {
    activeTab.value = "all";
    fetchBookings(listingId);
  },
  { immediate: true },
);

async function fetchBookings(listingId = props.listing?.id) {
  if (!listingId) {
    bookings.value = [];
    error.value = "";
    loading.value = false;
    return;
  }

  loading.value = true;
  error.value = "";

  try {
    const response = await bookingsAPI.getBookingsForListing(listingId);
    bookings.value = Array.isArray(response.data) ? response.data : [];
  } catch (err) {
    bookings.value = [];
    error.value = err.response?.data?.detail || "Failed to load bookings for this listing.";
  } finally {
    loading.value = false;
  }
}

function normalizedStatus(status) {
  return String(status || "").toLowerCase();
}

function canCancelBooking(booking) {
  const normalized = normalizedStatus(booking?.status);
  return normalized === "pending" || normalized === "approved";
}

function statusLabel(status, hasRefund = false) {
  const normalized = normalizedStatus(status);
  if (normalized === "cancelled" && hasRefund) return "Refunded";
  if (!normalized) return "Unknown";
  return normalized.charAt(0).toUpperCase() + normalized.slice(1);
}

function statusClasses(status, hasRefund = false) {
  const normalized = normalizedStatus(status);
  if (normalized === "pending") return "bg-amber-100 text-amber-800";
  if (normalized === "approved") return "bg-emerald-100 text-emerald-800";
  if (normalized === "completed") return "bg-cyan-100 text-cyan-800";
  if (normalized === "cancelled" && hasRefund) return "bg-green-100 text-green-800";
  if (normalized === "cancelled") return "bg-rose-100 text-rose-800";
  return "bg-slate-100 text-slate-700";
}

function statusMessage(booking) {
  const normalized = normalizedStatus(booking.status);
  if (normalized === "pending") {
    return "This booking is still awaiting confirmation.";
  }
  if (normalized === "approved") {
    return booking.paid_at
      ? "This booking has been approved and payment has been confirmed."
      : "This booking has been approved and is ready for the guest.";
  }
  if (normalized === "completed") {
    return "This booking has already been completed.";
  }
  if (normalized === "cancelled" && booking.has_refund) {
    if (booking.cancelled_by_role === "guest") {
      return "This booking was cancelled by the guest and refunded.";
    }
    if (booking.cancelled_by_role) {
      return "This booking was cancelled by the business team and refunded.";
    }
    return "This booking was cancelled and refunded.";
  }
  if (normalized === "cancelled") {
    if (booking.cancelled_by_role === "guest") {
      return "This booking was cancelled by the guest.";
    }
    if (booking.cancelled_by_role) {
      return "This booking was cancelled by the business team.";
    }
    return "This booking was cancelled.";
  }
  return "This booking status is up to date.";
}

function openCancelModal(booking) {
  bookingToCancel.value = booking;
  cancellationReason.value = "";
  cancelReasonError.value = "";
}

function closeCancelModal(force = false) {
  if (cancelling.value && !force) return;
  bookingToCancel.value = null;
  cancellationReason.value = "";
  cancelReasonError.value = "";
}

async function confirmCancelBooking() {
  if (!bookingToCancel.value) return;

  const reason = cancellationReason.value.trim();
  if (!reason) {
    cancelReasonError.value = "Please enter a cancellation reason for the guest.";
    return;
  }

  cancelling.value = true;
  cancelReasonError.value = "";

  try {
    await bookingsAPI.cancelByBusiness(bookingToCancel.value.id, { reason });
    toastStore.show("Booking cancelled.", "success");
    closeCancelModal(true);
    await fetchBookings();
  } catch (err) {
    const message = err.response?.data?.detail || "Failed to cancel booking.";
    cancelReasonError.value = message;
    toastStore.show(message, "error");
  } finally {
    cancelling.value = false;
  }
}

function formatDate(value) {
  if (!value) return "Not scheduled";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Not scheduled";

  return date.toLocaleString([], {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}
</script>
