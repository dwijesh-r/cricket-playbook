# Phase 1: Bug Reports via Neon

**Priority:** High (quick win, fixes current Web3Forms limitations)
**Effort:** 1-2 hours
**Dependencies:** Neon account, project created

---

## Goal

Replace Web3Forms with direct Neon Postgres inserts for the bug report form. This gives us:
- No 250/month submission limit
- Queryable report history (SQL access)
- Status tracking (open → reviewed → resolved)
- Foundation for all future Neon work

---

## Current State

```
User fills form → fetch('https://api.web3forms.com/submit', formData)
                     → Email to statsledge@gmail.com
                     → No storage, no tracking, 250/mo limit
```

## Target State

```
User fills form → fetch(NEON_HTTP_ENDPOINT, { INSERT INTO reports.issues })
                     → Stored in Postgres
                     → Queryable via SQL
                     → Email notification via Neon trigger (optional)
```

---

## Implementation Steps

### Step 1: Create Neon Project

1. Sign up at https://neon.tech (GitHub OAuth)
2. Create project: `statsledge`
3. Region: `us-east-2` (AWS)
4. Note the connection string

### Step 2: Create Schema

Run against Neon SQL console:

```sql
CREATE SCHEMA IF NOT EXISTS reports;

CREATE TABLE reports.issues (
    id              SERIAL PRIMARY KEY,
    type            VARCHAR(50) NOT NULL,
    context         VARCHAR(255),
    message         TEXT NOT NULL,
    expected_actual TEXT,
    email           VARCHAR(255) NOT NULL,
    page            VARCHAR(100),
    status          VARCHAR(20) NOT NULL DEFAULT 'open',
    reviewer_notes  TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    reviewed_at     TIMESTAMPTZ,
    resolved_at     TIMESTAMPTZ
);

CREATE INDEX idx_issues_status ON reports.issues(status);
CREATE INDEX idx_issues_created ON reports.issues(created_at DESC);
```

### Step 3: Create Reporter Role

```sql
-- Read-write on reports only, nothing else
CREATE ROLE reporter WITH LOGIN PASSWORD '***';
GRANT USAGE ON SCHEMA reports TO reporter;
GRANT INSERT ON reports.issues TO reporter;
GRANT USAGE, SELECT ON SEQUENCE reports.issues_id_seq TO reporter;
-- No SELECT, UPDATE, DELETE — insert only from browser
```

### Step 4: Update Dashboard JavaScript

Replace the current `submitReport()` fetch call in all 6 pages.

**Current:**
```javascript
fetch('https://api.web3forms.com/submit', { method: 'POST', body: formData })
```

**New:**
```javascript
function submitReport() {
    var form = document.getElementById('report-form');
    if (!form.reportValidity()) return;
    var btn = document.getElementById('report-submit-btn');
    btn.disabled = true;
    btn.textContent = 'Sending...';

    var payload = {
        type: form.querySelector('[name="type"]').value,
        context: form.querySelector('[name="context"]').value,
        message: form.querySelector('[name="message"]').value,
        expected_actual: form.querySelector('[name="expected_vs_actual"]').value,
        email: form.querySelector('[name="email"]').value,
        page: document.getElementById('report-page').value
    };

    fetch(NEON_API_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(function(res) { return res.json(); })
    .then(function(data) {
        if (data.success || data.rows) {
            form.reset();
            form.style.display = 'none';
            document.querySelector('.report-close').style.display = 'none';
            document.querySelector('.report-header').style.display = 'none';
            document.getElementById('report-success').style.display = 'block';
            btn.disabled = false;
            btn.textContent = 'Submit Report';
        } else {
            btn.disabled = false;
            btn.textContent = 'Submit Report';
            alert('Something went wrong. Please try again.');
        }
    })
    .catch(function() {
        btn.disabled = false;
        btn.textContent = 'Submit Report';
        alert('Network error. Please try again.');
    });
}
```

### Step 5: API Endpoint Options

**Option A: Neon Serverless Driver (recommended)**

Use Neon's HTTP query endpoint directly from browser:

```
https://ep-xxx.us-east-2.aws.neon.tech/sql
```

The `@neondatabase/serverless` package or raw HTTP POST with the pooled connection string.

**Option B: Lightweight Edge Function**

If we want to validate/sanitize before insert, deploy a Cloudflare Worker or Vercel Edge Function (~20 lines):

```javascript
// workers/report-submit.js
export default {
    async fetch(request) {
        const { type, context, message, expected_actual, email, page } = await request.json();

        // Basic validation
        if (!type || !message || !email) {
            return Response.json({ error: 'Missing required fields' }, { status: 400 });
        }

        const sql = neon(env.DATABASE_URL);
        await sql`INSERT INTO reports.issues (type, context, message, expected_actual, email, page)
                   VALUES (${type}, ${context}, ${message}, ${expected_actual}, ${email}, ${page})`;

        return Response.json({ success: true });
    }
};
```

**Recommendation:** Start with Option A (direct Neon HTTP). Move to Option B if we need validation or rate limiting.

### Step 6: Remove Web3Forms

- Remove `access_key` hidden input from all 6 pages
- Remove `subject` and `from_name` hidden inputs
- Update form to not use FormData (use JSON payload instead)
- Remove Web3Forms access key from codebase

### Step 7: Viewing Reports

Query from Neon SQL console or build a simple admin view:

```sql
-- All open reports
SELECT id, type, email, message, page, created_at
FROM reports.issues
WHERE status = 'open'
ORDER BY created_at DESC;

-- Mark as reviewed
UPDATE reports.issues
SET status = 'reviewed', reviewed_at = NOW(), reviewer_notes = 'Confirmed, fixing in next sprint'
WHERE id = 42;
```

---

## Rollback Plan

If Neon has issues, revert to Web3Forms by restoring the previous form action. Web3Forms access key: `b296c5b6-3635-4391-b75f-d65b7b25b4e8`.

---

## Success Criteria

- [ ] Report form submits successfully to Neon
- [ ] Data appears in `reports.issues` table
- [ ] No page redirect on submit
- [ ] Success modal displays correctly
- [ ] Works on all 6 dashboard pages
- [ ] Reporter role has insert-only access (no SELECT/DELETE)

---

## Files to Modify

| File | Change |
|------|--------|
| `scripts/the_lab/dashboard/index.html` | Update submitReport() JS |
| `scripts/the_lab/dashboard/teams.html` | Update submitReport() JS |
| `scripts/the_lab/dashboard/rankings.html` | Update submitReport() JS |
| `scripts/the_lab/dashboard/comparison.html` | Update submitReport() JS |
| `scripts/the_lab/dashboard/head-to-head.html` | Update submitReport() JS |
| `scripts/the_lab/dashboard/about.html` | Update submitReport() JS |
