# Founder Reviews

This directory contains Founder sign-offs and review documents for completed tickets.

## Structure

```
reviews/
├── README.md
├── TKT-XXX/                    # Review files for specific ticket
│   ├── founder_review.pdf      # Founder's review document
│   ├── sign_off.md            # Approval notes
│   └── feedback.md            # Any feedback or change requests
```

## Review States

| State | Meaning |
|-------|---------|
| **Pending** | Awaiting Founder review |
| **Approved** | Founder has signed off |
| **Changes Requested** | Needs revisions before approval |

## Linking to Tickets

Each ticket in Mission Control can link to its review folder via the `review` field:

```javascript
{
  id: 'TKT-045',
  title: 'Founder approval of depth charts',
  review: 'reviews/TKT-045'  // Links to this folder
}
```

---
*Last updated: 2026-02-06*
