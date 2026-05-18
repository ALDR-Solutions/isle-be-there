<template>
  <div class="rounded-2xl border border-slate-200 bg-white p-6">
    <div class="mb-4 flex items-center justify-between">
      <h2 class="text-lg font-bold text-slate-900">Availability Hours</h2>
      <button
        v-if="!isEditing"
        type="button"
        @click="startEditing"
        class="text-sm font-medium text-cyan-600 hover:text-cyan-700"
      >
        Edit
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-4">
      <div class="h-5 w-5 animate-spin rounded-full border-2 border-cyan-400 border-t-transparent"></div>
    </div>

    <!-- Display Mode -->
    <div v-else-if="!isEditing" class="space-y-1">
      <div
        v-for="day in days"
        :key="day.num"
        class="flex items-center justify-between text-sm"
      >
        <span class="text-slate-600">{{ day.name }}</span>
        <span v-if="hoursMap[day.num]" class="text-slate-800 font-medium">
          {{ hoursMap[day.num].open_time }} - {{ hoursMap[day.num].close_time }}
        </span>
        <span v-else class="text-slate-400">Closed</span>
      </div>
    </div>

    <!-- Edit Mode -->
    <div v-else class="space-y-4">
      <AvailabilityHoursEditor
        v-model="editedHours"
        :loading="saving"
      />

      <div class="flex justify-end gap-2">
        <button
          type="button"
          @click="cancelEditing"
          :disabled="saving"
          class="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50 disabled:opacity-50"
        >
          Cancel
        </button>
        <button
          type="button"
          @click="saveHours"
          :disabled="saving"
          class="rounded-lg bg-cyan-500 px-4 py-2 text-sm font-medium text-white hover:bg-cyan-600 disabled:opacity-50"
        >
          {{ saving ? 'Saving...' : 'Save' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../../../stores/auth'
import { useToastStore } from '../../../stores/toast'
import { availabilityAPI } from '../../../services/api'
import AvailabilityHoursEditor from '../detail-forms/AvailabilityHoursEditor.vue'

const props = defineProps({
  listingId: {
    type: String,
    required: true
  }
})

const authStore = useAuthStore()
const toast = useToastStore()

const days = [
  { num: 0, name: 'Sunday' },
  { num: 1, name: 'Monday' },
  { num: 2, name: 'Tuesday' },
  { num: 3, name: 'Wednesday' },
  { num: 4, name: 'Thursday' },
  { num: 5, name: 'Friday' },
  { num: 6, name: 'Saturday' },
]

const loading = ref(false)
const saving = ref(false)
const isEditing = ref(false)
const hoursMap = ref({})
const editedHours = ref({})

// Only show for business/admin users
if (!authStore.isBusiness && !authStore.isAdmin) {
  // Hide component by setting a flag
}

onMounted(async () => {
  await fetchHours()
})

async function fetchHours() {
  loading.value = true
  try {
    const response = await availabilityAPI.getListingHours(props.listingId)
    const hoursObj = {}
    for (const h of response.data) {
      hoursObj[h.day_of_week] = { open_time: h.open_time, close_time: h.close_time }
    }
    hoursMap.value = hoursObj
  } catch (error) {
    console.error('Failed to fetch hours:', error)
  } finally {
    loading.value = false
  }
}

function startEditing() {
  editedHours.value = { ...hoursMap.value }
  isEditing.value = true
}

function cancelEditing() {
  isEditing.value = false
  editedHours.value = {}
}

async function saveHours() {
  saving.value = true
  try {
    // For each day that has changes, update or create
    for (const [dayNum, hours] of Object.entries(editedHours.value)) {
      const day = parseInt(dayNum)
      if (hours === null) {
        // Delete if exists
        if (hoursMap.value[day]) {
          await availabilityAPI.deleteListingHours(props.listingId, day)
        }
      } else if (hoursMap.value[day]) {
        // Update existing
        await availabilityAPI.updateListingHours(props.listingId, day, hours)
      } else {
        // Create new - include day_of_week and listing_id in payload
        // Convert time strings to HH:MM:SS format for pydantic
        const payload = {
          day_of_week: day,
          listing_id: props.listingId,
          open_time: hours.open_time.includes(':') && hours.open_time.split(':').length === 2
            ? hours.open_time + ':00'
            : hours.open_time,
          close_time: hours.close_time.includes(':') && hours.close_time.split(':').length === 2
            ? hours.close_time + ':00'
            : hours.close_time,
        }
        await availabilityAPI.createListingHours(props.listingId, payload)
      }
    }

    // Also delete any days that were set to null
    for (const [dayNum, hours] of Object.entries(hoursMap.value)) {
      if (hours && !editedHours.value[dayNum]) {
        await availabilityAPI.deleteListingHours(props.listingId, parseInt(dayNum))
      }
    }

    toast.show('Hours saved successfully', 'success')
    isEditing.value = false
    await fetchHours()
  } catch (error) {
    console.error('Failed to save hours:', error)
    toast.show('Failed to save hours', 'error')
  } finally {
    saving.value = false
  }
}
</script>