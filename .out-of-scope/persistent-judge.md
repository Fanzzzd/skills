# Reusing one judge across rounds

Requests to keep the same judge subagent alive between rounds so it remembers earlier findings and costs less context.

## Why this is out of scope

A judge that remembers its last verdict defends it. It re-raises findings the owner already ruled on, holds scores to stay consistent with itself, and reads the diff instead of the code. A fresh judge, told only the previous scores and what changed, re-reads the code and finds what the last one missed. The previous scores and the owner-decision list carry everything a new round needs.
