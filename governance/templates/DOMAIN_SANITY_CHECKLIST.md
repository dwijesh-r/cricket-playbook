# Domain Sanity Checklist

**Task:** [Task Name]
**Date:** [YYYY-MM-DD]
**Build Owner:** [Agent Name]

---

## Pre-Review Summary

**What was built:**
[Brief description of the deliverable]

**Key outputs:**
- [ ] File 1: [path]
- [ ] File 2: [path]

---

## Jose Mourinho Review (Data & Robustness)

### Questions

| # | Question | Answer |
|---|----------|--------|
| 1 | Is the data robust with current sample sizes? | |
| 2 | Are baselines clearly defined? | |
| 3 | Is this scalable for future seasons/data? | |
| 4 | Are edge cases handled? | |
| 5 | Is the methodology reproducible? | |

### Specific Checks

- [ ] Sample size thresholds documented
- [ ] Null handling specified
- [ ] Data recency verified (2023+ if applicable)
- [ ] No silent assumptions in logic

### Sign-off

```
JOSE MOURINHO: [YES / NO / FIX]
Reason (if NO/FIX):
Date: [YYYY-MM-DD]
```

---

## Andy Flower Review (Cricket Truth)

### Questions

| # | Question | Answer |
|---|----------|--------|
| 1 | Would a coach find this useful? | |
| 2 | Would an analyst trust this? | |
| 3 | Would a fan understand this? | |
| 4 | Does this match cricket intuition? | |
| 5 | Are any claims surprising enough to double-check? | |

### Specific Checks

- [ ] Tags/labels make cricket sense
- [ ] Thresholds align with real-world performance
- [ ] No obvious misclassifications spotted
- [ ] Phase definitions are cricket-appropriate
- [ ] Player roles match expected behavior

### Spot Check Players

| Player | Expected | Actual | Match? |
|--------|----------|--------|--------|
| [Elite player] | | | |
| [Edge case player] | | | |
| [Recent form player] | | | |

### Sign-off

```
ANDY FLOWER: [YES / NO / FIX]
Reason (if NO/FIX):
Date: [YYYY-MM-DD]
```

---

## Pep Guardiola Review (System Integrity)

### Questions

| # | Question | Answer |
|---|----------|--------|
| 1 | Is this structurally coherent with existing system? | |
| 2 | Does it contradict any existing outputs? | |
| 3 | Does it follow established naming conventions? | |
| 4 | Is it consistent with the Constitution? | |
| 5 | Does it fit the overall architecture? | |

### Specific Checks

- [ ] File naming follows conventions
- [ ] Schema is consistent with existing outputs
- [ ] No duplicate/conflicting definitions
- [ ] Integrates cleanly with existing workflows
- [ ] Documentation structure matches standards

### Integration Points

| Existing Component | Compatible? | Notes |
|--------------------|-------------|-------|
| Stat pack template | | |
| Output manifests | | |
| Test suite | | |
| Other outputs | | |

### Sign-off

```
PEP GUARDIOLA: [YES / NO / FIX]
Reason (if NO/FIX):
Date: [YYYY-MM-DD]
```

---

## Summary

| Reviewer | Verdict | Date |
|----------|---------|------|
| Jose Mourinho | | |
| Andy Flower | | |
| Pep Guardiola | | |

### Overall Status

- [ ] **APPROVED** - All three YES, proceed to Enforcement Check
- [ ] **FIX REQUIRED** - Address issues, return for re-review
- [ ] **REJECTED** - Fundamental issues, return to build phase

### Issues to Address (if any)

| Issue | Owner | Resolution |
|-------|-------|------------|
| | | |

---

## Next Steps

After all three sign-offs are YES:
1. Submit to Tom Brady for Enforcement Check (Step 4)
2. Proceed to Commit and Ship (Step 5)

---

*Domain Sanity Checklist Template v1.0.0*
*Andy Flower, Domain Lead*
