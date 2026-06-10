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
      </article>
    </div>
  </section>
</template>

<script setup>
import { computed, ref, watch } from "vue";

import { bookingsAPI } from "../../services/api";

const props = defineProps({
  listing: {
    type: Object,
    default: null,
  },
});

const bookings = ref([]);
const loading = ref(false);
const error = ref("");
const activeTab = ref("all");

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
    return "This booking was cancelled and refunded.";
  }
  if (normalized === "cancelled") {
    return "This booking was cancelled.";
  }
  return "This booking status is up to date.";
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
