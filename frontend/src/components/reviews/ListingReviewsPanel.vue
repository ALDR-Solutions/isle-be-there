<template>
  <div>
    <div
      v-if="showFilters && !reviewsLoading && !reviewsError && reviews.length > 0"
      class="mt-4 flex flex-wrap gap-4"
    >
      <select
        v-model="reviewFilters.rating"
        class="rounded-lg border border-slate-200 px-3 py-2 text-sm"
      >
        <option :value="null">All Ratings</option>
        <option v-for="n in 5" :key="n" :value="n">
          {{ n }} star{{ n > 1 ? 's' : '' }}
        </option>
      </select>
      <select
        v-model="reviewFilters.mainLabel"
        class="rounded-lg border border-slate-200 px-3 py-2 text-sm"
      >
        <option :value="null">All Categories</option>
        <option v-for="label in availableLabels" :key="label" :value="label">
          {{ label }}
        </option>
      </select>
    </div>

    <div
      v-if="reviewsLoading"
      class="mt-6 rounded-3xl border border-slate-200 bg-white px-6 py-12 text-center shadow-sm"
    >
      <p class="text-base font-medium text-slate-500">Loading reviews...</p>
      <p class="mt-1 text-sm text-slate-400">{{ loadingSubtext }}</p>
    </div>

    <div
      v-else-if="reviewsError"
      class="mt-6 rounded-3xl border border-rose-200 bg-white px-6 py-12 text-center shadow-sm"
    >
      <p class="text-base font-medium text-slate-700">{{ reviewsError }}</p>
      <p class="mt-1 text-sm text-slate-400">Please try refreshing the page in a moment.</p>
    </div>

    <div
      v-else-if="reviews.length === 0"
      class="mt-6 rounded-3xl border border-slate-200 bg-white px-6 py-12 text-center shadow-sm"
    >
      <p class="text-base font-medium text-slate-500">{{ emptyTitle }}</p>
      <p class="mt-1 text-sm text-slate-400">{{ emptySubtext }}</p>
    </div>

    <div v-else class="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
      <div
        v-for="review in filteredReviews"
        :key="review.id"
        class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
      >
        <div class="flex items-start justify-between gap-4">
          <div class="flex items-center gap-3">
            <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-cyan-50 text-sm font-bold text-cyan-700">
              {{ review.user_name?.charAt(0).toUpperCase() || 'G' }}
            </div>
            <div>
              <p class="text-sm font-semibold text-slate-900">{{ review.user_name || 'Guest' }}</p>
              <p class="text-xs text-slate-400">{{ formatReviewDate(review.created_at) }}</p>
            </div>
          </div>
          <div class="flex shrink-0">
            <svg
              v-for="i in 5"
              :key="i"
              class="h-4 w-4"
              :class="i <= review.rating ? 'text-amber-400' : 'text-slate-200'"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
          </div>
        </div>

        <div v-if="review.main_label && review.main_label !== '(none)'" class="mt-3">
          <span class="inline-flex items-center rounded-full bg-cyan-100 px-2.5 py-0.5 text-xs font-medium text-cyan-800">
            {{ review.main_label }}
          </span>
        </div>

        <p v-if="getPublicReviewComment(review)" class="mt-3 text-sm leading-6 text-slate-600">
          {{ getPublicReviewComment(review) }}
        </p>

        <div
          v-if="review.business_reply"
          class="mt-4 rounded-lg border border-slate-100 bg-slate-50 p-4"
        >
          <div class="mb-2 flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-cyan-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
            <span class="text-xs font-semibold uppercase tracking-wider text-slate-500">Business Response</span>
          </div>
          <p class="text-sm text-slate-700">{{ review.business_reply.description }}</p>
          <p class="mt-2 text-xs text-slate-400">- {{ review.business_reply.user_name || 'Business' }}</p>
          <div v-if="canManageReply" class="mt-3 flex gap-3 border-t border-slate-200 pt-3">
            <button @click="openEditReplyModal(review)" class="text-xs text-cyan-600 hover:text-cyan-700">Edit</button>
            <button @click="confirmDeleteReply(review)" class="text-xs text-red-600 hover:text-red-700">Delete</button>
          </div>
        </div>

        <div v-else-if="canReply" class="mt-4">
          <button @click="openReplyModal(review)" class="text-sm text-cyan-600 hover:text-cyan-700">
            Respond as Business
          </button>
        </div>

        <slot name="review-actions" :review="review" />
      </div>
    </div>

    <BusinessReplyModal
      v-if="showReplyModal"
      :mode="editingReply ? 'edit' : 'submit'"
      :review-id="replyingToReview?.id"
      :reply="editingReply"
      @close="showReplyModal = false"
      @success="handleReplySuccess"
    />
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import BusinessReplyModal from '../BusinessReplyModal.vue'
import { businessReplyAPI, reviewsAPI } from '../../services/api'
import { useToastStore } from '../../stores/toast'
import { getPublicReviewComment } from '../../utils/reviews'

const props = defineProps({
  listingId: {
    type: [String, Number],
    default: null,
  },
  canReply: {
    type: Boolean,
    default: false,
  },
  canManageReply: {
    type: Boolean,
    default: false,
  },
  showFilters: {
    type: Boolean,
    default: true,
  },
  emptyTitle: {
    type: String,
    default: 'No reviews yet.',
  },
  emptySubtext: {
    type: String,
    default: 'Guest feedback for this listing will appear here.',
  },
  loadingSubtext: {
    type: String,
    default: 'Guest feedback is on the way.',
  },
})

const toastStore = useToastStore()
const reviews = ref([])
const reviewsLoading = ref(false)
const reviewsError = ref('')
const reviewFilters = ref({ rating: null, mainLabel: null })
const showReplyModal = ref(false)
const editingReply = ref(null)
const replyingToReview = ref(null)
let activeReviewsRequestId = 0

const filteredReviews = computed(() => {
  let result = reviews.value
  if (reviewFilters.value.rating) {
    result = result.filter((review) => review.rating === reviewFilters.value.rating)
  }
  if (reviewFilters.value.mainLabel) {
    result = result.filter((review) => review.main_label === reviewFilters.value.mainLabel)
  }
  return result
})

const availableLabels = computed(() => {
  const labels = reviews.value.map((review) => review.main_label).filter(Boolean)
  return [...new Set(labels)]
})

function formatReviewDate(date) {
  return new Date(date).toLocaleDateString()
}

async function refreshReviews() {
  const listingId = props.listingId
  activeReviewsRequestId += 1
  const requestId = activeReviewsRequestId

  if (!listingId) {
    reviews.value = []
    reviewsError.value = ''
    reviewsLoading.value = false
    return []
  }

  reviewsLoading.value = true
  reviewsError.value = ''

  try {
    const response = await reviewsAPI.getAll({ listing_id: listingId })
    if (requestId !== activeReviewsRequestId) {
      return []
    }

    reviews.value = Array.isArray(response.data) ? response.data : []
    return reviews.value
  } catch (error) {
    if (requestId !== activeReviewsRequestId) {
      return []
    }

    reviews.value = []
    reviewsError.value = 'Failed to load reviews for this listing.'
    console.error('Failed to load reviews', error)
    return []
  } finally {
    if (requestId === activeReviewsRequestId) {
      reviewsLoading.value = false
    }
  }
}

function openReplyModal(review) {
  if (!props.canReply) {
    toastStore.show('You are not assigned to respond to reviews for this listing.', 'error')
    return
  }

  replyingToReview.value = review
  editingReply.value = null
  showReplyModal.value = true
}

function openEditReplyModal(review) {
  if (!props.canManageReply) {
    toastStore.show('You are not assigned to manage responses for this listing.', 'error')
    return
  }

  replyingToReview.value = review
  editingReply.value = review.business_reply
  showReplyModal.value = true
}

function handleReplySuccess(message) {
  showReplyModal.value = false
  toastStore.show(message, 'success')
  refreshReviews()
}

async function confirmDeleteReply(review) {
  if (!props.canManageReply) {
    toastStore.show('You are not assigned to manage responses for this listing.', 'error')
    return
  }

  if (confirm('Are you sure you want to delete your response?')) {
    try {
      await businessReplyAPI.delete(review.id)
      toastStore.show('Response deleted', 'success')
      refreshReviews()
    } catch (error) {
      console.error('Failed to delete reply:', error)
      toastStore.show('Failed to delete response', 'error')
    }
  }
}

watch(
  () => props.listingId,
  () => {
    reviewFilters.value = { rating: null, mainLabel: null }
    refreshReviews()
  },
  { immediate: true },
)

defineExpose({
  refreshReviews,
})
</script>
