<template>
  <div class="bg-slate-50 min-h-screen">
    <div class="bg-white border-b border-slate-200">
      <div class="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <p
          class="text-sm font-semibold uppercase tracking-[0.28em] text-cyan-600"
        >
          {{ hasSearchQuery ? "Search Results" : "Browse All" }}
        </p>
        <h1 class="mt-3 text-3xl font-bold text-slate-900 sm:text-4xl">
          {{
            hasSearchQuery ? `Results for "${searchQuery}"` : "Explore Listings"
          }}
        </h1>
        <p class="mt-3 max-w-2xl text-base leading-7 text-slate-600">
          {{
            hasSearchQuery
              ? "Discover matching stays, adventures, and coastal escapes across the Caribbean."
              : "Discover handpicked stays, adventures, and coastal escapes across the Caribbean."
          }}
        </p>
      </div>
    </div>
    <div class="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <div v-if="loading" class="flex justify-center py-20">
        <svg
          class="h-8 w-8 animate-spin text-cyan-500"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            class="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            stroke-width="4"
          />
          <path
            class="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
          />
        </svg>
      </div>

      <div
        v-else-if="listings.length === 0"
        class="rounded-3xl border border-slate-200 bg-white px-6 py-16 text-center shadow-sm"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="mx-auto h-12 w-12 text-slate-300"
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
        <p class="mt-4 text-base font-medium text-slate-500">
          {{
            hasSearchQuery
              ? "No matching listings found."
              : "No listings available yet."
          }}
        </p>
        <p class="mt-1 text-sm text-slate-400">
          {{
            hasSearchQuery
              ? "Try another keyword."
              : "Check back soon for new destinations."
          }}
        </p>
      </div>
      <div v-else class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <DestinationCard
          v-for="listing in listings"
          :key="listing.id"
          :listing="listing"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { listingsAPI } from "../services/api";
import DestinationCard from "../components/DestinationCard.vue";

const listings = ref([]);
const businessTypes = ref([]);
const loading = ref(true);
const mobileFiltersOpen = ref(false);
const selectedCategoryIds = ref([]);
const activeSort = ref("popular");
const route = useRoute();
const router = useRouter();
const viewMode = ref("grid");

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
  return typeof rawQ === "string" ? rawQ.trim() : "";
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

const filters = computed(() => [
  {
    id: "country",
    name: "Country",
    options: countryOptions.value,
  },
]);

const hasActiveExtraFilters = computed(() =>
  Object.values(selectedFilters.value).some((values) => values.size > 0),
);

const filteredListings = computed(() => {
  let result = [...listings.value];

  // Business-type filter
  if (selectedCategoryIds.value.length > 0) {
    const selected = new Set(selectedCategoryIds.value);
    result = result.filter((listing) => selected.has(listing.business_type));
  }

  // Any extra accordion filters
  for (const [sectionId, values] of Object.entries(selectedFilters.value)) {
    if (values.size === 0) continue;
    result = result.filter((listing) =>
      values.has(getFilterValue(listing, sectionId)),
    );
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
  const extraCount = Object.values(selectedFilters.value).filter(
    (s) => s.size > 0,
  ).length;
  return categoryCount + extraCount;
});

// ── Helpers ───────────────────────────────────────────────────────────────────
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

function getFilterValue(listing, sectionId) {
  if (sectionId === "country") {
    return normalizeFilterValue(listing?.address?.country);
  }

  return normalizeFilterValue(listing?.[sectionId]);
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
    return;
  }
  selectedCategoryIds.value = [categoryId];
}

function clearQuickCategory() {
  selectedCategoryIds.value = [];
}

function clearAllFilters() {
  clearQuickCategory();
  selectedFilters.value = {};
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
    const response = hasSearchQuery.value
      ? await listingsAPI.search(searchQuery.value)
      : await listingsAPI.getAll();
    listings.value = response.data;
  } catch (err) {
    console.error("Failed to load listings", err);
    console.error("Failed to load listings", err);
    listings.value = [];
  } finally {
    loading.value = false;
  }
}

// ── Watchers ──────────────────────────────────────────────────────────────────

// Drop any selected category IDs that no longer exist in businessTypes
watch(
  businessTypes,
  (types) => {
    const allowedIds = new Set(types.map((type) => type.id));
    selectedCategoryIds.value = selectedCategoryIds.value.filter((id) =>
      allowedIds.has(id),
    );
  },
  { deep: true },
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

// Re-fetch listings whenever the search query changes
watch(
  () => route.query.q,
  () => {
    fetchListings();
  },
  { immediate: true },
  { immediate: true },
);

fetchBusinessTypes();
</script>
