import { defineStore } from 'pinia'
import { ref } from 'vue'
import { listingsAPI, businessesAPI } from '../services/api'
import { useAuthStore } from './auth'

export const useEmployeeStore = defineStore('employee', () => {
  const assignedListing = ref(null)
  const business = ref(null)
  const loading = ref(false)

  async function fetchAssignment() {
    const authStore = useAuthStore()
    loading.value = true
    try {
      // When backend supports employee accounts, the user object will carry
      // listing_id and business_id. Until then this resolves gracefully.
      const listingId = authStore.user?.listing_id
      if (listingId) {
        const [listingRes, bizRes] = await Promise.all([
          listingsAPI.getById(listingId),
          businessesAPI.getById(authStore.user?.business_id),
        ])
        assignedListing.value = listingRes.data
        business.value = bizRes.data
      }
    } catch (e) {
      console.error('Failed to load employee assignment', e)
    } finally {
      loading.value = false
    }
  }

  function reset() {
    assignedListing.value = null
    business.value = null
  }

  return {
    assignedListing,
    business,
    loading,
    fetchAssignment,
    reset,
  }
})
