<template>
  <div class="bg-slate-50 text-slate-900">
    <section
      class="relative overflow-hidden border-b border-slate-200 bg-slate-950"
      style="
        background-image:
          linear-gradient(rgba(2, 6, 23, 0.72), rgba(2, 6, 23, 0.82)),
          url(&quot;/images/beach-bkg.jpg&quot;);
        background-size: cover;
        background-position: center;
      "
    >
      <div
        class="mx-auto flex min-h-[320px] max-w-7xl flex-col justify-end px-4 pb-10 pt-24 sm:px-6 lg:px-8"
      >
        <p
          class="text-xs font-semibold uppercase tracking-[0.3em] text-cyan-300"
        >
          Itinerary builder
        </p>
        <h1
          class="mt-4 max-w-3xl text-4xl font-bold leading-tight text-white sm:text-5xl"
        >
          Shape your Caribbean trip one choice at a time
        </h1>
        <p class="mt-5 max-w-2xl text-base leading-7 text-slate-200">
          Pick your interests, dates, travelers, and trip style. We will turn
          those choices into a day-by-day preview.
        </p>
      </div>
    </section>

    <section class="px-4 py-10 sm:px-6 lg:px-8">
      <div v-if="!generatedItinerary" class="mx-auto max-w-7xl">
        <ItineraryWizardShell
          :title="activeStep.title"
          :description="activeStep.description"
          :current-step="currentStepIndex"
          :total-steps="steps.length"
          :can-go-back="currentStepIndex > 0"
          :next-label="nextLabel"
          :busy-label="busyLabel"
          :busy="isGenerating || isLoadingCountryInterests"
          :next-disabled="nextDisabled"
          :error="errorMessage"
          @back="goBack"
          @next="goNext"
        >
          <!-- Categories Modal -->
          <transition :name="slideDirection" mode="out-in">
            <div :key="activeStep.key">
              <div v-if="activeStep.type === 'categories'">
                <div
                  v-if="loadingInterests"
                  class="flex min-h-[280px] items-center justify-center"
                >
                  <div class="text-center">
                    <div
                      class="inline-block h-9 w-9 animate-spin rounded-full border-4 border-slate-200 border-t-cyan-500"
                    ></div>
                    <p class="mt-4 text-sm font-medium text-slate-500">
                      Loading categories...
                    </p>
                  </div>
                </div>

                <div
                  v-else-if="categoryNames.length === 0"
                  class="rounded-3xl border border-slate-200 bg-slate-50 px-6 py-12 text-center text-slate-500"
                >
                  No interest categories are available right now.
                </div>

                <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  <button
                    v-for="category in categoryCards"
                    :key="category.name"
                    type="button"
                    class="group flex min-h-40 flex-col justify-between rounded-3xl border p-5 text-left shadow-sm transition hover:-translate-y-0.5"
                    :class="
                      isCategorySelected(category.name)
                        ? 'border-cyan-400 bg-cyan-50 text-cyan-900 shadow-cyan-100'
                        : 'border-slate-200 bg-white text-slate-700 hover:border-slate-300'
                    "
                    @click="toggleCategory(category.name)"
                  >
                    <span class="flex items-start justify-between gap-4">
                      <span>
                        <span class="text-lg font-bold capitalize">{{
                          category.name
                        }}</span>
                        <span
                          v-if="category.description"
                          class="mt-2 block max-w-[24ch] text-sm font-medium leading-6 text-slate-500"
                        >
                          {{ category.description }}
                        </span>
                      </span>
                      <span
                        class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full border"
                        :class="
                          isCategorySelected(category.name)
                            ? 'border-cyan-500 bg-cyan-500 text-white'
                            : 'border-slate-300 text-transparent'
                        "
                      >
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          class="h-3.5 w-3.5"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            fill-rule="evenodd"
                            d="M16.704 5.29a1 1 0 010 1.42l-7.25 7.25a1 1 0 01-1.42 0l-3.25-3.25a1 1 0 111.42-1.42l2.54 2.55 6.54-6.55a1 1 0 011.42 0z"
                            clip-rule="evenodd"
                          />
                        </svg>
                      </span>
                    </span>
                    <span class="mt-8 text-sm font-medium text-slate-500">
                      {{ groupedInterests[category.name]?.length || 0 }}
                      {{
                        groupedInterests[category.name]?.length === 1
                          ? "interest"
                          : "interests"
                      }}
                    </span>
                  </button>
                </div>
              </div>

              <!-- Interest Modal -->
              <div v-else-if="activeStep.type === 'interests'">
                <div
                  class="mb-6 flex flex-col justify-between gap-4 sm:flex-row sm:items-end"
                >
                  <div>
                    <p class="text-sm font-semibold text-slate-500">
                      {{ selectedInterestIds.length }}
                      {{
                        selectedInterestIds.length === 1
                          ? "interest"
                          : "interests"
                      }}
                      selected
                    </p>
                    <div class="mt-3 flex flex-wrap gap-2">
                      <span
                        v-for="category in selectedCategories"
                        :key="category"
                        class="rounded-full bg-cyan-50 px-3 py-1 text-xs font-semibold capitalize text-cyan-700"
                      >
                        {{ category }}
                      </span>
                    </div>
                  </div>
                  <p class="text-sm font-medium text-slate-500">
                    Interest set {{ activeStep.pageIndex + 1 }} of
                    {{ interestPages.length }}
                  </p>
                </div>

                <div class="grid gap-3 sm:grid-cols-2">
                  <label
                    v-for="interest in activeInterestPage"
                    :key="interest.id"
                    class="cursor-pointer"
                  >
                    <input
                      v-model="selectedInterestIds"
                      type="checkbox"
                      :value="interest.id"
                      class="peer sr-only"
                    />
                    <span
                      class="flex min-h-20 items-center justify-between gap-4 rounded-2xl border border-slate-200 bg-white px-5 py-4 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-cyan-300 hover:bg-cyan-50 peer-checked:border-cyan-500 peer-checked:bg-cyan-50 peer-checked:text-cyan-800"
                    >
                      <span>
                        <span class="block text-base">{{ interest.name }}</span>
                        <span
                          class="mt-1 block text-xs font-medium capitalize text-slate-400"
                          >{{ interest.category }}</span
                        >
                      </span>
                      <span
                        class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full border"
                        :class="
                          isInterestSelected(interest.id)
                            ? 'border-cyan-500 bg-cyan-500 text-white'
                            : 'border-slate-300 text-transparent'
                        "
                      >
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          class="h-3.5 w-3.5"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            fill-rule="evenodd"
                            d="M16.704 5.29a1 1 0 010 1.42l-7.25 7.25a1 1 0 01-1.42 0l-3.25-3.25a1 1 0 111.42-1.42l2.54 2.55 6.54-6.55a1 1 0 011.42 0z"
                            clip-rule="evenodd"
                          />
                        </svg>
                      </span>
                    </span>
                  </label>
                </div>
              </div>

              <!-- Destination and Dates Modal -->
              <div
                v-else-if="activeStep.type === 'destination'"
                class="grid gap-5"
              >
                <div class="grid gap-5 md:grid-cols-2">
                  <label class="block md:col-span-2">
                    <span class="text-sm font-semibold text-slate-700"
                      >Country</span
                    >
                    <select
                      v-model="country"
                      class="mt-2 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-900 outline-none transition focus:border-cyan-500 focus:ring-4 focus:ring-cyan-100"
                    >
                      <option value="">Select a country</option>
                      <option
                        v-for="country in CARIBBEAN_COUNTRIES"
                        :key="country"
                        :value="country"
                      >
                        {{ country }}
                      </option>
                    </select>
                  </label>

                  <label class="block">
                    <span class="text-sm font-semibold text-slate-700"
                      >Start date</span
                    >
                    <input
                      v-model="startDate"
                      type="date"
                      :min="today"
                      class="mt-2 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-900 outline-none transition focus:border-cyan-500 focus:ring-4 focus:ring-cyan-100"
                    />
                  </label>

                  <label class="block">
                    <span class="text-sm font-semibold text-slate-700"
                      >End date</span
                    >
                    <input
                      v-model="endDate"
                      type="date"
                      :min="startDate || today"
                      class="mt-2 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-900 outline-none transition focus:border-cyan-500 focus:ring-4 focus:ring-cyan-100"
                    />
                  </label>
                </div>

                <div class="rounded-3xl border border-slate-200 bg-white p-5">
                  <label class="flex cursor-pointer items-start gap-3">
                    <input
                      v-model="bookableOnly"
                      type="checkbox"
                      class="mt-1 h-4 w-4 rounded border-slate-300 text-cyan-600 focus:ring-cyan-500"
                    />
                    <span>
                      <span class="block text-sm font-semibold text-slate-900">
                        Only show services available for booking
                      </span>
                      <span class="mt-1 block text-sm text-slate-500">
                        Limit interests and itinerary stops to listings with
                        active bookable services.
                      </span>
                    </span>
                  </label>
                </div>

                <div class="rounded-3xl border border-slate-200 bg-white p-5">
                  <p class="text-sm font-semibold text-slate-900">
                    Trip basics
                  </p>
                  <p class="mt-1 text-sm text-slate-500">
                    <template v-if="country && startDate && endDate">
                      Your itinerary will run for {{ tripLengthLabel }} and
                      focus on listings in {{ country }}.
                    </template>
                    <template v-else>
                      Choose a country and travel dates to guide the itinerary.
                    </template>
                  </p>
                </div>
              </div>

              <!-- Traveller Types Modal -->
              <div
                v-else-if="activeStep.type === 'travelers'"
                class="grid gap-5 sm:grid-cols-2"
              >
                <div class="rounded-3xl border border-slate-200 bg-white p-5">
                  <div class="flex items-center justify-between gap-4">
                    <div>
                      <p class="font-bold text-slate-900">Adults</p>
                      <p class="mt-1 text-sm text-slate-500">Ages 13 and up</p>
                    </div>
                    <div class="flex items-center gap-3">
                      <button
                        type="button"
                        class="flex h-10 w-10 items-center justify-center rounded-full border border-slate-200 bg-white text-xl font-semibold text-slate-700 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-40"
                        :disabled="adults <= 1"
                        @click="adults -= 1"
                      >
                        -
                      </button>
                      <span
                        class="w-8 text-center text-lg font-bold text-slate-950"
                        >{{ adults }}</span
                      >
                      <button
                        type="button"
                        class="flex h-10 w-10 items-center justify-center rounded-full bg-slate-950 text-xl font-semibold text-white transition hover:bg-slate-800"
                        @click="adults += 1"
                      >
                        +
                      </button>
                    </div>
                  </div>
                </div>

                <div class="rounded-3xl border border-slate-200 bg-white p-5">
                  <div class="flex items-center justify-between gap-4">
                    <div>
                      <p class="font-bold text-slate-900">Children</p>
                      <p class="mt-1 text-sm text-slate-500">
                        Ages 12 and under
                      </p>
                    </div>
                    <div class="flex items-center gap-3">
                      <button
                        type="button"
                        class="flex h-10 w-10 items-center justify-center rounded-full border border-slate-200 bg-white text-xl font-semibold text-slate-700 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-40"
                        :disabled="children <= 0"
                        @click="children -= 1"
                      >
                        -
                      </button>
                      <span
                        class="w-8 text-center text-lg font-bold text-slate-950"
                        >{{ children }}</span
                      >
                      <button
                        type="button"
                        class="flex h-10 w-10 items-center justify-center rounded-full bg-slate-950 text-xl font-semibold text-white transition hover:bg-slate-800"
                        @click="children += 1"
                      >
                        +
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Budget Level (Simple, Premium) and Trip Pace (Relaxed, Balanced )Modal -->
              <div
                v-else-if="activeStep.type === 'style'"
                class="grid gap-8 lg:grid-cols-2"
              >
                <div>
                  <p class="mb-3 text-sm font-semibold text-slate-700">
                    Budget level
                  </p>
                  <div class="grid gap-3">
                    <label
                      v-for="option in budgetOptions"
                      :key="option.value"
                      class="cursor-pointer"
                    >
                      <input
                        v-model="budgetLevel"
                        type="radio"
                        :value="option.value"
                        class="peer sr-only"
                      />
                      <span
                        class="block rounded-2xl border border-slate-200 bg-white p-5 transition hover:border-cyan-300 peer-checked:border-cyan-500 peer-checked:bg-cyan-50"
                      >
                        <span class="block font-bold text-slate-900">{{
                          option.label
                        }}</span>
                        <span
                          class="mt-2 inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-semibold"
                          :class="getBudgetToneClasses(option.value)"
                        >
                          <CurrencyDollarIcon
                            v-if="option.value === 'low'"
                            class="h-4 w-4 shrink-0"
                          />
                          <CreditCardIcon
                            v-else-if="option.value === 'medium'"
                            class="h-4 w-4 shrink-0"
                          />
                          <SparklesIcon
                            v-else-if="option.value === 'high'"
                            class="h-4 w-4 shrink-0"
                          />
                          ${{ option.dailyTarget}}/day target
                        </span>
                        <span
                          class="mt-1 block text-sm leading-6 text-slate-500"
                          >{{ option.description }}</span
                        >
                      </span>
                    </label>
                  </div>
                </div>

                <div>
                  <p class="mb-3 text-sm font-semibold text-slate-700">
                    Trip pace
                  </p>
                  <div class="grid gap-3">
                    <label
                      v-for="option in paceOptions"
                      :key="option.value"
                      class="cursor-pointer"
                    >
                      <input
                        v-model="pace"
                        type="radio"
                        :value="option.value"
                        class="peer sr-only"
                      />
                      <span
                        class="block rounded-2xl border border-slate-200 bg-white p-5 transition hover:border-cyan-300 peer-checked:border-cyan-500 peer-checked:bg-cyan-50"
                      >
                        <span class="block font-bold text-slate-900">{{
                          option.label
                        }}</span>

                        <span
                          class="mt-2 inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-semibold"
                          :class="getPaceToneClasses(option.value)"
                        >
                          <SunIcon
                            v-if="option.value === 'relaxed'"
                            class="h-4 w-4 shrink-0"
                          />
                          <ScaleIcon
                            v-else-if="option.value === 'balanced'"
                            class="h-4 w-4 shrink-0"
                          />
                          <BoltIcon
                            v-else-if="option.value === 'packed'"
                            class="h-4 w-4 shrink-0"
                          />
                          {{ option.activityLimit }} activities/day
                        </span>
                        <span
                          class="mt-1 block text-sm leading-6 text-slate-500"
                          >{{ option.description }}</span
                        >
                      </span>
                    </label>
                  </div>
                </div>
              </div>

              <!-- Review Modal (To see a preview of your decisions) -->
              <div
                v-else-if="activeStep.type === 'review'"
                class="grid gap-5 lg:grid-cols-2"
              >
                <div class="rounded-3xl border border-slate-200 bg-white p-5">
                  <p
                    class="text-sm font-semibold uppercase tracking-[0.18em] text-cyan-600"
                  >
                    Selections
                  </p>
                  <div class="mt-5 space-y-4 text-sm">
                    <div>
                      <p class="font-semibold text-slate-900">Categories</p>
                      <p class="mt-1 capitalize text-slate-500">
                        {{ selectedCategoriesLabel }}
                      </p>
                    </div>
                    <div>
                      <p class="font-semibold text-slate-900">Interests</p>
                      <p class="mt-1 text-slate-500">
                        {{ selectedInterestNamesLabel }}
                      </p>
                    </div>
                    <div>
                      <p class="font-semibold text-slate-900">Destination</p>
                      <p class="mt-1 text-slate-500">{{ country }}</p>
                    </div>
                    <div>
                      <p class="font-semibold text-slate-900">Dates</p>
                      <p class="mt-1 text-slate-500">
                        {{ startDate }} to {{ endDate }}
                      </p>
                    </div>
                  </div>
                </div>

                <div class="rounded-3xl border border-slate-200 bg-white p-5">
                  <p
                    class="text-sm font-semibold uppercase tracking-[0.18em] text-cyan-600"
                  >
                    Travel style
                  </p>
                  <div class="mt-5 grid gap-3 sm:grid-cols-2">
                    <div class="rounded-2xl bg-slate-50 p-4">
                      <p
                        class="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400"
                      >
                        Travelers
                      </p>
                      <p class="mt-2 font-bold text-slate-900">
                        {{ adults }} adult{{ adults === 1 ? "" : "s" }},
                        {{ children }} child{{ children === 1 ? "" : "ren" }}
                      </p>
                    </div>
                    <div class="rounded-2xl bg-slate-50 p-4">
                      <p
                        class="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400"
                      >
                        Budget
                      </p>
                      <p class="mt-2 font-bold capitalize text-slate-900">
                        {{ budgetLevel }}
                      </p>
                    </div>
                    <div class="rounded-2xl bg-slate-50 p-4 sm:col-span-2">
                      <p
                        class="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400"
                      >
                        Pace
                      </p>
                      <p class="mt-2 font-bold capitalize text-slate-900">
                        {{ pace }}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </transition>
        </ItineraryWizardShell>
      </div>

      <div v-else class="mx-auto max-w-7xl">
        <div
          class="mb-8 flex flex-col justify-between gap-5 lg:flex-row lg:items-end"
        >
          <div>
            <p
              class="text-xs font-semibold uppercase tracking-[0.3em] text-cyan-600"
            >
              {{ savedItinerary ? "Saved itinerary" : "Generated itinerary" }}
            </p>
            <h2 class="mt-3 text-3xl font-bold text-slate-950 sm:text-4xl">
              {{
                savedItinerary?.title ||
                `Your ${generatedItinerary.trip_days} day trip preview`
              }}
            </h2>
            <p class="mt-3 max-w-2xl text-sm leading-6 text-slate-500">
              Estimated total: ${{
                generatedItinerary.total_estimated_cost.toFixed(2)
              }}. Built from the live itinerary planner.
            </p>
          </div>

          <div
            class="flex w-full flex-col gap-3 lg:ml-auto lg:max-w-3xl lg:items-end"
          >
            <div class="flex w-full flex-col gap-3 sm:flex-row lg:justify-end">
              <input
                v-model="itineraryEmail"
                type="email"
                autocomplete="email"
                placeholder="Email itinerary to you@example.com"
                class="w-full min-w-0 rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-900 outline-none transition focus:border-cyan-500 focus:ring-4 focus:ring-cyan-100 lg:max-w-sm"
              />
              <button
                type="button"
                class="shrink-0 rounded-2xl bg-slate-950 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
                :disabled="isSendingEmail"
                @click="handleEmailItinerary"
              >
                {{ isSendingEmail ? "Sending..." : "Send itinerary" }}
              </button>
              <button
                v-if="!savedItinerary"
                type="button"
                class="shrink-0 rounded-2xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
                @click="generatedItinerary = null"
              >
                Adjust answers
              </button>
              <button
                v-if="!savedItinerary"
                type="button"
                class="shrink-0 rounded-2xl bg-slate-950 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
                :disabled="isSaving"
                @click="handleSaveItinerary"
              >
                {{ isSaving ? "Saving..." : "Save itinerary" }}
              </button>
            </div>
          </div>

          <div v-if="savedItinerary">
            <RouterLink
              to="/profile"
              class="rounded-2xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
            >
              Back to profile
            </RouterLink>
          </div>
        </div>

        <div class="grid gap-6">
          <article
            v-for="(day, dayIndex) in generatedItinerary.days"
            :key="day.date"
            class="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm"
          >
            <div
              class="border-b border-slate-200 bg-slate-50 px-5 py-4 sm:px-6"
            >
              <div
                class="flex flex-col justify-between gap-3 sm:flex-row sm:items-center"
              >
                <div>
                  <p
                    class="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-600"
                  >
                    Day {{ dayIndex + 1 }}
                  </p>
                  <h3 class="mt-1 text-xl font-bold text-slate-950">
                    {{ formatDisplayDate(day.date) }}
                  </h3>
                </div>
                <p class="text-sm font-semibold text-slate-500">
                  ${{ day.total_estimated_cost.toFixed(2) }} estimated |
                  {{ day.total_duration_hours }} hours
                </p>
              </div>
            </div>

            <div class="divide-y divide-slate-100">
              <div
                v-for="stop in day.stops"
                :key="stop.listing_id"
                class="grid gap-4 px-5 py-5 sm:grid-cols-[140px_1fr_auto] sm:px-6"
              >
                <div>
                  <p class="text-sm font-bold text-slate-950">
                    {{ stop.start_time }} - {{ stop.end_time }}
                  </p>
                  <p
                    class="mt-1 text-xs font-semibold uppercase tracking-[0.16em] text-slate-400"
                  >
                    {{ stop.business_type_name }}
                  </p>
                </div>

                <div>
                  <h4 class="font-bold text-slate-950">{{ stop.title }}</h4>
                  <p class="mt-1 text-sm font-medium text-slate-500">
                    {{ stop.address?.city }}, {{ stop.address?.country }}
                  </p>
                  <div class="mt-3 flex flex-wrap gap-2">
                    <span
                      v-for="tag in getNormalizedReasonTags(stop.reason_tags)"
                      :key="tag.key"
                      class="rounded-full px-3 py-1 text-xs font-semibold"
                      :class="getTagToneClasses(tag.tone)"
                    >
                      {{ tag.label }}
                    </span>
                  </div>
                </div>

                <p class="text-sm font-bold text-slate-950 sm:text-right">
                  ${{ stop.estimated_cost.toFixed(2) }}
                </p>
              </div>
            </div>
          </article>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import ItineraryWizardShell from "../components/itinerary/ItineraryWizardShell.vue";
import { interestsAPI, itinerariesAPI } from "../services/api";
import { useAuthStore } from "../stores/auth";
import { useToastStore } from "../stores/toast";
import { CARIBBEAN_COUNTRIES } from "../stores/caribbeanLocations";
import { normalizeItineraryTags, getTagToneClasses } from "../utils/itineraryTags";
import { SunIcon, ScaleIcon, BoltIcon, CurrencyDollarIcon, CreditCardIcon, SparklesIcon } from "@heroicons/vue/24/outline";

const router = useRouter();
const authStore = useAuthStore();
const toastStore = useToastStore();

const route = useRoute();
const savedItinerary = ref(null);
const isLoadingSavedItinerary = ref(false);

const allInterests = ref([]);
const availableCategories = ref([]);
const availableInterests = ref([]);
const loadingInterests = ref(true);
const isLoadingCountryInterests = ref(false);
const currentStepIndex = ref(0);
const selectedCategories = ref([]);
const selectedInterestIds = ref([]);

const country = ref("");
const startDate = ref("");
const endDate = ref("");
const bookableOnly = ref(false);
const adults = ref(2);
const children = ref(0);
const budgetLevel = ref("medium");
const pace = ref("balanced");
const generatedItinerary = ref(null);
const isGenerating = ref(false);
const isSaving = ref(false);
const isSendingEmail = ref(false);
const itineraryEmail = ref("");
const lastAutofilledEmail = ref("");
const errorMessage = ref("");
const slideDirection = ref("slide-left");

const countryOptions = ["Barbados", "Guyana", "Jamaica", "Trinidad and Tobago"];

const budgetOptions = [
  {
    value: "low",
    label: "Budget-friendly",
    dailyTarget: 120,
    description: "Prioritize lower-cost stops and lighter spending.",
  },
  {
    value: "medium",
    label: "Balanced",
    dailyTarget: 240,
    description: "Mix affordable picks with standout experiences.",
  },
  {
    value: "high",
    label: "Premium",
    dailyTarget: 420,
    description: "Leave room for higher-end stays, dining, and tours.",
  },
];

const paceOptions = [
  {
    value: "relaxed",
    label: "Relaxed",
    activityLimit: 2,
    description: "Fewer stops with more open time between plans.",
  },
  {
    value: "balanced",
    label: "Balanced",
    activityLimit: 3,
    description: "A steady day with time for both plans and rest.",
  },
  {
    value: "packed",
    label: "Packed",
    activityLimit: 4,
    description: "More stops for travelers who want a fuller schedule.",
  },
];

const today = computed(() => toDateInputValue(new Date()));

onMounted(async () => {
  if (route.params.id) {
    await loadSavedItinerary(route.params.id);
    return;
  }

  try {
    const response = await interestsAPI.getAll();
    allInterests.value = Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    console.error("Failed to load itinerary interests", error);
    toastStore.show("Failed to load trip interests.", "error");
  } finally {
    loadingInterests.value = false;
  }
});

const groupedInterests = computed(() => {
  return availableInterests.value.reduce((groups, interest) => {
    const category = interest.category || "Other";
    if (!groups[category]) groups[category] = [];
    groups[category].push(interest);
    groups[category].sort((a, b) => a.name.localeCompare(b.name));
    return groups;
  }, {});
});

const categoryCards = computed(() => {
  if (!availableCategories.value.length) {
    return Object.keys(groupedInterests.value)
      .sort((a, b) => a.localeCompare(b))
      .map((name) => ({ name, description: "" }));
  }

  return [...availableCategories.value]
    .filter((category) => groupedInterests.value[category.name]?.length)
    .sort((a, b) => a.name.localeCompare(b.name));
});

const categoryNames = computed(() =>
  categoryCards.value.map((category) => category.name),
);

const filteredInterests = computed(() => {
  const selected = new Set(selectedCategories.value);
  return availableInterests.value
    .filter((interest) => selected.has(interest.category || "Other"))
    .sort((a, b) => {
      const categorySort = (a.category || "Other").localeCompare(
        b.category || "Other",
      );
      if (categorySort !== 0) return categorySort;
      return a.name.localeCompare(b.name);
    });
});

const interestPages = computed(() => {
  const pages = [];
  const items = filteredInterests.value;
  for (let index = 0; index < items.length; index += 5) {
    pages.push(items.slice(index, index + 5));
  }
  return pages;
});

const steps = computed(() => [
  {
    key: "destination",
    type: "destination",
    title: "Choose your destination and dates",
    description:
      "Pick where you are going and the date range for this itinerary preview.",
  },

  ...(bookableOnly.value
    ? [
        {
          key: "travelers",
          type: "travelers",
          title: "Who is going?",
          description:
            "Traveler counts stay in this planner for trip context, but do not affect the backend request yet.",
        },
      ]
    : []),
  {
    key: "categories",
    type: "categories",
    title: "Choose your interest categories",
    description:
      "Start broad. These categories decide which specific interests appear next.",
  },

  ...interestPages.value.map((_, pageIndex) => ({
    key: `interests-${pageIndex}`,
    type: "interests",
    pageIndex,
    title: "Choose specific interests",
    description:
      "Pick the activities, food, places, and travel themes that should influence the itinerary.",
  })),
  {
    key: "style",
    type: "style",
    title: "Set the trip style",
    description:
      "Budget and pace help shape how full and flexible each day should feel.",
  },
  {
    key: "review",
    type: "review",
    title: "Review and generate",
    description:
      "Confirm your choices before generating the itinerary preview.",
  },
]);

const activeStep = computed(
  () => steps.value[currentStepIndex.value] || steps.value[0],
);
const activeInterestPage = computed(
  () => interestPages.value[activeStep.value?.pageIndex || 0] || [],
);

const nextLabel = computed(() => {
  if (activeStep.value.type === "review") return "Generate itinerary";
  return "Next";
});

const busyLabel = computed(() => {
  if (isLoadingCountryInterests.value) return "Loading...";
  if (activeStep.value.type === "review") return "Generating...";
  return "Working...";
});

const nextDisabled = computed(() => {
  const waitsForInterests = ["categories", "interests"].includes(
    activeStep.value.type,
  );
  return (
    isGenerating.value ||
    isLoadingCountryInterests.value ||
    (loadingInterests.value && waitsForInterests)
  );
});

const selectedInterestNames = computed(() => {
  const selectedIds = new Set(selectedInterestIds.value.map(String));
  return availableInterests.value
    .filter((interest) => selectedIds.has(String(interest.id)))
    .map((interest) => interest.name);
});

const selectedCategoriesLabel = computed(() =>
  selectedCategories.value.length
    ? selectedCategories.value.join(", ")
    : "None",
);

const selectedInterestNamesLabel = computed(() =>
  selectedInterestNames.value.length
    ? selectedInterestNames.value.join(", ")
    : "None",
);

const isLastInterestPage = computed(() => {
  if (activeStep.value.type !== "interests") return false;
  return activeStep.value.pageIndex === interestPages.value.length - 1;
});

const canManageSavedItineraries = computed(
  () => authStore.isAuthenticated && ["user", "admin"].includes(authStore.role),
);

const canEmailItinerary = computed(() => !!generatedItinerary.value);

const tripLength = computed(() => {
  if (!startDate.value || !endDate.value || endDate.value < startDate.value)
    return 0;
  const start = parseLocalDate(startDate.value);
  const end = parseLocalDate(endDate.value);
  return Math.max(
    1,
    Math.round((end.getTime() - start.getTime()) / 86400000) + 1,
  );
});

const tripLengthLabel = computed(() => {
  if (!startDate.value || !endDate.value)
    return "Choose both dates to preview the trip length.";
  if (endDate.value < startDate.value)
    return "End date must be on or after the start date.";
  if (tripLength.value > 14)
    return "Keep this first planner version to 14 days or fewer.";
  return `${tripLength.value} ${tripLength.value === 1 ? "day" : "days"}`;
});

watch(selectedCategories, () => {
  const validIds = new Set(
    filteredInterests.value.map((interest) => String(interest.id)),
  );
  selectedInterestIds.value = selectedInterestIds.value.filter((id) =>
    validIds.has(String(id)),
  );
});

watch(steps, () => {
  if (currentStepIndex.value > steps.value.length - 1) {
    currentStepIndex.value = Math.max(0, steps.value.length - 1);
  }
});

watch(
  () => authStore.user?.email?.trim() || "",
  (email) => {
    if (
      !itineraryEmail.value ||
      itineraryEmail.value === lastAutofilledEmail.value
    ) {
      itineraryEmail.value = email;
    }
    lastAutofilledEmail.value = email;
  },
  { immediate: true },
);

function toggleCategory(category) {
  errorMessage.value = "";
  if (isCategorySelected(category)) {
    selectedCategories.value = selectedCategories.value.filter(
      (item) => item !== category,
    );
    return;
  }
  selectedCategories.value = [...selectedCategories.value, category];
}

function isCategorySelected(category) {
  return selectedCategories.value.includes(category);
}

function isInterestSelected(interestId) {
  return selectedInterestIds.value.map(String).includes(String(interestId));
}

function goBack() {
  if (currentStepIndex.value === 0 || isGenerating.value) return;
  slideDirection.value = "slide-right";
  currentStepIndex.value -= 1;
  errorMessage.value = "";
}

async function goNext() {
  const validation = getValidationMessage();
  if (validation) {
    errorMessage.value = validation;
    return;
  }

  errorMessage.value = "";

  if (activeStep.value.type === "destination") {
    await getAvailableInterestsByListingCountry(country.value);
  }

  if (activeStep.value.type === "review") {
    await handleGenerate();
    return;
  }

  slideDirection.value = "slide-left";
  currentStepIndex.value += 1;
}

async function getAvailableInterestsByListingCountry(country) {
  isLoadingCountryInterests.value = true;
  loadingInterests.value = true;
  try {
    const response = await interestsAPI.getByListingCountry(country, {
      bookable_only: bookableOnly.value,
    });
    availableCategories.value = Array.isArray(response.data?.categories)
      ? response.data.categories
      : [];
    availableInterests.value = Array.isArray(response.data?.interests)
      ? response.data.interests
      : Array.isArray(response.data)
        ? response.data
        : [];
  } catch (error) {
    availableCategories.value = [];
    console.error("Failed to load interests for country", error);
    toastStore.show("Failed to load interests for selected country.", "error");
    return [];
  } finally {
    isLoadingCountryInterests.value = false;
    loadingInterests.value = false;
  }
}

async function handleGenerate() {
  isGenerating.value = true;

  try {
    const response = await itinerariesAPI.plan(buildPayload());
    generatedItinerary.value = response.data;
    window.scrollTo({ top: 0, behavior: "smooth" });
  } catch (error) {
    console.error("Failed to generate itinerary", error);
    errorMessage.value = extractApiError(
      error,
      "Could not generate an itinerary right now.",
    );
  } finally {
    isGenerating.value = false;
  }
}

function buildPayload() {
  return {
    start_date: startDate.value,
    end_date: endDate.value,
    country: country.value,
    interests: selectedInterestNames.value,
    bookable_only: bookableOnly.value,
    budget_level: budgetLevel.value,
    pace: pace.value,
  };
}

function getValidationMessage() {
  if (activeStep.value.type === "categories") {
    if (loadingInterests.value) return "Categories are still loading.";
  }

  if (activeStep.value.type === "interests") {
    if (activeInterestPage.value.length === 0) return "";

    if (isLastInterestPage.value && selectedInterestIds.value.length === 0)
      return "Choose at least one interest, or go back and remove that category to continue.";
  }

  if (activeStep.value.type === "destination") {
    if (!country.value) return "Choose a country.";
    if (!startDate.value || !endDate.value)
      return "Choose a start date and end date.";
    if (endDate.value < startDate.value)
      return "End date must be on or after the start date.";
    if (tripLength.value > 14) return "Choose a trip that is 14 days or fewer.";
  }

  if (activeStep.value.type === "travelers") {
    if (adults.value < 1) return "At least one adult is required.";
  }

  return "";
}

async function loadSavedItinerary(id) {
  isLoadingSavedItinerary.value = true;
  loadingInterests.value = false;

  try {
    const response = await itinerariesAPI.getById(id);
    savedItinerary.value = response.data;
    generatedItinerary.value = mapSavedItineraryToPreview(response.data);
    window.scrollTo({ top: 0, behavior: "smooth" });
  } catch (error) {
    console.error("Failed to load saved itinerary", error);
    toastStore.show(
      extractApiError(error, "Could not load itinerary."),
      "error",
    );
    router.push({ name: "Profile" });
  } finally {
    isLoadingSavedItinerary.value = false;
  }
}

function mapSavedItineraryToPreview(saved) {
  const groupedDays = {};

  for (const item of saved.items || []) {
    if (!groupedDays[item.day_date]) {
      groupedDays[item.day_date] = {
        date: item.day_date,
        total_estimated_cost: 0,
        total_duration_hours: 0,
        stops: [],
      };
    }

    const estimatedCost = Number(item.estimated_cost || 0);
    const estimatedDuration = Number(
      item.extra_metadata?.estimated_duration_hours || 0,
    );

    groupedDays[item.day_date].stops.push({
      listing_id: item.listing_id || item.id,
      title: item.title,
      description: item.description || "",
      business_type_name:
        item.extra_metadata?.business_type_name || item.item_type,
      address: item.address_snapshot || {},
      estimated_cost: estimatedCost,
      estimated_duration_hours: estimatedDuration,
      start_time: item.start_at?.slice(11, 16) || "",
      end_time: item.end_at?.slice(11, 16) || "",
      score: Number(item.extra_metadata?.score || 0),
      reason_tags: item.reason_tags || [],
    });

    groupedDays[item.day_date].total_estimated_cost += estimatedCost;
    groupedDays[item.day_date].total_duration_hours += estimatedDuration;
  }

  const days = Object.values(groupedDays)
    .sort((a, b) => a.date.localeCompare(b.date))
    .map((day) => ({
      ...day,
      total_estimated_cost: Math.round(day.total_estimated_cost * 100) / 100,
      total_duration_hours: Math.round(day.total_duration_hours * 100) / 100,
    }));

  return {
    trip_days: days.length,
    budget_level: saved.budget_level,
    pace: saved.pace,
    total_estimated_cost: Number(saved.total_estimated_cost || 0),
    target_total_budget: saved.total_budget,
    daily_target_budget: days.length
      ? Number(saved.total_estimated_cost || 0) / days.length
      : 0,
    days,
  };
}

function redirectToLogin() {
  router.push({ name: "Login", query: { redirect: route.fullPath } });
}

async function persistGeneratedItinerary({ redirectToCalendar = false } = {}) {
  if (!authStore.isAuthenticated) {
    toastStore.show("Sign in to save your itinerary.", "info");
    redirectToLogin();
    return null;
  }

  if (!canManageSavedItineraries.value) {
    toastStore.show(
      "Saved itineraries are only available for traveler accounts right now.",
      "info",
    );
    return null;
  }

  if (savedItinerary.value) {
    return savedItinerary.value;
  }

  if (!generatedItinerary.value || isSaving.value) {
    return null;
  }

  isSaving.value = true;

  try {
    const response = await itinerariesAPI.save({
      plan_request: buildPayload(),
      plan_response: generatedItinerary.value,
    });
    savedItinerary.value = response.data;
    generatedItinerary.value = mapSavedItineraryToPreview(response.data);

    if (redirectToCalendar) {
      toastStore.show("Itinerary saved to your account.", "success");
      router.push({ name: "Calendar" });
    } else {
      router.replace({
        name: "SavedItinerary",
        params: { id: response.data.id },
      });
    }

    return response.data;
  } catch (error) {
    console.error("Failed to save itinerary", error);
    toastStore.show(
      extractApiError(error, "Could not save itinerary right now."),
      "error",
    );
    return null;
  } finally {
    isSaving.value = false;
  }
}

async function handleSaveItinerary() {
  await persistGeneratedItinerary({ redirectToCalendar: true });
}

async function handleEmailItinerary() {
  if (savedItinerary.value?.id && !authStore.isAuthenticated) {
    toastStore.show("Sign in to email your saved itinerary.", "info");
    redirectToLogin();
    return;
  }

  if (savedItinerary.value?.id && !canManageSavedItineraries.value) {
    toastStore.show(
      "Email delivery is only available for traveler accounts right now.",
      "info",
    );
    return;
  }

  const recipientEmail = itineraryEmail.value.trim();
  if (!recipientEmail) {
    toastStore.show("Enter an email address before sending.", "error");
    return;
  }

  if (!isValidEmail(recipientEmail)) {
    toastStore.show("Enter a valid email address before sending.", "error");
    return;
  }

  if (!generatedItinerary.value) {
    toastStore.show("Generate an itinerary before sending it.", "error");
    return;
  }

  if (isSendingEmail.value) {
    return;
  }

  isSendingEmail.value = true;

  try {
    if (savedItinerary.value?.id) {
      await itinerariesAPI.sendEmail(savedItinerary.value.id, {
        email: recipientEmail,
      });
    } else {
      await itinerariesAPI.sendUnsavedEmail({
        email: recipientEmail,
        plan_request: buildPayload(),
        plan_response: generatedItinerary.value,
      });
    }
    toastStore.show(`Itinerary sent to ${recipientEmail}.`, "success");
  } catch (error) {
    console.error("Failed to send itinerary email", error);
    toastStore.show(
      extractApiError(error, "Could not send itinerary email right now."),
      "error",
    );
  } finally {
    isSendingEmail.value = false;
  }
}

function handleEmailSignIn() {
  toastStore.show("Sign in to email your itinerary.", "info");
  redirectToLogin();
}

function isValidEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

function formatDisplayDate(value) {
  return parseLocalDate(value).toLocaleDateString(undefined, {
    weekday: "long",
    month: "long",
    day: "numeric",
    year: "numeric",
  });
}

function parseLocalDate(value) {
  const [year, month, day] = value.split("-").map(Number);
  return new Date(year, month - 1, day);
}

function toDateInputValue(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function extractApiError(error, fallbackMessage) {
  const detail = error?.response?.data?.detail;
  if (typeof detail === "string" && detail.trim()) {
    return detail;
  }
  return fallbackMessage;
}

function getNormalizedReasonTags(tags) {
  return normalizeItineraryTags(tags);
}

function getPaceToneClasses(pace) {
  if (pace === "relaxed")
    return "bg-[#EAF3DE] text-[#27500A] ring-1 ring-inset ring-[#97C459]";
  if (pace === "balanced")
    return "bg-[#E6F1FB] text-[#0C447C] ring-1 ring-inset ring-[#85B7EB]";
  if (pace === "packed")
    return "bg-[#FAEEDA] text-[#633806] ring-1 ring-inset ring-[#EF9F27]";
  return "bg-[#F1EFE8] text-[#5F5E5A] ring-1 ring-inset ring-[#B4B2A9]";
}

function getBudgetToneClasses(budget) {
  if (budget === "low")
    return "bg-[#E1F5EE] text-[#085041] ring-1 ring-inset ring-[#5DCAA5]";
  if (budget === "medium")
    return "bg-[#EEEDFE] text-[#3C3489] ring-1 ring-inset ring-[#AFA9EC]";
  if (budget === "high")
    return "bg-[#FAECE7] text-[#712B13] ring-1 ring-inset ring-[#F0997B]";
  return "bg-[#F1EFE8] text-[#5F5E5A] ring-1 ring-inset ring-[#B4B2A9]";
}
</script>

<style scoped>
.slide-left-enter-active,
.slide-left-leave-active,
.slide-right-enter-active,
.slide-right-leave-active {
  transition: all 0.24s ease;
}

.slide-left-enter-from {
  opacity: 0;
  transform: translateX(28px);
}

.slide-left-leave-to {
  opacity: 0;
  transform: translateX(-28px);
}

.slide-right-enter-from {
  opacity: 0;
  transform: translateX(-28px);
}

.slide-right-leave-to {
  opacity: 0;
  transform: translateX(28px);
}
</style>
