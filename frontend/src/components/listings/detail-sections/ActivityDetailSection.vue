<template>
  <div class="rounded-2xl border border-slate-200 bg-white p-6">
    <h2 class="mb-4 text-lg font-bold text-slate-900">Activity Details</h2>

    <div class="space-y-4">
      <div v-if="details.estimated_duration" class="flex items-center gap-3">
        <span class="w-36 text-sm text-slate-500">Duration</span>
        <span class="text-sm font-medium text-slate-800">
          {{ details.estimated_duration }} {{ details.estimated_duration === 1 ? 'hour' : 'hours' }}
        </span>
      </div>

      <div v-if="details.difficulty_level" class="flex items-center gap-3">
        <span class="w-36 text-sm text-slate-500">Difficulty</span>
        <span class="rounded-full px-2.5 py-0.5 text-xs font-medium" :class="difficultyClass">
          {{ details.difficulty_level }}
        </span>
      </div>

      <div v-if="details.is_indoor != null" class="flex items-center gap-3">
        <span class="w-36 text-sm text-slate-500">Setting</span>
        <span class="text-sm font-medium text-slate-800">
          {{ details.is_indoor ? 'Indoor' : 'Outdoor' }}
        </span>
      </div>

      <div v-if="details.available_days?.length" class="flex items-start gap-3">
        <span class="w-36 shrink-0 text-sm text-slate-500">Available days</span>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="day in details.available_days"
            :key="day"
            class="rounded-full bg-violet-50 px-2.5 py-0.5 text-xs font-medium text-violet-700"
          >
            {{ day }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  details: {
    type: Object,
    default: () => ({}),
  },
})

const difficultyClass = computed(() => {
  switch (props.details.difficulty_level?.toLowerCase()) {
    case 'beginner':     return 'bg-emerald-50 text-emerald-700'
    case 'intermediate': return 'bg-amber-50 text-amber-700'
    case 'expert':       return 'bg-red-50 text-red-600'
    default:             return 'bg-slate-100 text-slate-600'
  }
})
</script>
