<template>
  <div class="bg-slate-50 min-h-screen">
    <!-- Hero Header -->
    <section
      class="relative overflow-hidden border-b border-slate-200 bg-slate-950"
      style="
        background-image:
          linear-gradient(rgba(2, 6, 23, 0.72), rgba(2, 6, 23, 0.82)),
          url('/images/beach-bkg.jpg');
        background-size: cover;
        background-position: center;
      "
    >
      <div class="mx-auto flex min-h-[280px] max-w-7xl flex-col justify-end px-4 pb-10 pt-24 sm:px-6 lg:px-8">
        <p class="text-xs font-semibold uppercase tracking-[0.3em] text-cyan-300">Bulk booking</p>
        <h1 class="mt-4 max-w-3xl text-4xl font-bold leading-tight text-white sm:text-5xl">
          Book {{ bookableItems.length }} {{ bookableItems.length === 1 ? 'Item' : 'Items' }}
        </h1>
        <p class="mt-5 max-w-2xl text-base leading-7 text-slate-200">{{ itinerary?.title || 'Your Itinerary' }}</p>
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
            @click="activeTab = tab.id"
          >
            {{ tab.label }}
          </button>
        </nav>
      </div>

      <!-- Loading Skeleton -->
      <div v-if="loading" class="grid gap-6">
        <div v-for="n in 3" :key="n" class="animate-pulse rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <div class="h-6 w-1/3 rounded bg-slate-200"></div>
          <div class="mt-4 h-4 w-1/2 rounded bg-slate-100"></div>
          <div class="mt-6 h-32 rounded-2xl bg-slate-100"></div>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="rounded-3xl border border-red-200 bg-red-50 px-6 py-12 text-center shadow-sm">
        <p class="text-base font-medium text-red-700">{{ error }}</p>
        <button @click="router.back()" class="mt-6 inline-flex items-center justify-center rounded-2xl bg-slate-900 px-6 py-3 text-sm font-semibold text-white transition hover:bg-slate-800">
          Go Back
        </button>
      </div>

      <!-- Empty State -->
      <div v-else-if="bookableItems.length === 0" class="rounded-3xl border border-slate-200 bg-white px-6 py-20 text-center shadow-sm">
        <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-slate-100 text-slate-400">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
        </div>
        <h2 class="mt-5 text-lg font-bold text-slate-900">No items to book</h2>
        <p class="mt-2 text-sm text-slate-500">This itinerary has no bookable items yet.</p>
        <button @click="router.back()" class="mt-6 inline-flex items-center justify-center rounded-2xl bg-slate-900 px-6 py-3 text-sm font-semibold text-white transition hover:bg-slate-800">
          Go Back
        </button>
      </div>

      <!-- Bulk Actions Bar -->
      <template v-if="!loading && !error && bookableItems.length > 0">
        <div class="mb-4 flex items-center justify-between px-4">
          <label class="flex cursor-pointer items-center gap-2">
            <input type="checkbox" :checked="allVisibleSelected" :indeterminate="someVisibleSelected && !allVisibleSelected" @change="toggleSelectAll" class="h-5 w-5 rounded border-slate-300 text-cyan-600 focus:ring-cyan-500" />
            <span class="text-sm font-medium text-slate-700">{{ allVisibleSelected ? 'Deselect All' : 'Select All' }} ({{ filteredItems.length }} visible)</span>
          </label>
          <div v-if="selectedItemsIds.size > 0" class="text-sm text-slate-600">{{ selectedItemsIds.size }} item{{ selectedItemsIds.size === 1 ? '' : 's' }} selected</div>
        </div>

        <!-- Items Grid -->
        <div class="grid gap-6">
          <div
            v-for="item in filteredItems"
            :key="item._key"
            :class="['relative overflow-hidden rounded-3xl border transition-all', isItemSelected(item._key) ? 'border-cyan-400 bg-cyan-50 ring-1 ring-cyan-200' : 'border-slate-200 bg-white']"
          >
            <!-- Checkbox -->
            <label class="absolute top-4 left-4 z-10 flex items-center justify-center">
              <input type="checkbox" :checked="isItemSelected(item._key)" @change="toggleItem(item._key)" class="h-5 w-5 rounded border-slate-300 text-cyan-600 focus:ring-cyan-500" />
            </label>

            <!-- Hotel Card -->
            <HotelBookingFormCard
              v-if="item.isHotel"
              :ref="el => { if (el) formCardRefs[item._key] = el }"
              :item="item"
              :modelValue="formDataMap[item._key]"
              :services="getServicesForItem(item)"
              :services-loading="isServicesLoading(item)"
              :availability="serviceAvailability[item._key]"
              :is-selected="isItemSelected(item._key)"
              @update:modelValue="val => formDataMap[item._key] = val"
            />
            <!-- Regular Card -->
            <BookingFormCard
              v-else
              :ref="el => { if (el) formCardRefs[item._key] = el }"
              :item="item"
              :modelValue="formDataMap[item._key]"
              :services="getServicesForItem(item)"
              :services-loading="isServicesLoading(item)"
              :availability="serviceAvailability[item._key]"
              @update:modelValue="val => formDataMap[item._key] = val"
            />
          </div>
        </div>

        <!-- Action Footer -->
        <div class="mt-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
          <div class="flex gap-3">
            <button type="button" @click="openReceiptModal" :disabled="confirming || selectedItemsIds.size === 0" class="rounded-2xl bg-cyan-600 px-6 py-3 text-sm font-semibold text-white transition hover:bg-cyan-700 disabled:opacity-60 disabled:cursor-not-allowed">
              {{ confirming ? 'Processing...' : (selectedItemsIds.size === 0 ? 'Select items to book' : `Review & Book (${selectedItemsIds.size})`) }}
            </button>
            <button type="button" @click="router.back()" class="rounded-2xl border border-slate-200 bg-white px-6 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-100">
              Cancel
            </button>
          </div>
          <p class="text-sm text-slate-500">{{ filteredItems.length }} booking{{ filteredItems.length === 1 ? '' : 's' }} ready to confirm</p>
        </div>
      </template>
    </section>

    <!-- Receipt Modal -->
    <Teleport to="body">
      <div v-if="showReceiptModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
        <div class="w-full max-w-lg rounded-3xl bg-white shadow-2xl">
          <div class="rounded-t-3xl border-b border-slate-100 bg-slate-50 px-6 py-5">
            <h2 class="text-xl font-bold text-slate-900">Booking Receipt</h2>
          </div>

          <div class="max-h-[60vh] overflow-y-auto px-6 py-5">
            <!-- Items List -->
            <div class="mb-6 space-y-3">
              <div v-for="item in selectedItems" :key="item._key" class="flex justify-between text-sm">
                <div class="flex-1">
                  <p class="font-medium text-slate-900">{{ item.title || item.name }}</p>
                  <p class="text-slate-500">
                    <template v-if="isHotelItem(item)">1 room × ${{ (item.estimated_cost || 0).toFixed(2) }}</template>
                    <template v-else>${{ (item.estimated_cost || 0).toFixed(2) }} × {{ formDataMap[item._key]?.amount_of_people || 1 }} people = ${{ ((item.estimated_cost || 0) * (formDataMap[item._key]?.amount_of_people || 1)).toFixed(2) }}</template>
                  </p>
                </div>
                <p class="font-medium text-slate-900">${{ ((item.estimated_cost || 0) * (formDataMap[item._key]?.amount_of_people || (isHotelItem(item) ? 1 : 1))).toFixed(2) }}</p>
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
              <template v-if="availableDiscounts.length === 0">
                <p class="text-sm text-slate-500">No discounts available</p>
              </template>
              <template v-else>
                <select v-model="selectedDiscountId" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-cyan-500 focus:outline-none focus:ring-1 focus:ring-cyan-500">
                  <option v-for="discount in availableDiscounts" :key="discount.id" :value="discount.id">{{ discount.name }} ({{ (discount.discount_percent * 100).toFixed(0) }}% off)</option>
                </select>
                <div class="mt-2 flex items-center gap-2">
                  <span v-if="isDiscountEligible && selectedDiscount" class="inline-flex items-center rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700">{{ (selectedDiscount.discount_percent * 100).toFixed(0) }}% discount applied!</span>
                  <span v-else-if="!isDiscountEligible" class="text-xs text-amber-600">Select 50%+ items to unlock discount</span>
                </div>
              </template>
            </div>

            <!-- Final Total -->
            <div class="mt-4 border-t border-slate-200 pt-4">
              <div class="flex justify-between">
                <p class="text-base font-semibold text-slate-900">Final Total</p>
                <p class="text-xl font-bold text-cyan-600">${{ receiptFinalTotal.toFixed(2) }}</p>
              </div>
            </div>
          </div>

          <div class="flex justify-end gap-3 rounded-b-3xl border-t border-slate-100 bg-slate-50 px-6 py-4">
            <button type="button" @click="showReceiptModal = false" class="rounded-xl border border-slate-200 bg-white px-5 py-2.5 text-sm font-medium text-slate-700 transition hover:bg-slate-100">← Back to Selection</button>
            <button type="button" @click="handleConfirmBooking" :disabled="confirming" class="rounded-xl bg-cyan-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-cyan-700 disabled:opacity-60">{{ confirming ? 'Processing...' : 'Confirm Booking' }}</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { itinerariesAPI, bookingsAPI, discountsAPI, servicesAPI, availabilityAPI } from '../services/api';
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
const formCardRefs = ref({});  // Fixed: was array, now object
const activeTab = ref('');
const showReceiptModal = ref(false);
const availableDiscounts = ref([]);
const selectedDiscountId = ref(null);
const selectedItemsIds = ref(new Set());
const servicesByListing = ref({});
const servicesLoadingByListing = ref({});
const serviceAvailability = ref({});
const receiptDiscountLoading = ref(false);

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
  filteredItems.value.forEach(item => {
    allVisibleSelected.value ? newSet.delete(item._key) : newSet.add(item._key);
  });
  selectedItemsIds.value = newSet;
}

const allVisibleSelected = computed(() => filteredItems.value.length > 0 && filteredItems.value.every(item => selectedItemsIds.value.has(item._key)));
const someVisibleSelected = computed(() => filteredItems.value.some(item => selectedItemsIds.value.has(item._key)));
const selectedItems = computed(() => bookableItems.value.filter(item => selectedItemsIds.value.has(item._key)));

// --- Helpers ---
const isHotelItem = (item) => item.item_type?.toLowerCase() === 'hotel' || item.extra_metadata?.business_type_name?.toLowerCase() === 'hotel';

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

const bookerName = computed(() => {
  const user = authStore.user;
  if (!user) return '';
  return [user.first_name, user.last_name].filter(Boolean).join(' ').trim() || '';
});

// --- Computed: Bookable Items ---
const bookableItems = computed(() => {
  if (!itinerary.value?.items) return [];

  const hotelGroups = {};
  const result = [];

  for (const item of itinerary.value.items) {
    if (isHotelItem(item)) {
      const key = item.listing_id;
      if (!hotelGroups[key]) {
        hotelGroups[key] = { ...item, _key: `hotel-${key}`, isHotel: true, check_in_date: item.day_date, check_out_date: item.day_date, _originalItems: [item] };
      } else {
        const existing = hotelGroups[key];
        existing.check_out_date = item.day_date;
        existing.estimated_cost = (existing.estimated_cost || 0) + (item.estimated_cost || 0);
        existing._originalItems.push(item);
      }
    } else {
      result.push({ ...item, _key: `item-${item.id}`, isHotel: false });
    }
  }

  return [...result, ...Object.values(hotelGroups)];
});

// --- Computed: Tabs (combined dayGroups + tabs) ---
const tabs = computed(() => {
  const dayMap = {};
  const hotelItems = [];

  // Group non-hotels by day, collect hotels separately
  for (const item of bookableItems.value) {
    if (item.isHotel) {
      hotelItems.push(item);
    } else {
      const dayKey = normalizeDayDate(item.day_date);
      (dayMap[dayKey] ||= []).push(item);
    }
  }

  // Build tabs: day tabs + hotels tab
  return [
    ...Object.keys(dayMap).sort().map(dayKey => ({
      id: `day-${dayKey}`,
      label: dayKey === 'unknown' ? 'Unscheduled' : `Day - ${dayKey}`,
    })),
    ...(hotelItems.length > 0 ? [{ id: 'hotels', label: `Hotels (${hotelItems.length})` }] : []),
  ];
});

// Set active tab to first tab when tabs change
watch(tabs, (newTabs) => {
  if (newTabs.length > 0 && !activeTab.value) activeTab.value = newTabs[0].id;
}, { immediate: true });

// --- Computed: Filtered Items by Tab ---
const filteredItems = computed(() => {
  if (!activeTab.value) return [];
  if (activeTab.value === 'hotels') return bookableItems.value.filter(item => item.isHotel);
  const dayKey = activeTab.value.replace('day-', '');
  return bookableItems.value.filter(item => !item.isHotel && normalizeDayDate(item.day_date) === dayKey).slice(0, 4);
});

// --- Receipt Computeds ---
const receiptSubtotal = computed(() => selectedItems.value.reduce((total, item) => {
  const people = formDataMap.value[item._key]?.amount_of_people || 1;
  return total + (item.estimated_cost || 0) * people;
}, 0));

const isDiscountEligible = computed(() => selectedItemsIds.value.size >= bookableItems.value.length * 0.5);
const selectedDiscount = computed(() => availableDiscounts.value.find(d => d.id === selectedDiscountId.value));
const receiptDiscountAmount = computed(() => isDiscountEligible.value ? receiptSubtotal.value * (selectedDiscount.value?.discount_percent || 0) : 0);
const receiptFinalTotal = computed(() => receiptSubtotal.value - receiptDiscountAmount.value);

// --- Watchers ---
watch(itinerary, (newItinerary) => {
  if (!newItinerary?.items) return;

  // Initialize form data for all items
  const newMap = {};
  for (const item of bookableItems.value) {
    newMap[item._key] = {
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
  const listingIds = [...new Set(items.map(item => item.listing_id).filter(Boolean))];
  if (listingIds.length === 0) return;

  // Set loading states
  servicesLoadingByListing.value = listingIds.reduce((acc, id) => { acc[id] = true; return acc; }, {});

  // Fetch services for all listings in parallel
  const results = await Promise.allSettled(listingIds.map(async (listingId) => {
    const response = await servicesAPI.getAll({ listing_id: listingId });
    return { listingId, services: Array.isArray(response.data) ? response.data : [] };
  }));

  // Process results
  const nextServices = {};
  for (const result of results) {
    if (result.status === 'fulfilled') {
      nextServices[result.value.listingId] = result.value.services;
    }
  }
  servicesByListing.value = nextServices;

  // Auto-select service if only one available
  const nextFormDataMap = { ...formDataMap.value };
  for (const item of items) {
    const availableServices = nextServices[item.listing_id] || [];
    const currentServiceId = nextFormDataMap[item._key]?.service_id;
    if (availableServices.length === 1) {
      nextFormDataMap[item._key] = { ...nextFormDataMap[item._key], service_id: availableServices[0].service_id };
    } else if (!availableServices.some(s => s.service_id === currentServiceId)) {
      nextFormDataMap[item._key] = { ...nextFormDataMap[item._key], service_id: null };
    }
  }
  formDataMap.value = nextFormDataMap;

  // Clear loading states
  const nextLoading = {};
  listingIds.forEach(id => { nextLoading[id] = false; });
  servicesLoadingByListing.value = nextLoading;
}, { immediate: true });

watch(formDataMap, (newMap) => {
  for (const [itemKey, formData] of Object.entries(newMap)) {
    const item = bookableItems.value.find(i => i._key === itemKey);
    if (!item) continue;
    const serviceId = formData?.service_id;
    const date = formData?.booking_from_time?.slice(0, 10);
    fetchAvailabilityForItem(itemKey, serviceId, date, formData?.amount_of_people || 1);
  }
}, { deep: true });

// --- Methods ---
async function fetchAvailabilityForItem(itemKey, serviceId, date, people) {
  if (!serviceId || !date) {
    serviceAvailability.value[itemKey] = null;
    return;
  }
  try {
    const response = await availabilityAPI.getServiceAvailability(serviceId, date, people);
    serviceAvailability.value[itemKey] = response.data;
  } catch {
    serviceAvailability.value[itemKey] = null;
  }
}

async function openReceiptModal() {
  if (!validateSelectedItems()) return;

  // Validate selected item cards
  for (const item of selectedItems.value) {
    const card = formCardRefs.value[item._key];
    if (card?.validate && !card.validate()) {
      toastStore.show('Please fix validation errors in the forms.', 'error');
      return;
    }
  }

  receiptDiscountLoading.value = true;
  try {
    const response = await discountsAPI.getPackageDiscounts();
    availableDiscounts.value = response.data || [];
    selectedDiscountId.value = availableDiscounts.value[0]?.id ?? null;
    showReceiptModal.value = true;
  } catch {
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
  if (!validateSelectedItems()) return;

  confirming.value = true;
  try {
    await Promise.all(selectedItems.value.map(item => {
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
    }));

    toastStore.show(`Confirmed ${selectedItems.value.length} bookings!`, 'success');
    showReceiptModal.value = false;
    router.back();
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