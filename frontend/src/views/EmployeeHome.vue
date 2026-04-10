<template>
  <div class="bg-slate-50 min-h-screen">

    <div v-if="employeeStore.loading" class="flex min-h-screen items-center justify-center">
      <svg class="h-8 w-8 animate-spin text-cyan-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
      </svg>
    </div>

    <div v-else-if="employeeStore.loadError" class="flex min-h-screen flex-col items-center justify-center px-4 text-center">
      <div class="flex h-16 w-16 items-center justify-center rounded-3xl bg-red-50">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9v3.75m0 3.75h.008v.008H12v-.008zm8.25-3.75a8.25 8.25 0 11-16.5 0 8.25 8.25 0 0116.5 0z" />
        </svg>
      </div>
      <h2 class="mt-6 text-2xl font-bold text-slate-900">Unable to load your dashboard</h2>
      <p class="mt-2 max-w-sm text-sm text-slate-500">{{ employeeStore.loadError }}</p>
      <button
        @click="employeeStore.fetchAssignments()"
        class="mt-6 rounded-2xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
      >
        Try again
      </button>
    </div>

    <div v-else-if="!employeeStore.hasAssignments" class="flex min-h-screen flex-col items-center justify-center px-4 text-center">
      <div class="flex h-16 w-16 items-center justify-center rounded-3xl bg-slate-100">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
        </svg>
      </div>
      <h2 class="mt-6 text-2xl font-bold text-slate-900">No listing assigned</h2>
      <p class="mt-2 max-w-sm text-sm text-slate-500">Your account has not been linked to a listing yet. Contact your business owner to get set up.</p>
    </div>

    <template v-else>
      <div class="bg-white border-b border-slate-200">
        <div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <p class="text-xs font-semibold uppercase tracking-[0.28em] text-cyan-600">
            {{ employeeStore.business?.name || 'Your Business' }}
          </p>
          <div class="mt-2 flex flex-wrap items-center gap-3">
            <span
              class="rounded-xl px-3 py-1 text-xs font-semibold"
              :class="statusBadgeClass(employeeStore.activeListing.status)"
            >
              {{ statusLabel(employeeStore.activeListing.status) }}
            </span>
            <h1 class="text-2xl font-bold text-slate-900 sm:text-3xl">
              {{ employeeStore.activeListing.title }}
            </h1>
          </div>
          <p v-if="employeeStore.activeListing.address" class="mt-2 flex items-center gap-1.5 text-sm text-slate-500">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 shrink-0 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a2 2 0 01-2.828 0l-4.243-4.243a8 8 0 1111.314 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            {{ [employeeStore.activeListing.address?.city, employeeStore.activeListing.address?.country].filter(Boolean).join(', ') }}
          </p>
        </div>
      </div>

      <div class="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8 space-y-8">

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
            <p class="mt-2 text-3xl font-bold text-slate-900">{{ employeeStore.activeListing.review_count ?? 0 }}</p>
          </div>
          <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <p class="text-sm font-medium text-slate-500">Avg Rating</p>
            <p class="mt-2 text-3xl font-bold text-amber-500">
              {{ employeeStore.activeListing.avg_rating ? employeeStore.activeListing.avg_rating.toFixed(1) : '—' }}
            </p>
          </div>
        </div>

        <ListingServicesSection
          :listing="employeeStore.activeListing"
          @services-changed="handleServicesChanged"
        />

      </div>
    </template>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useEmployeeStore } from '../stores/employee'
import ListingServicesSection from '../components/services/ListingServicesSection.vue'

const employeeStore = useEmployeeStore()

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

// Services
const services = ref([])

function handleServicesChanged(nextServices) {
  services.value = nextServices
}
</script>
