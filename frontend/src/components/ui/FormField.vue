<template>
  <div>
    <div class="mb-2 flex items-center justify-between gap-4">
      <label :for="forId" class="block text-sm font-medium text-slate-700">
        {{ label }}
        <span v-if="required" class="text-red-500">*</span>
      </label>
      <span v-if="helpText" class="text-xs text-slate-400">{{ helpText }}</span>
    </div>

    <slot />

    <p v-if="error" class="mt-2 text-sm text-red-600">{{ error }}</p>
  </div>
</template>

<script setup>
defineProps({
  forId: {
    type: String,
    default: '',
  },
  label: {
    type: String,
    required: true,
  },
  error: {
    type: String,
    default: '',
  },
  helpText: {
    type: String,
    default: '',
  },
  required: {
    type: Boolean,
    default: false,
  },
})
</script>
