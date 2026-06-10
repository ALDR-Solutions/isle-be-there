<template>
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 px-4 backdrop-blur-sm"
    @click.self="handleBackdropClick"
  >
    <div class="relative flex w-full max-w-md flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl">
      <div class="flex items-start justify-between border-b border-slate-200 px-6 py-5">
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.28em] text-cyan-600">
            {{ mode === 'submit' ? 'Respond to review' : 'Edit your response' }}
          </p>
          <h3 class="mt-2 text-xl font-bold text-slate-900">
            {{ mode === 'submit' ? 'Business Reply' : 'Edit Reply' }}
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
        <div>
          <label class="block text-sm font-medium text-slate-700">Your Response</label>
          <textarea
            v-model="description"
            placeholder="Thank you for your feedback..."
            maxlength="2000"
            rows="4"
            class="mt-2 w-full resize-none rounded-xl border border-slate-200 p-3 text-sm placeholder:text-slate-400 focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/20"
            :disabled="submitting"
          ></textarea>
          <p class="mt-1 text-xs text-slate-400">{{ description.length }}/2000</p>
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
          :disabled="submitting || !description.trim()"
          class="rounded-xl bg-cyan-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-cyan-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <span v-if="submitting">Saving...</span>
          <span v-else>{{ mode === 'submit' ? 'Submit Reply' : 'Save Changes' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { businessReplyAPI } from '../services/api';
import { useToastStore } from '../stores/toast';

const props = defineProps({
  mode: {
    type: String,
    required: true,
    validator: (v) => ['submit', 'edit'].includes(v)
  },
  reviewId: {
    type: String,
    required: true
  },
  reply: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['close', 'success']);

const toastStore = useToastStore();
const description = ref(props.reply?.description || '');
const submitting = ref(false);

watch(() => props.reply, (newReply) => {
  description.value = newReply?.description || '';
}, { immediate: true });

async function submit() {
  if (!description.value.trim()) {
    toastStore.show('Please enter a response', 'error');
    return;
  }

  submitting.value = true;

  try {
    const formData = new FormData();
    formData.append('description', description.value);

    if (props.mode === 'submit') {
      await businessReplyAPI.create(props.reviewId, formData);
      emit('success', 'Response submitted successfully');
    } else {
      await businessReplyAPI.update(props.reviewId, formData);
      emit('success', 'Response updated successfully');
    }
  } catch (err) {
    console.error('Failed to save reply:', err);
    toastStore.show('Failed to save response. Please try again.', 'error');
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
