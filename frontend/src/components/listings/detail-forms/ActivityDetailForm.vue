<template>
  <div class="space-y-5 rounded-2xl border border-slate-200 bg-slate-50 p-6">
    <p class="text-sm font-semibold uppercase tracking-[0.2em] text-cyan-600">Activity Details</p>
    <div>
      <label class="block text-sm font-semibold text-slate-700 mb-1.5">Estimated Duration (hours)</label>
      <input
        :value="modelValue.estimated_duration ?? ''"
        @input="update('estimated_duration', $event.target.value ? Number($event.target.value) : null)"
        type="number" min="0" step="0.5" placeholder="e.g. 2"
        class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400"
      />
    </div>
    <div>
      <label class="block text-sm font-semibold text-slate-700 mb-2">Difficulty Level</label>
      <div class="flex gap-3">
        <button
          v-for="level in difficultyLevels"
          :key="level.value"
          type="button"
          @click="update('difficulty_level', level.value)"
          class="flex-1 rounded-2xl border py-2.5 text-xs font-semibold transition"
          :class="modelValue.difficulty_level === level.value ? level.activeClass : 'border-slate-200 bg-white text-slate-500 hover:border-slate-300'"
        >{{ level.label }}</button>
      </div>
    </div>
    <div>
      <label class="block text-sm font-semibold text-slate-700 mb-2">Setting</label>
      <div class="flex gap-3">
        <button
          type="button"
          @click="update('is_indoor', true)"
          class="flex-1 rounded-2xl border py-2.5 text-xs font-semibold transition"
          :class="modelValue.is_indoor === true ? 'border-cyan-400 bg-cyan-50 text-cyan-700' : 'border-slate-200 bg-white text-slate-500 hover:border-slate-300'"
        >Indoor</button>
        <button
          type="button"
          @click="update('is_indoor', false)"
          class="flex-1 rounded-2xl border py-2.5 text-xs font-semibold transition"
          :class="modelValue.is_indoor === false ? 'border-cyan-400 bg-cyan-50 text-cyan-700' : 'border-slate-200 bg-white text-slate-500 hover:border-slate-300'"
        >Outdoor</button>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  modelValue: { type: Object, default: () => ({}) },
  listingId: { type: String, default: null },
})
const emit = defineEmits(['update:modelValue'])

function update(key, value) {
  emit('update:modelValue', { ...props.modelValue, [key]: value })
}

const difficultyLevels = [
  { value: 'beginner',     label: 'Beginner',     activeClass: 'border-emerald-400 bg-emerald-50 text-emerald-700' },
  { value: 'intermediate', label: 'Intermediate', activeClass: 'border-amber-400 bg-amber-50 text-amber-700' },
  { value: 'expert',       label: 'Expert',       activeClass: 'border-red-300 bg-red-50 text-red-600' },
]
</script>
