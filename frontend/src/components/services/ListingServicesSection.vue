<template>
  <div>
    <div class="mb-6 flex items-center justify-between">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.28em] text-cyan-600">Listing</p>
        <h2 class="mt-1 text-xl font-bold text-slate-900">Services</h2>
      </div>
      <p
        v-if="readOnly"
        class="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-amber-700"
      >
        Read only while suspended
      </p>
      <button
        v-else
        @click="openServiceModal()"
        :disabled="!listing?.id"
        class="inline-flex items-center gap-2 rounded-2xl bg-cyan-400 px-5 py-2.5 text-sm font-semibold text-slate-950 transition hover:-translate-y-0.5 hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:translate-y-0"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4" />
        </svg>
        Add Service
      </button>
    </div>

    <div v-if="loading" class="rounded-3xl border border-slate-200 bg-white px-6 py-20 text-center">
      <svg class="mx-auto h-7 w-7 animate-spin text-cyan-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
      </svg>
      <p class="mt-4 text-sm font-medium text-slate-500">Loading services...</p>
    </div>

    <div v-else-if="services.length === 0" class="rounded-3xl border-2 border-dashed border-slate-200 bg-white px-6 py-20 text-center">
      <div class="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-100">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
      </div>
      <p class="mt-4 text-base font-semibold text-slate-700">No services yet</p>
      <p class="mt-1.5 text-sm text-slate-400">
        {{ readOnly ? 'No services are available for this suspended listing.' : 'Add the first service for this listing.' }}
      </p>
    </div>

    <div v-else class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="service in services"
        :key="service.service_id"
        class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
        :class="{ 'opacity-60': service.status === 'inactive' }"
      >
        <img
          v-if="service.image_urls?.length"
          :src="service.image_urls[0]"
          alt="Service image"
          class="mb-4 h-40 w-full rounded-2xl object-cover"
        />
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0">
            <p class="truncate text-base font-bold text-slate-900">{{ service.name }}</p>
            <div class="mt-1 flex flex-wrap gap-2 text-xs text-slate-400">
              <span v-if="service.capacity != null">Default capacity {{ service.capacity }}</span>
              <span v-if="typeSummary(service)">{{ typeSummary(service) }}</span>
            </div>
          </div>
          <span
            class="shrink-0 rounded-xl px-2.5 py-1 text-xs font-semibold"
            :class="service.status === 'active' ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-500'"
          >
            {{ service.status === 'active' ? 'Active' : 'Inactive' }}
          </span>
        </div>

        <p v-if="service.description" class="mt-3 text-sm leading-6 text-slate-500 line-clamp-2">{{ service.description }}</p>

        <div v-if="availabilitySummary(service)" class="mt-3 rounded-2xl bg-slate-50 px-4 py-3 text-xs text-slate-500">
          {{ availabilitySummary(service) }}
        </div>

        <div class="mt-4 space-y-1">
          <p class="text-xl font-bold text-slate-900">${{ formatCurrency(service.price) }}</p>
          <p v-if="service.season_price != null" class="text-sm font-medium text-cyan-600">
            Seasonal price: ${{ formatCurrency(service.season_price) }}
          </p>
        </div>

        <div v-if="!readOnly" class="mt-4 flex flex-wrap gap-2">
          <button
            @click="openServiceModal(service)"
            :disabled="isActionPending(service.service_id)"
            class="rounded-xl border border-slate-200 px-3 py-1.5 text-xs font-semibold text-slate-700 transition hover:border-slate-300 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
          >
            Edit
          </button>
          <button
            @click="toggleServiceStatus(service)"
            :disabled="isActionPending(service.service_id)"
            class="rounded-xl border px-3 py-1.5 text-xs font-semibold transition disabled:cursor-not-allowed disabled:opacity-60"
            :class="service.status === 'inactive'
              ? 'border-emerald-100 text-emerald-600 hover:bg-emerald-50'
              : 'border-amber-100 text-amber-600 hover:bg-amber-50'"
          >
            {{ service.status === 'inactive' ? 'Reactivate' : 'Deactivate' }}
          </button>
          <button
            @click="openDeleteServiceModal(service)"
            :disabled="isActionPending(service.service_id)"
            class="rounded-xl border border-red-100 px-3 py-1.5 text-xs font-semibold text-red-500 transition hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-60"
          >
            Delete
          </button>
        </div>
      </div>
    </div>

    <div
      v-if="showServiceModal"
      class="fixed inset-0 z-50 flex items-center justify-center px-4"
      @click.self="closeServiceModal"
    >
      <div class="absolute inset-0 bg-slate-950/50 backdrop-blur-sm"></div>
      <div class="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-3xl border border-slate-200 bg-white shadow-2xl no-scrollbar">
        <div class="sticky top-0 z-10 flex items-center justify-between border-b border-slate-100 bg-white px-8 py-6">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.28em] text-cyan-600">
              {{ editingService ? 'Edit Service' : 'New Service' }}
            </p>
            <h2 class="mt-1 text-xl font-bold text-slate-900">
              {{ editingService ? 'Update service details' : 'Add a service' }}
            </h2>
          </div>
          <button
            @click="closeServiceModal"
            class="flex h-9 w-9 items-center justify-center rounded-2xl border border-slate-200 text-slate-500 transition hover:bg-slate-50"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form @submit.prevent="submitService" class="px-8 py-6 space-y-5">
          <div>
            <label class="mb-1.5 block text-sm font-semibold text-slate-700">Service Name <span class="text-red-500">*</span></label>
            <input
              v-model="serviceForm.name"
              type="text"
              placeholder="e.g. Airport Transfer"
              class="w-full rounded-2xl border px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition"
              :class="serviceErrors.name ? 'border-red-300 bg-red-50 focus:border-red-400' : 'border-slate-200 bg-white focus:border-cyan-400'"
            />
            <p v-if="serviceErrors.name" class="mt-1.5 text-xs text-red-500">{{ serviceErrors.name }}</p>
          </div>

          <div>
            <label class="mb-1.5 block text-sm font-semibold text-slate-700">Description</label>
            <textarea
              v-model="serviceForm.description"
              rows="3"
              placeholder="Describe this service..."
              class="w-full resize-none rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400"
            ></textarea>
          </div>

          <div>
            <label class="mb-1.5 block text-sm font-semibold text-slate-700">Service Images</label>
            <div
              class="relative flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 py-10 text-center transition"
              :class="serviceImageDragging
                ? 'border-cyan-400 bg-cyan-50'
                : 'border-slate-200 bg-slate-50 hover:border-slate-300 hover:bg-white'"
              @dragover.prevent="serviceImageDragging = true"
              @dragleave.prevent="serviceImageDragging = false"
              @drop.prevent="onServiceImageDrop"
              @click="openServiceImagePicker"
            >
              <input
                ref="serviceImageInputRef"
                type="file"
                accept="image/*"
                multiple
                class="hidden"
                @change="onServiceImageChange"
              />
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="mb-3 h-10 w-10 text-slate-300"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="1.5"
                  d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
              <p class="text-sm font-semibold text-slate-600">Drag & drop images here</p>
              <p class="mt-1 text-xs text-slate-400">or click to browse files</p>
              <p
                v-if="serviceImageUploadingCount > 0"
                class="mt-2 text-xs font-semibold text-cyan-600"
              >
                Uploading {{ serviceImageUploadingCount }} file{{ serviceImageUploadingCount > 1 ? 's' : '' }}...
              </p>
            </div>
            <p
              v-if="pendingServiceImages.length > 0"
              class="mt-2 text-xs font-semibold text-cyan-600"
            >
              {{ pendingServiceImages.length }} new image{{ pendingServiceImages.length > 1 ? 's' : '' }}
              ready to upload when you save.
            </p>
            <div
              v-if="serviceDisplayImages.length"
              class="mt-3 grid grid-cols-3 gap-3 sm:grid-cols-4"
            >
              <div
                v-for="image in serviceDisplayImages"
                :key="image.key"
                class="group relative aspect-square overflow-hidden rounded-2xl border border-slate-200 bg-slate-100"
              >
                <img
                  :src="image.url"
                  class="h-full w-full cursor-zoom-in object-cover"
                  @click="openServiceImagePreview(image.key)"
                />
                <div
                  v-if="image.isPending"
                  class="absolute left-1.5 top-1.5 rounded-full bg-cyan-500/90 px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.18em] text-white"
                >
                  New
                </div>
                <button
                  type="button"
                  @click.stop="showServiceRemoveConfirmation(image)"
                  class="absolute right-1.5 top-1.5 flex h-6 w-6 items-center justify-center rounded-full bg-slate-900/70 text-white opacity-0 transition group-hover:opacity-100"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-3 w-3"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2.5"
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <div class="grid gap-4 sm:grid-cols-3">
            <div>
              <label class="mb-1.5 block text-sm font-semibold text-slate-700">Base Price (USD) <span class="text-red-500">*</span></label>
              <div class="relative">
                <span class="absolute left-4 top-1/2 -translate-y-1/2 text-sm font-semibold text-slate-400">$</span>
                <input
                  v-model="serviceForm.price"
                  type="number"
                  min="0"
                  step="0.01"
                  placeholder="0.00"
                  class="w-full rounded-2xl border px-8 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition"
                  :class="serviceErrors.price ? 'border-red-300 bg-red-50 focus:border-red-400' : 'border-slate-200 bg-white focus:border-cyan-400'"
                />
              </div>
              <p v-if="serviceErrors.price" class="mt-1.5 text-xs text-red-500">{{ serviceErrors.price }}</p>
            </div>

            <div>
              <label class="mb-1.5 block text-sm font-semibold text-slate-700">Seasonal Price (USD)</label>
              <div class="relative">
                <span class="absolute left-4 top-1/2 -translate-y-1/2 text-sm font-semibold text-slate-400">$</span>
                <input
                  v-model="serviceForm.season_price"
                  type="number"
                  min="0"
                  step="0.01"
                  placeholder="0.00"
                  class="w-full rounded-2xl border border-slate-200 bg-white px-8 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400"
                />
              </div>
            </div>

            <div>
              <label class="mb-1.5 block text-sm font-semibold text-slate-700">Default Capacity</label>
              <input
                v-model="serviceForm.capacity"
                type="number"
                min="0"
                placeholder="e.g. 4"
                class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400"
              />
              <p class="mt-1.5 text-xs text-slate-500">
                Used as the general capacity, and as the fallback when a slot does not override it.
              </p>
            </div>
          </div>

          <div>
            <label class="mb-2 block text-sm font-semibold text-slate-700">Status</label>
            <div class="flex gap-3">
              <button
                type="button"
                @click="serviceForm.status = 'active'"
                class="flex-1 rounded-2xl border py-2.5 text-sm font-semibold transition"
                :class="serviceForm.status === 'active' ? 'border-emerald-400 bg-emerald-50 text-emerald-700' : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300'"
              >
                Active
              </button>
              <button
                type="button"
                @click="serviceForm.status = 'inactive'"
                class="flex-1 rounded-2xl border py-2.5 text-sm font-semibold transition"
                :class="serviceForm.status === 'inactive' ? 'border-slate-400 bg-slate-100 text-slate-700' : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300'"
              >
                Inactive
              </button>
            </div>
          </div>

          <div v-if="isHotelType" class="space-y-4 rounded-2xl border border-slate-200 bg-slate-50 p-6">
            <div>
              <p class="text-sm font-semibold uppercase tracking-[0.2em] text-cyan-600">Hotel Service Details</p>
              <p class="mt-1 text-xs text-slate-500">Stored in `type_data` for hotel listings.</p>
            </div>

            <div>
              <label class="mb-1.5 block text-sm font-semibold text-slate-700">Room Type</label>
              <input
                v-model="serviceForm.room_type"
                type="text"
                placeholder="e.g. Deluxe Ocean View"
                class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400"
              />
            </div>

            <div>
              <label class="mb-1.5 block text-sm font-semibold text-slate-700">Room Amenities</label>
              <div class="flex gap-2">
                <input
                  v-model="roomAmenityInput"
                  @keydown.enter.prevent="addListValue('room_amenities', roomAmenityInput)"
                  type="text"
                  placeholder="e.g. Balcony"
                  class="flex-1 rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400"
                />
                <button
                  type="button"
                  @click="addListValue('room_amenities', roomAmenityInput)"
                  class="rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
                >
                  Add
                </button>
              </div>
              <div v-if="serviceForm.room_amenities.length" class="mt-3 flex flex-wrap gap-2">
                <span
                  v-for="(amenity, index) in serviceForm.room_amenities"
                  :key="`${amenity}-${index}`"
                  class="flex items-center gap-1.5 rounded-full bg-white px-3 py-1 text-xs font-medium text-slate-700"
                >
                  {{ amenity }}
                  <button type="button" @click="removeListValue('room_amenities', index)" class="text-slate-400 hover:text-slate-700">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </span>
              </div>
            </div>
          </div>

          <!-- Service Slots Section (inline) -->
          <div v-if="!isHotelType" class="space-y-4 rounded-2xl border border-slate-200 bg-slate-50 p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-semibold uppercase tracking-[0.2em] text-cyan-600">Service Slots</p>
                <p class="mt-1 text-xs text-slate-500">
                  {{ editingService ? 'Define time slots for this service.' : 'Add slots now and they will be created when you save the service.' }}
                </p>
              </div>
              <span v-if="loadingSlots" class="text-xs text-slate-400">Loading...</span>
            </div>

            <!-- Day Tabs -->
            <div class="flex gap-1 flex-wrap">
              <button
                v-for="(name, idx) in slotDayNames"
                :key="idx"
                type="button"
                @click="selectedSlotDay = idx"
                class="rounded-lg px-3 py-1.5 text-xs font-semibold transition border"
                :class="selectedSlotDay === idx
                  ? 'border-cyan-400 bg-cyan-50 text-cyan-700'
                  : 'border-slate-200 bg-white text-slate-500 hover:border-slate-300'"
              >
                {{ name }}
                <span v-if="slotCountForDay(idx) > 0" class="ml-1 rounded-full bg-cyan-100 text-cyan-700 px-1.5 py-0.5 text-[10px]">
                  {{ slotCountForDay(idx) }}
                </span>
              </button>
            </div>

            <!-- Slots for selected day -->
            <div v-if="serviceSlots.length > 0 && slotsForSelectedDay().length > 0" class="space-y-2">
              <div
                v-for="slot in slotsForSelectedDay()"
                :key="slot.id"
                class="flex items-center justify-between rounded-lg border border-slate-200 bg-white px-4 py-3"
              >
                <div class="flex-1">
                  <span class="font-medium text-slate-700">{{ slotDayNames[slot.day_of_week] }}</span>
                  <span class="ml-2 text-slate-600">
                    {{ formatSlotTime(slot.start_time) }} - {{ formatSlotTime(slot.end_time) }}
                  </span>
                  <span class="ml-2 text-xs text-slate-400">Capacity {{ slot.capacity }}</span>
                </div>
                <div class="flex items-center gap-2">
                  <button
                    type="button"
                    @click="startEditingSlot(slot)"
                    class="text-xs text-slate-600 hover:text-slate-800 font-medium"
                  >
                    Edit
                  </button>
                  <!-- Copy single slot to another day -->
                  <div class="relative" :ref="'copySlotDropup-' + slot.id">
                    <button
                      type="button"
                      @click="toggleCopySlotDropup(slot.id)"
                      class="text-xs text-cyan-600 hover:text-cyan-700 font-medium"
                    >
                      Copy
                    </button>
                    <div v-if="activeCopySlotDropup === slot.id" class="absolute right-0 mt-1 z-10 bg-white rounded-lg border border-slate-200 shadow-sm p-1 min-w-[120px]">
                      <button
                        v-for="item in availableCopyDays(slot)"
                        :key="item.idx"
                        type="button"
                        @click="handleCopySlotToDay(slot, item.idx)"
                        class="block w-full text-left px-3 py-1.5 text-xs hover:bg-cyan-50 rounded-md"
                      >
                        {{ item.name }}
                      </button>
                    </div>
                  </div>
                  <button
                    type="button"
                    @click="handleDeleteSlot(slot.id)"
                    class="text-xs text-red-500 hover:text-red-600"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
            <p v-else class="text-sm text-slate-400">No slots for {{ slotDayNames[selectedSlotDay] }}.</p>

            <!-- Add Slot Form -->
            <div class="rounded-lg border border-slate-200 bg-white p-4 space-y-3">
              <div class="flex items-center justify-between gap-3">
                <h4 class="text-sm font-medium text-slate-700">
                  {{ editingSlotId ? `Edit Slot for ${slotDayNames[selectedSlotDay]}` : `Add New Slot for ${slotDayNames[selectedSlotDay]}` }}
                </h4>
                <button
                  v-if="editingSlotId"
                  type="button"
                  @click="resetSlotEditor"
                  class="text-xs font-medium text-slate-500 transition hover:text-slate-700"
                >
                  Cancel Edit
                </button>
              </div>

              <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
                <div>
                  <label class="block text-xs text-slate-500 mb-1">Start Time</label>
                  <input
                    type="time"
                    v-model="newSlot.startTime"
                    class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-cyan-400 focus:outline-none"
                    step="300"
                  />
                </div>
                <div>
                  <label class="block text-xs text-slate-500 mb-1">End Time</label>
                  <input
                    type="time"
                    v-model="newSlot.endTime"
                    class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-cyan-400 focus:outline-none"
                    step="300"
                  />
                </div>
                <div>
                  <label class="block text-xs text-slate-500 mb-1">Capacity</label>
                  <input
                    type="number"
                    min="1"
                    v-model="newSlot.capacity"
                    placeholder="Defaults to the service default capacity"
                    class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-cyan-400 focus:outline-none"
                  />
                </div>
              </div>

              <p v-if="slotValidationError" class="text-xs text-red-500">{{ slotValidationError }}</p>

              <div class="flex flex-col gap-3 sm:flex-row">
                <button
                  type="button"
                  @click="handleAddSlot"
                  class="w-full rounded-lg bg-cyan-500 px-4 py-2 text-sm font-medium text-white hover:bg-cyan-600"
                >
                  {{ editingSlotId ? 'Save Slot Changes' : `Add Slot for ${slotDayNames[selectedSlotDay]}` }}
                </button>
                <button
                  v-if="editingSlotId"
                  type="button"
                  @click="resetSlotEditor"
                  class="w-full rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
                >
                  Keep Current Slot
                </button>
              </div>
            </div>
          </div>

          <p v-if="serviceErrors.submit" class="text-sm text-red-500">{{ serviceErrors.submit }}</p>

          <div class="flex gap-3 pt-2">
            <button
              type="button"
              @click="closeServiceModal"
              :disabled="modalSubmitting"
              class="flex-1 rounded-2xl border border-slate-200 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="modalSubmitting"
              class="flex-1 rounded-2xl bg-slate-900 py-3 text-sm font-semibold text-white transition hover:-translate-y-0.5 hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:translate-y-0"
            >
              {{ modalSubmitting ? 'Saving...' : editingService ? 'Save Changes' : 'Add Service' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div
      v-if="showServiceImagePreviewModal && activeServicePreviewImage"
      class="fixed inset-0 z-[60] flex items-center justify-center px-4"
      @click.self="closeServiceImagePreview"
    >
      <div class="absolute inset-0 bg-slate-950/85 backdrop-blur-sm"></div>
      <div class="relative flex w-full max-w-5xl items-center justify-center">
        <button
          type="button"
          @click="closeServiceImagePreview"
          class="absolute right-0 top-0 z-10 flex h-10 w-10 items-center justify-center rounded-full bg-slate-900/70 text-white transition hover:bg-slate-800"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        <button
          v-if="serviceDisplayImages.length > 1"
          type="button"
          @click.stop="showPreviousServiceImage"
          class="absolute left-0 z-10 flex h-11 w-11 items-center justify-center rounded-full bg-slate-900/70 text-white transition hover:bg-slate-800"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </button>

        <img
          :src="activeServicePreviewImage.url"
          class="max-h-[85vh] max-w-full rounded-3xl object-contain shadow-2xl"
        />

        <button
          v-if="serviceDisplayImages.length > 1"
          type="button"
          @click.stop="showNextServiceImage"
          class="absolute right-0 z-10 flex h-11 w-11 items-center justify-center rounded-full bg-slate-900/70 text-white transition hover:bg-slate-800"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>

    <div
      v-if="showServiceRemoveImageConfirmation && serviceImagePendingRemoval"
      class="fixed inset-0 z-[70] flex items-center justify-center px-4"
      @click.self="cancelServiceRemoveImage"
    >
      <div class="absolute inset-0 bg-slate-950/60 backdrop-blur-sm"></div>
      <div class="relative w-full max-w-lg overflow-hidden rounded-3xl border border-slate-200 bg-white text-left shadow-2xl">
        <div class="px-6 py-6 sm:px-7">
          <div class="sm:flex sm:items-start">
            <div class="mx-auto flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-red-500/10 sm:mx-0 sm:h-10 sm:w-10">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="1.5"
                  d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z"
                />
              </svg>
            </div>
            <div class="mt-3 text-center sm:ml-4 sm:mt-0 sm:text-left">
              <h3 class="text-base font-semibold text-slate-900">Remove image?</h3>
              <div class="mt-2 space-y-2">
                <p class="text-sm text-slate-600">This image will be removed from the service now.</p>
                <p class="text-sm text-slate-500">
                  If you save this edit, the image will be permanently deleted from storage. If you cancel the edit instead, the image will stay.
                </p>
              </div>
            </div>
          </div>
        </div>
        <div class="border-t border-slate-100 bg-slate-50 px-6 py-4 sm:flex sm:flex-row-reverse sm:px-7">
          <button
            type="button"
            @click="confirmServiceRemoveImage"
            class="inline-flex w-full justify-center rounded-2xl bg-red-500 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-red-400 sm:ml-3 sm:w-auto"
          >
            Remove Image
          </button>
          <button
            type="button"
            @click="cancelServiceRemoveImage"
            class="mt-3 inline-flex w-full justify-center rounded-2xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 sm:mt-0 sm:w-auto"
          >
            Keep Image
          </button>
        </div>
      </div>
    </div>

    <div
      v-if="showDeleteServiceModal"
      class="fixed inset-0 z-[70] flex items-center justify-center px-4"
      @click.self="!deleteSubmitting && closeDeleteServiceModal()"
    >
      <div class="absolute inset-0 bg-slate-950/60 backdrop-blur-sm"></div>
      <div class="relative w-full max-w-lg overflow-hidden rounded-3xl border border-slate-200 bg-white text-left shadow-2xl">
        <div class="px-6 py-6 sm:px-7">
          <div class="sm:flex sm:items-start">
            <div class="mx-auto flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-red-500/10 sm:mx-0 sm:h-10 sm:w-10">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="1.5"
                  d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z"
                />
              </svg>
            </div>
            <div class="mt-3 text-center sm:ml-4 sm:mt-0 sm:text-left">
              <h3 class="text-base font-semibold text-slate-900">Delete service?</h3>
              <div class="mt-2 space-y-2">
                <p class="text-sm text-slate-600">
                  This will permanently remove
                  <span class="font-semibold text-slate-900">{{ serviceToDelete?.name || 'this service' }}</span>
                  from this listing.
                </p>
                <p class="text-sm text-slate-500">
                  Any saved service slots for this service will no longer be usable.
                </p>
              </div>
            </div>
          </div>
        </div>
        <div class="border-t border-slate-100 bg-slate-50 px-6 py-4 sm:flex sm:flex-row-reverse sm:px-7">
          <button
            type="button"
            @click="confirmDeleteService"
            :disabled="deleteSubmitting"
            class="inline-flex w-full justify-center rounded-2xl bg-red-500 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-red-400 disabled:cursor-not-allowed disabled:opacity-60 sm:ml-3 sm:w-auto"
          >
            {{ deleteSubmitting ? 'Deleting...' : 'Delete Service' }}
          </button>
          <button
            type="button"
            @click="closeDeleteServiceModal"
            :disabled="deleteSubmitting"
            class="mt-3 inline-flex w-full justify-center rounded-2xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-60 sm:mt-0 sm:w-auto"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue'

import { servicesAPI, availabilityAPI } from '../../services/api'
import { useImageManager } from '../../composables/useImageManager'
import { useToastStore } from '../../stores/toast'

const props = defineProps({
  listing: {
    type: Object,
    default: null,
  },
  readOnly: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['services-changed'])

const toastStore = useToastStore()

const availableDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

const services = ref([])
const loading = ref(false)
const showServiceModal = ref(false)
const editingService = ref(null)
const modalSubmitting = ref(false)
const actionServiceId = ref(null)
const showDeleteServiceModal = ref(false)
const serviceToDelete = ref(null)
const deleteSubmitting = ref(false)
const serviceErrors = ref({})
const roomAmenityInput = ref('')
const serviceSlots = ref([])
const loadingSlots = ref(false)
const slotDayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
const newSlot = ref(blankSlotForm())
const slotValidationError = ref('')
const selectedSlotDay = ref(1) // Default to Monday
const activeCopySlotDropup = ref(null)
const localSlotIdCounter = ref(0)
const editingSlotId = ref(null)

const businessTypeName = computed(() => props.listing?.business_type_name ?? '')
const isHotelType = computed(() => businessTypeName.value === 'Hotel')
const readOnly = computed(() => props.readOnly)

function blankSlotForm(defaultCapacity = '') {
  return {
    day: 1,
    startTime: '09:00',
    endTime: '17:00',
    capacity: defaultCapacity === '' || defaultCapacity == null ? '' : String(defaultCapacity),
  }
}

function sortSlots(slots) {
  return [...slots].sort((a, b) => {
    if (a.day_of_week !== b.day_of_week) return a.day_of_week - b.day_of_week
    return String(a.start_time ?? '').localeCompare(String(b.start_time ?? ''))
  })
}

const blankServiceForm = () => ({
  name: '',
  description: '',
  price: '',
  season_price: '',
  capacity: '',
  status: 'active',
  available_days: [],
  availability_notes: '',
  room_type: '',
  room_amenities: [],
  image_urls: [],
})

const serviceForm = ref(blankServiceForm())
const {
  fileInputRef: serviceImageInputRef,
  isDragging: serviceImageDragging,
  uploadingCount: serviceImageUploadingCount,
  pendingImages: pendingServiceImages,
  imagePendingRemoval: serviceImagePendingRemoval,
  originalPayload: originalServicePayload,
  showImagePreviewModal: showServiceImagePreviewModal,
  showRemoveImageConfirmation: showServiceRemoveImageConfirmation,
  displayImages: serviceDisplayImages,
  activePreviewImage: activeServicePreviewImage,
  resetImageUi: resetServiceImageUi,
  setOriginalState: setOriginalServiceState,
  clearOriginalState: clearOriginalServiceState,
  onFileChange: onServiceImageChange,
  onDrop: onServiceImageDrop,
  uploadPendingImages: uploadPendingServiceImages,
  cleanupUploadedImages: cleanupUploadedServiceImages,
  deleteImagesOrThrow: deleteServiceImagesOrThrow,
  getMergedImageUrls: getMergedServiceImageUrls,
  getRemovedOriginalUrls: getRemovedOriginalServiceImageUrls,
  openFilePicker: openServiceImagePicker,
  openImagePreview: openServiceImagePreview,
  closeImagePreview: closeServiceImagePreview,
  showPreviousImage: showPreviousServiceImage,
  showNextImage: showNextServiceImage,
  showRemoveConfirmation: showServiceRemoveConfirmation,
  cancelRemoveImage: cancelServiceRemoveImage,
  confirmRemoveImage: confirmServiceRemoveImage,
} = useImageManager({
  form: serviceForm,
  imageField: 'image_urls',
  folder: 'services',
})

function setServices(nextServices) {
  services.value = nextServices
  emit('services-changed', nextServices)
}

function normalizeStringArray(value) {
  if (!Array.isArray(value)) return []
  return value.map((item) => String(item).trim()).filter(Boolean)
}

function normalizeAvailability(availability) {
  if (!availability || typeof availability !== 'object') return null
  const available_days = normalizeStringArray(availability.available_days)
  const notes = typeof availability.notes === 'string' ? availability.notes.trim() : ''
  if (!available_days.length && !notes) return null
  return {
    available_days,
    notes: notes || null,
  }
}

function mapServiceToForm(service) {
  const availability = normalizeAvailability(service.availability) ?? { available_days: [], notes: '' }
  const typeData = service.type_data && typeof service.type_data === 'object' ? service.type_data : {}

  return {
    name: service.name ?? '',
    description: service.description ?? '',
    price: service.price ?? '',
    season_price: service.season_price ?? '',
    capacity: service.capacity ?? '',
    status: service.status ?? 'active',
    available_days: availability.available_days ?? [],
    availability_notes: availability.notes ?? '',
    room_type: typeData.room_type ?? '',
    room_amenities: normalizeStringArray(typeData.room_amenities),
    image_urls: Array.isArray(service.image_urls) ? service.image_urls.filter(Boolean) : [],
  }
}

function buildAvailabilityPayload() {
  const available_days = normalizeStringArray(serviceForm.value.available_days)
  const notes = serviceForm.value.availability_notes.trim()
  if (!available_days.length && !notes) return null
  return {
    available_days,
    notes: notes || null,
  }
}

function buildTypeDataPayload() {
  if (isHotelType.value) {
    const room_type = serviceForm.value.room_type.trim()
    const room_amenities = normalizeStringArray(serviceForm.value.room_amenities)
    if (!room_type && !room_amenities.length) return null
    return {
      room_type: room_type || null,
      room_amenities,
    }
  }

  return null
}

function buildServicePayload(uploadedUrls = [], { includeListingId = true } = {}) {
  const payload = {
    name: serviceForm.value.name.trim(),
    description: serviceForm.value.description.trim() || null,
    price: Number(serviceForm.value.price),
    season_price: serviceForm.value.season_price === '' ? null : Number(serviceForm.value.season_price),
    capacity: serviceForm.value.capacity === '' ? null : Number(serviceForm.value.capacity),
    status: serviceForm.value.status,
    availability: buildAvailabilityPayload(),
    type_data: buildTypeDataPayload(),
    image_urls: getMergedServiceImageUrls(uploadedUrls),
  }

  if (includeListingId) {
    payload.listing_id = props.listing.id
  }

  return payload
}

function normalizeSlotTimeValue(time) {
  if (!time) return ''
  return time.length === 5 ? `${time}:00` : time
}

function buildPendingSlot(dayOverride, overrides = {}) {
  const day = dayOverride !== undefined ? dayOverride : selectedSlotDay.value
  localSlotIdCounter.value += 1
  return {
    id: `local-slot-${localSlotIdCounter.value}`,
    service_id: null,
    day_of_week: day,
    start_time: normalizeSlotTimeValue(overrides.start_time ?? newSlot.value.startTime),
    end_time: normalizeSlotTimeValue(overrides.end_time ?? newSlot.value.endTime),
    capacity: overrides.capacity ?? getSlotCapacity(),
  }
}

function getSlotCapacity() {
  const parsedSlotCapacity = Number(newSlot.value.capacity)
  if (Number.isFinite(parsedSlotCapacity) && parsedSlotCapacity > 0) {
    return parsedSlotCapacity
  }

  const parsedCapacity = Number(serviceForm.value.capacity)
  return Number.isFinite(parsedCapacity) && parsedCapacity > 0 ? parsedCapacity : 1
}

function validateServiceForm() {
  const errors = {}

  if (!serviceForm.value.name.trim()) {
    errors.name = 'Service name is required.'
  }

  const price = Number(serviceForm.value.price)
  if (serviceForm.value.price === '' || Number.isNaN(price) || price < 0) {
    errors.price = 'Please enter a valid base price.'
  }

  serviceErrors.value = errors
  return Object.keys(errors).length === 0
}

async function fetchServices(listingId = props.listing?.id) {
  if (!listingId) {
    setServices([])
    return
  }

  loading.value = true
  try {
    const response = await servicesAPI.getAll({ listing_id: listingId })
    setServices(Array.isArray(response.data) ? response.data : [])
  } catch (error) {
    console.error('Failed to load services', error)
    setServices([])
    toastStore.show(error.response?.data?.detail || 'Failed to load services.', 'error')
  } finally {
    loading.value = false
  }
}

watch(
  () => props.listing?.id,
  (listingId) => {
    closeServiceModal()
    fetchServices(listingId)
  },
  { immediate: true }
)

watch(
  () => readOnly.value,
  (nextReadOnly) => {
    if (nextReadOnly) {
      closeServiceModal()
    }
  }
)

function openServiceModal(service = null) {
  if (!props.listing?.id || readOnly.value) return
  editingService.value = service
  serviceForm.value = service ? mapServiceToForm(service) : blankServiceForm()
  resetServiceImageUi()
  serviceErrors.value = {}
  roomAmenityInput.value = ''
  slotValidationError.value = ''
  editingSlotId.value = null
  selectedSlotDay.value = 1
  newSlot.value = blankSlotForm(serviceForm.value.capacity)
  activeCopySlotDropup.value = null
  showServiceModal.value = true
  setOriginalServiceState({
    imageUrls: serviceForm.value.image_urls,
    payload: service ? buildServicePayload([], { includeListingId: false }) : null,
  })

  if (service) {
    loadingSlots.value = true
    availabilityAPI.getServiceSlots(service.service_id)
      .then(response => { serviceSlots.value = sortSlots(response.data || []) })
      .catch(err => { console.error('Failed to load slots', err); serviceSlots.value = [] })
      .finally(() => { loadingSlots.value = false })
  } else {
    serviceSlots.value = []
    loadingSlots.value = false
  }
}

function closeServiceModal() {
  resetServiceImageUi()
  clearOriginalServiceState()
  showServiceModal.value = false
  editingService.value = null
  serviceErrors.value = {}
  roomAmenityInput.value = ''
  serviceSlots.value = []
  loadingSlots.value = false
  slotValidationError.value = ''
  editingSlotId.value = null
  selectedSlotDay.value = 1
  newSlot.value = blankSlotForm()
  activeCopySlotDropup.value = null
}

function openDeleteServiceModal(service) {
  if (readOnly.value || isActionPending(service.service_id)) return
  serviceToDelete.value = service
  showDeleteServiceModal.value = true
}

function closeDeleteServiceModal() {
  if (deleteSubmitting.value) return
  showDeleteServiceModal.value = false
  serviceToDelete.value = null
}

async function rollbackServiceUpdate() {
  if (!editingService.value?.service_id || !originalServicePayload.value) return
  const rollbackResponse = await servicesAPI.update(
    editingService.value.service_id,
    originalServicePayload.value,
  )
  setServices(
    services.value.map((service) =>
      service.service_id === rollbackResponse.data.service_id ? rollbackResponse.data : service
    )
  )
}

async function syncSlotsForCreatedService(service) {
  if (!service?.service_id || serviceSlots.value.length === 0) {
    return []
  }

  const createdSlots = []
  for (const slot of serviceSlots.value) {
    const payload = {
      day_of_week: slot.day_of_week,
      service_id: service.service_id,
      start_time: normalizeSlotTimeValue(slot.start_time),
      end_time: normalizeSlotTimeValue(slot.end_time),
      capacity: slot.capacity,
    }
    const response = await availabilityAPI.createServiceSlot(service.service_id, payload)
    createdSlots.push(response.data)
  }
  return createdSlots
}

async function submitService() {
  if (!props.listing?.id || readOnly.value || !validateServiceForm()) return

  modalSubmitting.value = true
  serviceErrors.value = {}
  let uploadedUrls = []

  try {
    uploadedUrls = await uploadPendingServiceImages()
    const payload = buildServicePayload(uploadedUrls)

    if (editingService.value) {
      const removedOriginalUrls = getRemovedOriginalServiceImageUrls(payload.image_urls)
      const response = await servicesAPI.update(editingService.value.service_id, payload)
      try {
        await deleteServiceImagesOrThrow(removedOriginalUrls)
      } catch (deleteError) {
        await rollbackServiceUpdate()
        await cleanupUploadedServiceImages(uploadedUrls)
        uploadedUrls = []
        throw deleteError
      }
      setServices(
        services.value.map((service) =>
          service.service_id === response.data.service_id ? response.data : service
        )
      )
      toastStore.show('Service updated.', 'success')
    } else {
      const response = await servicesAPI.create(payload)
      const createdService = response.data
      let createdSlots = []

      setServices([...services.value, createdService])
      editingService.value = createdService
      setOriginalServiceState({
        imageUrls: createdService.image_urls ?? [],
        payload: buildServicePayload([], { includeListingId: false }),
      })

      try {
        createdSlots = await syncSlotsForCreatedService(createdService)
      } catch (slotError) {
        try {
          const slotResponse = await availabilityAPI.getServiceSlots(createdService.service_id)
          serviceSlots.value = sortSlots(Array.isArray(slotResponse.data) ? slotResponse.data : [])
        } catch (loadError) {
          console.error('Failed to reload slots after slot creation error', loadError)
        }

        serviceErrors.value.submit =
          slotError.response?.data?.detail ||
          'Service was created, but at least one slot could not be saved. You can fix the slots and save again.'
        toastStore.show('Service created, but some slots could not be saved.', 'error')
        return
      }

      serviceSlots.value = sortSlots(createdSlots)
      toastStore.show(
        createdSlots.length ? 'Service and slots added.' : 'Service added.',
        'success'
      )
    }

    closeServiceModal()
  } catch (error) {
    console.error('Failed to save service', error)
    const urlsToCleanup = uploadedUrls.length ? uploadedUrls : (error.uploadedUrls ?? [])
    await cleanupUploadedServiceImages(urlsToCleanup)
    serviceErrors.value.submit = error.response?.data?.detail || 'Failed to save service. Please try again.'
    toastStore.show('Failed to save service.', 'error')
  } finally {
    modalSubmitting.value = false
  }
}

function isActionPending(serviceId) {
  return actionServiceId.value === serviceId
}

async function toggleServiceStatus(service) {
  if (readOnly.value || isActionPending(service.service_id)) return

  const nextStatus = service.status === 'inactive' ? 'active' : 'inactive'
  actionServiceId.value = service.service_id
  try {
    const response = nextStatus === 'inactive'
      ? await servicesAPI.deactivate(service.service_id)
      : await servicesAPI.update(service.service_id, { status: nextStatus })
    setServices(
      services.value.map((item) =>
        item.service_id === response.data.service_id ? response.data : item
      )
    )
    toastStore.show(
      nextStatus === 'inactive' ? 'Service deactivated.' : 'Service reactivated.',
      'success'
    )
  } catch (error) {
    console.error('Failed to update service status', error)
    toastStore.show(
      error.response?.data?.detail || 'Failed to update service status.',
      'error'
    )
  } finally {
    actionServiceId.value = null
  }
}

async function confirmDeleteService() {
  if (!serviceToDelete.value || readOnly.value || isActionPending(serviceToDelete.value.service_id)) return

  deleteSubmitting.value = true
  actionServiceId.value = serviceToDelete.value.service_id
  try {
    await servicesAPI.delete(serviceToDelete.value.service_id)
    setServices(services.value.filter((item) => item.service_id !== serviceToDelete.value.service_id))
    showDeleteServiceModal.value = false
    serviceToDelete.value = null
    toastStore.show('Service deleted.', 'info')
  } catch (error) {
    console.error('Failed to delete service', error)
    toastStore.show(error.response?.data?.detail || 'Failed to delete service.', 'error')
  } finally {
    actionServiceId.value = null
    deleteSubmitting.value = false
  }
}

function toggleAvailableDay(day) {
  const nextDays = [...serviceForm.value.available_days]
  const index = nextDays.indexOf(day)
  if (index === -1) nextDays.push(day)
  else nextDays.splice(index, 1)
  serviceForm.value.available_days = nextDays
}

function addListValue(field, inputRef) {
  const value = inputRef.value.trim()
  if (!value) return

  const current = normalizeStringArray(serviceForm.value[field])
  if (!current.includes(value)) {
    serviceForm.value[field] = [...current, value]
  }
  inputRef.value = ''
}

function removeListValue(field, index) {
  const nextValues = [...serviceForm.value[field]]
  nextValues.splice(index, 1)
  serviceForm.value[field] = nextValues
}

function formatCurrency(value) {
  const numericValue = Number(value ?? 0)
  return Number.isFinite(numericValue) ? numericValue.toFixed(2) : '0.00'
}

function formatSlotTime(time) {
  if (!time) return ''
  return time.substring(0, 5)
}

function validateSlotForm() {
  if (newSlot.value.startTime >= newSlot.value.endTime) {
    slotValidationError.value = 'Start time must be before end time'
    return false
  }
  if (getSlotCapacity() < 1) {
    slotValidationError.value = 'Slot capacity must be at least 1'
    return false
  }
  slotValidationError.value = ''
  return true
}

function resetSlotEditor() {
  editingSlotId.value = null
  newSlot.value = blankSlotForm(serviceForm.value.capacity)
  slotValidationError.value = ''
}

function slotsForSelectedDay() {
  return serviceSlots.value.filter(s => s.day_of_week === selectedSlotDay.value)
}

function slotCountForDay(day) {
  return serviceSlots.value.filter(s => s.day_of_week === day).length
}

function availableCopyDays(slot) {
  return slotDayNames
    .map((name, idx) => ({ name, idx }))
    .filter(({ idx }) => {
      if (idx === slot.day_of_week) return false
      const existing = serviceSlots.value.find(
        s => s.day_of_week === idx && s.start_time === slot.start_time && s.end_time === slot.end_time
      )
      return !existing
    })
}

function buildSlotPayload(dayOverride) {
  const day = dayOverride !== undefined ? dayOverride : selectedSlotDay.value
  return {
    day_of_week: day,
    service_id: editingService.value?.service_id ?? null,
    start_time: normalizeSlotTimeValue(newSlot.value.startTime),
    end_time: normalizeSlotTimeValue(newSlot.value.endTime),
    capacity: getSlotCapacity(),
  }
}

function startEditingSlot(slot) {
  editingSlotId.value = slot.id
  selectedSlotDay.value = slot.day_of_week
  newSlot.value = {
    day: slot.day_of_week,
    startTime: formatSlotTime(slot.start_time),
    endTime: formatSlotTime(slot.end_time),
    capacity: slot.capacity == null ? '' : String(slot.capacity),
  }
  slotValidationError.value = ''
}

async function handleAddSlot() {
  if (!validateSlotForm()) return

  if (editingSlotId.value && !editingService.value) {
    serviceSlots.value = sortSlots(
      serviceSlots.value.map((slot) =>
        slot.id === editingSlotId.value
          ? {
              ...slot,
              day_of_week: selectedSlotDay.value,
              start_time: normalizeSlotTimeValue(newSlot.value.startTime),
              end_time: normalizeSlotTimeValue(newSlot.value.endTime),
              capacity: getSlotCapacity(),
            }
          : slot
      )
    )
    toastStore.show('Slot updated.', 'success')
    resetSlotEditor()
    return
  }

  if (editingSlotId.value && editingService.value) {
    try {
      const payload = {
        day_of_week: selectedSlotDay.value,
        start_time: normalizeSlotTimeValue(newSlot.value.startTime),
        end_time: normalizeSlotTimeValue(newSlot.value.endTime),
        capacity: getSlotCapacity(),
      }
      const response = await availabilityAPI.updateServiceSlot(
        editingService.value.service_id,
        editingSlotId.value,
        payload,
      )
      serviceSlots.value = sortSlots(
        serviceSlots.value.map((slot) => (slot.id === editingSlotId.value ? response.data : slot))
      )
      toastStore.show('Slot updated.', 'success')
      resetSlotEditor()
    } catch (error) {
      console.error('Failed to update slot', error)
      slotValidationError.value = error.response?.data?.detail || 'Failed to update slot'
      toastStore.show(error.response?.data?.detail || 'Failed to update slot', 'error')
    }
    return
  }

  if (!editingService.value) {
    serviceSlots.value = sortSlots([...serviceSlots.value, buildPendingSlot()])
    toastStore.show('Slot added to the new service.', 'success')
    resetSlotEditor()
    return
  }

  try {
    const payload = buildSlotPayload()
    const response = await availabilityAPI.createServiceSlot(editingService.value.service_id, payload)
    serviceSlots.value = sortSlots([...serviceSlots.value, response.data])
    toastStore.show('Slot added', 'success')
    resetSlotEditor()
  } catch (error) {
    console.error('Failed to add slot', error)
    toastStore.show(error.response?.data?.detail || 'Failed to add slot', 'error')
  }
}

async function handleCopySlotToDay(slot, targetDay) {
  activeCopySlotDropup.value = null

  if (!editingService.value) {
    serviceSlots.value = sortSlots([
      ...serviceSlots.value,
      buildPendingSlot(targetDay, {
        start_time: slot.start_time,
        end_time: slot.end_time,
        capacity: slot.capacity,
      }),
    ])
    toastStore.show('Slot copied', 'success')
    return
  }

  try {
    const payload = {
      day_of_week: targetDay,
      service_id: editingService.value.service_id,
      start_time: slot.start_time,
      end_time: slot.end_time,
      capacity: slot.capacity
    }
    const response = await availabilityAPI.createServiceSlot(editingService.value.service_id, payload)
    serviceSlots.value = sortSlots([...serviceSlots.value, response.data])
    toastStore.show('Slot copied', 'success')
  } catch (error) {
    console.error('Failed to copy slot', error)
    toastStore.show(error.response?.data?.detail || 'Failed to copy slot', 'error')
  }
}

function toggleCopySlotDropup(slotId) {
  activeCopySlotDropup.value = activeCopySlotDropup.value === slotId ? null : slotId
}

async function handleDeleteSlot(slotId) {
  if (editingSlotId.value === slotId) {
    resetSlotEditor()
  }

  if (!editingService.value) {
    serviceSlots.value = serviceSlots.value.filter(s => s.id !== slotId)
    toastStore.show('Slot removed.', 'info')
    return
  }

  try {
    await availabilityAPI.deleteServiceSlot(editingService.value.service_id, slotId)
    serviceSlots.value = serviceSlots.value.filter(s => s.id !== slotId)
    toastStore.show('Slot deleted', 'success')
  } catch (error) {
    console.error('Failed to delete slot', error)
    toastStore.show('Failed to delete slot', 'error')
  }
}

function availabilitySummary(service) {
  const availability = normalizeAvailability(service.availability)
  if (!availability) return ''

  const dayLabel = availability.available_days.length ? availability.available_days.join(', ') : ''
  if (dayLabel && availability.notes) return `${dayLabel} - ${availability.notes}`
  return dayLabel || availability.notes || ''
}

function typeSummary(service) {
  const typeData = service.type_data && typeof service.type_data === 'object' ? service.type_data : {}

  if (businessTypeName.value === 'Hotel') {
    const parts = []
    if (typeData.room_type) parts.push(typeData.room_type)
    if (Array.isArray(typeData.room_amenities) && typeData.room_amenities.length) {
      parts.push(typeData.room_amenities.join(', '))
    }
    return parts.join(' | ')
  }

  return ''
}

onBeforeUnmount(() => {
  resetServiceImageUi()
})
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
</style>
