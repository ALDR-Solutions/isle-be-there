import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { employeesAPI } from '../services/api'
import { useAuthStore } from './auth'

export const useEmployeeStore = defineStore('employee', () => {
  const assignedListings = ref([])
  const activeListingId = ref(null)
  const business = ref(null)
  const loading = ref(false)
  const loadError = ref(null)

  const activeListing = computed(() =>
    assignedListings.value.find(l => l.id === activeListingId.value) ?? assignedListings.value[0] ?? null
  )
  const hasAssignments = computed(() => assignedListings.value.length > 0)

  async function fetchAssignments() {
    const authStore = useAuthStore()
    const userId = authStore.user?.id
    if (!userId) {
      reset()
      return
    }
    loading.value = true
    loadError.value = null
    try {
      const res = await employeesAPI.getListings(userId)
      assignedListings.value = res.data ?? []
      if (!assignedListings.value.some(listing => listing.id === activeListingId.value)) {
        activeListingId.value = null
      }
      if (assignedListings.value.length && !activeListingId.value) {
        activeListingId.value = assignedListings.value[0].id
      }
    } catch (e) {
      assignedListings.value = []
      activeListingId.value = null
      loadError.value = e.response?.data?.detail || 'Unable to load employee listings.'
      console.error('Failed to load employee assignments', e)
    } finally {
      loading.value = false
    }
  }

  // Keep old name as alias so EmployeeLayout's onMounted still works
  // until we update the call site
  const fetchAssignment = fetchAssignments

  function setActiveListing(id) {
    activeListingId.value = id
  }

  function reset() {
    assignedListings.value = []
    activeListingId.value = null
    business.value = null
    loadError.value = null
  }

  return {
    assignedListings,
    activeListingId,
    activeListing,
    hasAssignments,
    business,
    loading,
    loadError,
    fetchAssignments,
    fetchAssignment,
    setActiveListing,
    reset,
  }
})
