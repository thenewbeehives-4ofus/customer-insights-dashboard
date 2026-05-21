# Design Decisions

## Chart Types

- **Line over bar for time trends** — continuity matters more than per-period magnitude.
- **Small multiples for segment comparison** — keeps axes aligned, lets the eye compare shapes directly instead of decoding stacked colors.
- **Annotated callouts on the overview** — direct the viewer to the inflection points rather than expecting them to find these unaided.

## Color

- One categorical palette across all segment views (consistent segment → color mapping).
- Sequential palette for RFM scores.
- Neutral gray for context series; saturated color reserved for the series the view is about.

## Annotation Strategy

Every annotation answers "so what?" — no labels that just restate what an axis already shows.

## Interactivity

- Hover tooltips include the absolute number AND the period-over-period change.
- Filters limited to ones that reveal something — avoid filter-for-filter's-sake.
