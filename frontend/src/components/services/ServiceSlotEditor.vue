<template>
  <Teleport to="body">
    <div
      v-if="visible"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      @click.self="$emit('close')"
    >
      <div class="w-full max-w-lg rounded-xl bg-white shadow-xl">
        <!-- Header -->
        <div class="flex items-center justify-between border-b border-slate-200 px-6 py-4">
          <h3 class="text-lg font-semibold text-slate-800">Service Slots</h3>
          <button
            type="button"
            @click="$emit('close')"
            class="text-slate-400 hover:text-slate-600"
          >
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Body -->
        <div class="max-h-[60vh] overflow-y-auto p-6 space-y-4">
          <!-- Existing Slots List -->
          <div v-if="slots.length > 0" class="space-y-2">
            <div
              v-for="slot in slots"
              :key="slot.id"
              class="flex items-center justify-between rounded-lg border border-slate-200 bg-slate-50 px-4 py-3"
            >
              <div class="flex-1">
                <span class="font-medium text-slate-700">{{ dayNames[slot.day_of_week] }}</span>
                <span class="ml-2 text-slate-600">
                  {{ slot.start_time }} - {{ slot.end_time }}
                </span>
                <span class="ml-2 text-xs text-slate-500">Cap: {{ slot.capacity }}</span>
              </div>
              <div class="flex items-center gap-2">
                <button
                  type="button"
                  @click="deleteSlot(slot.id)"
                  class="text-xs text-red-500 hover:text-red-600"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
          <p v-else class="text-sm text-slate-500">No slots configured yet.</p>

          <!-- Add Slot Form -->
          <div class="rounded-lg border border-slate-200 p-4 space-y-3">
            <h4 class="text-sm font-medium text-slate-700">Add New Slot</h4>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs text-slate-500 mb-1">Day</label>
                <select
                  v-model="newSlot.day"
                  class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-cyan-400 focus:outline-none"
                >
                  <option v-for="(name, idx) in dayNames" :key="idx" :value="idx">
                    {{ name }}
                  </option>
                </select>
              </div>
              <div>
                <label class="block text-xs text-slate-500 mb-1">Capacity</label>
                <input
                  type="number"
                  v-model.number="newSlot.capacity"
                  min="1"
                  class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-cyan-400 focus:outline-none"
                />
              </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs text-slate-500 mb-1">Start Time</label>
                <input
                  type="time"
                  v-model="newSlot.startTime"
                  class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-cyan-400 focus:outline-none"
                  step="300"
                />
              </div>
              <div>
                <label class="block text-xs text-slate-500 mb-1">End Time</label>
                <input
                  type="time"
                  v-model="newSlot.endTime"
                  class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-cyan-400 focus:outline-none"
                  step="300"
                />
              </div>
            </div>

            <p v-if="validationError" class="text-xs text-red-500">{{ validationError }}</p>

            <!-- Copy to other days -->
            <div class="flex items-center gap-2">
              <button
                type="button"
                @click="showCopyTargets = !showCopyTargets"
                class="text-xs text-cyan-600 hover:text-cyan-700 font-medium"
              >
                Copy to other days...
              </button>
              <div v-if="showCopyTargets" class="flex flex-wrap gap-1">
                <button
                  v-for="(name, idx) in dayNames.filter((_, i) => i !== newSlot.day)"
                  :key="idx"
                  type="button"
                  @click="addCopySlot(idx)"
                  class="rounded-lg border border-slate-200 bg-white px-2 py-1 text-xs hover:border-cyan-300 hover:bg-cyan-50"
                >
                  {{ name }}
                </button>
              </div>
            </div>

            <button
              type="button"
              @click="addSlot"
              :disabled="isAdding"
              class="w-full rounded-lg bg-cyan-500 px-4 py-2 text-sm font-medium text-white hover:bg-cyan-600 disabled:opacity-50"
            >
              {{ isAdding ? 'Adding...' : 'Add Slot' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  modelValue: {
    type: Array,
    default: () => []
  },
  serviceId: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['update:modelValue', 'close'])

const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

const slots = computed(() => props.modelValue)

const newSlot = reactive({
  day: 1,
  startTime: '09:00',
  endTime: '17:00',
  capacity: 10
})

const validationError = ref('')
const isAdding = ref(false)
const showCopyTargets = ref(false)

function validateSlot() {
  if (newSlot.startTime >= newSlot.endTime) {
    validationError.value = 'Start time must be before end time'
    return false
  }
  if (!newSlot.capacity || newSlot.capacity < 1) {
    validationError.value = 'Capacity must be at least 1'
    return false
  }
  validationError.value = ''
  return true
}

function buildSlot(dayOverride) {
  const day = dayOverride !== undefined ? dayOverride : newSlot.day
  return {
    id: Date.now() + Math.random(), // temporary id for UI
    day_of_week: day,
    start_time: newSlot.startTime,
    end_time: newSlot.endTime,
    capacity: newSlot.capacity
  }
}

function addSlot() {
  if (!validateSlot()) return

  const newSlots = [...slots.value, buildSlot()]
  emit('update:modelValue', newSlots)

  // Reset form
  newSlot.day = 1
  newSlot.startTime = '09:00'
  newSlot.endTime = '17:00'
  newSlot.capacity = 10
  showCopyTargets.value = false
}

function addCopySlot(targetDay) {
  if (!validateSlot()) return

  const copySlot = buildSlot(targetDay)
  const newSlots = [...slots.value, copySlot]
  emit('update:modelValue', newSlots)
}

function deleteSlot(slotId) {
  const newSlots = slots.value.filter(s => s.id !== slotId)
  emit('update:modelValue', newSlots)
}
</script>