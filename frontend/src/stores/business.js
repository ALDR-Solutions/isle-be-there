import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { businessesAPI } from '../services/api'

export const useBusinessStore = defineStore('business', () => {
  const business = ref(null)
  const listings = ref([])
  const activeListingId = ref(null)
  const loading = ref(false)
  const showCreateModal = ref(false)

  const activeListing = computed(() =>
    listings.value.find(l => l.id === activeListingId.value) ?? listings.value[0] ?? null
  )

  async function fetchBusiness() {
    loading.value = true
    try {
      const [bizRes, listingsRes] = await Promise.all([
        businessesAPI.getMe(),
        businessesAPI.getListings(),
      ])
      business.value = bizRes.data
      listings.value = listingsRes.data || []
      if (!activeListingId.value && listings.value.length > 0) {
        activeListingId.value = listings.value[0].id
      }
    } catch (e) {
      console.error('Failed to load business data', e)
    } finally {
      loading.value = false
    }
  }

  function setActiveListing(id) {
    activeListingId.value = id
  }

  function addListing(listing) {
    listings.value.unshift(listing)
    activeListingId.value = listing.id
  }

  function updateListing(updated) {
    const idx = listings.value.findIndex(l => l.id === updated.id)
    if (idx !== -1) listings.value[idx] = updated
  }

  function reset() {
    business.value = null
    listings.value = []
    activeListingId.value = null
  }

  return {
    business,
    listings,
    activeListingId,
    activeListing,
    loading,
    showCreateModal,
    fetchBusiness,
    setActiveListing,
    addListing,
    updateListing,
    reset,
  }
})
