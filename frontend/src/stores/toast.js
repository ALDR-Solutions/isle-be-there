import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useToastStore = defineStore('toast', () => {
    const toasts = ref([])

    function show(message, type = 'info', duration = 3000) {
        const id = Date.now() + Math.random()

        toasts.value.push({
            id,
            message,
            type,
        })

        setTimeout(() => {
            remove(id)
        }, duration)
    }

    function remove(id) {
        toasts.value = toasts.value.filter((toast) => toast.id != id)

    }

    return {
        toasts,
        show,
        remove,
    }
})

