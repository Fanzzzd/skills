# A judge that also fixes

Requests to let the `standing-judge` judge apply its own fixes, to save a round trip.

## Why this is out of scope

The loop works because the two roles can't help each other. A judge that edits is grading its own work: it stops finding problems in code it wrote, and it softens findings it would have to fix. The fixer, in turn, stops proving fixes with tests once the judge has "already checked". Keeping the judge read-only is the cheapest way to keep both honest.

If a round trip is too slow, shrink the round (narrower scope, fewer dimensions), not the separation.
