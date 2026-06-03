<template>
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 px-4 backdrop-blur-sm"
    @click.self="handleBackdropClick"
  >
    <div class="relative flex w-full max-w-md flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl">
      <div class="flex items-start justify-between border-b border-slate-200 px-6 py-5">
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.28em] text-cyan-600">
            {{ mode === 'submit' ? 'Share your experience' : 'Edit your review' }}
          </p>
          <h3 class="mt-2 text-xl font-bold text-slate-900">
            {{ mode === 'submit' ? 'Write a Review' : 'Edit Review' }}
          </h3>
        </div>

        <button
          @click="handleClose"
          class="rounded-xl p-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div class="px-6 py-6">
        <div class="mb-4">
          <p class="text-sm font-medium text-slate-700">Your Rating</p>
          <div class="mt-2 flex items-center gap-1">
            <button
              v-for="i in 5"
              :key="i"
              @click="setRating(i)"
              class="p-1 transition hover:scale-110"
              :disabled="submitting"
            >
              <svg
                class="h-8 w-8 transition-colors"
                :class="i <= rating ? 'text-amber-400' : 'text-slate-200'"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
              </svg>
            </button>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700">Your Review</label>
          <textarea
            v-model="comment"
            placeholder="Share your experience at this place..."
            maxlength="5000"
            rows="4"
            class="mt-2 w-full resize-none rounded-xl border border-slate-200 p-3 text-sm placeholder:text-slate-400 focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/20"
            :disabled="submitting"
          ></textarea>
          <p class="mt-1 text-xs text-slate-400">{{ comment.length }}/5000</p>
        </div>
      </div>

      <div class="flex items-center justify-end gap-3 border-t border-slate-200 bg-slate-50 px-6 py-4">
        <button
          @click="handleClose"
          :disabled="submitting"
          class="rounded-xl border border-slate-200 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 disabled:opacity-50"
        >
          Cancel
        </button>
        <button
          @click="submit"
          :disabled="submitting || !rating"
          class="rounded-xl bg-cyan-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-cyan-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <span v-if="submitting">Saving...</span>
          <span v-else>{{ mode === 'submit' ? 'Submit Review' : 'Save Changes' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { reviewsAPI } from '../services/api';
import { useToastStore } from '../stores/toast';

const props = defineProps({
  mode: {
    type: String,
    required: true,
    validator: (v) => ['submit', 'edit'].includes(v)
  },
  review: {
    type: Object,
    default: null
  },
  listingId: {
    type: String,
    required: true
  }
});

const emit = defineEmits(['close', 'success']);

const toastStore = useToastStore();
const rating = ref(props.review?.rating || 0);
const comment = ref(props.review?.comment || '');
const submitting = ref(false);

watch(() => props.review, (newReview) => {
  if (newReview) {
    rating.value = newReview.rating || 0;
    comment.value = newReview.comment || '';
  }
}, { immediate: true });

function setRating(n) {
  rating.value = n;
}

async function submit() {
  if (!rating.value) {
    toastStore.show('Please select a rating', 'error');
    return;
  }

  submitting.value = true;

  try {
    if (props.mode === 'submit') {
      const formData = new FormData();
      formData.append('listing_id', props.listingId);
      formData.append('rating', rating.value);
      formData.append('comment', comment.value);
      await reviewsAPI.create(formData);
      emit('success', 'Review submitted successfully');
    } else {
      const formData = new FormData();
      formData.append('rating', rating.value);
      formData.append('comment', comment.value);
      await reviewsAPI.update(props.review.id, formData);
      emit('success', 'Review updated successfully');
    }
  } catch (err) {
    console.error('Failed to save review:', err);
    toastStore.show('Failed to save review. Please try again.', 'error');
  } finally {
    submitting.value = false;
  }
}

function handleClose() {
  emit('close');
}

function handleBackdropClick() {
  emit('close');
}
</script>