<template>
  <div class="bg-slate-50 min-h-screen">

    <div v-if="loading" class="flex min-h-screen items-center justify-center">
      <svg class="h-8 w-8 animate-spin text-cyan-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
      </svg>
    </div>

    <template v-else>
      <!-- Header -->
      <div class="bg-white border-b border-slate-200">
        <div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <p class="text-xs font-semibold uppercase tracking-[0.28em] text-cyan-600">
            {{ businessStore.business?.business_name || 'Your Business' }}
          </p>
          <div class="mt-2 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <h1 class="text-2xl font-bold text-slate-900 sm:text-3xl">Employees</h1>
            <button
              @click="openAddModal"
              class="inline-flex items-center gap-2 rounded-2xl bg-cyan-400 px-6 py-3 text-sm font-semibold text-slate-950 transition hover:-translate-y-0.5 hover:bg-cyan-300"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4" />
              </svg>
              Add Employee
            </button>
          </div>
        </div>
      </div>

      <div class="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">

        <!-- Empty state -->
        <div v-if="employees.length === 0" class="rounded-3xl border-2 border-dashed border-slate-200 bg-white px-6 py-20 text-center">
          <div class="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-100">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <p class="mt-4 text-base font-semibold text-slate-700">No employees yet</p>
          <p class="mt-1.5 text-sm text-slate-400">Add your first employee and assign them to a listing.</p>
        </div>

        <!-- Employee grid -->
        <div v-else class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <div
            v-for="emp in employees"
            :key="emp.id"
            class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
          >
            <div class="flex items-center gap-3">
              <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-cyan-500 text-base font-bold text-white">
                {{ (emp.first_name || emp.email || '?').charAt(0).toUpperCase() }}
              </div>
              <div class="min-w-0 flex-1">
                <p class="truncate text-sm font-semibold text-slate-900">
                  {{ [emp.first_name, emp.last_name].filter(Boolean).join(' ') || '—' }}
                </p>
                <p class="truncate text-xs text-slate-500">{{ emp.email }}</p>
              </div>
            </div>

            <!-- Assigned listings pills -->
            <div class="mt-4">
              <p class="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Assigned to</p>
              <div v-if="emp.assignedListings?.length" class="flex flex-wrap gap-2">
                <span
                  v-for="listing in emp.assignedListings"
                  :key="listing.id"
                  class="flex items-center gap-1 rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-700"
                >
                  {{ listing.title }}
                  <button
                    type="button"
                    @click="unassign(emp, listing)"
                    class="ml-0.5 text-slate-400 hover:text-red-500 transition"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </span>
              </div>
              <p v-else class="text-xs text-slate-400">Not assigned to any listing</p>
            </div>

            <div class="mt-5">
              <button
                @click="openAssignModal(emp)"
                class="w-full rounded-2xl border border-slate-200 py-2 text-xs font-semibold text-slate-700 transition hover:bg-slate-50"
              >
                Assign to Listing
              </button>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Add Employee Modal -->
    <div
      v-if="showAddModal"
      class="fixed inset-0 z-50 flex items-center justify-center px-4"
      @click.self="closeAddModal"
    >
      <div class="absolute inset-0 bg-slate-950/50 backdrop-blur-sm"></div>
      <div class="relative w-full max-w-lg max-h-[90vh] overflow-y-auto rounded-3xl border border-slate-200 bg-white shadow-2xl no-scrollbar">
        <div class="sticky top-0 z-10 flex items-center justify-between border-b border-slate-100 bg-white px-8 py-6">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.28em] text-cyan-600">Team</p>
            <h2 class="mt-1 text-xl font-bold text-slate-900">Add an employee</h2>
          </div>
          <button @click="closeAddModal" class="flex h-9 w-9 items-center justify-center rounded-2xl border border-slate-200 text-slate-500 transition hover:bg-slate-50">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <form @submit.prevent="submitAdd" class="px-8 py-6 space-y-5">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-1.5">First Name</label>
              <input v-model="addForm.first_name" type="text" placeholder="Jane"
                class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400" />
            </div>
            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-1.5">Last Name</label>
              <input v-model="addForm.last_name" type="text" placeholder="Doe"
                class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-1.5">Username</label>
            <input v-model="addForm.username" type="text" placeholder="janedoe"
              class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400" />
          </div>
          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-1.5">Email Address <span class="text-red-500">*</span></label>
            <input v-model="addForm.email" type="email" required placeholder="jane@example.com"
              class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400" />
          </div>
          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-1.5">Password <span class="text-red-500">*</span></label>
            <input v-model="addForm.password" type="password" required placeholder="••••••••"
              class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400" />
          </div>
          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-1.5">Phone</label>
            <input v-model="addForm.phone" type="tel" placeholder="+1 246 555 0100"
              class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400" />
          </div>
          <p v-if="addError" class="text-sm text-red-500 text-center">{{ addError }}</p>
          <div class="flex gap-3 pt-2">
            <button type="button" @click="closeAddModal"
              class="flex-1 rounded-2xl border border-slate-200 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50">
              Cancel
            </button>
            <button type="submit" :disabled="addSubmitting"
              class="flex-1 rounded-2xl bg-slate-900 py-3 text-sm font-semibold text-white transition hover:-translate-y-0.5 hover:bg-slate-800 disabled:opacity-50">
              {{ addSubmitting ? 'Adding...' : 'Add Employee' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Assign to Listing Modal -->
    <div
      v-if="showAssignModal"
      class="fixed inset-0 z-50 flex items-center justify-center px-4"
      @click.self="closeAssignModal"
    >
      <div class="absolute inset-0 bg-slate-950/50 backdrop-blur-sm"></div>
      <div class="relative w-full max-w-md max-h-[90vh] overflow-y-auto rounded-3xl border border-slate-200 bg-white shadow-2xl no-scrollbar">
        <div class="sticky top-0 z-10 flex items-center justify-between border-b border-slate-100 bg-white px-8 py-6">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.28em] text-cyan-600">Assign</p>
            <h2 class="mt-1 text-xl font-bold text-slate-900">
              {{ [assignTarget?.first_name, assignTarget?.last_name].filter(Boolean).join(' ') || assignTarget?.email }}
            </h2>
          </div>
          <button @click="closeAssignModal" class="flex h-9 w-9 items-center justify-center rounded-2xl border border-slate-200 text-slate-500 transition hover:bg-slate-50">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="px-8 py-6 space-y-3">
          <p class="text-sm text-slate-500">Select a listing to assign this employee to.</p>
          <div
            v-for="listing in businessStore.listings"
            :key="listing.id"
            class="flex items-center justify-between rounded-2xl border px-4 py-3 transition"
            :class="isAssigned(assignTarget, listing) ? 'border-cyan-400 bg-cyan-50' : 'border-slate-200 bg-white hover:bg-slate-50'"
          >
            <div>
              <p class="text-sm font-semibold text-slate-900">{{ listing.title }}</p>
              <p class="text-xs text-slate-400">{{ listing.address?.city }}, {{ listing.address?.country }}</p>
            </div>
            <span v-if="isAssigned(assignTarget, listing)" class="text-xs font-semibold text-cyan-600">Assigned</span>
            <button
              v-else
              @click="assign(assignTarget, listing)"
              :disabled="assignSubmitting"
              class="rounded-xl bg-slate-900 px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-slate-800 disabled:opacity-50"
            >
              Assign
            </button>
          </div>
          <p v-if="assignError" class="text-sm text-red-500 text-center">{{ assignError }}</p>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { employeesAPI } from '../services/api'
import { useBusinessStore } from '../stores/business'
import { useToastStore } from '../stores/toast'

const businessStore = useBusinessStore()
const toastStore = useToastStore()

const employees = ref([])
const loading = ref(true)

async function loadEmployees() {
  loading.value = true
  try {
    const res = await employeesAPI.getAll()
    const list = res.data ?? []
    // Fetch assigned listings for each employee in parallel
    const withListings = await Promise.all(
      list.map(async (emp) => {
        try {
          const lr = await employeesAPI.getListings(emp.employee_id)
          return { ...emp, assignedListings: lr.data ?? [] }
        } catch {
          return { ...emp, assignedListings: [] }
        }
      })
    )
    employees.value = withListings
  } catch (e) {
    console.error('Failed to load employees', e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadEmployees()
})

// ── Add Employee ────────────────────────────────────────────────────────────
const showAddModal = ref(false)
const addSubmitting = ref(false)
const addError = ref('')
const blankAddForm = () => ({ first_name: '', last_name: '', username: '', email: '', password: '', phone: '' })
const addForm = ref(blankAddForm())

function openAddModal() {
  addForm.value = blankAddForm()
  addError.value = ''
  showAddModal.value = true
}

function closeAddModal() {
  showAddModal.value = false
}

async function submitAdd() {
  addError.value = ''
  addSubmitting.value = true
  try {
    const res = await employeesAPI.create({
      email: addForm.value.email,
      password: addForm.value.password,
      username: addForm.value.username || undefined,
      first_name: addForm.value.first_name || undefined,
      last_name: addForm.value.last_name || undefined,
      phone: addForm.value.phone || undefined,
    })
    employees.value.unshift({ ...res.data, assignedListings: [] })
    toastStore.show('Employee added successfully.', 'success')
    closeAddModal()
  } catch (e) {
    addError.value = e.response?.data?.detail || 'Failed to add employee. Please try again.'
  } finally {
    addSubmitting.value = false
  }
}

// ── Assign / Unassign ────────────────────────────────────────────────────────
const showAssignModal = ref(false)
const assignTarget = ref(null)
const assignSubmitting = ref(false)
const assignError = ref('')

function openAssignModal(emp) {
  assignTarget.value = emp
  assignError.value = ''
  showAssignModal.value = true
}

function closeAssignModal() {
  showAssignModal.value = false
  assignTarget.value = null
}

function isAssigned(emp, listing) {
  return emp?.assignedListings?.some(l => l.id === listing.id)
}

async function assign(emp, listing) {
  assignSubmitting.value = true
  assignError.value = ''
  try {
    await employeesAPI.assignToListing(emp.employee_id, listing.id)
    const idx = employees.value.findIndex(e => e.id === emp.id)
    if (idx !== -1) {
      employees.value[idx].assignedListings.push(listing)
    }
    toastStore.show(`Assigned to ${listing.title}.`, 'success')
  } catch (e) {
    assignError.value = e.response?.data?.detail || 'Failed to assign employee.'
  } finally {
    assignSubmitting.value = false
  }
}

async function unassign(emp, listing) {
  try {
    await employeesAPI.unassignFromListing(emp.employee_id, listing.id)
    const idx = employees.value.findIndex(e => e.id === emp.id)
    if (idx !== -1) {
      employees.value[idx].assignedListings = employees.value[idx].assignedListings.filter(l => l.id !== listing.id)
    }
    toastStore.show(`Removed from ${listing.title}.`, 'info')
  } catch (e) {
    toastStore.show(e.response?.data?.detail || 'Failed to unassign employee.', 'error')
  }
}
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
</style>
