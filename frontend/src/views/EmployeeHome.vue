<template>
  <div class="bg-slate-50 min-h-screen">

    <div v-if="employeeStore.loading" class="flex min-h-screen items-center justify-center">
      <svg class="h-8 w-8 animate-spin text-cyan-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
      </svg>
    </div>

    <!-- No assignment yet (backend pending) -->
    <div v-else-if="!employeeStore.assignedListing" class="flex min-h-screen flex-col items-center justify-center px-4 text-center">
      <div class="flex h-16 w-16 items-center justify-center rounded-3xl bg-slate-100">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
        </svg>
      </div>
      <h2 class="mt-6 text-2xl font-bold text-slate-900">No listing assigned</h2>
      <p class="mt-2 max-w-sm text-sm text-slate-500">Your account has not been linked to a listing yet. Contact your business owner to get set up.</p>
    </div>

    <!-- Listing view -->
    <template v-else>
      <div class="bg-white border-b border-slate-200">
        <div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <p class="text-xs font-semibold uppercase tracking-[0.28em] text-cyan-600">
            {{ employeeStore.business?.name || 'Your Business' }}
          </p>
          <div class="mt-2 flex flex-wrap items-center gap-3">
            <span
              class="rounded-xl px-3 py-1 text-xs font-semibold"
              :class="statusBadgeClass(employeeStore.assignedListing.status)"
            >
              {{ statusLabel(employeeStore.assignedListing.status) }}
            </span>
            <h1 class="text-2xl font-bold text-slate-900 sm:text-3xl">
              {{ employeeStore.assignedListing.title }}
            </h1>
          </div>
          <p v-if="employeeStore.assignedListing.address" class="mt-2 flex items-center gap-1.5 text-sm text-slate-500">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 shrink-0 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a2 2 0 01-2.828 0l-4.243-4.243a8 8 0 1111.314 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            {{ [employeeStore.assignedListing.address?.city, employeeStore.assignedListing.address?.country].filter(Boolean).join(', ') }}
          </p>
        </div>
      </div>

      <div class="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8 space-y-8">

        <!-- Stats -->
        <div class="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <p class="text-sm font-medium text-slate-500">Total Services</p>
            <p class="mt-2 text-3xl font-bold text-slate-900">{{ services.length }}</p>
          </div>
          <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <p class="text-sm font-medium text-slate-500">Active Services</p>
            <p class="mt-2 text-3xl font-bold text-cyan-600">{{ services.filter(s => s.status === 'active').length }}</p>
          </div>
          <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <p class="text-sm font-medium text-slate-500">Reviews</p>
            <p class="mt-2 text-3xl font-bold text-slate-900">{{ employeeStore.assignedListing.review_count ?? 0 }}</p>
          </div>
          <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <p class="text-sm font-medium text-slate-500">Avg Rating</p>
            <p class="mt-2 text-3xl font-bold text-amber-500">
              {{ employeeStore.assignedListing.avg_rating ? employeeStore.assignedListing.avg_rating.toFixed(1) : '—' }}
            </p>
          </div>
        </div>

        <!-- Services -->
        <div>
          <div class="mb-6 flex items-center justify-between">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.28em] text-cyan-600">Listing</p>
              <h2 class="mt-1 text-xl font-bold text-slate-900">Services</h2>
            </div>
            <button
              @click="openServiceModal()"
              class="inline-flex items-center gap-2 rounded-2xl bg-cyan-400 px-5 py-2.5 text-sm font-semibold text-slate-950 transition hover:-translate-y-0.5 hover:bg-cyan-300"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4" />
              </svg>
              Add Service
            </button>
          </div>

          <!-- Empty state -->
          <div v-if="services.length === 0" class="rounded-3xl border-2 border-dashed border-slate-200 bg-white px-6 py-20 text-center">
            <div class="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-100">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <p class="mt-4 text-base font-semibold text-slate-700">No services yet</p>
            <p class="mt-1.5 text-sm text-slate-400">Add the first service for this listing.</p>
          </div>

          <!-- Service cards -->
          <div v-else class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <div
              v-for="service in services"
              :key="service.id"
              class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
              :class="{ 'opacity-60': service.status === 'inactive' }"
            >
              <div class="flex items-start justify-between gap-3">
                <div class="min-w-0">
                  <p class="truncate text-base font-bold text-slate-900">{{ service.name }}</p>
                  <p v-if="service.duration" class="mt-0.5 text-xs text-slate-400">{{ service.duration }}</p>
                </div>
                <span
                  class="shrink-0 rounded-xl px-2.5 py-1 text-xs font-semibold"
                  :class="service.status === 'active' ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-500'"
                >{{ service.status === 'active' ? 'Active' : 'Inactive' }}</span>
              </div>
              <p v-if="service.description" class="mt-3 text-sm leading-6 text-slate-500 line-clamp-2">{{ service.description }}</p>
              <div class="mt-4 flex items-center justify-between">
                <p class="text-xl font-bold text-slate-900">${{ parseFloat(service.price || 0).toFixed(2) }}</p>
                <div class="flex gap-2">
                  <button
                    @click="openServiceModal(service)"
                    class="rounded-xl border border-slate-200 px-3 py-1.5 text-xs font-semibold text-slate-700 transition hover:border-slate-300 hover:bg-slate-50"
                  >Edit</button>
                  <button
                    @click="removeService(service.id)"
                    class="rounded-xl border border-red-100 px-3 py-1.5 text-xs font-semibold text-red-500 transition hover:bg-red-50"
                  >Remove</button>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </template>

    <!-- Add / Edit Service Modal -->
    <div
      v-if="showServiceModal"
      class="fixed inset-0 z-50 flex items-center justify-center px-4"
      @click.self="closeServiceModal"
    >
      <div class="absolute inset-0 bg-slate-950/50 backdrop-blur-sm"></div>
      <div class="relative w-full max-w-lg overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-2xl">

        <div class="flex items-center justify-between border-b border-slate-100 px-8 py-6">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.28em] text-cyan-600">
              {{ editingService ? 'Edit Service' : 'New Service' }}
            </p>
            <h2 class="mt-1 text-xl font-bold text-slate-900">
              {{ editingService ? 'Update service details' : 'Add a service' }}
            </h2>
          </div>
          <button @click="closeServiceModal" class="flex h-9 w-9 items-center justify-center rounded-2xl border border-slate-200 text-slate-500 transition hover:bg-slate-50">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form @submit.prevent="submitService" class="px-8 py-6 space-y-4">
          <div>
            <label class="mb-1.5 block text-sm font-semibold text-slate-700">Service Name <span class="text-red-500">*</span></label>
            <input v-model="serviceForm.name" type="text" required placeholder="e.g. Airport Transfer"
              class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400" />
          </div>

          <div>
            <label class="mb-1.5 block text-sm font-semibold text-slate-700">Description</label>
            <textarea v-model="serviceForm.description" rows="3" placeholder="Describe this service..."
              class="w-full resize-none rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400"></textarea>
          </div>

          <div class="grid gap-4 sm:grid-cols-2">
            <div>
              <label class="mb-1.5 block text-sm font-semibold text-slate-700">Price (USD) <span class="text-red-500">*</span></label>
              <div class="relative">
                <span class="absolute left-4 top-1/2 -translate-y-1/2 text-sm font-semibold text-slate-400">$</span>
                <input v-model="serviceForm.price" type="number" min="0" step="0.01" required placeholder="0.00"
                  class="w-full rounded-2xl border border-slate-200 bg-white pl-8 pr-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400" />
              </div>
            </div>
            <div>
              <label class="mb-1.5 block text-sm font-semibold text-slate-700">Duration</label>
              <input v-model="serviceForm.duration" type="text" placeholder="e.g. 2 hours, Per night"
                class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400" />
            </div>
          </div>

          <div>
            <label class="mb-1.5 block text-sm font-semibold text-slate-700">Status</label>
            <div class="flex gap-3">
              <button type="button" @click="serviceForm.status = 'active'"
                class="flex-1 rounded-2xl border py-2.5 text-sm font-semibold transition"
                :class="serviceForm.status === 'active' ? 'border-emerald-400 bg-emerald-50 text-emerald-700' : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300'">
                Active
              </button>
              <button type="button" @click="serviceForm.status = 'inactive'"
                class="flex-1 rounded-2xl border py-2.5 text-sm font-semibold transition"
                :class="serviceForm.status === 'inactive' ? 'border-slate-400 bg-slate-100 text-slate-700' : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300'">
                Inactive
              </button>
            </div>
          </div>

          <div class="flex gap-3 pt-2">
            <button type="button" @click="closeServiceModal"
              class="flex-1 rounded-2xl border border-slate-200 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50">
              Cancel
            </button>
            <button type="submit"
              class="flex-1 rounded-2xl bg-slate-900 py-3 text-sm font-semibold text-white transition hover:-translate-y-0.5 hover:bg-slate-800">
              {{ editingService ? 'Save Changes' : 'Add Service' }}
            </button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useEmployeeStore } from '../stores/employee'
import { useToastStore } from '../stores/toast'

const employeeStore = useEmployeeStore()
const toastStore = useToastStore()

onMounted(() => {
  employeeStore.fetchAssignment()
})

function statusLabel(status) {
  if (status === 'active') return 'Active'
  if (status === 'pending') return 'Pending Approval'
  if (status === 'inactive') return 'Archived'
  return status ?? ''
}

function statusBadgeClass(status) {
  if (status === 'active') return 'bg-emerald-500 text-white'
  if (status === 'pending') return 'bg-amber-400 text-slate-900'
  if (status === 'inactive') return 'bg-slate-500 text-white'
  return 'bg-slate-300 text-slate-900'
}

// Services (local state until API is ready)
const services = ref([])
const showServiceModal = ref(false)
const editingService = ref(null)

const blankServiceForm = () => ({
  name: '',
  description: '',
  price: '',
  duration: '',
  status: 'active',
})

const serviceForm = ref(blankServiceForm())

function openServiceModal(service = null) {
  editingService.value = service
  serviceForm.value = service
    ? { name: service.name, description: service.description, price: service.price, duration: service.duration, status: service.status }
    : blankServiceForm()
  showServiceModal.value = true
}

function closeServiceModal() {
  showServiceModal.value = false
  editingService.value = null
}

function submitService() {
  if (editingService.value) {
    const idx = services.value.findIndex(s => s.id === editingService.value.id)
    if (idx !== -1) services.value[idx] = { ...editingService.value, ...serviceForm.value }
    toastStore.show('Service updated.', 'success')
  } else {
    services.value.push({ id: Date.now(), ...serviceForm.value })
    toastStore.show('Service added.', 'success')
  }
  closeServiceModal()
}

function removeService(id) {
  services.value = services.value.filter(s => s.id !== id)
  toastStore.show('Service removed.', 'info')
}
</script>
