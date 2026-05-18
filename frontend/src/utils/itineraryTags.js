const ITINERARY_TAG_META = {
  interest_match: { label: "Matches interests", tone: "success" },
  variety: { label: "Adds variety", tone: "info" },
  within_budget: { label: "Within budget", tone: "success" },
  near_previous_stop: { label: "Near previous stop", tone: "neutral" },
  hotel_checkin: { label: "Hotel check-in", tone: "warning" },
  hotel_stay: { label: "Hotel stay", tone: "neutral" },
}

function toTitleCase(value) {
  return value
    .split(" ")
    .filter(Boolean)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ")
}

function humanizeTag(tag) {
  return toTitleCase(tag.replace(/[_-]+/g, " "))
}

function normalizePrefixedTag(tag) {
  const [rawPrefix, ...rest] = tag.split(":")
  const prefix = (rawPrefix || "").trim().toLowerCase()
  const value = rest.join(":").trim()

  if (!prefix || !value) {
    return null
  }

  if (prefix === "interest") {
    return {
      key: `${prefix}:${value.toLowerCase()}`,
      label: `Interest: ${toTitleCase(value)}`,
      tone: "success",
    }
  }

  if (prefix === "category") {
    return {
      key: `${prefix}:${value.toLowerCase()}`,
      label: `Category: ${toTitleCase(value)}`,
      tone: "info",
    }
  }

  if (prefix === "pace") {
    return {
      key: `${prefix}:${value.toLowerCase()}`,
      label: `Pace: ${toTitleCase(value.replace(/[_-]+/g, " "))}`,
      tone: "neutral",
    }
  }

  return {
    key: `${prefix}:${value.toLowerCase()}`,
    label: `${toTitleCase(prefix)}: ${toTitleCase(value)}`,
    tone: "neutral",
  }
}

export function normalizeItineraryTag(tag) {
  const normalized = String(tag || "").trim().toLowerCase()
  if (!normalized) {
    return null
  }

  if (normalized.includes(":")) {
    return normalizePrefixedTag(normalized)
  }

  const meta = ITINERARY_TAG_META[normalized]
  return {
    key: normalized,
    label: meta?.label || humanizeTag(normalized),
    tone: meta?.tone || "neutral",
  }
}

export function normalizeItineraryTags(tags) {
  return (Array.isArray(tags) ? tags : [])
    .map(normalizeItineraryTag)
    .filter(Boolean)
}
