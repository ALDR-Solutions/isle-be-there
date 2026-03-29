# Frontend Architecture

## Structure
- `src/app`: app-wide bootstrap and session persistence
- `src/router`: routes, guards, and page metadata
- `src/pages`: route-level screens only
- `src/features`: domain-specific UI and composables
- `src/components`: shared reusable UI and layout building blocks
- `src/services`: HTTP client plus domain API modules
- `src/composables`: reusable state and interaction patterns
- `src/stores`: Pinia stores for shared application state
- `src/utils`: pure formatting and mapping helpers

## Working Rules
- Route components should orchestrate screens, not hold every detail inline.
- Reusable UI belongs in `components`; domain-specific UI belongs in `features`.
- API calls should go through `services`, not directly from templates.
- `localStorage` access is restricted to `src/app/session.js`.
- Async screens should use a consistent state shape:
  `data`, `loading`, `error`, `isEmpty`, `load()`, `refresh()`.
- Forms should use a consistent state shape:
  `values`, `errors`, `isDirty`, `isSubmitting`, `submitError`.
- Shared dialogs, empty states, alerts, and loading states should be reused instead of duplicated.

## Naming
- Components: `PascalCase.vue`
- Composables: `useThing.js`
- Stores: `thing.js` exporting `useThingStore`
- Services: `thingService.js`

## Refactor Priorities
- Keep pages small and focused.
- Prefer pure utilities for formatting and derived display data.
- Centralize auth/session behavior so routing and API refresh logic stay predictable.
