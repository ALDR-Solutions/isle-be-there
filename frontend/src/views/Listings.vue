<template>
  <div class="bg-white">
    <div>
      <TransitionRoot as="template" :show="mobileFiltersOpen">
        <Dialog
          class="relative z-40 lg:hidden"
          @close="mobileFiltersOpen = false">
          <TransitionChild
            as="template"
            enter="transition-opacity ease-linear duration-300"
            enter-from="opacity-0"
            enter-to="opacity-100"
            leave="transition-opacity ease-linear duration-300"
            leave-from="opacity-100"
            leave-to="opacity-0">
            <div class="fixed inset-0 bg-black/25" />
          </TransitionChild>

          <div class="fixed inset-0 z-40 flex">
            <TransitionChild
              as="template"
              enter="transition ease-in-out duration-300 transform"
              enter-from="translate-x-full"
              enter-to="translate-x-0"
              leave="transition ease-in-out duration-300 transform"
              leave-from="translate-x-0"
              leave-to="translate-x-full">
              <DialogPanel
                class="relative ml-auto flex size-full w-full max-w-sm flex-col overflow-hidden bg-white pt-4 shadow-xl">
                <div class="flex items-center justify-between px-4">
                  <h2 class="text-lg font-medium text-gray-900">Filters</h2>
                  <button
                    type="button"
                    class="relative -mr-2 flex size-10 items-center justify-center rounded-md bg-white p-2 text-gray-400 hover:bg-gray-50 focus:ring-2 focus:ring-indigo-500 focus:outline-hidden"
                    @click="mobileFiltersOpen = false">
                    <span class="absolute -inset-0.5" />
                    <span class="sr-only">Close menu</span>
                    <XMarkIcon class="size-6" aria-hidden="true" />
                  </button>
                </div>

                <!-- Mobile Filters -->
                <form
                  class="mt-4 flex-1 overflow-y-auto border-t border-gray-200 pb-24"
                  @submit.prevent>
                  <!-- Quick category chips -->
                  <div class="px-4 pt-4">
                    <div class="flex items-center justify-between gap-3">
                      <h3 class="text-sm font-semibold text-gray-900">
                        Categories
                      </h3>
                      <button
                        v-if="
                          selectedCategoryIds.length || hasActiveExtraFilters
                        "
                        type="button"
                        class="rounded-md px-2 py-1 text-xs font-medium text-indigo-600 hover:bg-indigo-50 hover:text-indigo-700"
                        @click="clearAllFilters">
                        Clear 
                      </button>
                    </div>

                    <div class="mt-3 grid grid-cols-2 gap-2">
                      <button
                        type="button"
                        class="min-h-11 rounded-xl border px-3 py-2 text-sm font-medium"
                        :class="
                          selectedCategoryIds.length === 0
                            ? 'border-indigo-200 bg-indigo-50 text-indigo-700'
                            : 'border-gray-200 text-gray-700 hover:border-indigo-200 hover:bg-indigo-50/40'
                        "
                        @click="clearQuickCategory">
                        All categories
                      </button>
                      <button
                        v-for="category in subCategories"
                        :key="category.id"
                        type="button"
                        class="min-h-11 rounded-xl border px-3 py-2 text-left text-sm font-medium"
                        :class="
                          isCategorySelected(category.id)
                            ? 'border-indigo-200 bg-indigo-50 text-indigo-700'
                            : 'border-gray-200 text-gray-700 hover:border-indigo-200 hover:bg-indigo-50/40'
                        "
                        @click="toggleQuickCategory(category.id)">
                        {{ category.name }}
                      </button>
                    </div>
                  </div>

                  <!-- Additional filter sections (no category — already shown above) -->
                  <div class="border-t border-gray-200 px-4 py-6">
                    <div class="flex items-center justify-between gap-3">
                      <h3 class="text-sm font-semibold text-gray-900">
                        Price range
                      </h3>
                      <button
                        v-if="hasPriceRangeFilter"
                        type="button"
                        class="rounded-md px-2 py-1 text-xs font-medium text-indigo-600 hover:bg-indigo-50 hover:text-indigo-700"
                        @click="clearPriceRange">
                        Clear
                      </button>
                    </div>

                    <div class="mt-4 px-1">
                      <Slider v-model="priceRangeModel" :min="0" :max="priceMax" :step="5" class="mb-3" showTooltip="drag" />
                      <div class="flex justify-between gap-4">
                        <label class="flex-1">
                          <span class="text-xs font-medium uppercase tracking-wide text-gray-500">Min</span>
                          <input
                            v-model.number="priceRangeModel[0]"
                            type="number"
                            min="0"
                            :max="priceRangeModel[1]"
                            class="mt-1 w-full rounded-xl border border-gray-200 px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-indigo-500 focus:outline-hidden focus:ring-2 focus:ring-indigo-200"
                          />
                        </label>
                        <label class="flex-1">
                          <span class="text-xs font-medium uppercase tracking-wide text-gray-500">Max</span>
                          <input
                            v-model.number="priceRangeModel[1]"
                            type="number"
                            :min="priceRangeModel[0]"
                            :max="priceMax"
                            class="mt-1 w-full rounded-xl border border-gray-200 px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-indigo-500 focus:outline-hidden focus:ring-2 focus:ring-indigo-200"
                          />
                        </label>
                      </div>
                    </div>
                  </div>

                  <!-- City Filter -->
                  <div v-if="selectedCountry && cityOptions.length > 0" class="border-t border-gray-200 px-4 py-6">
                    <div class="flex items-center justify-between gap-3">
                      <h3 class="text-sm font-semibold text-gray-900">City</h3>
                      <button
                        v-if="selectedCity"
                        type="button"
                        class="rounded-md px-2 py-1 text-xs font-medium text-indigo-600 hover:bg-indigo-50 hover:text-indigo-700"
                        @click="clearCitySelection">
                        Clear
                      </button>
                    </div>
                    <select
                      v-model="selectedCity"
                      class="mt-3 w-full rounded-xl border border-gray-200 bg-white px-3 py-2.5 text-sm text-gray-900 shadow-sm focus:border-indigo-500 focus:outline-hidden focus:ring-2 focus:ring-indigo-200"
                    >
                      <option value="">All cities</option>
                      <option v-for="city in cityOptions" :key="city.value" :value="city.label">
                        {{ city.label }}
                      </option>
                    </select>
                  </div>

                  <!-- Radius Filter -->
                  <div v-if="selectedCity && radiusOptions.length > 0" class="border-t border-gray-200 px-4 py-6">
                    <div class="flex items-center justify-between gap-3">
                      <h3 class="text-sm font-semibold text-gray-900">Distance</h3>
                      <button
                        v-if="selectedRadius"
                        type="button"
                        class="rounded-md px-2 py-1 text-xs font-medium text-indigo-600 hover:bg-indigo-50 hover:text-indigo-700"
                        @click="clearRadiusSelection">
                        Clear
                      </button>
                    </div>
                    <div class="mt-3 flex flex-wrap gap-2">
                      <button
                        v-for="radius in radiusOptions"
                        :key="radius"
                        type="button"
                        :class="[
                          'rounded-full px-3 py-1.5 text-xs font-medium border transition',
                          selectedRadius === radius
                            ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                            : 'border-gray-200 text-gray-600 hover:border-indigo-300 hover:bg-indigo-50'
                        ]"
                        @click="selectRadius(radius)"
                      >
                        {{ radius }}km
                      </button>
                    </div>
                  </div>

                  <!-- Date Availability -->
                  <div class="border-t border-gray-200 px-4 py-6">
                    <div class="flex items-center justify-between gap-3">
                      <h3 class="text-sm font-semibold text-gray-900">Availability</h3>
                      <button
                        v-if="availabilityDateInput"
                        type="button"
                        class="rounded-md px-2 py-1 text-xs font-medium text-indigo-600 hover:bg-indigo-50 hover:text-indigo-700"
                        @click="clearDateFilter">
                        Clear
                      </button>
                    </div>
                    <input
                      v-model="availabilityDateInput"
                      type="date"
                      class="mt-3 w-full rounded-xl border border-gray-200 bg-white px-3 py-2.5 text-sm text-gray-900 shadow-sm focus:border-indigo-500 focus:outline-hidden focus:ring-2 focus:ring-indigo-200"
                    />
                  </div>

                  <!-- Rating Filter -->
                  <div class="border-t border-gray-200 px-4 py-6">
                    <div class="flex items-center justify-between gap-3">
                      <h3 class="text-sm font-semibold text-gray-900">Rating</h3>
                      <button
                        v-if="minRating !== null"
                        type="button"
                        class="rounded-md px-2 py-1 text-xs font-medium text-indigo-600 hover:bg-indigo-50 hover:text-indigo-700"
                        @click="clearRatingFilter">
                        Clear
                      </button>
                    </div>
                    <div class="mt-3 space-y-2">
                      <label class="flex items-center gap-2 cursor-pointer">
                        <input v-model="minRating" type="radio" :value="null" class="h-4 w-4 text-indigo-600 border-gray-300 focus:ring-indigo-500" />
                        <span class="text-sm text-gray-600">Any rating</span>
                      </label>
                      <label v-for="stars in [4, 3, 2]" :key="stars" class="flex items-center gap-2 cursor-pointer">
                        <input v-model="minRating" type="radio" :value="stars" class="h-4 w-4 text-indigo-600 border-gray-300 focus:ring-indigo-500" />
                        <span class="text-sm text-gray-600">{{ stars }}+ stars</span>
                      </label>
                    </div>
                  </div>

                  <Disclosure
                    v-for="section in filters"
                    :key="section.id"
                    v-slot="{ open }"
                    as="div"
                    class="border-t border-gray-200 px-4 py-6">
                    <h3 class="-mx-2 -my-3 flow-root">
                      <DisclosureButton
                        class="flex w-full items-center justify-between bg-white px-2 py-3 text-gray-400 hover:text-gray-500">
                        <span class="font-medium text-gray-900">{{
                          section.name
                        }}</span>
                        <span class="ml-6 flex items-center">
                          <PlusIcon
                            v-if="!open"
                            class="size-5"
                            aria-hidden="true"
                          />
                          <MinusIcon v-else class="size-5" aria-hidden="true" />
                        </span>
                      </DisclosureButton>
                    </h3>
                    <DisclosurePanel class="pt-6">
                      <div class="space-y-6">
                        <div
                          v-for="(option, optionIdx) in section.options"
                          :key="option.value"
                          class="flex gap-3">
                          <div class="flex h-5 shrink-0 items-center">
                            <input
                              :id="`filter-mobile-${section.id}-${optionIdx}`"
                              :name="`${section.id}[]`"
                              :value="option.value"
                              type="checkbox"
                              :checked="selectedCountry === option.value"
                              class="h-4 w-4 rounded-sm border border-gray-300 text-indigo-600 focus:ring-indigo-500"
                              @change="
                                section.id === 'country'
                                  ? ($event.target.checked ? selectCountry(option.label) : clearCountrySelection())
                                  : setFilterSelection(section.id, option.value, $event.target.checked)
                              "
                            />
                          </div>
                          <label
                            :for="`filter-mobile-${section.id}-${optionIdx}`"
                            class="min-w-0 flex-1 text-gray-500">
                            {{ option.label }}
                          </label>
                        </div>
                      </div>
                    </DisclosurePanel>
                  </Disclosure>
                </form>

                <div class="border-t border-gray-200 bg-white p-4">
                  <button
                    type="button"
                    class="w-full rounded-xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
                    @click="mobileFiltersOpen = false">
                    View {{ resultsLabel }}
                  </button>
                </div>
              </DialogPanel>
            </TransitionChild>
          </div>
        </Dialog>
      </TransitionRoot>

      <div
        class="relative z-30 border-b border-slate-200/80 bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/80 lg:sticky lg:top-20">
        <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div
            class="flex flex-col gap-4 py-4 lg:min-h-[5.5rem] lg:flex-row lg:items-center lg:justify-between">
            <div class="min-w-0">
              <div class="flex min-w-0 flex-wrap items-center gap-3">
                <h1
                  class="text-2xl font-bold tracking-tight text-gray-900 sm:text-4xl">
                  {{
                    hasSearchQuery
                      ? `Results for "${searchQuery}"`
                      : "Explore Listings"
                  }}
                </h1>
                <button
                  v-if="hasSearchQuery"
                  @click="clearSearch"
                  class="whitespace-nowrap text-sm text-slate-400 underline hover:text-slate-600">
                  Clear search
                </button>
              </div>
              <p class="mt-1 text-sm text-slate-500">{{ resultsLabel }}</p>
            </div>

            <div class="flex items-center justify-between gap-3 sm:justify-end">
              <!-- Sort menu -->
              <Menu as="div" class="relative inline-block text-left">
                <MenuButton
                  class="group inline-flex items-center justify-center rounded-full border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 shadow-sm transition hover:border-slate-300 hover:text-gray-900">
                  <span class="hidden sm:inline">{{ activeSortLabel }}</span>
                  <span class="sm:hidden">Sort</span>
                  <ChevronDownIcon
                    class="-mr-1 ml-1 size-5 shrink-0 text-gray-400 group-hover:text-gray-500"
                    aria-hidden="true"/>
                </MenuButton>

                <transition
                  enter-active-class="transition ease-out duration-100"
                  enter-from-class="transform opacity-0 scale-95"
                  enter-to-class="transform opacity-100 scale-100"
                  leave-active-class="transition ease-in duration-75"
                  leave-from-class="transform opacity-100 scale-100"
                  leave-to-class="transform opacity-0 scale-95">
                  <MenuItems
                    class="absolute left-0 sm:left-auto sm:right-0 z-50 mt-2 w-48 origin-top-right rounded-2xl bg-white shadow-2xl ring-1 ring-black/5 focus:outline-hidden">
                    <div class="py-1">
                      <MenuItem
                        v-for="option in sortOptions"
                        :key="option.value"
                        v-slot="{ active }">
                        <button
                          type="button"
                          class="block w-full px-4 py-2 text-left text-sm"
                          :class="[
                            activeSort === option.value
                              ? 'font-medium text-gray-900'
                              : 'text-gray-500',
                            active ? 'bg-gray-100' : '',
                          ]"
                          @click="selectSort(option.value)">
                          {{ option.name }}
                        </button>
                      </MenuItem>
                    </div>
                  </MenuItems>
                </transition>
              </Menu>

              <button
                type="button"
                class="hidden sm:inline-flex items-center justify-center rounded-full border border-slate-200 bg-white p-2.5 text-gray-400 shadow-sm transition hover:border-slate-300 hover:text-gray-500"
                @click="viewMode = viewMode === 'grid' ? 'list' : 'grid'">
                <span class="sr-only">Toggle view</span>
                <Squares2X2Icon
                  v-if="viewMode === 'list'"
                  class="size-5"
                  aria-hidden="true"/>
                <ListBulletIcon v-else class="size-5" aria-hidden="true" />
              </button>
              <!-- Mobile filter button -->
              <button
                type="button"
                class="relative inline-flex items-center justify-center rounded-full border border-slate-200 bg-white p-2.5 text-gray-400 shadow-sm transition hover:border-slate-300 hover:text-gray-500 lg:hidden"
                :class="activeFilterCount > 0 ? 'text-indigo-600' : ''"
                @click="mobileFiltersOpen = true">
                <span class="sr-only">Filters</span>
                <FunnelIcon class="size-5" aria-hidden="true" />
                <span
                  v-if="activeFilterCount > 0"
                  class="absolute -top-1 -right-1 flex size-4 items-center justify-center rounded-full bg-indigo-600 text-[10px] font-bold text-white">
                  {{ activeFilterCount }}
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <main class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <section aria-labelledby="products-heading" class="pt-6 pb-24">
          <h2 id="products-heading" class="sr-only">Products</h2>

          <div class="mb-5 lg:hidden">
            <div class="flex items-center justify-between gap-2">
              <p class="text-sm font-semibold text-gray-900">Categories</p>
              <button
                v-if="selectedCategoryIds.length || hasActiveExtraFilters"
                type="button"
                class="rounded-md px-2 py-1 text-xs font-medium text-indigo-600 hover:bg-indigo-50 hover:text-indigo-700"
                @click="clearAllFilters">
                Clear 
              </button>
            </div>

            <div class="-mx-4 mt-3 flex gap-2 overflow-x-auto px-4 pb-1">
              <button
                type="button"
                class="shrink-0 rounded-full border px-4 py-2 text-sm font-medium whitespace-nowrap"
                :class="
                  selectedCategoryIds.length === 0
                    ? 'border-indigo-200 bg-indigo-50 text-indigo-700'
                    : 'border-gray-200 text-gray-700'
                "
                @click="clearQuickCategory">
                All categories
              </button>
              <button
                v-for="category in subCategories"
                :key="`mobile-quick-${category.id}`"
                type="button"
                class="shrink-0 rounded-full border px-4 py-2 text-sm font-medium whitespace-nowrap"
                :class="
                  isCategorySelected(category.id)
                    ? 'border-indigo-200 bg-indigo-50 text-indigo-700'
                    : 'border-gray-200 text-gray-700'
                "
                @click="toggleQuickCategory(category.id)"
              >
                {{ category.name }}
              </button>
            </div>
          </div>

          <div
            class="grid grid-cols-1 gap-x-8 gap-y-8 lg:grid-cols-[15rem_minmax(0,1fr)] xl:grid-cols-[16rem_minmax(0,1fr)]">
            <!-- Desktop sidebar filters -->
            <div class="hidden lg:block">
              <form
                class="sticky top-44 max-h-[calc(100vh-12rem)] self-start overflow-y-auto rounded-[1.75rem] border border-slate-200 bg-white p-5 shadow-sm xl:p-6"
                @submit.prevent>
                <!-- Quick-filter category list (business types) -->
                <h3 class="sr-only">Categories</h3>
                <div class="mb-5 flex items-center justify-between gap-3">
                  <div>
                    <p class="text-sm font-semibold text-slate-900">
                      Filters
                    </p>
                    <p class="text-xs text-slate-500">
                      Narrow the listings without leaving the page.
                    </p>
                  </div>
                  <button
                    v-if="selectedCategoryIds.length || hasActiveExtraFilters"
                    type="button"
                    class="text-xs font-medium text-indigo-600 hover:text-indigo-800"
                    @click="clearAllFilters">
                    Clear 
                  </button>
                </div>
                <div class="border-b border-gray-200 pb-6">
                  <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">
                    Categories
                  </p>
                  <ul
                    role="list"
                    class="mt-4 space-y-3 text-sm font-medium text-gray-900">
                    <li>
                      <button
                        type="button"
                        class="text-left transition"
                        :class="
                          selectedCategoryIds.length === 0
                            ? 'text-indigo-700'
                            : 'hover:text-indigo-700'
                        "
                        @click="clearQuickCategory">
                        All categories
                      </button>
                    </li>
                    <li v-for="category in subCategories" :key="category.id">
                      <button
                        type="button"
                        class="text-left transition"
                        :class="
                          isOnlyQuickCategorySelected(category.id)
                            ? 'text-indigo-700'
                            : 'hover:text-indigo-700'
                        "
                        @click="toggleQuickCategory(category.id)">
                        {{ category.name }}
                      </button>
                    </li>
                  </ul>
                </div>

              <!-- Additional filter sections (no category — already shown above) -->
              <div class="border-b border-gray-200 py-6">
                <div class="flex items-center justify-between gap-3">
                  <h3 class="text-sm font-medium text-gray-900">Price range</h3>
                  <button
                    v-if="hasPriceRangeFilter"
                    type="button"
                    class="text-xs font-medium text-indigo-600 hover:text-indigo-800"
                    @click="clearPriceRange">
                    Clear
                  </button>
                </div>

                <div class="mt-4 px-1">
                  <Slider v-model="priceRangeModel" :min="0" :max="priceMax" :step="5" class="mb-3" showTooltip="drag" />
                  <div class="flex justify-between gap-4">
                    <label class="flex-1">
                      <span class="text-xs font-medium uppercase tracking-wide text-gray-500">Min</span>
                      <input
                        v-model.number="priceRangeModel[0]"
                        type="number"
                        min="0"
                        :max="priceRangeModel[1]"
                        class="mt-1 w-full rounded-xl border border-gray-200 px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-indigo-500 focus:outline-hidden focus:ring-2 focus:ring-indigo-200"
                      />
                    </label>
                    <label class="flex-1">
                      <span class="text-xs font-medium uppercase tracking-wide text-gray-500">Max</span>
                      <input
                        v-model.number="priceRangeModel[1]"
                        type="number"
                        :min="priceRangeModel[0]"
                        :max="priceMax"
                        class="mt-1 w-full rounded-xl border border-gray-200 px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-indigo-500 focus:outline-hidden focus:ring-2 focus:ring-indigo-200"
                      />
                    </label>
                  </div>
                </div>
              </div>

              <!-- City Filter -->
              <div v-if="selectedCountry && cityOptions.length > 0" class="border-b border-gray-200 py-6">
                <div class="flex items-center justify-between gap-3">
                  <h3 class="text-sm font-medium text-gray-900">City</h3>
                  <button
                    v-if="selectedCity"
                    type="button"
                    class="text-xs font-medium text-indigo-600 hover:text-indigo-800"
                    @click="clearCitySelection">
                    Clear
                  </button>
                </div>
                <select
                  v-model="selectedCity"
                  class="mt-3 w-full rounded-xl border border-gray-200 bg-white px-3 py-2.5 text-sm text-gray-900 shadow-sm focus:border-indigo-500 focus:outline-hidden focus:ring-2 focus:ring-indigo-200"
                >
                  <option value="">All cities</option>
                  <option v-for="city in cityOptions" :key="city.value" :value="city.label">
                    {{ city.label }}
                  </option>
                </select>
              </div>

              <!-- Radius Filter -->
              <div v-if="selectedCity && radiusOptions.length > 0" class="border-b border-gray-200 py-6">
                <div class="flex items-center justify-between gap-3">
                  <h3 class="text-sm font-medium text-gray-900">Distance</h3>
                  <button
                    v-if="selectedRadius"
                    type="button"
                    class="text-xs font-medium text-indigo-600 hover:text-indigo-800"
                    @click="clearRadiusSelection">
                    Clear
                  </button>
                </div>
                <div class="mt-3 flex flex-wrap gap-2">
                  <button
                    v-for="radius in radiusOptions"
                    :key="radius"
                    type="button"
                    :class="[
                      'rounded-full px-3 py-1.5 text-xs font-medium border transition',
                      selectedRadius === radius
                        ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                        : 'border-gray-200 text-gray-600 hover:border-indigo-300 hover:bg-indigo-50'
                    ]"
                    @click="selectRadius(radius)"
                  >
                    {{ radius }}km
                  </button>
                </div>
              </div>

              <!-- Date Availability Filter -->
              <div class="border-b border-gray-200 py-6">
                <div class="flex items-center justify-between gap-3">
                  <h3 class="text-sm font-medium text-gray-900">Availability</h3>
                  <button
                    v-if="availabilityDateInput"
                    type="button"
                    class="text-xs font-medium text-indigo-600 hover:text-indigo-800"
                    @click="clearDateFilter">
                    Clear
                  </button>
                </div>
                <input
                  v-model="availabilityDateInput"
                  type="date"
                  class="mt-3 w-full rounded-xl border border-gray-200 bg-white px-3 py-2.5 text-sm text-gray-900 shadow-sm focus:border-indigo-500 focus:outline-hidden focus:ring-2 focus:ring-indigo-200"
                />
              </div>

              <!-- Min Rating Filter -->
              <div class="border-b border-gray-200 py-6">
                <div class="flex items-center justify-between gap-3">
                  <h3 class="text-sm font-medium text-gray-900">Rating</h3>
                  <button
                    v-if="minRating !== null"
                    type="button"
                    class="text-xs font-medium text-indigo-600 hover:text-indigo-800"
                    @click="clearRatingFilter">
                    Clear
                  </button>
                </div>
                <div class="mt-3 space-y-2">
                  <label class="flex items-center gap-2 cursor-pointer">
                    <input
                      v-model="minRating"
                      type="radio"
                      :value="null"
                      class="h-4 w-4 text-indigo-600 border-gray-300 focus:ring-indigo-500"
                    />
                    <span class="text-sm text-gray-600">Any rating</span>
                  </label>
                  <label v-for="stars in [4, 3, 2]" :key="stars" class="flex items-center gap-2 cursor-pointer">
                    <input
                      v-model="minRating"
                      type="radio"
                      :value="stars"
                      class="h-4 w-4 text-indigo-600 border-gray-300 focus:ring-indigo-500"
                    />
                    <span class="text-sm text-gray-600">{{ stars }}+ stars</span>
                  </label>
                </div>
              </div>

              <Disclosure
                v-for="section in filters"
                :key="section.id"
                v-slot="{ open }"
                as="div"
                class="border-b border-gray-200 py-6">
                <h3 class="-my-3 flow-root">
                  <DisclosureButton
                    class="flex w-full items-center justify-between bg-white py-3 text-sm text-gray-400 hover:text-gray-500">
                    <span class="font-medium text-gray-900">{{
                      section.name
                    }}</span>
                    <span class="ml-6 flex items-center">
                      <PlusIcon
                        v-if="!open"
                        class="size-5"
                        aria-hidden="true"/>
                      <MinusIcon v-else class="size-5" aria-hidden="true" />
                    </span>
                  </DisclosureButton>
                </h3>
                <DisclosurePanel class="pt-6">
                  <div class="space-y-4">
                    <div
                      v-for="(option, optionIdx) in section.options"
                      :key="option.value"
                      class="flex gap-3">
                      <div class="flex h-5 shrink-0 items-center">
                        <input
                          :id="`filter-${section.id}-${optionIdx}`"
                          :name="`${section.id}[]`"
                          :value="option.value"
                          type="checkbox"
                          :checked="selectedCountry === option.value"
                          class="h-4 w-4 rounded-sm border border-gray-300 text-indigo-600 focus:ring-indigo-500"
                          @change="
                            section.id === 'country'
                              ? ($event.target.checked ? selectCountry(option.label) : clearCountrySelection())
                              : setFilterSelection(section.id, option.value, $event.target.checked)
                          "/>
                      </div>
                      <label
                        :for="`filter-${section.id}-${optionIdx}`"
                        class="text-sm text-gray-600">
                        {{ option.label }}
                      </label>
                    </div>
                  </div>
                </DisclosurePanel>
              </Disclosure>
              </form>
            </div>

            <!-- Listing grid -->
            <div class="min-w-0">
              <div v-if="loading" class="flex justify-center py-20">
                <svg
                  class="h-8 w-8 animate-spin text-cyan-500"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24">
                  <circle
                    class="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    stroke-width="4"/>
                  <path
                    class="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"/>
                </svg>
              </div>

              <div
                v-else-if="filteredListings.length === 0"
                class="rounded-3xl border border-slate-200 bg-white px-6 py-16 text-center shadow-sm">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="mx-auto h-12 w-12 text-slate-300"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="1.5"
                    d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                </svg>
                <p class="mt-4 text-base font-medium text-slate-500">
                  {{
                    hasSearchQuery
                      ? "No matching listings found."
                      : "No listings available yet."
                  }}
                </p>
                <p class="mt-1 text-sm text-slate-400">
                  {{
                    selectedCategoryIds.length || hasActiveExtraFilters
                      ? "Try another category filter."
                      : hasSearchQuery
                        ? "Try another keyword."
                        : "Check back soon for new destinations."
                  }}
                </p>
              </div>

              <div
                v-else
                :class="
                  viewMode === 'grid'
                    ? 'grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-3'
                    : 'flex flex-col gap-4'
                ">
                <DestinationCard
                  v-for="listing in filteredListings"
                  :key="listing.id"
                  :listing="listing"
                  :viewMode="viewMode"/>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { businessesAPI, listingsAPI } from "../services/api";
import { useAuthStore } from "../stores/auth";
import { useFavouritesStore } from "../stores/favourites";
import DestinationCard from "../components/DestinationCard.vue";
import {
  Dialog,
  DialogPanel,
  Disclosure,
  DisclosureButton,
  DisclosurePanel,
  Menu,
  MenuButton,
  MenuItem,
  MenuItems,
  TransitionChild,
  TransitionRoot,
} from "@headlessui/vue";
import Slider from "@vueform/slider";
import { XMarkIcon } from "@heroicons/vue/24/outline";
import {
  ChevronDownIcon,
  FunnelIcon,
  MinusIcon,
  PlusIcon,
  Squares2X2Icon,
  ListBulletIcon,
} from "@heroicons/vue/20/solid";

// ── State ─────────────────────────────────────────────────────────────────────
const listings = ref([]);
const businessTypes = ref([]);
const loading = ref(true);
const mobileFiltersOpen = ref(false);
const selectedCategoryIds = ref([]);
const activeSort = ref("popular");
const minPriceInput = ref("");
const maxPriceInput = ref("");
const priceRange = ref([0, 900]);
const priceMax = ref(900);
const selectedCountry = ref("");
const cityCentroids = ref({});
const selectedCity = ref("");
const radiusOptions = ref([]);
const selectedRadius = ref(null);
const availabilityDateInput = ref("");
const minRating = ref(null);
const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const favouritesStore = useFavouritesStore();
const viewMode = ref("list");
const CATEGORY_SLUG_TO_TYPE_NAME = {
  hotel: "Hotel",
  restaurant: "Restaurant",
  tour: "Tour Operator",
  activity: "Activity Provider",
};

// selectedFilters stores checkbox state for non-category filter sections.
// Shape: { [sectionId]: Set<value> }
const selectedFilters = ref({});

// ── Static config ─────────────────────────────────────────────────────────────
const sortOptions = [
  { value: "popular", name: "Most Popular" },
  { value: "rating", name: "Best Rating" },
  { value: "newest", name: "Newest" },
  { value: "price_low", name: "Price: Low to High" },
  { value: "price_high", name: "Price: High to Low" },
];

/**
 * Add any extra filter sections here (price range, island, amenities, etc.).
 * DO NOT add a "category" / business-type section here — that is already
 * rendered as the quick-filter list above the accordion.
 */
// ── Computed ──────────────────────────────────────────────────────────────────
const searchQuery = computed(() => {
  const rawQ = route.query.q;
  return typeof rawQ === "string" ? rawQ.trim() : "";
});
const routeCategorySlug = computed(() => {
  const rawCategory = route.query.category;
  return typeof rawCategory === "string"
    ? rawCategory.trim().toLowerCase()
    : "";
});

const hasSearchQuery = computed(() => Boolean(searchQuery.value));

const activeSortLabel = computed(
  () => sortOptions.find((o) => o.value === activeSort.value)?.name ?? "Sort",
);

/** Business-type quick-filter list rendered above the accordion. */
const subCategories = computed(() =>
  businessTypes.value.map((type) => ({ id: type.id, name: type.name })),
);

/** Accordion filter sections — business types excluded to avoid duplication. */
const countryOptions = computed(() => {
  const uniqueCountries = new Map();

  for (const listing of listings.value) {
    if (!listing?.location?.lat || !listing?.location?.lng) continue;
    const rawCountry = listing?.address?.country;
    const label = typeof rawCountry === "string" ? rawCountry.trim() : "";
    if (!label) continue;

    const normalizedCountry = normalizeFilterValue(label);
    if (!normalizedCountry || uniqueCountries.has(normalizedCountry)) continue;
    uniqueCountries.set(normalizedCountry, label);
  }

  return [...uniqueCountries.entries()]
    .map(([value, label]) => ({ value, label }))
    .sort((a, b) => a.label.localeCompare(b.label));
});

/** City options derived from selected country. */
const cityOptions = computed(() => {
  if (!selectedCountry.value) return [];
  const normalizedCountry = normalizeFilterValue(selectedCountry.value);
  const citiesInCountry = new Map();

  for (const listing of listings.value) {
    if (!listing?.location?.lat || !listing?.location?.lng) continue;
    const rawCountry = listing?.address?.country;
    const countryNorm = normalizeFilterValue(typeof rawCountry === "string" ? rawCountry.trim() : "");
    if (countryNorm !== normalizedCountry) continue;

    const rawCity = listing?.address?.city;
    const cityLabel = typeof rawCity === "string" ? rawCity.trim() : "";
    if (!cityLabel) continue;

    const normalizedCity = normalizeFilterValue(cityLabel);
    if (!normalizedCity || citiesInCountry.has(normalizedCity)) continue;
    citiesInCountry.set(normalizedCity, cityLabel);
  }

  return [...citiesInCountry.entries()]
    .map(([value, label]) => ({ value, label }))
    .sort((a, b) => a.label.localeCompare(b.label));
});

/** Selected city centroid data. */
const selectedCityData = computed(() => {
  if (!selectedCity.value) return null;
  const normalizedCity = normalizeFilterValue(selectedCity.value);
  return cityCentroids.value[normalizedCity] || null;
});

const filters = computed(() => {
  const sections = [];
  if (countryOptions.value.length > 0) {
    sections.push({ id: "country", name: "Country", options: countryOptions.value });
  }
  return sections;
});

const minPrice = computed(() => parsePriceInput(minPriceInput.value));
const maxPrice = computed(() => parsePriceInput(maxPriceInput.value));

const hasPriceRangeFilter = computed(
  () => priceRangeModel.value[0] > 0 || priceRangeModel.value[1] < priceMax,
);

const priceRangeModel = computed({
  get: () => priceRange.value,
  set: (val) => {
    if (val[0] > val[1]) {
      priceRange.value = [val[1], val[1]];
    } else {
      priceRange.value = val;
    }
  },
});

const hasActiveExtraFilters = computed(() =>
  hasPriceRangeFilter.value ||
  Object.values(selectedFilters.value).some((values) => values.size > 0) ||
  selectedCountry.value !== "" ||
  selectedRadius.value !== null ||
  availabilityDateInput.value !== "" ||
  minRating.value !== null,
);

const filteredListings = computed(() => {
  let result = [...listings.value];

  // Business-type filter
  if (selectedCategoryIds.value.length > 0) {
    const selected = new Set(selectedCategoryIds.value);
    result = result.filter((listing) => selected.has(listing.business_type));
  }

  // City filter (country already filtered via API, city from dropdown)
  if (selectedCity.value) {
    const normalizedCity = normalizeFilterValue(selectedCity.value);
    result = result.filter((listing) =>
      normalizeFilterValue(listing?.address?.city) === normalizedCity,
    );
  }

  // Any extra accordion filters (country)
  for (const [sectionId, values] of Object.entries(selectedFilters.value)) {
    if (values.size === 0) continue;
    result = result.filter((listing) =>
      values.has(getFilterValue(listing, sectionId)),
    );
  }

  // Price range filter (slider)
  if (hasPriceRangeFilter.value) {
    result = result.filter((listing) => {
      const price = listingPriceValue(listing?.base_price);
      if (price === null) return false;
      if (price < priceRangeModel.value[0]) return false;
      if (priceRangeModel.value[1] < priceMax && price > priceRangeModel.value[1]) return false;
      return true;
    });
  }

  // Min rating filter (client-side - avg_rating not in DB)
  if (minRating.value !== null) {
    result = result.filter((listing) => {
      const rating = numberValue(listing?.avg_rating);
      return rating >= minRating.value;
    });
  }

  // Sorting
  switch (activeSort.value) {
    case "rating":
      return result.sort(
        (a, b) => numberValue(b.avg_rating) - numberValue(a.avg_rating),
      );
    case "newest":
      return result.sort(
        (a, b) => dateValue(b.created_at) - dateValue(a.created_at),
      );
    case "price_low":
      return result.sort(
        (a, b) => numberValue(a.base_price) - numberValue(b.base_price),
      );
    case "price_high":
      return result.sort(
        (a, b) => numberValue(b.base_price) - numberValue(a.base_price),
      );
    default:
      return result.sort((a, b) => {
        const reviewDelta =
          numberValue(b.review_count) - numberValue(a.review_count);
        if (reviewDelta !== 0) return reviewDelta;
        return numberValue(b.avg_rating) - numberValue(a.avg_rating);
      });
  }
});

const activeFilterCount = computed(() => {
  const categoryCount = selectedCategoryIds.value.length > 0 ? 1 : 0;
  const priceCount = hasPriceRangeFilter.value ? 1 : 0;
  const extraCount = Object.values(selectedFilters.value).filter(
    (s) => s.size > 0,
  ).length;
  const countryCount = selectedCountry.value ? 1 : 0;
  const cityCount = selectedCity.value ? 1 : 0;
  const radiusCount = selectedRadius.value ? 1 : 0;
  const dateCount = availabilityDateInput.value ? 1 : 0;
  const ratingCount = minRating.value !== null ? 1 : 0;
  return categoryCount + priceCount + extraCount + countryCount + cityCount + radiusCount + dateCount + ratingCount;
});

// ── Helpers ───────────────────────────────────────────────────────────────────
const resultsLabel = computed(
  () =>
    `${filteredListings.value.length} result${
      filteredListings.value.length === 1 ? "" : "s"
    }`,
);

function numberValue(value) {
  const num = Number(value ?? 0);
  return Number.isFinite(num) ? num : 0;
}

function dateValue(value) {
  const timestamp = new Date(value ?? 0).getTime();
  return Number.isFinite(timestamp) ? timestamp : 0;
}

function normalizeFilterValue(value) {
  return typeof value === "string" ? value.trim().toLowerCase() : "";
}

function findBusinessTypeBySlug(categorySlug) {
  const expectedTypeName = CATEGORY_SLUG_TO_TYPE_NAME[categorySlug];
  if (!expectedTypeName) return null;
  return (
    businessTypes.value.find((type) => type.name === expectedTypeName) ?? null
  );
}

function getCategorySlugForId(categoryId) {
  const matchingType = businessTypes.value.find((type) => type.id === categoryId);
  if (!matchingType) return null;

  return (
    Object.entries(CATEGORY_SLUG_TO_TYPE_NAME).find(
      ([, typeName]) => typeName === matchingType.name,
    )?.[0] ?? null
  );
}

function syncCategorySelectionFromRoute() {
  const matchingType = findBusinessTypeBySlug(routeCategorySlug.value);
  selectedCategoryIds.value = matchingType ? [matchingType.id] : [];
}

function updateCategoryQuery(categorySlug) {
  const nextQuery = { ...route.query };

  if (categorySlug) {
    nextQuery.category = categorySlug;
  } else {
    delete nextQuery.category;
  }

  router.replace({ name: "Listings", query: nextQuery });
}

function parsePriceInput(value) {
  if (value === "" || value === null || value === undefined) return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) && parsed >= 0 ? parsed : null;
}

function listingPriceValue(value) {
  if (value === "" || value === null || value === undefined) return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) && parsed >= 0 ? parsed : null;
}

function getFilterValue(listing, sectionId) {
  if (sectionId === "country") {
    return normalizeFilterValue(listing?.address?.country);
  }

  return normalizeFilterValue(listing?.[sectionId]);
}

// ── Country / City / Radius helpers ─────────────────────────────────────────
async function fetchCitiesForCountry(country) {
  if (!country) {
    cityCentroids.value = {};
    radiusOptions.value = [];
    return;
  }
  try {
    const normalizedCountry = normalizeFilterValue(country);
    const response = await listingsAPI.getCitiesByCountry(country);
    const data = response.data;
    const lookup = {};
    for (const city of (data.cities || [])) {
      lookup[normalizeFilterValue(city.name)] = city;
    }
    cityCentroids.value = lookup;
    radiusOptions.value = data.radius_options || [];
  } catch (err) {
    console.error("Failed to load cities for country", err);
    cityCentroids.value = {};
    radiusOptions.value = [];
  }
}

function selectCountry(countryLabel) {
  const normalized = normalizeFilterValue(countryLabel);
  if (selectedCountry.value === normalized) {
    return;
  }
  selectedCountry.value = normalized;
  selectedCity.value = "";
  selectedRadius.value = null;
  cityCentroids.value = {};
  radiusOptions.value = [];
  fetchCitiesForCountry(countryLabel);
}

function clearCountrySelection() {
  selectedCountry.value = "";
  selectedCity.value = "";
  selectedRadius.value = null;
  cityCentroids.value = {};
  radiusOptions.value = [];
}

function selectCity(cityName) {
  selectedCity.value = cityName;
  selectedRadius.value = null;
}

function clearCitySelection() {
  selectedCity.value = "";
  selectedRadius.value = null;
}

function selectRadius(radius) {
  selectedRadius.value = radius;
}

function clearRadiusSelection() {
  selectedRadius.value = null;
}

function clearAllFilters() {
  clearQuickCategory();
  clearPriceRange();
  selectedFilters.value = {};
  clearCountrySelection();
  availabilityDateInput.value = "";
  minRating.value = null;
}

function clearDateFilter() {
  availabilityDateInput.value = "";
}

function clearRatingFilter() {
  minRating.value = null;
}

function clearPriceRange() {
  minPriceInput.value = "";
  maxPriceInput.value = "";
  priceRange.value = [0, priceMax];
}

// ── Category (quick-filter) helpers ───────────────────────────────────────────
function isCategorySelected(categoryId) {
  return selectedCategoryIds.value.includes(categoryId);
}

function isOnlyQuickCategorySelected(categoryId) {
  return (
    selectedCategoryIds.value.length === 1 &&
    selectedCategoryIds.value[0] === categoryId
  );
}

function toggleQuickCategory(categoryId) {
  // Clicking the active sole selection clears it (acts as a toggle/reset)
  if (
    selectedCategoryIds.value.length === 1 &&
    selectedCategoryIds.value[0] === categoryId
  ) {
    selectedCategoryIds.value = [];
    updateCategoryQuery(null);
    return;
  }
  selectedCategoryIds.value = [categoryId];
  updateCategoryQuery(getCategorySlugForId(categoryId));
}

function clearQuickCategory() {
  selectedCategoryIds.value = [];
  updateCategoryQuery(null);
}

// ── Extra accordion filter helpers ────────────────────────────────────────────
function isFilterSelected(sectionId, value) {
  return (
    selectedFilters.value[sectionId]?.has(normalizeFilterValue(value)) ?? false
  );
}

function setFilterSelection(sectionId, value, isSelected) {
  const normalizedValue = normalizeFilterValue(value);
  if (!normalizedValue) return;

  if (!selectedFilters.value[sectionId]) {
    selectedFilters.value[sectionId] = new Set();
  }
  const set = new Set(selectedFilters.value[sectionId]);
  isSelected ? set.add(normalizedValue) : set.delete(normalizedValue);
  selectedFilters.value = { ...selectedFilters.value, [sectionId]: set };
}

// ── Sort helper ───────────────────────────────────────────────────────────────
function selectSort(sortValue) {
  activeSort.value = sortValue;
}

function clearSearch() {
  const nextQuery = { ...route.query };
  delete nextQuery.q;
  router.push({ name: "Listings", query: nextQuery });
}

// ── Data fetching ─────────────────────────────────────────────────────────────
async function fetchBusinessTypes() {
  try {
    const response = await businessesAPI.getTypes();
    businessTypes.value = Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    console.error("Failed to load business types", error);
    businessTypes.value = [];
  }
}

async function fetchListings() {
  loading.value = true;
  try {
    const params = { status: "active" };
    if (selectedCountry.value) {
      params.country = selectedCountry.value;
    }
    if (selectedCityData.value) {
      params.city_lat = selectedCityData.value.lat;
      params.city_lng = selectedCityData.value.lng;
      params.radius_km = selectedRadius.value;
    }
    if (availabilityDateInput.value) {
      params.availability_date = availabilityDateInput.value;
    }
    if (hasPriceRangeFilter.value) {
      if (minPrice.value !== null) params.min_price = minPrice.value;
      if (maxPrice.value !== null) params.max_price = maxPrice.value;
    }
    if (activeSort.value === "price_low") {
      params.sort_by = "base_price";
      params.sort_order = "asc";
    } else if (activeSort.value === "price_high") {
      params.sort_by = "base_price";
      params.sort_order = "desc";
    } else if (activeSort.value === "newest") {
      params.sort_by = "created_at";
      params.sort_order = "desc";
    }
    const response = hasSearchQuery.value
      ? await listingsAPI.search(searchQuery.value)
      : await listingsAPI.getAll(params);
    listings.value = Array.isArray(response.data) ? response.data : [];
  } catch (err) {
    console.error("Failed to load listings", err);
    listings.value = [];
  } finally {
    loading.value = false;
  }
}

// ── Watchers ──────────────────────────────────────────────────────────────────

// Drop any selected category IDs that no longer exist in businessTypes
watch(
  [businessTypes, routeCategorySlug],
  () => {
    syncCategorySelectionFromRoute();
  },
  { deep: true, immediate: true },
);

watch(
  filters,
  (sections) => {
    const allowedBySection = Object.fromEntries(
      sections.map((section) => [
        section.id,
        new Set(section.options.map((option) => option.value)),
      ]),
    );

    const nextSelections = {};
    for (const [sectionId, values] of Object.entries(selectedFilters.value)) {
      const allowedValues = allowedBySection[sectionId];
      if (!allowedValues) continue;

      const keptValues = [...values].filter((value) =>
        allowedValues.has(value),
      );
      if (keptValues.length > 0) {
        nextSelections[sectionId] = new Set(keptValues);
      }
    }

    selectedFilters.value = nextSelections;
  },
  { deep: true },
);

watch(
  () => authStore.isAuthenticated,
  (isAuthenticated) => {
    if (isAuthenticated && !favouritesStore.loaded) {
      favouritesStore.fetchAll().catch((err) => {
        console.error("Failed to load favourites", err);
      });
    }
  },
  { immediate: true },
);

// Re-fetch listings whenever the search query changes
watch(
  () => route.query.q,
  () => {
    fetchListings();
  },
  { immediate: true },
);

// Re-fetch when area filters change
watch(
  [selectedCountry, selectedCity, selectedRadius, availabilityDateInput, hasPriceRangeFilter, activeSort],
  () => {
    fetchListings();
  },
  { deep: true },
);

fetchBusinessTypes();
</script>
<style>
@import '@vueform/slider/themes/default.css';
</style>
