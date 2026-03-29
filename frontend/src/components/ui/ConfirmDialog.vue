<template>
  <BaseDialog
    :model-value="modelValue"
    :title="title"
    :description="description"
    :eyebrow="eyebrow"
    @update:modelValue="emit('update:modelValue', $event)"
  >
    <template #footer>
      <div class="flex gap-3">
        <button
          type="button"
          class="flex-1 rounded-2xl border border-slate-200 bg-white py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
          @click="emit('update:modelValue', false)"
        >
          {{ cancelLabel }}
        </button>
        <button
          type="button"
          class="flex-1 rounded-2xl py-3 text-sm font-semibold text-white transition"
          :class="confirmToneClass"
          :disabled="loading"
          @click="emit('confirm')"
        >
          {{ loading ? loadingLabel : confirmLabel }}
        </button>
      </div>
    </template>
  </BaseDialog>
</template>

<script setup>
import { computed } from 'vue'
import BaseDialog from '@/components/ui/BaseDialog.vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  eyebrow: {
    type: String,
    default: '',
  },
  title: {
    type: String,
    required: true,
  },
  description: {
    type: String,
    default: '',
  },
  confirmLabel: {
    type: String,
    default: 'Confirm',
  },
  cancelLabel: {
    type: String,
    default: 'Cancel',
  },
  loadingLabel: {
    type: String,
    default: 'Working...',
  },
  tone: {
    type: String,
    default: 'danger',
  },
  loading: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue', 'confirm'])

const confirmToneClass = computed(() => {
  if (props.tone === 'success') return 'bg-emerald-500 hover:bg-emerald-400 disabled:bg-emerald-300'
  return 'bg-red-500 hover:bg-red-400 disabled:bg-red-300'
})
</script>
