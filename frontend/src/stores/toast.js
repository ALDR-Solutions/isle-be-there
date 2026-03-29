import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useToastStore = defineStore('toast', () => {
    const toasts = ref([])
    const timers = new Map()

    function show(message, type = 'info', duration = 3000) {
        const id = Date.now() + Math.random()

        if (toasts.value.length >= 4) {
            const oldest = toasts.value[0]
            remove(oldest.id)
        }

        toasts.value.push({
            id,
            message,
            type,
        })

        const timer = window.setTimeout(() => {
            remove(id)
        }, duration)

        timers.set(id, timer)
    }

    function remove(id) {
        const timer = timers.get(id)
        if (timer) {
            clearTimeout(timer)
            timers.delete(id)
        }

        toasts.value = toasts.value.filter((toast) => toast.id != id)

    }

    return {
        toasts,
        show,
        remove,
    }
})

