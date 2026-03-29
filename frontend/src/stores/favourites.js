import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { hasSession } from '@/app/session'
import { favouritesService } from '@/services/favouritesService'

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
    if (!hasSession()) {
      reset()
      return []
    }

    if (!force && loaded.value) {
      return items.value
    }

    if (pendingRequest) {
      return pendingRequest
    }

    loading.value = true
    pendingRequest = favouritesService.getAll()
      .then((favourites) => {
        items.value = favourites
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
    const favourite = await favouritesService.add(listingId)
    if (!has(listingId)) {
      items.value.push(favourite)
    }
    loaded.value = true
    return favourite
  }

  async function remove(listingId) {
    await favouritesService.remove(listingId)
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
