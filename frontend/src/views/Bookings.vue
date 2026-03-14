<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <h1 class="text-3xl font-bold text-gray-900 mb-8">My Bookings</h1>
    
    <div v-if="loading" class="text-center py-8">
      <p class="text-gray-500">Loading bookings...</p>
    </div>
    
    <div v-else-if="bookings.length === 0" class="text-center py-8">
      <p class="text-gray-500">No bookings yet.</p>
      <router-link to="/listings" class="text-indigo-600 hover:text-indigo-500 mt-2 inline-block">
        Browse listings
      </router-link>
    </div>
    
    <div v-else class="space-y-4">
      <div v-for="booking in bookings" :key="booking.id" class="bg-white rounded-lg shadow-md p-6">
        <div class="flex justify-between items-start">
          <div>
            <h3 class="text-lg font-semibold">Booking #{{ booking.id }}</h3>
            <p class="text-gray-600">Service ID: {{ booking.service_id }}</p>
          </div>
          <span 
            :class="{
              'bg-yellow-100 text-yellow-800': booking.status === 'pending',
              'bg-green-100 text-green-800': booking.status === 'confirmed',
              'bg-red-100 text-red-800': booking.status === 'cancelled',
              'bg-blue-100 text-blue-800': booking.status === 'completed'
            }"
            class="px-3 py-1 rounded-full text-sm font-medium"
          >
            {{ booking.status }}
          </span>
        </div>
        
        <div class="mt-4">
          <p class="text-sm text-gray-500">Booking Time</p>
          <p class="font-medium">{{ formatDate(booking.booking_time) }}</p>
        </div>
        
        <div class="mt-4 flex justify-between items-center">
          <button 
            v-if="booking.status === 'pending'"
            @click="cancelBooking(booking.id)"
            class="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { bookingsAPI } from '../services/api';

const bookings = ref([]);
const loading = ref(true);
const error = ref('');

const fetchBookings = async () => {
  try {
    const response = await bookingsAPI.getAll();
    bookings.value = response.data;
  } catch (err) {
    error.value = 'Failed to load bookings';
  } finally {
    loading.value = false;
  }
};

const cancelBooking = async (id) => {
  if (!confirm('Are you sure you want to cancel this booking?')) return;
  
  try {
    await bookingsAPI.cancel(id);
    await fetchBookings();
  } catch (err) {
    error.value = 'Failed to cancel booking';
  }
};

const formatDate = (date) => {
  return new Date(date).toLocaleDateString();
};

onMounted(() => {
  fetchBookings();
});
</script>
