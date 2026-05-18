<template>
  <div class="space-y-4">
    <div v-if="loading" class="flex items-center justify-center py-4">
      <div class="h-5 w-5 animate-spin rounded-full border-2 border-cyan-400 border-t-transparent"></div>
    </div>

    <template v-else>
      <!-- Day Tabs -->
      <div class="flex gap-1 flex-wrap">
        <button
          v-for="day in days"
          :key="day.num"
          type="button"
          @click="selectedDay = day.num"
          class="rounded-lg px-3 py-1.5 text-xs font-semibold transition border"
          :class="selectedDay === day.num
            ? 'border-cyan-400 bg-cyan-50 text-cyan-700'
            : 'border-slate-200 bg-white text-slate-500 hover:border-slate-300'"
        >
          {{ day.name }}
          <span v-if="getHours(day.num)" class="ml-1 text-[10px] opacity-70">●</span>
        </button>
      </div>

      <!-- Hours for selected day -->
      <div v-if="selectedDay !== null" class="rounded-lg border border-slate-200 bg-slate-50 p-4 space-y-3">
        <div class="flex items-center justify-between">
          <span class="text-sm font-medium text-slate-700">
            {{ days.find(d => d.num === selectedDay)?.name }} Hours
          </span>
          <button
            v-if="getHours(selectedDay)"
            type="button"
            @click="setClosed"
            class="text-xs text-red-500 hover:text-red-600"
          >
            Mark as Closed
          </button>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-xs text-slate-500 mb-1">Open Time</label>
            <input
              type="time"
              v-model="editorOpenTime"
              class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-cyan-400 focus:outline-none"
              step="300"
            />
          </div>
          <div>
            <label class="block text-xs text-slate-500 mb-1">Close Time</label>
            <input
              type="time"
              v-model="editorCloseTime"
              class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-cyan-400 focus:outline-none"
              step="300"
            />
          </div>
        </div>

        <p v-if="validationError" class="text-xs text-red-500">{{ validationError }}</p>

        <button
          type="button"
          @click="saveDayHours"
          class="w-full rounded-lg bg-cyan-500 px-4 py-2 text-sm font-medium text-white hover:bg-cyan-600"
        >
          Save {{ days.find(d => d.num === selectedDay)?.name }} Hours
        </button>
      </div>

      <!-- All days summary with copy buttons -->
      <div class="space-y-1">
        <div
          v-for="day in days"
          :key="day.num"
          class="flex items-center justify-between rounded-lg border border-slate-200 bg-white px-4 py-3"
        >
          <div class="flex-1">
            <span class="text-sm font-medium text-slate-700">{{ day.name }}</span>
            <span v-if="getHours(day.num)" class="ml-2 text-slate-600">
              {{ formatTime(getHours(day.num)?.open_time) }} - {{ formatTime(getHours(day.num)?.close_time) }}
            </span>
            <span v-else class="ml-2 text-slate-400">Closed</span>
          </div>
          <div v-if="getHours(day.num)" class="relative" :ref="'copyHoursDropup-' + day.num">
            <button
              type="button"
              @click="toggleCopyDropup(day.num)"
              class="text-xs text-cyan-600 hover:text-cyan-700 font-medium"
            >
              Copy
            </button>
            <div v-if="activeCopyDropup === day.num" class="absolute right-0 mt-1 z-10 bg-white rounded-lg border border-slate-200 shadow-sm p-1 min-w-[120px]">
              <button
                v-for="item in availableCopyDays(day.num)"
                :key="item.num"
                type="button"
                @click="copyHoursToDay(day, item.num)"
                class="block w-full text-left px-3 py-1.5 text-xs hover:bg-cyan-50 rounded-md"
              >
                {{ item.name }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({})
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const days = [
  { num: 0, name: 'Sunday' },
  { num: 1, name: 'Monday' },
  { num: 2, name: 'Tuesday' },
  { num: 3, name: 'Wednesday' },
  { num: 4, name: 'Thursday' },
  { num: 5, name: 'Friday' },
  { num: 6, name: 'Saturday' },
]

const selectedDay = ref(1) // Default to Monday
const editorOpenTime = ref('09:00')
const editorCloseTime = ref('17:00')
const validationError = ref('')
const activeCopyDropup = ref(null)

function getHours(dayNum) {
  return props.modelValue[dayNum] || null
}

function setClosed() {
  const updated = { ...props.modelValue }
  updated[selectedDay.value] = null
  emit('update:modelValue', updated)
}

function validateTimes() {
  if (editorOpenTime.value && editorCloseTime.value) {
    if (editorOpenTime.value >= editorCloseTime.value) {
      validationError.value = 'Open time must be before close time'
      return false
    }
  }
  validationError.value = ''
  return true
}

function saveDayHours() {
  if (!validateTimes()) return

  const updated = { ...props.modelValue }
  updated[selectedDay.value] = {
    open_time: editorOpenTime.value,
    close_time: editorCloseTime.value
  }
  emit('update:modelValue', updated)
}

function availableCopyDays(currentDayNum) {
  return days.filter(d => {
    if (d.num === currentDayNum) return false
    const existing = getHours(d.num)
    if (existing) return false
    return true
  })
}

function copyHoursToDay(sourceDay, targetDayNum) {
  const hours = getHours(sourceDay.num)
  if (!hours) return
  const updated = { ...props.modelValue }
  updated[targetDayNum] = {
    open_time: hours.open_time,
    close_time: hours.close_time
  }
  emit('update:modelValue', updated)
  activeCopyDropup.value = null
}

function toggleCopyDropup(dayNum) {
  activeCopyDropup.value = activeCopyDropup.value === dayNum ? null : dayNum
}

function formatTime(time) {
  if (!time) return ''
  return time
}

// Sync editor times when selectedDay changes
watch(selectedDay, (newDay) => {
  const hours = getHours(newDay)
  if (hours && hours.open_time && hours.close_time) {
    editorOpenTime.value = hours.open_time
    editorCloseTime.value = hours.close_time
  } else {
    editorOpenTime.value = '09:00'
    editorCloseTime.value = '17:00'
  }
  validationError.value = ''
})
</script>