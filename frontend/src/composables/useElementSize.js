import { onBeforeUnmount, onMounted, ref } from 'vue'

export function useElementSize(targetRef) {
  const width = ref(0)
  const height = ref(0)
  let observer = null

  function measure() {
    const element = targetRef.value
    if (!element) return
    width.value = element.offsetWidth
    height.value = element.offsetHeight
  }

  onMounted(() => {
    measure()

    if (typeof ResizeObserver !== 'undefined') {
      observer = new ResizeObserver(() => measure())
      if (targetRef.value) {
        observer.observe(targetRef.value)
      }
    } else {
      window.addEventListener('resize', measure)
    }
  })

  onBeforeUnmount(() => {
    observer?.disconnect()
    window.removeEventListener('resize', measure)
  })

  return {
    width,
    height,
    measure,
  }
}
