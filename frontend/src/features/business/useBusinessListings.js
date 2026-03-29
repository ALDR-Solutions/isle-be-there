import { computed, ref } from 'vue'
import { useAsyncData } from '@/composables/useAsyncData'
import { businessesService } from '@/services/businessesService'
import { listingsService } from '@/services/listingsService'

export function useBusinessListings() {
  const activeTab = ref('all')

  const dashboardState = useAsyncData(async ({ signal }) => {
    const [listings, businessTypes] = await Promise.all([
      businessesService.getListings({}, { signal }),
      businessesService.getTypes({ signal }),
    ])

    return {
      listings,
      businessTypes,
    }
  }, {
    initialData: {
      listings: [],
      businessTypes: [],
    },
  })

  const tabs = [
    { label: 'All', value: 'all' },
    { label: 'Active', value: 'active' },
    { label: 'Pending Approval', value: 'pending' },
    { label: 'Archived', value: 'inactive' },
  ]

  const listings = computed(() => dashboardState.data.value.listings || [])
  const businessTypes = computed(() => dashboardState.data.value.businessTypes || [])
  const filteredListings = computed(() => {
    if (activeTab.value === 'all') return listings.value
    return listings.value.filter((item) => item.status === activeTab.value)
  })

  const stats = computed(() => ({
    total: listings.value.length,
    active: listings.value.filter((item) => item.status === 'active').length,
    pending: listings.value.filter((item) => item.status === 'pending').length,
    inactive: listings.value.filter((item) => item.status === 'inactive').length,
  }))

  async function loadDashboard() {
    return dashboardState.load()
  }

  async function saveListing(listingId, payload) {
    const savedListing = listingId
      ? await listingsService.update(listingId, payload)
      : await listingsService.create(payload)

    const index = listings.value.findIndex((item) => item.id === savedListing.id)

    if (index === -1) {
      dashboardState.data.value = {
        ...dashboardState.data.value,
        listings: [savedListing, ...listings.value],
      }
    } else {
      const nextListings = [...listings.value]
      nextListings[index] = savedListing
      dashboardState.data.value = {
        ...dashboardState.data.value,
        listings: nextListings,
      }
    }

    return savedListing
  }

  async function archiveListing(listing) {
    const updatedListing = await listingsService.update(listing.id, { status: 'inactive' })
    replaceListing(updatedListing)
    return updatedListing
  }

  async function unarchiveListing(listing) {
    const updatedListing = await listingsService.update(listing.id, { status: 'active' })
    replaceListing(updatedListing)
    return updatedListing
  }

  function replaceListing(updatedListing) {
    const nextListings = listings.value.map((item) => (item.id === updatedListing.id ? updatedListing : item))
    dashboardState.data.value = {
      ...dashboardState.data.value,
      listings: nextListings,
    }
  }

  return {
    activeTab,
    archiveListing,
    businessTypes,
    dashboardState,
    filteredListings,
    listings,
    loadDashboard,
    saveListing,
    stats,
    tabs,
    unarchiveListing,
  }
}
