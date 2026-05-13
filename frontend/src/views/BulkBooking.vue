<template>
  <div class="bg-slate-50 min-h-screen">
    <section
      class="relative overflow-hidden border-b border-slate-200 bg-slate-950"
      style="
        background-image:
          linear-gradient(rgba(2, 6, 23, 0.72), rgba(2, 6, 23, 0.82)),
          url(&quot;/images/beach-bkg.jpg&quot;);
        background-size: cover;
        background-position: center;
      "
    >
      <div
        class="mx-auto flex min-h-[280px] max-w-7xl flex-col justify-end px-4 pb-10 pt-24 sm:px-6 lg:px-8"
      >
        <p
          class="text-xs font-semibold uppercase tracking-[0.3em] text-cyan-300"
        >
          Bulk booking
        </p>
        <h1
          class="mt-4 max-w-3xl text-4xl font-bold leading-tight text-white sm:text-5xl"
        >
          Book {{ bookableItems.length }} {{ bookableItems.length === 1 ? 'Item' : 'Items' }}
        </h1>
        <p class="mt-5 max-w-2xl text-base leading-7 text-slate-200">
          {{ itineraryTitle }}
        </p>
      </div>

      <!-- Tab Navigation -->
      <div v-if="tabs.length > 1" class="mb-6 border-b border-slate-200">
        <nav class="flex gap-6 px-4">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            :class="[
              'pb-3 text-sm font-medium transition-colors',
              activeTab === tab.id
                ? 'border-b-2 border-cyan-600 text-cyan-600'
                : 'text-slate-500 hover:text-slate-700'
            ]"
            @click="setActiveTab(tab.id)"
          >
            {{ tab.label }}
          </button>
        </nav>
      </div>

      <div v-if="loading" class="grid gap-6">
        <div
          v-for="n in 3"
          :key="n"
          class="animate-pulse rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
        >
          <div class="h-6 w-1/3 rounded bg-slate-200"></div>
          <div class="mt-4 h-4 w-1/2 rounded bg-slate-100"></div>
          <div class="mt-6 h-32 rounded-2xl bg-slate-100"></div>
        </div>
      </div>

      <div
        v-else-if="error"
        class="rounded-3xl border border-red-200 bg-red-50 px-6 py-12 text-center shadow-sm"
      >
        <p class="text-base font-medium text-red-700">{{ error }}</p>
        <button
          @click="goBack"
          class="mt-6 inline-flex items-center justify-center rounded-2xl bg-slate-900 px-6 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
        >
          Go Back
        </button>
      </div>

      <div
        v-else-if="bookableItems.length === 0"
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
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
            />
          </svg>
        </div>
        <h2 class="mt-5 text-lg font-bold text-slate-900">No items to book</h2>
        <p class="mt-2 text-sm text-slate-500">
          This itinerary has no bookable items yet.
        </p>
        <button
          @click="goBack"
          class="mt-6 inline-flex items-center justify-center rounded-2xl bg-slate-900 px-6 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
        >
          Go Back
        </button>
      </div>

      <div v-if="!loading && !error && bookableItems.length > 0" class="mb-4 flex items-center justify-between px-4">
        <label class="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            :checked="allVisibleSelected"
            :indeterminate="someVisibleSelected && !allVisibleSelected"
            @change="toggleSelectAllVisible"
            class="h-5 w-5 rounded border-slate-300 text-cyan-600 focus:ring-cyan-500"
          />
          <span class="text-sm font-medium text-slate-700">
            {{ allVisibleSelected ? 'Deselect All' : 'Select All' }} ({{ filteredItems.length }} visible)
          </span>
        </label>
        <div v-if="selectedCount > 0" class="text-sm text-slate-600">
          {{ selectedCount }} item{{ selectedCount === 1 ? '' : 's' }} selected
        </div>
      </div>

      <div class="grid gap-6">
        <template v-for="(item, index) in filteredItems" :key="item._key">
          <div
            :class="[
              'relative overflow-hidden rounded-3xl border transition-all',
              isItemSelected(item._key)
                ? 'border-cyan-400 bg-cyan-50 ring-1 ring-cyan-200'
                : 'border-slate-200 bg-white'
            ]"
          >
            <!-- Checkbox -->
            <label class="absolute top-4 left-4 z-10 flex items-center justify-center">
              <input
                type="checkbox"
                :checked="isItemSelected(item._key)"
                @change="toggleItem(item._key)"
                class="h-5 w-5 rounded border-slate-300 text-cyan-600 focus:ring-cyan-500"
              />
            </label>

            <HotelBookingFormCard
              v-if="item.isHotel"
              :ref="el => { if (el) formCardRefs[item._key] = el }"
              :item="item"
              :modelValue="formDataMap[item._key]"
              :services="getServicesForItem(item)"
              :services-loading="isServicesLoading(item)"
              @update:modelValue="val => formDataMap[item._key] = val"
            />
            <BookingFormCard
              v-else
              :ref="el => { if (el) formCardRefs[item._key] = el }"
              :item="item"
              :modelValue="formDataMap[item._key]"
              :services="getServicesForItem(item)"
              :services-loading="isServicesLoading(item)"
              @update:modelValue="val => formDataMap[item._key] = val"
            />
          </div>
        </template>
      </div>

      <div
        v-if="!loading && !error && bookableItems.length > 0"
        class="mt-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-center"
      >
        <div class="flex gap-3">
          <button
            type="button"
            @click="openReceiptModal"
            :disabled="confirming || selectedCount === 0"
            class="rounded-2xl bg-cyan-600 px-6 py-3 text-sm font-semibold text-white transition hover:bg-cyan-700 disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {{ confirming ? 'Processing...' : (selectedCount === 0 ? 'Select items to book' : `Review & Book (${selectedCount})`) }}
          </button>

          <button
            type="button"
            @click="goBack"
            class="rounded-2xl border border-slate-200 bg-white px-6 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
          >
            Cancel
          </button>
        </div>

        <p class="text-sm text-slate-500">
          {{ filteredItems.length }} booking{{ filteredItems.length === 1 ? '' : 's' }} ready to confirm
        </p>
      </div>
    </section>

    <!-- Receipt Modal -->
    <Teleport to="body">
      <div v-if="showReceiptModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
        <div class="w-full max-w-lg rounded-3xl bg-white shadow-2xl">
          <!-- Header -->
          <div class="rounded-t-3xl border-b border-slate-100 bg-slate-50 px-6 py-5">
            <h2 class="text-xl font-bold text-slate-900">Booking Receipt</h2>
          </div>

          <!-- Body -->
          <div class="max-h-[60vh] overflow-y-auto px-6 py-5">
            <!-- Items List -->
            <div class="mb-6 space-y-3">
              <div v-for="item in selectedItems" :key="item._key" class="flex justify-between text-sm">
                <div class="flex-1">
                  <p class="font-medium text-slate-900">{{ item.title || item.name }}</p>
                  <p class="text-slate-500">{{ item.start_at ? new Date(item.start_at).toLocaleDateString() : (item.day_date || 'N/A') }}</p>
                </div>
                <p class="font-medium text-slate-900">${{ (item.estimated_cost || 0).toFixed(2) }}</p>
              </div>
            </div>

            <!-- Subtotal -->
            <div class="border-t border-slate-100 pt-4">
              <div class="flex justify-between text-sm">
                <p class="text-slate-600">Subtotal</p>
                <p class="font-medium text-slate-900">${{ receiptSubtotal.toFixed(2) }}</p>
              </div>
            </div>

            <!-- Discount Section -->
            <div class="mt-4 border-t border-slate-100 pt-4">
              <p class="mb-2 text-sm font-medium text-slate-700">Discount</p>
              <div v-if="availableDiscounts.length === 0" class="text-sm text-slate-500">
                No discounts available
              </div>
              <div v-else-if="availableDiscounts.length > 0">
                <select
                  v-model="selectedDiscountId"
                  class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-cyan-500 focus:outline-none focus:ring-1 focus:ring-cyan-500"
                >
                  <option v-for="discount in availableDiscounts" :key="discount.id" :value="discount.id">
                    {{ discount.name }} ({{ (discount.discount_percent * 100).toFixed(0) }}% off)
                  </option>
                </select>
                <div class="mt-2 flex items-center gap-2">
                  <span v-if="isDiscountEligible && selectedDiscount" class="inline-flex items-center rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700">
                    {{ (selectedDiscount.discount_percent * 100).toFixed(0) }}% discount applied!
                  </span>
                  <span v-else-if="!isDiscountEligible" class="text-xs text-amber-600">
                    Select 50%+ items to unlock discount
                  </span>
                </div>
              </div>
            </div>

            <!-- Final Total -->
            <div class="mt-4 border-t border-slate-200 pt-4">
              <div class="flex justify-between">
                <p class="text-base font-semibold text-slate-900">Final Total</p>
                <p class="text-xl font-bold text-cyan-600">${{ receiptFinalTotal.toFixed(2) }}</p>
              </div>
            </div>
          </div>

          <!-- Footer -->
          <div class="flex justify-end gap-3 rounded-b-3xl border-t border-slate-100 bg-slate-50 px-6 py-4">
            <button
              type="button"
              @click="showReceiptModal = false"
              class="rounded-xl border border-slate-200 bg-white px-5 py-2.5 text-sm font-medium text-slate-700 transition hover:bg-slate-100"
            >
              ← Back to Selection
            </button>
            <button
              type="button"
              @click="handleConfirmBooking"
              :disabled="confirming"
              class="rounded-xl bg-cyan-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-cyan-700 disabled:opacity-60"
            >
              {{ confirming ? 'Processing...' : 'Confirm Booking' }}
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
import { itinerariesAPI, bookingsAPI, discountsAPI, servicesAPI } from '../services/api';
import { useAuthStore } from '../stores/auth';
import { useToastStore } from '../stores/toast';
import BookingFormCard from '../components/BookingFormCard.vue';
import HotelBookingFormCard from '../components/HotelBookingFormCard.vue';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const toastStore = useToastStore();

const loading = ref(true);
const error = ref('');
const confirming = ref(false);
const itinerary = ref(null);
const formDataMap = ref({});
const formCardRefs = ref([]);
const activeTab = ref('');
const showReceiptModal = ref(false);
const availableDiscounts = ref([]);
const selectedDiscountId = ref(null);
const receiptDiscountLoading = ref(false);
const selectedItemsIds = ref(new Set());
const servicesByListing = ref({});
const servicesLoadingByListing = ref({});

// Selection helpers
function isItemSelected(key) {
  return selectedItemsIds.value.has(key);
}

function toggleItem(key) {
  const newSet = new Set(selectedItemsIds.value);
  if (newSet.has(key)) {
    newSet.delete(key);
  } else {
    newSet.add(key);
  }
  selectedItemsIds.value = newSet;
}

function toggleSelectAllVisible() {
  if (allVisibleSelected.value) {
    // Deselect all visible
    const newSet = new Set(selectedItemsIds.value);
    filteredItems.value.forEach(item => newSet.delete(item._key));
    selectedItemsIds.value = newSet;
  } else {
    // Select all visible
    const newSet = new Set(selectedItemsIds.value);
    filteredItems.value.forEach(item => newSet.add(item._key));
    selectedItemsIds.value = newSet;
  }
}

const allVisibleSelected = computed(() => {
  return filteredItems.value.length > 0 && filteredItems.value.every(item => selectedItemsIds.value.has(item._key));
});

const someVisibleSelected = computed(() => {
  return filteredItems.value.some(item => selectedItemsIds.value.has(item._key));
});

const selectedCount = computed(() => selectedItemsIds.value.size);

const itineraryTitle = computed(() => {
  return itinerary.value?.title || 'Your Itinerary';
});

// Items that are checked/selected (based on checkbox selection, not form data)
const selectedItems = computed(() => {
  // Return all bookable items that are selected via checkbox
  return bookableItems.value.filter(item => selectedItemsIds.value.has(item._key));
});

// Receipt computeds
const receiptSubtotal = computed(() => {
  return selectedItems.value.map(i => i.estimated_cost).reduce((a, b) => a + b, 0);
});

const isDiscountEligible = computed(() => {
  return selectedCount.value >= bookableItems.value.length * 0.5;
});

const selectedDiscount = computed(() => {
  return availableDiscounts.value.find(d => d.id === selectedDiscountId.value);
});

const receiptDiscountAmount = computed(() => {
  // Only apply discount if 50%+ items are selected
  if (!isDiscountEligible.value) return 0;
  return receiptSubtotal.value * (selectedDiscount.value?.discount_percent || 0);
});

const receiptFinalTotal = computed(() => {
  return receiptSubtotal.value - receiptDiscountAmount.value;
});

// Helper to normalize day date to YYYY-MM-DD string
function normalizeDayDate(dateValue) {
  if (!dateValue) return 'unknown';
  try {
    const d = new Date(dateValue);
    if (isNaN(d.getTime())) return 'unknown';
    return d.toISOString().split('T')[0];
  } catch {
    return 'unknown';
  }
}

// Check if item is a hotel
function isHotelItem(item) {
  if (item.item_type?.toLowerCase() === 'hotel') return true;
  if (item.extra_metadata?.business_type_name?.toLowerCase() === 'hotel') return true;
  return false;
}

// Capitalize first letter of each word for booker's name
function capitalizeName(name) {
  if (!name) return '';
  return name
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

// Get user's full name (first + last name) with capitalization
function getUserFullName() {
  const user = authStore.user;
  if (!user) return '';
  const first = user.first_name || '';
  const last = user.last_name || '';
  const fullName = (first + ' ' + last).trim();
  return capitalizeName(fullName);
}

// Set active tab
function setActiveTab(tabId) {
  activeTab.value = tabId;
}

function getServicesForItem(item) {
  return servicesByListing.value[item.listing_id] || [];
}

function isServicesLoading(item) {
  return Boolean(servicesLoadingByListing.value[item.listing_id]);
}

// Build bookable items from itinerary items
// - Consolidate hotels with same listing_id into single booking
const bookableItems = computed(() => {
  if (!itinerary.value?.items) return [];

  const items = itinerary.value.items;
  const result = [];
  const hotelGroups = {}; // keyed by listing_id

  // First pass: identify hotels and group by listing_id
  for (const item of items) {
    if (isHotelItem(item)) {
      const key = item.listing_id;
      if (!hotelGroups[key]) {
        hotelGroups[key] = {
          ...item,
          _key: `hotel-${key}`,
          isHotel: true,
          check_in_date: item.day_date,
          check_out_date: item.day_date,
          _originalItems: [item],
        };
      } else {
        // Extend check_out_date to this item's day
        const existing = hotelGroups[key];
        existing.check_out_date = item.day_date;
        existing.estimated_cost = (existing.estimated_cost || 0) + (item.estimated_cost || 0);
        existing._originalItems.push(item);
      }
    } else {
      // Non-hotel item - add directly
      result.push({
        ...item,
        _key: `item-${item.id}`,
        isHotel: false,
      });
    }
  }

  // Add consolidated hotel groups
  for (const key in hotelGroups) {
    result.push(hotelGroups[key]);
  }

  return result;
});

// Group bookable items by day_date for tabs (excluding hotels)
const dayGroups = computed(() => {
  const groups = {};
  for (const item of bookableItems.value) {
    if (item.isHotel) continue; // Hotels have their own tab
    const dayKey = normalizeDayDate(item.day_date);
    if (!groups[dayKey]) {
      groups[dayKey] = [];
    }
    groups[dayKey].push(item);
  }
  return groups;
});

// Build tabs from day groups + Hotels tab
const tabs = computed(() => {
  const tabList = [];
  const dayKeys = Object.keys(dayGroups.value).sort();

  for (const dayKey of dayKeys) {
    const label = dayKey === 'unknown' ? 'Unscheduled' : `Day - ${dayKey}`;
    tabList.push({
      id: `day-${dayKey}`,
      label: label,
    });
  }

  // Add Hotels tab if there are hotel items
  const hotelItems = bookableItems.value.filter(item => item.isHotel);
  if (hotelItems.length > 0) {
    tabList.push({
      id: 'hotels',
      label: `Hotels (${hotelItems.length})`,
    });
  }

  return tabList;
});

// Set active tab to first tab on load
watch(tabs, (newTabs) => {
  if (newTabs.length > 0 && !activeTab.value) {
    activeTab.value = newTabs[0].id;
  }
}, { immediate: true });

// Filter items based on active tab
const filteredItems = computed(() => {
  if (!activeTab.value) return [];

  // Hotels tab shows all hotels
  if (activeTab.value === 'hotels') {
    return bookableItems.value.filter(item => item.isHotel);
  }

  // Day tabs show non-hotel items for that day (max 4)
  const dayKey = activeTab.value.startsWith('day-') ? activeTab.value.replace('day-', '') : activeTab.value;
  const dayItems = (dayGroups.value[dayKey] || []).filter(item => !item.isHotel);
  return dayItems.slice(0, 4);
});

// Initialize form data when items change
watch(bookableItems, (items) => {
  const capitalizedName = getUserFullName();
  const newMap = {};

  for (const item of items) {
    if (item.isHotel) {
      // Hotel: use check_in_date/check_out_date with standard times
      newMap[item._key] = {
        service_id: null,
        bookers_name: capitalizedName,
        amount_of_people: 1,
        special_requests: '',
        booking_from_time: item.check_in_date ? `${item.check_in_date}T14:00:00` : null,
        booking_to_time: item.check_out_date ? `${item.check_out_date}T11:00:00` : null,
      };
    } else {
      // Regular item: use start_at/end_at
      newMap[item._key] = {
        service_id: null,
        bookers_name: capitalizedName,
        amount_of_people: 1,
        special_requests: '',
        booking_from_time: item.start_at ? new Date(item.start_at).toISOString() : null,
        booking_to_time: item.end_at ? new Date(item.end_at).toISOString() : null,
      };
    }
  }

  formDataMap.value = newMap;
  formCardRefs.value = [];
}, { immediate: true });

watch(
  bookableItems,
  async (items) => {
    const listingIds = [...new Set(items.map((item) => item.listing_id).filter(Boolean))];
    const nextServicesByListing = {};
    const nextLoadingState = {};

    if (listingIds.length === 0) {
      servicesByListing.value = nextServicesByListing;
      servicesLoadingByListing.value = nextLoadingState;
      return;
    }

    servicesLoadingByListing.value = listingIds.reduce((acc, listingId) => {
      acc[listingId] = true;
      return acc;
    }, {});

    await Promise.all(
      listingIds.map(async (listingId) => {
        try {
          const response = await servicesAPI.getAll({ listing_id: listingId });
          nextServicesByListing[listingId] = Array.isArray(response.data) ? response.data : [];
        } catch (serviceError) {
          console.error(`Failed to load services for listing ${listingId}`, serviceError);
          nextServicesByListing[listingId] = [];
        } finally {
          nextLoadingState[listingId] = false;
        }
      })
    );

    servicesByListing.value = nextServicesByListing;
    servicesLoadingByListing.value = nextLoadingState;

    const nextFormDataMap = { ...formDataMap.value };
    for (const item of items) {
      const availableServices = nextServicesByListing[item.listing_id] || [];
      const currentFormData = nextFormDataMap[item._key] || {};
      const hasCurrentSelection = availableServices.some(
        (service) => service.service_id === currentFormData.service_id
      );

      if (availableServices.length === 1) {
        nextFormDataMap[item._key] = {
          ...currentFormData,
          service_id: availableServices[0].service_id,
        };
      } else if (!hasCurrentSelection) {
        nextFormDataMap[item._key] = {
          ...currentFormData,
          service_id: null,
        };
      }
    }
    formDataMap.value = nextFormDataMap;
  },
  { immediate: true }
);

async function fetchItinerary() {
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
}

async function openReceiptModal() {
  if (!validateSelectedItems()) {
    return;
  }

  // Validate all cards first
  const cardRefs = formCardRefs.value;
  for (const key in cardRefs) {
    const card = cardRefs[key];
    if (card && typeof card.validate === 'function') {
      if (!card.validate()) {
        toastStore.show('Please fix validation errors in the forms.', 'error');
        return;
      }
    }
  }

  receiptDiscountLoading.value = true;
  try {
    const response = await discountsAPI.getPackageDiscounts();
    availableDiscounts.value = response.data || [];
    if (availableDiscounts.value.length > 0) {
      selectedDiscountId.value = availableDiscounts.value[0].id;
    } else {
      selectedDiscountId.value = null;
    }
    showReceiptModal.value = true;
  } catch (err) {
    console.error('Failed to load discounts', err);
    availableDiscounts.value = [];
    selectedDiscountId.value = null;
    showReceiptModal.value = true;
  } finally {
    receiptDiscountLoading.value = false;
  }
}

function validateSelectedItems() {
  for (const item of selectedItems.value) {
    const formData = formDataMap.value[item._key];
    const services = getServicesForItem(item);

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
  }

  return true;
}

async function handleConfirmBooking() {
  if (!validateSelectedItems()) {
    return;
  }

  confirming.value = true;
  try {
    // Create bookings for each selected item
    const bookingPromises = selectedItems.value.map((item) => {
      const formData = formDataMap.value[item._key];
      return bookingsAPI.create({
        service_id: formData.service_id,
        itinerary_item_id: item._originalItems?.[0]?.id || item.id,
        booking_from_time: formData.booking_from_time,
        booking_to_time: formData.booking_to_time,
        bookers_name: formData.bookers_name,
        amount_of_people: formData.amount_of_people || 1,
        special_requests: formData.special_requests || null,
      });
    });

    await Promise.all(bookingPromises);

    toastStore.show(`Confirmed ${selectedItems.value.length} bookings!`, 'success');
    showReceiptModal.value = false;
    router.back();
  } catch (err) {
    console.error('Booking failed', err);
    const detail = err.response?.data?.detail;
    toastStore.show(
      typeof detail === 'string' && detail.trim()
        ? detail
        : 'Booking failed. Please try again.',
      'error'
    );
  } finally {
    confirming.value = false;
  }
}

function goBack() {
  router.back();
}

onMounted(() => {
  fetchItinerary();
});
</script>
