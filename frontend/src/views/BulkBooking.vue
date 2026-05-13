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

      <div v-else class="grid gap-6">
        <template v-for="(item, index) in filteredItems" :key="item._key">
          <HotelBookingFormCard
            v-if="item.isHotel"
            :ref="el => { if (el) formCardRefs[item._key] = el }"
            :item="item"
            :modelValue="formDataMap[item._key]"
            @update:modelValue="val => formDataMap[item._key] = val"
          />
          <BookingFormCard
            v-else
            :ref="el => { if (el) formCardRefs[item._key] = el }"
            :item="item"
            :modelValue="formDataMap[item._key]"
            @update:modelValue="val => formDataMap[item._key] = val"
          />
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
            :disabled="confirming"
            class="rounded-2xl bg-cyan-600 px-6 py-3 text-sm font-semibold text-white transition hover:bg-cyan-700 disabled:opacity-60"
          >
            {{ confirming ? 'Processing...' : 'Review & Book' }}
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
import { itinerariesAPI, bookingsAPI, discountsAPI } from '../services/api';
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

const itineraryTitle = computed(() => {
  return itinerary.value?.title || 'Your Itinerary';
});

// Items that are checked/selected (have valid form data)
const selectedItems = computed(() => {
  return bookableItems.value.filter(item => {
    const form = formDataMap.value[item._key];
    return form && form.bookers_name && form.amount_of_people >= 1;
  });
});

const selectedCount = computed(() => selectedItems.value.length);

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
        bookers_name: capitalizedName,
        amount_of_people: 1,
        special_requests: '',
        booking_from_time: item.check_in_date ? `${item.check_in_date}T14:00:00` : null,
        booking_to_time: item.check_out_date ? `${item.check_out_date}T11:00:00` : null,
      };
    } else {
      // Regular item: use start_at/end_at
      newMap[item._key] = {
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

async function handleConfirmBooking() {
  confirming.value = true;
  try {
    // Create bookings for each selected item
    const bookingPromises = selectedItems.value.map((item) => {
      const formData = formDataMap.value[item._key];
      return bookingsAPI.create({
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
    toastStore.show('Booking failed. Please try again.', 'error');
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