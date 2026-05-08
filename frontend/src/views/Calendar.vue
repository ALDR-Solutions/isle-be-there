<template>
  <div class="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
    <div class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-[0.25em] text-slate-500">
          Trips
        </p>
        <h1 class="mt-2 text-3xl font-bold text-slate-900">Travel Calendar</h1>
        <p class="mt-2 max-w-2xl text-sm text-slate-500">
          See approved bookings and saved itinerary stops in one place.
        </p>
      </div>

      <div class="flex flex-wrap gap-3">
        <router-link
          to="/bookings"
          class="inline-flex items-center rounded-2xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
        >
          View Bookings
        </router-link>
        <button
          type="button"
          class="inline-flex items-center rounded-2xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800"
          @click="refreshCalendar"
        >
          Refresh
        </button>
      </div>
    </div>

    <div
      v-if="error"
      class="mt-6 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
    >
      {{ error }}
    </div>

    <div class="mt-8 grid gap-8 xl:grid-cols-[minmax(0,1.7fr)_340px]">
      <div class="overflow-hidden rounded-[28px] border border-slate-200 bg-white shadow-sm">
        <div class="flex flex-wrap items-center gap-4 border-b border-slate-200 px-6 py-4">
          <div class="flex items-center gap-3 text-sm text-slate-600">
            <span class="inline-flex items-center gap-2">
              <span class="h-3 w-3 rounded-full bg-emerald-600"></span>
              Bookings
            </span>
            <span class="inline-flex items-center gap-2">
              <span class="h-3 w-3 rounded-full bg-violet-600"></span>
              Saved itineraries
            </span>
            <span class="inline-flex items-center gap-2">
              <span class="h-3 w-3 rounded-full bg-blue-600"></span>
              Draft itineraries
            </span>
          </div>
          <p v-if="calendarLoading" class="text-sm text-slate-400">Updating calendar…</p>
        </div>

        <div class="calendar-shell px-2 py-4 sm:px-4">
          <FullCalendar :options="calendarOptions" />
        </div>
      </div>

      <div class="space-y-6">
        <section class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
          <div class="flex items-center justify-between gap-3">
            <div>
              <p class="text-sm font-semibold uppercase tracking-[0.22em] text-slate-400">
                Selected Event
              </p>
              <h2 class="mt-2 text-lg font-bold text-slate-900">
                {{ selectedEvent ? selectedEvent.title : "Pick an event" }}
              </h2>
            </div>
            <span
              v-if="selectedEvent"
              class="rounded-full px-3 py-1 text-xs font-semibold capitalize"
              :style="{
                backgroundColor: `${selectedEvent.color}18`,
                color: selectedEvent.color,
              }"
            >
              {{ selectedEvent.source }}
            </span>
          </div>

          <div v-if="selectedEvent" class="mt-5 space-y-4 text-sm text-slate-600">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                When
              </p>
              <p class="mt-1 font-medium text-slate-800">
                {{ formatDateTime(selectedEvent.start) }}
              </p>
              <p class="text-slate-500">
                to {{ formatDateTime(selectedEvent.end) }}
              </p>
            </div>

            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                Status
              </p>
              <p class="mt-1 font-medium capitalize text-slate-800">
                {{ selectedEvent.status }}
              </p>
            </div>

            <div v-if="selectedEvent.details?.service_name || selectedEvent.details?.listing_title">
              <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                Linked Details
              </p>
              <p v-if="selectedEvent.details?.service_name" class="mt-1">
                Service: <span class="font-medium text-slate-800">{{ selectedEvent.details.service_name }}</span>
              </p>
              <p v-if="selectedEvent.details?.listing_title">
                Listing: <span class="font-medium text-slate-800">{{ selectedEvent.details.listing_title }}</span>
              </p>
              <p v-if="selectedEvent.details?.itinerary_title">
                Itinerary: <span class="font-medium text-slate-800">{{ selectedEvent.details.itinerary_title }}</span>
              </p>
            </div>

            <div v-if="selectedEvent.details?.estimated_cost !== undefined && selectedEvent.details?.estimated_cost !== null">
              <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                Estimated Cost
              </p>
              <p class="mt-1 font-medium text-slate-800">
                {{ formatCurrency(selectedEvent.details.estimated_cost) }}
              </p>
            </div>

            <div v-if="selectedEvent.details?.reason_tags?.length">
              <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                Tags
              </p>
              <div class="mt-2 flex flex-wrap gap-2">
                <span
                  v-for="tag in selectedEvent.details.reason_tags"
                  :key="tag"
                  class="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700"
                >
                  {{ tag }}
                </span>
              </div>
            </div>
          </div>

          <p v-else class="mt-5 text-sm text-slate-500">
            Click a booking or itinerary stop to inspect it here.
          </p>
        </section>

        <section class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
          <div class="flex items-center justify-between gap-3">
            <div>
              <p class="text-sm font-semibold uppercase tracking-[0.22em] text-slate-400">
                Saved Itineraries
              </p>
              <h2 class="mt-2 text-lg font-bold text-slate-900">Trip Plans</h2>
            </div>
            <button
              type="button"
              class="text-sm font-semibold text-slate-600 transition hover:text-slate-900"
              @click="fetchItineraries"
            >
              Reload
            </button>
          </div>

          <div v-if="itinerariesLoading" class="mt-5 space-y-3">
            <div
              v-for="n in 3"
              :key="n"
              class="h-20 animate-pulse rounded-2xl bg-slate-100"
            ></div>
          </div>

          <div v-else-if="itineraries.length === 0" class="mt-5 rounded-2xl bg-slate-50 px-4 py-5 text-sm text-slate-500">
            Saved itineraries will appear here once you persist them through the itinerary planner flow.
          </div>

          <div v-else class="mt-5 space-y-3">
            <article
              v-for="itinerary in itineraries"
              :key="itinerary.id"
              class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4"
            >
              <div class="flex items-start justify-between gap-3">
                <div class="min-w-0">
                  <h3 class="truncate text-sm font-semibold text-slate-900">
                    {{ itinerary.title }}
                  </h3>
                  <p class="mt-1 text-xs text-slate-500">
                    {{ formatDate(itinerary.start_date) }} to {{ formatDate(itinerary.end_date) }}
                  </p>
                </div>
                <span
                  class="rounded-full px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em]"
                  :class="itinerary.status === 'saved' ? 'bg-violet-100 text-violet-700' : 'bg-blue-100 text-blue-700'"
                >
                  {{ itinerary.status }}
                </span>
              </div>

              <div class="mt-3 flex items-center justify-between text-xs text-slate-500">
                <span>{{ itinerary.item_count }} stops</span>
                <span>{{ formatCurrency(itinerary.total_estimated_cost) }}</span>
              </div>
            </article>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import FullCalendar from "@fullcalendar/vue3";
import dayGridPlugin from "@fullcalendar/daygrid";
import interactionPlugin from "@fullcalendar/interaction";
import listPlugin from "@fullcalendar/list";
import timeGridPlugin from "@fullcalendar/timegrid";

import { calendarAPI, itinerariesAPI } from "../services/api";

const events = ref([]);
const itineraries = ref([]);
const selectedEvent = ref(null);
const calendarLoading = ref(false);
const itinerariesLoading = ref(false);
const error = ref("");
const visibleRange = ref({ start: null, end: null });

const calendarOptions = computed(() => ({
  plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin, listPlugin],
  initialView: "dayGridMonth",
  headerToolbar: {
    left: "prev,next today",
    center: "title",
    right: "dayGridMonth,timeGridWeek,listWeek",
  },
  events: events.value.map((event) => ({
    id: event.id,
    title: event.title,
    start: event.start,
    end: event.end,
    backgroundColor: event.color,
    borderColor: event.color,
    extendedProps: event,
  })),
  height: "auto",
  eventClick: handleEventClick,
  datesSet: handleDatesSet,
  dayMaxEvents: true,
  nowIndicator: true,
}));

async function fetchCalendarEvents() {
  if (!visibleRange.value.start || !visibleRange.value.end) {
    return;
  }

  calendarLoading.value = true;
  error.value = "";

  try {
    const response = await calendarAPI.getAll({
      start: visibleRange.value.start,
      end: visibleRange.value.end,
    });
    events.value = Array.isArray(response.data) ? response.data : [];
  } catch (err) {
    error.value = "Failed to load calendar events.";
  } finally {
    calendarLoading.value = false;
  }
}

async function fetchItineraries() {
  itinerariesLoading.value = true;

  try {
    const response = await itinerariesAPI.getAll();
    itineraries.value = Array.isArray(response.data) ? response.data : [];
  } catch (err) {
    error.value = "Failed to load saved itineraries.";
  } finally {
    itinerariesLoading.value = false;
  }
}

function handleDatesSet(info) {
  visibleRange.value = {
    start: info.startStr,
    end: info.endStr,
  };
  fetchCalendarEvents();
}

function handleEventClick(info) {
  selectedEvent.value = info.event.extendedProps;
}

function refreshCalendar() {
  fetchCalendarEvents();
  fetchItineraries();
}

function formatDate(value) {
  return new Date(value).toLocaleDateString();
}

function formatDateTime(value) {
  return new Date(value).toLocaleString();
}

function formatCurrency(value) {
  const amount = Number(value ?? 0);
  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  }).format(Number.isFinite(amount) ? amount : 0);
}

onMounted(() => {
  fetchItineraries();
});
</script>

<style scoped>
.calendar-shell :deep(.fc) {
  font-family: inherit;
}

.calendar-shell :deep(.fc-toolbar-title) {
  font-size: 1.1rem;
  font-weight: 700;
  color: #0f172a;
}

.calendar-shell :deep(.fc-button) {
  border-radius: 0.9rem;
  border: 1px solid #cbd5e1;
  background: white;
  color: #334155;
  box-shadow: none;
  padding: 0.55rem 0.9rem;
}

.calendar-shell :deep(.fc-button:hover),
.calendar-shell :deep(.fc-button:focus) {
  background: #f8fafc;
  color: #0f172a;
  box-shadow: none;
}

.calendar-shell :deep(.fc-button-primary:not(:disabled).fc-button-active) {
  background: #0f172a;
  border-color: #0f172a;
  color: white;
}

.calendar-shell :deep(.fc-theme-standard td),
.calendar-shell :deep(.fc-theme-standard th),
.calendar-shell :deep(.fc-theme-standard .fc-scrollgrid) {
  border-color: #e2e8f0;
}

.calendar-shell :deep(.fc-daygrid-event),
.calendar-shell :deep(.fc-timegrid-event) {
  border-radius: 0.65rem;
  padding: 0.15rem 0.35rem;
}
</style>
