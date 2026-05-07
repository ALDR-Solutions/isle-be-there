<template>
  <div class="min-h-screen bg-slate-100 p-8">
    <div class="mx-auto max-w-6xl">
      <!-- Header -->
      <div class="mb-8 rounded-2xl bg-white p-6 shadow-sm">
        <h1 class="text-3xl font-bold text-slate-900">Booking API Mock Tester</h1>
        <p class="mt-2 text-slate-600">Test all booking endpoints with a visual interface</p>
        <div class="mt-4 flex gap-4">
          <span class="rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold text-blue-800">Vue 3</span>
          <span class="rounded-full bg-green-100 px-3 py-1 text-xs font-semibold text-green-800">Tailwind</span>
          <span class="rounded-full bg-purple-100 px-3 py-1 text-xs font-semibold text-purple-800">Axios</span>
        </div>
      </div>

      <!-- Tab Navigation -->
      <div class="mb-6 flex gap-2 rounded-2xl bg-white p-2 shadow-sm">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'flex-1 rounded-xl px-4 py-3 text-sm font-semibold transition',
            activeTab === tab.id
              ? 'bg-slate-900 text-white'
              : 'text-slate-600 hover:bg-slate-50'
          ]"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Alert Messages -->
      <div v-if="alert.message" class="mb-6 rounded-2xl p-4" :class="alert.type === 'error' ? 'bg-red-50 text-red-700 border border-red-200' : 'bg-green-50 text-green-700 border border-green-200'">
        <p class="font-medium">{{ alert.message }}</p>
      </div>

      <!-- Create Booking Tab -->
      <div v-if="activeTab === 'create'" class="rounded-2xl bg-white p-6 shadow-sm">
        <h2 class="mb-6 text-xl font-bold text-slate-900">Create New Booking</h2>
        <form @submit.prevent="handleCreateBooking" class="space-y-6">
          <div class="grid gap-6 md:grid-cols-2">
            <div>
              <label class="block text-sm font-semibold text-slate-700">Listing</label>
              <select v-model="createForm.listing_id" class="mt-2 w-full rounded-xl border border-slate-200 px-4 py-3 focus:border-slate-500 focus:outline-none">
                <option value="">-- Select a Listing --</option>
                <option v-for="listing in listings" :key="listing.id" :value="listing.id">
                  {{ listing.title }} ({{ listing.type }})
                </option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-semibold text-slate-700">Service</label>
              <select v-model="createForm.service_id" class="mt-2 w-full rounded-xl border border-slate-200 px-4 py-3 focus:border-slate-500 focus:outline-none">
                <option value="">-- Select a Service --</option>
                <option v-for="service in services" :key="service.service_id" :value="service.service_id">
                  {{ service.name }}
                </option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-semibold text-slate-700">Booker's Name</label>
              <input v-model="createForm.bookers_name" type="text" required placeholder="John Doe" class="mt-2 w-full rounded-xl border border-slate-200 px-4 py-3 focus:border-slate-500 focus:outline-none" />
            </div>
            <div>
              <label class="block text-sm font-semibold text-slate-700">Amount of People</label>
              <input v-model.number="createForm.amount_of_people" type="number" min="1" placeholder="2" class="mt-2 w-full rounded-xl border border-slate-200 px-4 py-3 focus:border-slate-500 focus:outline-none" />
            </div>
            <div>
              <label class="block text-sm font-semibold text-slate-700">Booking From</label>
              <input v-model="createForm.booking_from_time" type="datetime-local" class="mt-2 w-full rounded-xl border border-slate-200 px-4 py-3 focus:border-slate-500 focus:outline-none" />
            </div>
            <div>
              <label class="block text-sm font-semibold text-slate-700">Booking To</label>
              <input v-model="createForm.booking_to_time" type="datetime-local" class="mt-2 w-full rounded-xl border border-slate-200 px-4 py-3 focus:border-slate-500 focus:outline-none" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-semibold text-slate-700">Special Requests</label>
            <textarea v-model="createForm.special_requests" rows="3" placeholder="Any special requirements..." class="mt-2 w-full rounded-xl border border-slate-200 px-4 py-3 focus:border-slate-500 focus:outline-none"></textarea>
          </div>
          
          <button type="submit" :disabled="loading.create" class="rounded-xl bg-slate-900 px-6 py-3 font-semibold text-white transition hover:bg-slate-800 disabled:opacity-50">
            {{ loading.create ? 'Creating...' : 'Create Booking' }}
          </button>
        </form>
      </div>

      <!-- List Bookings Tab -->
      <div v-if="activeTab === 'list'" class="rounded-2xl bg-white p-6 shadow-sm">
        <div class="mb-6 flex items-center justify-between">
          <h2 class="text-xl font-bold text-slate-900">All Bookings</h2>
          <button @click="fetchBookings" :disabled="loading.list" class="rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:opacity-50">
            {{ loading.list ? 'Loading...' : 'Refresh' }}
          </button>
        </div>
        <div v-if="loading.list" class="py-12 text-center text-slate-500">Loading bookings...</div>
        <div v-else-if="bookings.length === 0" class="py-12 text-center text-slate-500">No bookings found</div>
        <div v-else class="space-y-4">
          <div v-for="booking in bookings" :key="booking.id" class="rounded-xl border border-slate-200 p-4 hover:bg-slate-50">
            <div class="flex items-center justify-between">
              <div>
                <p class="font-semibold text-slate-900">#{{ booking.id }}</p>
                <p class="text-sm text-slate-500">{{ booking.listing_name || 'No listing' }} / {{ booking.service_name || 'No service' }}</p>
              </div>
              <div class="flex items-center gap-3">
                <span :class="statusClasses(booking.status)" class="rounded-full px-3 py-1 text-xs font-semibold">
                  {{ booking.status }}
                </span>
                <button @click="selectBooking(booking)" class="rounded-xl bg-slate-100 px-3 py-1 text-sm font-semibold text-slate-700 hover:bg-slate-200">Edit</button>
                <button @click="confirmCancel(booking)" class="rounded-xl bg-red-50 px-3 py-1 text-sm font-semibold text-red-700 hover:bg-red-100">Cancel</button>
              </div>
            </div>
            <div class="mt-3 grid grid-cols-3 gap-4 text-sm">
              <div><span class="text-slate-400">Name:</span> {{ booking.bookers_name }}</div>
              <div><span class="text-slate-400">People:</span> {{ booking.amount_of_people }}</div>
              <div><span class="text-slate-400">From:</span> {{ formatDate(booking.booking_from_time) }}</div>
            </div>
            <div v-if="booking.final_price" class="mt-3 text-sm">
              <span class="text-slate-400">Price:</span> <span class="font-semibold text-slate-900">${{ booking.final_price }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Update Booking Tab -->
      <div v-if="activeTab === 'update'" class="rounded-2xl bg-white p-6 shadow-sm">
        <h2 class="mb-6 text-xl font-bold text-slate-900">Update Booking</h2>
        <div class="mb-6">
          <label class="block text-sm font-semibold text-slate-700">Booking ID</label>
          <input v-model="updateForm.id" type="text" placeholder="Enter booking ID" class="mt-2 w-full rounded-xl border border-slate-200 px-4 py-3 focus:border-slate-500 focus:outline-none" />
          <button @click="fetchBookingById" :disabled="loading.update" class="mt-3 rounded-xl bg-slate-700 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-600 disabled:opacity-50">
            Load Booking
          </button>
        </div>
        <div v-if="updateForm.id" class="space-y-6">
          <div class="grid gap-6 md:grid-cols-2">
            <div>
              <label class="block text-sm font-semibold text-slate-700">Booker's Name</label>
              <input v-model="updateForm.bookers_name" type="text" class="mt-2 w-full rounded-xl border border-slate-200 px-4 py-3 focus:border-slate-500 focus:outline-none" />
            </div>
            <div>
              <label class="block text-sm font-semibold text-slate-700">Amount of People</label>
              <input v-model.number="updateForm.amount_of_people" type="number" min="1" class="mt-2 w-full rounded-xl border border-slate-200 px-4 py-3 focus:border-slate-500 focus:outline-none" />
            </div>
            <div>
              <label class="block text-sm font-semibold text-slate-700">Booking From</label>
              <input v-model="updateForm.booking_from_time" type="datetime-local" class="mt-2 w-full rounded-xl border border-slate-200 px-4 py-3 focus:border-slate-500 focus:outline-none" />
            </div>
            <div>
              <label class="block text-sm font-semibold text-slate-700">Booking To</label>
              <input v-model="updateForm.booking_to_time" type="datetime-local" class="mt-2 w-full rounded-xl border border-slate-200 px-4 py-3 focus:border-slate-500 focus:outline-none" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-semibold text-slate-700">Special Requests</label>
            <textarea v-model="updateForm.special_requests" rows="3" class="mt-2 w-full rounded-xl border border-slate-200 px-4 py-3 focus:border-slate-500 focus:outline-none"></textarea>
          </div>
          <div>
            <label class="block text-sm font-semibold text-slate-700">Status</label>
            <select v-model="updateForm.status" class="mt-2 w-full rounded-xl border border-slate-200 px-4 py-3 focus:border-slate-500 focus:outline-none">
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="cancelled">Cancelled</option>
              <option value="completed">Completed</option>
            </select>
          </div>
          <button @click="handleUpdateBooking" :disabled="loading.update" class="rounded-xl bg-slate-900 px-6 py-3 font-semibold text-white transition hover:bg-slate-800 disabled:opacity-50">
            {{ loading.update ? 'Updating...' : 'Update Booking' }}
          </button>
        </div>
      </div>

      <!-- Get Price Tab -->
      <div v-if="activeTab === 'price'" class="rounded-2xl bg-white p-6 shadow-sm">
        <h2 class="mb-6 text-xl font-bold text-slate-900">Get Booking Price</h2>
        <div class="mb-6">
          <label class="block text-sm font-semibold text-slate-700">Booking ID</label>
          <div class="flex gap-3">
            <input v-model="priceForm.booking_id" type="text" placeholder="Enter booking ID" class="mt-2 flex-1 rounded-xl border border-slate-200 px-4 py-3 focus:border-slate-500 focus:outline-none" />
            <button @click="fetchBookingPrice" :disabled="loading.price" class="mt-2 rounded-xl bg-slate-900 px-6 py-3 font-semibold text-white transition hover:bg-slate-800 disabled:opacity-50">
              Get Price
            </button>
          </div>
        </div>
        <div v-if="priceData" class="rounded-xl border border-slate-200 p-6">
          <h3 class="mb-4 font-semibold text-slate-900">Price Breakdown</h3>
          <div class="space-y-3">
            <div class="flex justify-between"><span class="text-slate-600">Base Price</span><span class="font-semibold">${{ priceData.base_price?.toFixed(2) }}</span></div>
            <div class="flex justify-between"><span class="text-slate-600">Service Fee ({{ (priceData.service_fee_percent * 100)?.toFixed(1) }}%)</span><span class="font-semibold">${{ priceData.service_fee_amount?.toFixed(2) }}</span></div>
            <div class="flex justify-between"><span class="text-slate-600">Discount ({{ (priceData.discount_percent * 100)?.toFixed(1) }}%)</span><span class="font-semibold text-green-600">-${{ priceData.discount_amount?.toFixed(2) }}</span></div>
            <hr class="border-slate-200" />
            <div class="flex justify-between text-lg"><span class="font-semibold text-slate-900">Display Price</span><span class="font-semibold">${{ priceData.display_price?.toFixed(2) }}</span></div>
            <div class="flex justify-between text-xl"><span class="font-bold text-slate-900">Final Price</span><span class="font-bold text-green-600">${{ priceData.final_price?.toFixed(2) }}</span></div>
          </div>
        </div>
      </div>

      <!-- Raw Response Tab -->
      <div v-if="activeTab === 'response'" class="rounded-2xl bg-white p-6 shadow-sm">
        <h2 class="mb-6 text-xl font-bold text-slate-900">Raw API Response</h2>
        <pre class="overflow-auto rounded-xl bg-slate-900 p-4 text-sm text-green-400">{{ JSON.stringify(lastResponse, null, 2) }}</pre>
      </div>

      <!-- Cancel Confirmation Modal -->
      <div v-if="bookingToCancel" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 px-4">
        <div class="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
          <h3 class="text-lg font-bold text-slate-900">Cancel Booking?</h3>
          <p class="mt-2 text-sm text-slate-600">Booking #{{ bookingToCancel.id }} will be cancelled immediately.</p>
          <div class="mt-4 flex gap-3">
            <button @click="bookingToCancel = null" class="flex-1 rounded-xl border border-slate-200 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50">Keep</button>
            <button @click="handleCancelBooking" :disabled="cancelling" class="flex-1 rounded-xl bg-red-600 py-2 text-sm font-semibold text-white hover:bg-red-700 disabled:opacity-50">
              {{ cancelling ? 'Cancelling...' : 'Cancel Booking' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from "vue";
import { bookingsAPI, listingsAPI, servicesAPI } from "../services/api";
import { useToastStore } from "../stores/toast";

const toastStore = useToastStore();

const tabs = [
  { id: "create", label: "Create Booking" },
  { id: "list", label: "List Bookings" },
  { id: "update", label: "Update Booking" },
  { id: "price", label: "Get Price" },
  { id: "response", label: "Raw Response" }
];

const activeTab = ref("create");
const alert = reactive({ message: "", type: "" });
const bookings = ref([]);
const lastResponse = ref(null);

const loading = reactive({ create: false, list: false, update: false, price: false });
const cancelling = ref(false);
const bookingToCancel = ref(null);

const listings = ref([]);
const services = ref([]);

const createForm = reactive({
  listing_id: "",
  service_id: "",
  bookers_name: "",
  amount_of_people: 1,
  booking_from_time: "",
  booking_to_time: "",
  special_requests: ""
});

const updateForm = reactive({
  id: "",
  bookers_name: "",
  amount_of_people: 1,
  booking_from_time: "",
  booking_to_time: "",
  special_requests: "",
  status: "pending"
});

const priceForm = reactive({ booking_id: "" });
const priceData = ref(null);

// When listing is selected, fetch its services
watch(() => createForm.listing_id, async (newListingId) => {
  if (newListingId) {
    try {
      const response = await servicesAPI.getAll({ listing_id: newListingId });
      services.value = response.data;
    } catch (err) {
      console.error("Failed to load services for listing:", err);
      services.value = [];
    }
  } else {
    services.value = [];
  }
  createForm.service_id = ""; // Reset service selection
});

function showAlert(message, type = "success") {
  alert.message = message;
  alert.type = type;
  setTimeout(() => { alert.message = ""; }, 4000);
}

function formatDate(dateStr) {
  if (!dateStr) return "N/A";
  return new Date(dateStr).toLocaleString();
}

function statusClasses(status) {
  const classes = {
    pending: "bg-amber-100 text-amber-800",
    approved: "bg-emerald-100 text-emerald-800",
    cancelled: "bg-red-100 text-red-800",
    completed: "bg-cyan-100 text-cyan-800"
  };
  return classes[status] || "bg-slate-100 text-slate-700";
}

async function handleCreateBooking() {
  loading.create = true;
  try {
    const payload = { ...createForm };
    // Remove empty fields
    Object.keys(payload).forEach(key => {
      if (payload[key] === "" || payload[key] === null) delete payload[key];
    });
    // Convert datetime-local to ISO
    if (payload.booking_from_time) {
      payload.booking_from_time = new Date(payload.booking_from_time).toISOString();
    }
    if (payload.booking_to_time) {
      payload.booking_to_time = new Date(payload.booking_to_time).toISOString();
    }
    const response = await bookingsAPI.create(payload);
    lastResponse.value = response.data;
    showAlert(`Booking created: ${response.data.id}`);
    // Reset form
    Object.keys(createForm).forEach(key => {
      if (key === "amount_of_people") createForm[key] = 1;
      else createForm[key] = "";
    });
    activeTab.value = "response";
  } catch (err) {
    showAlert(err.response?.data?.detail || "Failed to create booking", "error");
    lastResponse.value = err.response?.data;
  } finally {
    loading.create = false;
  }
}

async function fetchBookings() {
  loading.list = true;
  try {
    const response = await bookingsAPI.getAll();
    bookings.value = response.data;
    lastResponse.value = response.data;
  } catch (err) {
    showAlert("Failed to fetch bookings", "error");
    lastResponse.value = err.response?.data;
  } finally {
    loading.list = false;
  }
}

async function fetchBookingById() {
  if (!updateForm.id) return;
  loading.update = true;
  try {
    const response = await bookingsAPI.getById(updateForm.id);
    const b = response.data;
    updateForm.bookers_name = b.bookers_name || "";
    updateForm.amount_of_people = b.amount_of_people || 1;
    updateForm.booking_from_time = b.booking_from_time ? new Date(b.booking_from_time).toISOString().slice(0, 16) : "";
    updateForm.booking_to_time = b.booking_to_time ? new Date(b.booking_to_time).toISOString().slice(0, 16) : "";
    updateForm.special_requests = b.special_requests || "";
    updateForm.status = b.status || "pending";
    lastResponse.value = b;
  } catch (err) {
    showAlert("Failed to fetch booking", "error");
    lastResponse.value = err.response?.data;
  } finally {
    loading.update = false;
  }
}

async function handleUpdateBooking() {
  if (!updateForm.id) return;
  loading.update = true;
  try {
    const payload = { ...updateForm };
    delete payload.id;
    if (payload.booking_from_time) {
      payload.booking_from_time = new Date(payload.booking_from_time).toISOString();
    }
    if (payload.booking_to_time) {
      payload.booking_to_time = new Date(payload.booking_to_time).toISOString();
    }
    const response = await bookingsAPI.update(updateForm.id, payload);
    lastResponse.value = response.data;
    showAlert("Booking updated successfully");
    await fetchBookings();
  } catch (err) {
    showAlert(err.response?.data?.detail || "Failed to update booking", "error");
    lastResponse.value = err.response?.data;
  } finally {
    loading.update = false;
  }
}

function selectBooking(booking) {
  updateForm.id = booking.id;
  activeTab.value = "update";
  fetchBookingById();
}

function confirmCancel(booking) {
  bookingToCancel.value = booking;
}

async function handleCancelBooking() {
  if (!bookingToCancel.value) return;
  cancelling.value = true;
  try {
    await bookingsAPI.cancel(bookingToCancel.value.id);
    showAlert("Booking cancelled successfully");
    bookingToCancel.value = null;
    await fetchBookings();
  } catch (err) {
    showAlert(err.response?.data?.detail || "Failed to cancel booking", "error");
  } finally {
    cancelling.value = false;
  }
}

async function fetchBookingPrice() {
  if (!priceForm.booking_id) return;
  loading.price = true;
  try {
    const response = await fetch(`http://localhost:8000/api/bookings/${priceForm.booking_id}/price`, {
      headers: { Authorization: `Bearer ${localStorage.getItem("access_token") || ""}` }
    });
    priceData.value = await response.json();
    lastResponse.value = priceData.value;
  } catch (err) {
    showAlert("Failed to fetch price", "error");
    lastResponse.value = err;
  } finally {
    loading.price = false;
  }
}

// Load bookings on mount if tab is list
if (activeTab.value === "list") {
  fetchBookings();
}

// Fetch listings on mount (services are fetched when listing is selected)
onMounted(async () => {
  try {
    const listingsRes = await listingsAPI.getAll({ limit: 100 });
    listings.value = listingsRes.data;
  } catch (err) {
    console.error("Failed to load listings:", err);
  }
});
</script>