# Deep fix and REWRITE protocol

Load this reference when a verified finding repeats an earlier class (2nd round in the same area/rule) or when the verdict is `REWRITE`. Do not run this ceremony on one-off Round 1 bugs that already live inside a single obvious module.

## 1. Generalize the sample

A recurring finding is a **sample** of a structural class. Fixing only the reported instance leaves siblings for the next judge. Write three lines in `.judge/reports/r<N>-fix.md`:

- **Rule broken:** one sentence stating the invariant ("a field commits only when its value changed").
- **Direction:** adjacent flows a user or caller hits next along the same path.
- **Lineage:** prior rounds in `.judge/rounds.md` where this same rule broke.

Sweep the codebase and running product for every other entry point, element type, client, or transport that enforces the same rule. Each uncovered sibling joins the fix list at its own severity.

## 2. Locate the owning module

Call the Skill tool with `codebase-design` and apply its vocabulary (module, interface, seam, depth, locality) and deletion test:

- **One crossing module already exists:** move the rule into it; delete caller-side workarounds.
- **Each call site holds its own copy (shallow seam):** deepen it behind one small interface so every path calls the owning module. Follow `codebase-design`'s deepening and design-it-twice guidance when multiple interface shapes fit.
- **ADR conflict:** read local ADRs first; reopen an ADR only if the lineage proves its boundary keeps the rule scattered, and note that in the round summary.

Record one line in `.judge/rounds.md` (`Fixed / Classes:`): `<rule> -> <owning module> (replaced <N> copies)`.

## 3. Execute `REWRITE` (max once per area)

When `REWRITE` fires:

1. State the owning module's interface and invariant in 2 to 3 sentences before editing.
2. Move every path behind that interface and delete the replaced copies and their redundant copy-level tests.
3. Add end-to-end tests through the owning module's interface covering the judge's failure plus every swept sibling.
4. In the next judge prompt, name the owning module and ask the judge to look specifically for any path that still bypasses it.

If the rewritten module still produces a blocking finding in the very next round, the loop stops on `PLATEAU` instead of looping another rewrite.
