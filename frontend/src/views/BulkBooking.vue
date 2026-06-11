<template>
  <div class="min-h-screen bg-slate-50">
    <div class="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <div class="mb-8 flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
        <div class="max-w-3xl">
          <p class="text-sm font-semibold uppercase tracking-[0.25em] text-slate-500">Book All</p>
          <h1 class="mt-2 text-3xl font-bold text-slate-900 sm:text-4xl">
            Book {{ bookableItems.length }} {{ bookableItems.length === 1 ? 'item' : 'items' }}
          </h1>
          <p class="mt-2 text-sm leading-6 text-slate-500 sm:text-base">
            Review the services in {{ itinerary?.title || 'your itinerary' }}, confirm the booking details, and finish everything in one flow.
          </p>
        </div>

        <button
          type="button"
          @click="router.back()"
          class="inline-flex items-center justify-center rounded-2xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
        >
          Back
        </button>
      </div>

      <div v-if="loading" class="grid gap-6 md:grid-cols-2">
        <div v-for="n in 4" :key="n" class="animate-pulse rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <div class="h-5 w-1/3 rounded bg-slate-200"></div>
          <div class="mt-4 h-4 w-1/2 rounded bg-slate-100"></div>
          <div class="mt-6 h-40 rounded-2xl bg-slate-100"></div>
        </div>
      </div>

      <div v-else-if="error" class="rounded-3xl border border-red-200 bg-red-50 px-6 py-12 text-center shadow-sm">
        <p class="text-base font-medium text-red-700">{{ error }}</p>
        <button
          type="button"
          @click="router.back()"
          class="mt-6 inline-flex items-center justify-center rounded-2xl bg-slate-900 px-6 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
        >
          Go back
        </button>
      </div>

      <div v-else-if="bookableItems.length === 0" class="rounded-3xl border border-slate-200 bg-white px-6 py-20 text-center shadow-sm">
        <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-slate-100 text-slate-400">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
        </div>
        <h2 class="mt-5 text-lg font-bold text-slate-900">No items to book</h2>
        <p class="mt-2 text-sm text-slate-500">This itinerary has no bookable items yet.</p>
        <button
          type="button"
          @click="router.back()"
          class="mt-6 inline-flex items-center justify-center rounded-2xl bg-slate-900 px-6 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
        >
          Go back
        </button>
      </div>

      <template v-else>
        <div v-if="tabs.length > 1" class="mb-6 rounded-3xl border border-slate-200 bg-white p-4 shadow-sm sm:px-5 sm:py-0">
          <div class="sm:hidden">
            <nav class="-mx-1 flex gap-2 overflow-x-auto px-1 pb-1 pt-0">
              <button
                v-for="tab in tabs"
                :key="tab.id"
                :class="[
                  'shrink-0 rounded-full border px-4 py-2.5 text-sm font-semibold transition-colors',
                  activeTab === tab.id
                    ? 'border-cyan-600 bg-cyan-50 text-cyan-700 shadow-sm'
                    : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300 hover:text-slate-800'
                ]"
                @click="activeTab = tab.id"
              >
                {{ tab.mobileLabel }}
              </button>
            </nav>
            <p v-if="activeTabSummary" class="mt-3 text-sm text-slate-500">
              {{ activeTabSummary }}
            </p>
          </div>

          <nav class="hidden gap-6 overflow-x-auto sm:flex">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              :class="[
                'border-b-2 px-1 py-4 text-sm font-medium transition-colors',
                activeTab === tab.id
                  ? 'border-cyan-600 text-cyan-600'
                  : 'border-transparent text-slate-500 hover:text-slate-700'
              ]"
              @click="activeTab = tab.id"
            >
              {{ tab.desktopLabel }}
            </button>
          </nav>
        </div>

        <div class="mb-6 rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <label class="flex cursor-pointer items-center gap-3">
              <input
                type="checkbox"
                :checked="allVisibleSelected"
                :indeterminate="someVisibleSelected && !allVisibleSelected"
                @change="toggleSelectAll"
                class="h-5 w-5 rounded border-slate-300 text-cyan-600 focus:ring-cyan-500"
              />
              <span class="text-sm font-semibold text-slate-700">
                {{ allVisibleSelected ? 'Deselect all' : 'Select all' }} in this view
              </span>
            </label>

            <div class="flex flex-wrap items-center gap-3 text-sm text-slate-500">
              <span>{{ filteredItems.length }} visible</span>
              <span class="hidden h-1 w-1 rounded-full bg-slate-300 sm:block"></span>
              <span>{{ selectedItemsIds.size }} selected</span>
            </div>
          </div>
        </div>

        <div class="grid gap-6">
          <div
            v-for="item in filteredItems"
            :key="item.itemKey"
            :class="[
              'rounded-[1.9rem] border bg-white transition-all',
              isItemSelected(item.itemKey)
                ? 'border-cyan-300 bg-cyan-50/70 ring-1 ring-cyan-100'
                : 'border-transparent bg-transparent'
            ]"
          >
            <div class="flex items-center justify-end px-4 pt-4 pb-3">
              <label :class="[
                'inline-flex items-center gap-2 rounded-2xl border px-3 py-2 text-sm font-medium shadow-sm',
                getServicesForItem(item).length === 0
                  ? 'cursor-not-allowed border-slate-200 bg-slate-50 text-slate-400'
                  : 'cursor-pointer border-slate-200 bg-white text-slate-600 hover:bg-slate-50'
              ]">
                <span v-if="getServicesForItem(item).length === 0">Not bookable</span>
                <span v-else>{{ isItemSelected(item.itemKey) ? 'Selected' : 'Select' }}</span>
                <input
                  type="checkbox"
                  :checked="isItemSelected(item.itemKey)"
                  :disabled="getServicesForItem(item).length === 0"
                  @change="toggleItem(item.itemKey)"
                  :class="[
                    'h-5 w-5 rounded border-slate-300 focus:ring-cyan-500',
                    getServicesForItem(item).length === 0
                      ? 'cursor-not-allowed opacity-50'
                      : 'text-cyan-600'
                  ]"
                />
              </label>
            </div>

            <HotelBookingFormCard
              v-if="item.isHotel"
              :ref="el => { if (el) formCardRefs[item.itemKey] = el }"
              :item="item"
              :modelValue="formDataMap[item.itemKey]"
              :services="getServicesForItem(item)"
              :services-loading="isServicesLoading(item)"
              :availability="serviceAvailability[item.itemKey]"
              :is-selected="isItemSelected(item.itemKey)"
              @update:modelValue="val => formDataMap[item.itemKey] = val"
            />
            <BookingFormCard
              v-else
              :ref="el => { if (el) formCardRefs[item.itemKey] = el }"
              :item="item"
              :modelValue="formDataMap[item.itemKey]"
              :services="getServicesForItem(item)"
              :services-loading="isServicesLoading(item)"
              :availability="serviceAvailability[item.itemKey]"
              @update:modelValue="val => formDataMap[item.itemKey] = val"
            />
          </div>
        </div>

        <div class="mt-8 rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <p class="text-sm font-semibold text-slate-900">
                {{ selectedItemsIds.size === 0 ? 'Choose the bookings you want to confirm.' : `${selectedItemsIds.size} booking${selectedItemsIds.size === 1 ? '' : 's'} selected` }}
              </p>
              <p class="mt-1 text-sm text-slate-500">
                {{ filteredItems.length }} booking{{ filteredItems.length === 1 ? '' : 's' }} visible in this section.
              </p>
              <p v-if="unavailableItems.length > 0" class="mt-1 text-sm text-amber-600">
                {{ unavailableItems.length }} item{{ unavailableItems.length === 1 ? '' : 's' }} cannot be booked (no services) and {{ unavailableItems.length === 1 ? 'was' : 'were' }} excluded.
              </p>
            </div>

            <div class="flex flex-col gap-3 sm:flex-row">
              <button
                type="button"
                @click="router.back()"
                class="rounded-2xl border border-slate-200 bg-white px-6 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
              >
                Cancel
              </button>
              <button
                type="button"
                @click="openReceiptModal"
                :disabled="confirming || selectedItemsIds.size === 0"
                class="rounded-2xl bg-slate-900 px-6 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {{ confirming ? 'Processing...' : (selectedItemsIds.size === 0 ? 'Select items to book' : `Review & Book (${selectedItemsIds.size})`) }}
              </button>
            </div>
          </div>
        </div>
      </template>
    </div>

    <Teleport to="body">
      <div v-if="showReceiptModal" class="fixed inset-0 z-50 flex items-center justify-center px-4">
        <div class="absolute inset-0 bg-slate-950/50 backdrop-blur-sm" @click="showReceiptModal = false"></div>
        <div class="relative w-full max-w-2xl rounded-3xl border border-slate-200 bg-white shadow-2xl">
          <div class="border-b border-slate-100 px-6 py-5 sm:px-8">
            <p class="text-xs font-semibold uppercase tracking-[0.28em] text-cyan-600">Review booking</p>
            <div class="mt-2 flex items-start justify-between gap-4">
              <div>
                <h2 class="text-2xl font-bold text-slate-900">Booking receipt</h2>
                <p class="mt-1 text-sm text-slate-500">
                  Confirm {{ selectedItems.length }} selected booking{{ selectedItems.length === 1 ? '' : 's' }} before checkout.
                </p>
              </div>
              <button
                type="button"
                @click="showReceiptModal = false"
                class="flex h-10 w-10 items-center justify-center rounded-2xl border border-slate-200 text-slate-500 transition hover:bg-slate-50"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          <div class="max-h-[65vh] overflow-y-auto px-6 py-6 sm:px-8">
            <div class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <div v-for="item in selectedItems" :key="item.itemKey" class="flex items-start justify-between gap-4 py-3 text-sm first:pt-0 last:pb-0">
                <div class="min-w-0 flex-1">
                  <p class="font-semibold text-slate-900">
                    {{ formatServiceName(getServicesForItem(item), formDataMap[item.itemKey]?.service_id) || (item.title || item.name) }}
                  </p>
                  <p class="mt-1 text-slate-500">
                    <template v-if="isHotelItem(item)">1 room × {{ getHotelNights(item) }} night{{ getHotelNights(item) > 1 ? 's' : '' }}</template>
                    <template v-else>{{ formDataMap[item.itemKey]?.amount_of_people || 1 }} person{{ (formDataMap[item.itemKey]?.amount_of_people || 1) > 1 ? 's' : '' }}</template>
                  </p>
                </div>
                <p class="shrink-0 font-semibold text-slate-900">${{ calculateItemTotal(item).toFixed(2) }}</p>
              </div>
            </div>

            <div class="mt-6 rounded-2xl border border-slate-200 bg-white p-4">
              <div class="flex items-center justify-between text-sm">
                <p class="text-slate-500">Subtotal</p>
                <p class="font-semibold text-slate-900">${{ receiptSubtotal.toFixed(2) }}</p>
              </div>
              <div class="mt-3 flex items-center justify-between text-sm">
                <p class="text-slate-500">Service fee ({{ formatPercent(currentServiceFeePercent) }})</p>
                <p class="font-semibold text-slate-900">${{ receiptServiceFee.toFixed(2) }}</p>
              </div>
            </div>

            <div class="mt-6 rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <div class="flex items-center justify-between gap-4">
                <div>
                  <p class="text-sm font-semibold text-slate-900">Discount</p>
                  <p class="mt-1 text-sm text-slate-500">
                    Eligible itinerary discounts are applied automatically from the active admin setting.
                  </p>
                </div>
                <span
                  v-if="packageDiscountEligibility?.eligible && packageDiscount"
                  class="inline-flex rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-semibold text-emerald-700"
                >
                  {{ formatPercent(packageDiscount.discount_percent) }} applied
                </span>
              </div>

              <template v-if="receiptPricingLoading || receiptDiscountLoading">
                <p class="mt-4 text-sm text-slate-500">Checking live pricing and discount rules...</p>
              </template>
              <template v-else-if="!packageDiscount">
                <p class="mt-4 text-sm text-slate-500">No active package discount is configured right now.</p>
              </template>
              <template v-else-if="packageDiscountEligibility?.eligible">
                <div class="mt-4 rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3">
                  <p class="text-sm font-semibold text-emerald-700">
                    {{ packageDiscount.name || 'Package Discount' }} is active for this itinerary.
                  </p>
                  <p class="mt-1 text-sm text-emerald-700/90">
                    {{ formatPercent(packageDiscount.discount_percent) }} will be applied to each selected booking total.
                  </p>
                  <p class="mt-2 text-sm font-semibold text-emerald-700">
                    Estimated savings: ${{ receiptDiscountAmount.toFixed(2) }}
                  </p>
                </div>
              </template>
              <template v-else>
                <p class="mt-4 text-sm text-amber-600">
                  {{ packageDiscountEligibility?.reason || 'This itinerary does not currently qualify for the package discount.' }}
                </p>
              </template>
            </div>

            <div class="mt-6 rounded-2xl bg-slate-950 px-5 py-4 text-white">
              <div class="flex items-center justify-between gap-4">
                <div>
                  <p class="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-300">Final total</p>
                  <p class="mt-1 text-sm text-slate-300">
                    Includes service fee and any eligible discount.
                  </p>
                </div>
                <p class="text-2xl font-bold">${{ receiptFinalTotal.toFixed(2) }}</p>
              </div>
            </div>
          </div>

          <div class="flex flex-col-reverse gap-3 border-t border-slate-100 bg-white px-6 py-5 sm:flex-row sm:justify-end sm:px-8">
            <button
              type="button"
              @click="showReceiptModal = false"
              class="rounded-2xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
            >
              Back to selection
            </button>
            <button
              type="button"
              @click="handleConfirmBooking"
              :disabled="confirming"
              class="rounded-2xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:opacity-60"
            >
              {{ confirming ? 'Processing...' : 'Confirm booking' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { itinerariesAPI, bookingsAPI, discountsAPI, servicesAPI, availabilityAPI, pricingAPI } from '../services/api';
import { useAuthStore } from '../stores/auth';
import { useToastStore } from '../stores/toast';
import BookingFormCard from '../components/BookingFormCard.vue';
import HotelBookingFormCard from '../components/HotelBookingFormCard.vue';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const toastStore = useToastStore();

// --- State ---
const loading = ref(true);
const error = ref('');
const confirming = ref(false);
const itinerary = ref(null);
const formDataMap = ref({});
const formCardRefs = ref({});
const activeTab = ref('');
const showReceiptModal = ref(false);
const packageDiscount = ref(null);
const packageDiscountEligibility = ref(null);
const selectedItemsIds = ref(new Set());
const servicesByListing = ref({});
const servicesLoadingByListing = ref({});
const serviceAvailability = ref({});
const receiptDiscountLoading = ref(false);
const receiptPricingLoading = ref(false);
const currentServiceFeePercent = ref(0.10);

// --- Selection Logic ---
function isItemSelected(key) {
  return selectedItemsIds.value.has(key);
}

function toggleItem(key) {
  const newSet = new Set(selectedItemsIds.value);
  newSet.has(key) ? newSet.delete(key) : newSet.add(key);
  selectedItemsIds.value = newSet;
}

function toggleSelectAll() {
  const newSet = new Set(selectedItemsIds.value);
  filteredItems.value.forEach((item) => {
    allVisibleSelected.value ? newSet.delete(item.itemKey) : newSet.add(item.itemKey);
  });
  selectedItemsIds.value = newSet;
}

const allVisibleSelected = computed(() => filteredItems.value.length > 0 && filteredItems.value.every((item) => selectedItemsIds.value.has(item.itemKey)));
const someVisibleSelected = computed(() => filteredItems.value.some((item) => selectedItemsIds.value.has(item.itemKey)));
const selectedItems = computed(() => {
  return bookableItems.value.filter((item) => {
    if (!selectedItemsIds.value.has(item.itemKey)) return false;
    const services = getServicesForItem(item);
    return services.length > 0;
  });
});

const unavailableItems = computed(() => {
  return bookableItems.value.filter((item) => {
    if (!selectedItemsIds.value.has(item.itemKey)) return false;
    const services = getServicesForItem(item);
    return services.length === 0;
  });
});

// --- Helpers ---
const isHotelItem = (item) => item.extra_metadata?.business_type_name?.toLowerCase() === 'hotel';

const getServicesForItem = (item) => servicesByListing.value[item.listing_id] || [];
const isServicesLoading = (item) => Boolean(servicesLoadingByListing.value[item.listing_id]);

const normalizeDayDate = (dateValue) => {
  if (!dateValue) return 'unknown';
  try {
    const d = new Date(dateValue);
    return isNaN(d.getTime()) ? 'unknown' : d.toISOString().split('T')[0];
  } catch {
    return 'unknown';
  }
};

const formatTabSummaryDate = (dateValue) => {
  if (!dateValue || dateValue === 'unknown') return 'Unscheduled itinerary stops';

  const date = new Date(`${dateValue}T00:00:00`);
  if (isNaN(date.getTime())) return 'Unscheduled itinerary stops';

  return date.toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
};

const bookerName = computed(() => {
  const user = authStore.user;
  if (!user) return '';
  return [user.first_name, user.last_name].filter(Boolean).join(' ').trim() || '';
});

const normalizeFractionalPercent = (value) => {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return 0;
  if (numeric > 1) return numeric / 100;
  return Math.max(numeric, 0);
};

const formatPercent = (value) => {
  const numeric = normalizeFractionalPercent(value);
  if (!Number.isFinite(numeric)) return '-';
  return `${(numeric * 100).toFixed(2).replace(/\.00$/, '')}%`;
};

// --- Computed: Bookable Items ---
const bookableItems = computed(() => {
  if (!itinerary.value?.items) return [];

  const hotelGroups = {};
  const result = [];

  for (const item of itinerary.value.items) {
    if (isHotelItem(item)) {
      const key = item.listing_id;
      if (!hotelGroups[key]) {
        hotelGroups[key] = { ...item, itemKey: `hotel-${key}`, isHotel: true, check_in_date: item.day_date, check_out_date: item.day_date, originalItems: [item] };
      } else {
        const existing = hotelGroups[key];
        existing.check_out_date = item.day_date;
        existing.estimated_cost = (existing.estimated_cost || 0) + (item.estimated_cost || 0);
        existing.originalItems.push(item);
      }
    } else {
      result.push({ ...item, itemKey: `item-${item.id}`, isHotel: false });
    }
  }

  return [...result, ...Object.values(hotelGroups)];
});

// --- Computed: Tabs (combined dayGroups + tabs) ---
const tabs = computed(() => {
  const dayMap = {};
  const hotelItems = [];

  for (const item of bookableItems.value) {
    if (item.isHotel) {
      hotelItems.push(item);
    } else {
      const dayKey = normalizeDayDate(item.day_date);
      (dayMap[dayKey] ||= []).push(item);
    }
  }

  const dayTabs = Object.keys(dayMap).sort().map((dayKey, index) => ({
    id: `day-${dayKey}`,
    type: 'day',
    desktopLabel: dayKey === 'unknown' ? 'Unscheduled' : `Day - ${dayKey}`,
    mobileLabel: dayKey === 'unknown' ? 'Unscheduled' : `Day ${index + 1}`,
    summary: formatTabSummaryDate(dayKey),
  }));

  const hotelTab = hotelItems.length > 0
    ? [{
        id: 'hotels',
        type: 'hotels',
        desktopLabel: `Hotels (${hotelItems.length})`,
        mobileLabel: 'Hotels',
        summary: `${hotelItems.length} hotel ${hotelItems.length === 1 ? 'stay' : 'stays'} in this itinerary`,
      }]
    : [];

  return [...dayTabs, ...hotelTab];
});

watch(tabs, (newTabs) => {
  if (newTabs.length === 0) {
    activeTab.value = '';
    return;
  }

  if (!newTabs.some((tab) => tab.id === activeTab.value)) {
    activeTab.value = newTabs[0].id;
  }
}, { immediate: true });

const activeTabMeta = computed(() => tabs.value.find((tab) => tab.id === activeTab.value) || null);
const activeTabSummary = computed(() => activeTabMeta.value?.summary || '');

// --- Computed: Filtered Items by Tab ---
const filteredItems = computed(() => {
  if (!activeTab.value) return [];
  if (activeTab.value === 'hotels') return bookableItems.value.filter((item) => item.isHotel);
  const dayKey = activeTab.value.replace('day-', '');
  return bookableItems.value.filter((item) => !item.isHotel && normalizeDayDate(item.day_date) === dayKey).slice(0, 4);
});

// --- Receipt Computeds ---
const receiptSubtotal = computed(() => selectedItems.value.reduce((total, item) => total + calculateItemTotal(item), 0));

const receiptDiscountAmount = computed(() => {
  if (!packageDiscount.value || !packageDiscountEligibility.value?.eligible) {
    return 0;
  }

  const discountPercent = normalizeFractionalPercent(packageDiscount.value.discount_percent);
  const maxDiscountAmount = packageDiscount.value.max_discount_amount;

  return selectedItems.value.reduce((total, item) => {
    const itemBasePrice = calculateItemTotal(item);
    const itemDisplayPrice = itemBasePrice + (itemBasePrice * currentServiceFeePercent.value);
    const rawDiscount = itemDisplayPrice * discountPercent;
    const cappedDiscount =
      maxDiscountAmount != null ? Math.min(rawDiscount, Number(maxDiscountAmount)) : rawDiscount;
    return total + cappedDiscount;
  }, 0);
});
const receiptServiceFee = computed(() => receiptSubtotal.value * currentServiceFeePercent.value);
const receiptFinalTotal = computed(() => receiptSubtotal.value + receiptServiceFee.value - receiptDiscountAmount.value);

const formatServiceName = (services, serviceId) => {
  if (!services || !serviceId) return '';
  const service = services.find((s) => s.service_id === serviceId);
  return service ? service.name || 'Service' : '';
};

// Helper to calculate hotel nights
const getHotelNights = (item) => {
  const formData = formDataMap.value[item.itemKey];
  const checkIn = formData?.booking_from_time;
  const checkOut = formData?.booking_to_time;
  if (checkIn && checkOut) {
    const checkInDate = new Date(checkIn);
    const checkOutDate = new Date(checkOut);
    const diffTime = checkOutDate - checkInDate;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays > 0 ? diffDays : 1;
  }
  return 1;
};

const calculateItemTotal = (item) => {
  const formData = formDataMap.value[item.itemKey];
  const services = getServicesForItem(item);
  const people = formData?.amount_of_people || 1;
  const serviceId = formData?.service_id;

  if (services.length > 0 && serviceId) {
    const service = services.find((s) => s.service_id === serviceId);
    if (service?.price) {
      if (isHotelItem(item)) {
        // For hotels, calculate number of nights between check-out and check-in
        const checkIn = formData?.booking_from_time;
        const checkOut = formData?.booking_to_time;
        let nights = 1;
        if (checkIn && checkOut) {
          const checkInDate = new Date(checkIn);
          const checkOutDate = new Date(checkOut);
          const diffTime = checkOutDate - checkInDate;
          const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
          nights = diffDays > 0 ? diffDays : 1;
        }
        return service.price * nights;
      }
      return service.price * people;
    }
  }

  if (isHotelItem(item)) {
    return item.estimated_cost || 0;
  }

  return (item.estimated_cost || 0) * people;
};

// --- Watchers ---
watch(itinerary, (newItinerary) => {
  if (!newItinerary?.items) return;

  const newMap = {};
  for (const item of bookableItems.value) {
    newMap[item.itemKey] = {
      service_id: null,
      bookers_name: bookerName.value,
      amount_of_people: 1,
      special_requests: '',
      booking_from_time: item.isHotel
        ? (item.check_in_date ? `${item.check_in_date}T14:00:00` : null)
        : (item.start_at ? new Date(item.start_at).toISOString() : null),
      booking_to_time: item.isHotel
        ? (item.check_out_date ? `${item.check_out_date}T11:00:00` : null)
        : (item.end_at ? new Date(item.end_at).toISOString() : null),
    };
  }
  formDataMap.value = newMap;
  formCardRefs.value = {};
}, { immediate: true });

watch(bookableItems, async (items) => {
  const listingIds = [...new Set(items.map((item) => item.listing_id).filter(Boolean))];
  if (listingIds.length === 0) return;

  servicesLoadingByListing.value = listingIds.reduce((acc, id) => {
    acc[id] = true;
    return acc;
  }, {});

  const results = await Promise.allSettled(listingIds.map(async (listingId) => {
    const response = await servicesAPI.getAll({ listing_id: listingId });
    return { listingId, services: Array.isArray(response.data) ? response.data : [] };
  }));

  const nextServices = {};
  for (const result of results) {
    if (result.status === 'fulfilled') {
      nextServices[result.value.listingId] = result.value.services;
    }
  }
  servicesByListing.value = nextServices;

  const nextFormDataMap = { ...formDataMap.value };
  for (const item of items) {
    const availableServices = nextServices[item.listing_id] || [];
    const currentServiceId = nextFormDataMap[item.itemKey]?.service_id;
    if (availableServices.length === 1) {
      nextFormDataMap[item.itemKey] = { ...nextFormDataMap[item.itemKey], service_id: availableServices[0].service_id };
    } else if (!availableServices.some((s) => s.service_id === currentServiceId)) {
      nextFormDataMap[item.itemKey] = { ...nextFormDataMap[item.itemKey], service_id: null };
    }
  }
  formDataMap.value = nextFormDataMap;

  const nextLoading = {};
  listingIds.forEach((id) => {
    nextLoading[id] = false;
  });
  servicesLoadingByListing.value = nextLoading;
}, { immediate: true });

watch(formDataMap, (newMap) => {
  for (const [itemKey, formData] of Object.entries(newMap)) {
    const item = bookableItems.value.find((i) => i.itemKey === itemKey);
    if (!item) continue;
    const serviceId = formData?.service_id;
    const date = formData?.booking_from_time?.slice(0, 10);
    // Fetch availability - don't skip even if selected_slot_id changes (availability needs to be loaded)
    fetchAvailabilityForItem(itemKey, serviceId, date);
  }
}, { deep: true });

// --- Methods ---
async function fetchAvailabilityForItem(itemKey, serviceId, date) {
  if (!serviceId || !date) {
    serviceAvailability.value[itemKey] = null;
    return;
  }
  try {
    // Don't pass people count to get all slots - capacity handled in UI
    const response = await availabilityAPI.getServiceAvailability(serviceId, date);
    serviceAvailability.value[itemKey] = response.data;
  } catch {
    serviceAvailability.value[itemKey] = null;
  }
}

async function openReceiptModal() {
  if (!validateSelectedItems()) return;

  for (const item of selectedItems.value) {
    const card = formCardRefs.value[item.itemKey];
    if (card?.validate && !card.validate()) {
      toastStore.show('Please fix validation errors in the forms.', 'error');
      return;
    }
  }

  const firstSelectedItem = selectedItems.value[0];
  const firstSelectedForm = firstSelectedItem ? formDataMap.value[firstSelectedItem.itemKey] : null;

  receiptDiscountLoading.value = true;
  receiptPricingLoading.value = true;
  try {
    const [pricingResult, discountResult] = await Promise.allSettled([
      firstSelectedItem && firstSelectedForm?.service_id
        ? pricingAPI.getListingPrice(firstSelectedItem.listing_id, { service_id: firstSelectedForm.service_id })
        : Promise.resolve({ data: { service_fee_percent: 0.10 } }),
      discountsAPI.getPackageDiscounts(),
    ]);

    if (pricingResult.status === 'fulfilled') {
      currentServiceFeePercent.value = normalizeFractionalPercent(
        pricingResult.value.data?.service_fee_percent ?? 0.10,
      );
    } else {
      currentServiceFeePercent.value = 0.10;
    }

    if (discountResult.status === 'fulfilled') {
      const activePackageDiscounts = Array.isArray(discountResult.value.data) ? discountResult.value.data : [];
      packageDiscount.value = activePackageDiscounts[0] ?? null;
    } else {
      packageDiscount.value = null;
    }

    if (packageDiscount.value?.id) {
      try {
        const eligibilityResponse = await discountsAPI.getDiscountEligibility(
          packageDiscount.value.id,
          route.params.itineraryId,
        );
        packageDiscountEligibility.value = eligibilityResponse.data;
      } catch {
        packageDiscountEligibility.value = {
          eligible: false,
          reason: 'This itinerary does not currently qualify for the package discount.',
        };
      }
    } else {
      packageDiscountEligibility.value = null;
    }

    showReceiptModal.value = true;
  } catch {
    packageDiscount.value = null;
    packageDiscountEligibility.value = null;
    currentServiceFeePercent.value = 0.10;
    showReceiptModal.value = true;
  } finally {
    receiptDiscountLoading.value = false;
    receiptPricingLoading.value = false;
  }
}

function validateSelectedItems() {
  for (const item of selectedItems.value) {
    const formData = formDataMap.value[item.itemKey];
    const services = getServicesForItem(item);
    const availability = serviceAvailability.value[item.itemKey];

    if (isServicesLoading(item)) {
      toastStore.show('Services are still loading for one or more selections.', 'error');
      return false;
    }
    if (services.length === 0) {
      toastStore.show(`"${item.title}" is not bookable because it has no active services.`, 'error');
      return false;
    }
    if (!formData?.service_id) {
      toastStore.show(`Choose a service for "${item.title}" before continuing.`, 'error');
      return false;
    }
    if (!formData.bookers_name?.trim()) {
      toastStore.show(`Enter the booking name for "${item.title}".`, 'error');
      return false;
    }
    if (!formData.booking_from_time || !formData.booking_to_time) {
      toastStore.show(`Complete the booking dates/times for "${item.title}".`, 'error');
      return false;
    }
    if (new Date(formData.booking_to_time) <= new Date(formData.booking_from_time)) {
      toastStore.show(`The booking time range for "${item.title}" is invalid.`, 'error');
      return false;
    }
    if (isHotelItem(item) && availability && availability.is_open === false) {
      toastStore.show(`"${item.title}" is unavailable for the selected check-in date.`, 'error');
      return false;
    }

    // Check if slot selection is required (when availability has slots)
    if (!isHotelItem(item)) {
      const hasSlots = availability?.slots && availability.slots.length > 0;
      if (hasSlots && !formData.selected_slot_id) {
        toastStore.show(`Please select a time slot for "${item.title}".`, 'error');
        return false;
      }
      // If no slots available, user must use the fallback time inputs (no slot selection required)
    }

    // Check capacity if availability/slots exist
    if (!isHotelItem(item) && availability?.slots && availability.slots.length > 0) {
      const people = formData?.amount_of_people || 1;
      const matchingSlot = availability.slots.find(s => String(s.slot_id) === String(formData.selected_slot_id));
      if (matchingSlot && matchingSlot.remaining_capacity < people) {
        toastStore.show(`Please reduce the number of people for "${item.title}". Maximum available is ${matchingSlot.remaining_capacity}.`, 'error');
        return false;
      }
    }
  }
  return true;
}

async function handleConfirmBooking() {
  if (!validateSelectedItems()) return;

  confirming.value = true;
  let createdBookings = [];
  try {
    const results = await Promise.all(selectedItems.value.map((item) => {
      const formData = formDataMap.value[item.itemKey];
      return bookingsAPI.create({
        service_id: formData.service_id,
        service_slot_id: formData.selected_slot_id || null,
        itinerary_item_id: item.originalItems?.[0]?.id || item.id,
        booking_from_time: formData.booking_from_time,
        booking_to_time: formData.booking_to_time,
        bookers_name: formData.bookers_name,
        amount_of_people: formData.amount_of_people || 1,
        special_requests: formData.special_requests || null,
      }).then((response) => response.data);
    }));

    createdBookings = results;
    toastStore.show(`Confirmed ${createdBookings.length} bookings!`, 'success');
    showReceiptModal.value = false;

    if (createdBookings.length > 0) {
      const firstBookingId = createdBookings[0].booking_id || createdBookings[0].id;
      router.push(`/bookings/${firstBookingId}`);
    } else {
      router.back();
    }
  } catch (err) {
    console.error('Booking failed', err);
    const detail = err.response?.data?.detail;
    toastStore.show(typeof detail === 'string' && detail.trim() ? detail : 'Booking failed. Please try again.', 'error');
  } finally {
    confirming.value = false;
  }
}

// --- Lifecycle ---
onMounted(async () => {
  loading.value = true;
  error.value = '';
  try {
    const response = await itinerariesAPI.getById(route.params.itineraryId);
    itinerary.value = response.data;
  } catch (err) {
    console.error('Failed to load itinerary', err);
    error.value = 'Could not load itinerary. Please try again.';
    toastStore.show('Failed to load itinerary.', 'error');
  } finally {
    loading.value = false;
  }
});
</script>
