const stopTemplates = [
  {
    type: 'activity',
    title: 'Coastal welcome walk',
    description: 'Ease into the island with a scenic route, local views, and time to settle in.',
    duration: 2,
  },
  {
    type: 'restaurant',
    title: 'Local lunch stop',
    description: 'A relaxed meal built around the flavors travelers selected in their interests.',
    duration: 1.5,
  },
  {
    type: 'tour',
    title: 'Guided island experience',
    description: 'A curated stop matched to the selected categories and trip pace.',
    duration: 3,
  },
  {
    type: 'activity',
    title: 'Sunset free-time block',
    description: 'A lighter stop with room to explore, rest, or add a booking later.',
    duration: 1.5,
  },
]

const budgetCost = {
  low: [24, 36, 52, 18],
  medium: [45, 58, 96, 35],
  high: [85, 110, 180, 75],
}

export async function generateItinerary(payload) {
  await wait(700)

  const tripDays = countTripDays(payload.start_date, payload.end_date)
  const dailyTargetBudget = getDailyTargetBudget(payload.budget_level)
  const stopsPerDay = getStopsPerDay(payload.pace)
  const costs = budgetCost[payload.budget_level] || budgetCost.medium
  const days = []

  for (let dayIndex = 0; dayIndex < tripDays; dayIndex += 1) {
    const date = addDays(payload.start_date, dayIndex)
    const stops = []
    let currentHour = payload.pace === 'relaxed' ? 10 : 9

    for (let stopIndex = 0; stopIndex < stopsPerDay; stopIndex += 1) {
      const template = stopTemplates[(dayIndex + stopIndex) % stopTemplates.length]
      const startHour = currentHour
      const endHour = startHour + template.duration
      const interestName = payload.interests?.[(dayIndex + stopIndex) % payload.interests.length]
      const categoryName = payload.preferred_business_types?.[(dayIndex + stopIndex) % payload.preferred_business_types.length]

      stops.push({
        listing_id: fakeUuid(dayIndex, stopIndex),
        title: buildStopTitle(template.title, interestName),
        business_type_name: template.type,
        address: {
          city: payload.city || 'Bridgetown',
          country: payload.country || 'Barbados',
        },
        estimated_cost: costs[stopIndex % costs.length],
        estimated_duration_hours: template.duration,
        start_time: formatHour(startHour),
        end_time: formatHour(endHour),
        score: 88 - stopIndex * 3,
        reason_tags: [
          ...(interestName ? [`interest:${interestName}`] : []),
          ...(categoryName ? [`category:${categoryName}`] : []),
          `pace:${payload.pace}`,
        ],
        description: template.description,
      })

      currentHour = endHour + 0.75
    }

    days.push({
      date,
      total_estimated_cost: roundCurrency(sum(stops.map((stop) => stop.estimated_cost))),
      total_duration_hours: roundCurrency(sum(stops.map((stop) => stop.estimated_duration_hours))),
      stops,
    })
  }

  return {
    trip_days: tripDays,
    budget_level: payload.budget_level,
    pace: payload.pace,
    total_estimated_cost: roundCurrency(sum(days.map((day) => day.total_estimated_cost))),
    target_total_budget: payload.total_budget || null,
    daily_target_budget: dailyTargetBudget,
    days,
  }
}

function countTripDays(startDate, endDate) {
  const start = parseLocalDate(startDate)
  const end = parseLocalDate(endDate)
  const diff = end.getTime() - start.getTime()
  return Math.max(1, Math.round(diff / 86400000) + 1)
}

function addDays(dateValue, amount) {
  const date = parseLocalDate(dateValue)
  date.setDate(date.getDate() + amount)
  return toDateInputValue(date)
}

function parseLocalDate(value) {
  const [year, month, day] = value.split('-').map(Number)
  return new Date(year, month - 1, day)
}

function toDateInputValue(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function getStopsPerDay(pace) {
  if (pace === 'relaxed') return 2
  if (pace === 'packed') return 4
  return 3
}

function getDailyTargetBudget(budgetLevel) {
  if (budgetLevel === 'low') return 120
  if (budgetLevel === 'high') return 420
  return 240
}

function formatHour(value) {
  const totalMinutes = Math.round(value * 60)
  const hours = String(Math.floor(totalMinutes / 60)).padStart(2, '0')
  const minutes = String(totalMinutes % 60).padStart(2, '0')
  return `${hours}:${minutes}`
}

function buildStopTitle(baseTitle, interestName) {
  if (!interestName) return baseTitle
  return `${baseTitle}: ${interestName}`
}

function fakeUuid(dayIndex, stopIndex) {
  const tail = String(dayIndex * 10 + stopIndex + 1).padStart(12, '0')
  return `00000000-0000-4000-8000-${tail}`
}

function sum(values) {
  return values.reduce((total, value) => total + Number(value || 0), 0)
}

function roundCurrency(value) {
  return Math.round(value * 100) / 100
}

function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}
