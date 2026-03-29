<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <div class="flex justify-between items-start">
      <div class="flex items-center">
        <div class="h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center">
          <span class="text-indigo-600 font-bold">{{ getInitial(review.user?.username) }}</span>
        </div>
        <div class="ml-3">
          <p class="text-sm font-medium text-gray-900">{{ review.user?.username || 'Anonymous' }}</p>
          <p class="text-sm text-gray-500">{{ formatDate(review.created_at) }}</p>
        </div>
      </div>
      <div class="flex items-center">
        <svg 
          v-for="i in 5" 
          :key="i"
          class="h-5 w-5"
          :class="i <= review.rating ? 'text-yellow-400' : 'text-gray-300'"
          fill="currentColor" 
          viewBox="0 0 20 20"
        >
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1.5 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1.5 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1.5 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1.5 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1.5 0 00.951-.69l1.07-3.292z" />
        </svg>
      </div>
    </div>
    <p v-if="review.comment" class="mt-4 text-gray-600">{{ review.comment }}</p>
  </div>
</template>

<script setup>
defineProps({
  review: {
    type: Object,
    required: true
  }
});

const getInitial = (name) => {
  return name ? name.charAt(0).toUpperCase() : '?';
};

const formatDate = (date) => {
  return new Date(date).toLocaleDateString();
};
</script>
