import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { favouritesAPI } from '../services/api'

export const useFavouritesStore = defineStore('favourites', () => {
  const items = ref([])
  const loading = ref(false)
  const loaded = ref(false)
  let pendingRequest = null

  const listingIds = computed(() => items.value.map(item => item.listing_id))

  function reset() {
    items.value = []
    loading.value = false
    loaded.value = false
    pendingRequest = null
  }

  function has(listingId) {
    return listingIds.value.includes(listingId)
  }

  async function fetchAll(force = false) {
    if (!force && loaded.value) {
      return items.value
    }

    if (pendingRequest) {
      return pendingRequest
    }

    loading.value = true
    pendingRequest = favouritesAPI.getAll()
      .then((response) => {
        items.value = response.data
        loaded.value = true
        return items.value
      })
      .catch((error) => {
        if (error.response?.status === 401) {
          reset()
        }
        throw error
      })
      .finally(() => {
        loading.value = false
        pendingRequest = null
      })

    return pendingRequest
  }

  async function add(listingId) {
    const response = await favouritesAPI.add(listingId)
    if (!has(listingId)) {
      items.value.push(response.data)
    }
    loaded.value = true
    return response.data
  }

  async function remove(listingId) {
    await favouritesAPI.remove(listingId)
    items.value = items.value.filter(item => item.listing_id !== listingId)
    loaded.value = true
  }

  async function toggle(listingId) {
    if (has(listingId)) {
      await remove(listingId)
      return false
    }

    await add(listingId)
    return true
  }

  return {
    items,
    loading,
    loaded,
    listingIds,
    reset,
    has,
    fetchAll,
    add,
    remove,
    toggle,
  }
})
