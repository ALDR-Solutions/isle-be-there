import { computed, onBeforeUnmount, ref } from 'vue'
import { isRequestCancelled } from '@/services/http/errors'

export function useAsyncData(loader, options = {}) {
  const data = ref(options.initialData ?? null)
  const loading = ref(Boolean(options.immediate))
  const error = ref(null)
  const hasLoaded = ref(false)
  const requestId = ref(0)
  let controller = null

  const isEmpty = computed(() => {
    if (typeof options.isEmpty === 'function') {
      return options.isEmpty(data.value)
    }

    if (Array.isArray(data.value)) {
      return data.value.length === 0
    }

    return !data.value
  })

  async function load(params) {
    requestId.value += 1
    const currentRequest = requestId.value

    controller?.abort()
    controller = new AbortController()
    loading.value = true
    error.value = null

    try {
      const result = await loader({ ...(params || {}), signal: controller.signal })

      if (currentRequest === requestId.value) {
        data.value = result
        hasLoaded.value = true
      }

      return result
    } catch (err) {
      if (!isRequestCancelled(err) && currentRequest === requestId.value) {
        error.value = err
        hasLoaded.value = true
      }

      throw err
    } finally {
      if (currentRequest === requestId.value) {
        loading.value = false
      }
    }
  }

  function refresh(params) {
    return load(params)
  }

  function reset(nextValue = options.initialData ?? null) {
    data.value = nextValue
    error.value = null
    loading.value = false
    hasLoaded.value = false
  }

  onBeforeUnmount(() => {
    controller?.abort()
  })

  return {
    data,
    error,
    hasLoaded,
    isEmpty,
    loading,
    load,
    refresh,
    reset,
  }
}
