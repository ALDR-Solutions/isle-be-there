<template>
  <div class="space-y-5 rounded-2xl border border-slate-200 bg-slate-50 p-6">
    <p class="text-sm font-semibold uppercase tracking-[0.2em] text-cyan-600">
      Restaurant Details
    </p>

    <div>
      <label class="mb-3 block text-sm font-semibold text-slate-700">Service Options</label>
      <div class="space-y-3">
        <div
          v-for="option in serviceOptions"
          :key="option.key"
          class="flex items-center justify-between"
        >
          <span class="text-sm text-slate-700">{{ option.label }}</span>
          <button
            type="button"
            @click="update(option.key, !modelValue[option.key])"
            class="relative inline-flex h-6 w-11 items-center rounded-full transition"
            :class="modelValue[option.key] ? 'bg-cyan-400' : 'bg-slate-200'"
          >
            <span
              class="inline-block h-4 w-4 transform rounded-full bg-white shadow transition"
              :class="modelValue[option.key] ? 'translate-x-6' : 'translate-x-1'"
            />
          </button>
        </div>
      </div>
    </div>

    <div class="flex items-center justify-between">
      <label class="text-sm font-semibold text-slate-700">Table Seating Available</label>
      <button
        type="button"
        @click="update('table_seating', !modelValue.table_seating)"
        class="relative inline-flex h-6 w-11 items-center rounded-full transition"
        :class="modelValue.table_seating ? 'bg-cyan-400' : 'bg-slate-200'"
      >
        <span
          class="inline-block h-4 w-4 transform rounded-full bg-white shadow transition"
          :class="modelValue.table_seating ? 'translate-x-6' : 'translate-x-1'"
        />
      </button>
    </div>

    <div>
      <label class="mb-1.5 block text-sm font-semibold text-slate-700">Opening Hours</label>
      <input
        :value="modelValue.service_availability ?? ''"
        @input="update('service_availability', $event.target.value || null)"
        type="text"
        placeholder="e.g. Mon-Fri 11am-10pm, Sat-Sun 10am-11pm"
        class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400"
      />
    </div>

    <div class="space-y-4 rounded-2xl border border-slate-200 bg-white p-5">
      <div>
        <p class="text-sm font-semibold uppercase tracking-[0.2em] text-cyan-600">Menu</p>
        <p class="mt-1 text-xs text-slate-500">
          Add sections and items. This is stored in listing details.
        </p>
      </div>

      <div class="flex gap-2">
        <input
          v-model="newSectionName"
          @keydown.enter.prevent="addSection"
          type="text"
          placeholder="Section name (e.g. Starters)"
          class="flex-1 rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400"
        />
        <button
          type="button"
          @click="addSection"
          class="rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
        >
          Add Section
        </button>
      </div>

      <p v-if="!menuSections.length" class="text-sm text-slate-400">No menu sections yet.</p>

      <div v-else class="space-y-4">
        <div
          v-for="(section, sectionIndex) in menuSections"
          :key="`${section.name}-${sectionIndex}`"
          class="rounded-2xl border border-slate-200 bg-slate-50 p-4"
        >
          <div class="mb-3 flex items-center justify-between gap-3">
            <p class="truncate text-sm font-semibold text-slate-800">{{ section.name }}</p>
            <button
              type="button"
              @click="removeSection(sectionIndex)"
              class="rounded-xl border border-red-100 px-2.5 py-1 text-xs font-semibold text-red-500 transition hover:bg-red-50"
            >
              Remove
            </button>
          </div>

          <div v-if="section.items?.length" class="space-y-2">
            <div
              v-for="(item, itemIndex) in section.items"
              :key="`${item.name}-${itemIndex}`"
              class="rounded-xl border border-slate-200 bg-white px-3 py-2"
            >
              <div class="flex items-start justify-between gap-3">
                <div class="min-w-0">
                  <p class="truncate text-sm font-semibold text-slate-800">{{ item.name }}</p>
                  <p v-if="item.description" class="mt-0.5 text-xs text-slate-500">
                    {{ item.description }}
                  </p>
                  <p v-if="item.price != null" class="mt-1 text-xs font-semibold text-cyan-700">
                    ${{ formatPrice(item.price) }}
                  </p>
                </div>
                <button
                  type="button"
                  @click="removeItem(sectionIndex, itemIndex)"
                  class="rounded-lg border border-red-100 px-2 py-1 text-xs font-semibold text-red-500 transition hover:bg-red-50"
                >
                  Remove
                </button>
              </div>
            </div>
          </div>
          <p v-else class="text-xs text-slate-400">No items yet.</p>

          <div class="mt-3 space-y-2 rounded-xl border border-slate-200 bg-white p-3">
            <input
              v-model="itemDrafts[sectionIndex].name"
              type="text"
              placeholder="Item name"
              class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400"
            />
            <input
              v-model="itemDrafts[sectionIndex].description"
              type="text"
              placeholder="Description (optional)"
              class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400"
            />
            <div class="flex gap-2">
              <input
                v-model="itemDrafts[sectionIndex].price"
                type="number"
                min="0"
                step="0.01"
                placeholder="Price (optional)"
                class="flex-1 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400"
              />
              <button
                type="button"
                @click="addItem(sectionIndex)"
                class="rounded-xl bg-slate-900 px-3 py-2 text-sm font-semibold text-white transition hover:bg-slate-800"
              >
                Add Item
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from "vue";

const props = defineProps({
  modelValue: { type: Object, default: () => ({}) },
});
const emit = defineEmits(["update:modelValue"]);

const newSectionName = ref("");
const itemDrafts = ref([]);

const serviceOptions = [
  { key: "has_dining", label: "Dine-in" },
  { key: "has_take_out", label: "Takeout" },
  { key: "has_delivery", label: "Delivery" },
];

const menuSections = computed(() => {
  const sections = props.modelValue?.menu?.sections;
  if (!Array.isArray(sections)) return [];
  syncItemDrafts(sections.length);
  return sections;
});

function syncItemDrafts(sectionCount) {
  while (itemDrafts.value.length < sectionCount) {
    itemDrafts.value.push({ name: "", description: "", price: "" });
  }
  if (itemDrafts.value.length > sectionCount) {
    itemDrafts.value.splice(sectionCount);
  }
}

function update(key, value) {
  emit("update:modelValue", { ...props.modelValue, [key]: value });
}

function setMenuSections(sections) {
  const normalized = sections
    .map((section) => ({
      name: String(section?.name ?? "").trim(),
      items: Array.isArray(section?.items)
        ? section.items
            .map((item) => ({
              name: String(item?.name ?? "").trim(),
              description: item?.description ? String(item.description).trim() : null,
              price:
                item?.price === null || item?.price === undefined || item?.price === ""
                  ? null
                  : Number(item.price),
            }))
            .filter((item) => item.name)
        : [],
    }))
    .filter((section) => section.name);

  syncItemDrafts(normalized.length);
  update("menu", normalized.length ? { sections: normalized } : null);
}

function addSection() {
  const name = newSectionName.value.trim();
  if (!name) return;
  const sections = [...menuSections.value, { name, items: [] }];
  setMenuSections(sections);
  newSectionName.value = "";
}

function removeSection(sectionIndex) {
  const sections = [...menuSections.value];
  sections.splice(sectionIndex, 1);
  setMenuSections(sections);
}

function addItem(sectionIndex) {
  const draft = itemDrafts.value[sectionIndex] ?? { name: "", description: "", price: "" };
  const name = String(draft.name ?? "").trim();
  if (!name) return;

  const description = String(draft.description ?? "").trim();
  let price = null;
  if (draft.price !== "" && draft.price !== null && draft.price !== undefined) {
    const numericPrice = Number(draft.price);
    if (Number.isFinite(numericPrice) && numericPrice >= 0) {
      price = numericPrice;
    } else {
      return;
    }
  }

  const sections = [...menuSections.value];
  const nextItems = Array.isArray(sections[sectionIndex].items)
    ? [...sections[sectionIndex].items]
    : [];
  nextItems.push({
    name,
    description: description || null,
    price,
  });
  sections[sectionIndex] = { ...sections[sectionIndex], items: nextItems };
  setMenuSections(sections);
  itemDrafts.value[sectionIndex] = { name: "", description: "", price: "" };
}

function removeItem(sectionIndex, itemIndex) {
  const sections = [...menuSections.value];
  const nextItems = [...(sections[sectionIndex].items ?? [])];
  nextItems.splice(itemIndex, 1);
  sections[sectionIndex] = { ...sections[sectionIndex], items: nextItems };
  setMenuSections(sections);
}

function formatPrice(value) {
  const numericValue = Number(value);
  return Number.isFinite(numericValue) ? numericValue.toFixed(2) : "0.00";
}
</script>
