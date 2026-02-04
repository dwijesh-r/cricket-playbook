# Player ID Validation System Specification

**Document ID:** P2-11 | **Version:** 1.0.0
**Author:** Brock Purdy (Data Pipeline Engineer)
**Created:** 2026-02-04 | **Status:** APPROVED FOR IMPLEMENTATION

---

## 1. Problem Statement

The Cricket Playbook data pipeline has experienced **15 documented player ID mismatches** that resulted in incorrect career statistics being displayed in stat packs. These errors are unacceptable for a production analytics system and undermine trust in our data quality.

### Impact Summary

| Severity | Count | Example |
|----------|-------|---------|
| CRITICAL | 5 | Uncapped player shows veteran's 100+ match career |
| HIGH | 6 | Two different players sharing identical player_id |
| MEDIUM | 4 | Minor data inconsistencies or missing IDs |

**Business Impact:**
- Incorrect player profiles delivered to coaching staff
- Risk of strategic decisions based on wrong data
- Manual audit time wasted on preventable errors

---

## 2. Root Causes

### 2.1 Surname Collisions

Common Indian surnames create ambiguity during player ID assignment:

| Surname | Players in Squad | Collision Risk |
|---------|------------------|----------------|
| Singh | 14 | HIGH - 4 collisions documented |
| Khan | 7 | HIGH - 3 collisions documented |
| Kumar | 6 | MEDIUM - 2 collisions documented |
| Sharma | 9 | MEDIUM - 0 collisions (luck) |
| Yadav | 5 | LOW - 0 collisions |

**Example Collision:**
- "Ravi Singh" (RR, uncapped) assigned ID `0a509d6b`
- "Rinku Singh" (KKR, 51 innings) already owns ID `0a509d6b`
- Result: RR stat pack shows Rinku Singh's finisher stats for wrong player

### 2.2 Manual Entry Errors

- Copy-paste of player_ids from similar-named players
- Typos in 8-character hex IDs not caught during review
- No automated validation before CSV commit

### 2.3 Data Source Inconsistencies

- Cricsheet assigns IDs based on first appearance, not disambiguation
- New uncapped players have no existing Cricsheet ID
- Manual ID generation follows no standard format

### 2.4 Fuzzy Matching Failures

- Name similarity algorithms match on surname weight
- "Mohammed Izhar" fuzzy-matched to "Mohammed Siraj" (108 wickets)
- "Shubham Dubey" fuzzy-matched to "Shivam Dube" (75 innings)

---

## 3. Proposed Solution

### 3.1 Validation Rules at Ingestion Time

Implement a **three-tier validation gate** before any player data enters the pipeline:

#### Tier 1: Format Validation
```
RULE: player_id MUST be exactly 8 lowercase hexadecimal characters
REGEX: ^[a-f0-9]{8}$
ACTION: REJECT if format invalid
```

#### Tier 2: Uniqueness Validation
```
RULE: player_id MUST be unique within ipl_2026_squads.csv
ACTION: REJECT if duplicate found
EXCEPTION: Same player on multiple teams (rare)
```

#### Tier 3: Cross-Reference Validation
```
RULE: (player_id + team + role) tuple must be logically consistent
ACTION: FLAG for review if name doesn't match historical data for that ID
```

### 3.2 Cross-Reference Checks

Before accepting a player_id assignment, validate against multiple attributes:

| Check | Source | Confidence |
|-------|--------|------------|
| Name exact match | dim_player.current_name | HIGH |
| Team affiliation | Historical team appearances | MEDIUM |
| Player role | Batter vs Bowler classification | MEDIUM |
| Bowling arm | Left-arm vs Right-arm | HIGH (immutable) |
| Age reasonableness | First seen date vs claimed experience | MEDIUM |

**Validation Logic:**
```python
def validate_player_id(player_id, player_name, team, role, bowling_arm):
    historical = lookup_player(player_id)

    if historical is None:
        return VALID  # New player, no collision possible

    confidence_score = 0

    # Name similarity check
    if fuzzy_ratio(player_name, historical.name) < 85:
        confidence_score -= 50

    # Role consistency
    if role != historical.primary_role:
        confidence_score -= 20

    # Bowling arm (should never change)
    if bowling_arm and historical.bowling_arm:
        if bowling_arm != historical.bowling_arm:
            confidence_score -= 100  # Critical mismatch

    return VALID if confidence_score >= 0 else REQUIRES_REVIEW
```

### 3.3 Automated Alerts for Potential Duplicates

**Alert Triggers:**

1. **Surname Collision Alert**
   - Triggered when adding player with surname in HIGH-RISK list
   - Surnames: Singh, Sharma, Kumar, Khan, Yadav, Patel, Reddy, Pandey
   - Action: Require explicit confirmation of correct player_id

2. **ID Reuse Alert**
   - Triggered when player_id exists in dim_player but name differs
   - Action: Block commit until manually approved

3. **Experience Mismatch Alert**
   - Triggered when "uncapped" player has > 5 matches in historical data
   - Action: Flag for review with historical stats displayed

**Alert Notification:**
- Console output during validation script
- GitHub PR comment (via pre-commit webhook)
- Slack notification for CRITICAL alerts (future)

### 3.4 Manual Review Queue

Create a structured review process for ambiguous cases:

**Review Queue Entry:**
```json
{
  "queue_id": "REV-2026-0042",
  "player_name": "Ravi Singh",
  "team": "RR",
  "assigned_id": "0a509d6b",
  "conflict_with": "Rinku Singh (KKR)",
  "alert_type": "ID_REUSE",
  "status": "PENDING_REVIEW",
  "created_at": "2026-02-04T10:30:00Z",
  "reviewer": null,
  "resolution": null
}
```

**Review Workflow:**
1. Data Engineer runs validation script
2. Alerts generate review queue entries
3. Queue entries assigned to domain expert (Andy Flower role)
4. Reviewer confirms correct action (create new ID vs. accept existing)
5. Resolution logged with audit trail

---

## 4. Implementation Plan

### 4.1 Pre-Commit Hook for Squad CSV Changes

**File:** `.pre-commit-config.yaml`

```yaml
repos:
  - repo: local
    hooks:
      - id: validate-player-ids
        name: Validate Player IDs
        entry: python scripts/validation/validate_player_ids.py
        language: python
        files: ^data/ipl_2026_squads\.csv$
        pass_filenames: true
```

**Validation Script:** `scripts/validation/validate_player_ids.py`

```python
#!/usr/bin/env python3
"""
Pre-commit hook to validate player IDs in squad CSV files.
Exit codes:
  0 - All validations passed
  1 - Validation errors (commit blocked)
  2 - Warnings only (commit allowed with notice)
"""

import csv
import re
import sys
from pathlib import Path

# High-risk surnames for surname collision detection
HIGH_RISK_SURNAMES = {
    'Singh', 'Sharma', 'Kumar', 'Khan', 'Yadav',
    'Patel', 'Reddy', 'Pandey', 'Gupta', 'Chauhan'
}

def validate_id_format(player_id):
    """Validate player_id is 8-char lowercase hex."""
    return bool(re.match(r'^[a-f0-9]{8}$', player_id))

def check_duplicates(players):
    """Check for duplicate player_ids assigned to different players."""
    id_to_players = {}
    duplicates = []

    for player in players:
        pid = player['player_id']
        name = player['player_name']

        if pid in id_to_players:
            if id_to_players[pid] != name:
                duplicates.append((pid, id_to_players[pid], name))
        else:
            id_to_players[pid] = name

    return duplicates

def check_surname_risk(players):
    """Flag high-risk surname players for extra scrutiny."""
    warnings = []

    for player in players:
        surname = player['player_name'].split()[-1]
        if surname in HIGH_RISK_SURNAMES:
            warnings.append(f"High-risk surname: {player['player_name']} ({surname})")

    return warnings

def main(csv_path):
    errors = []
    warnings = []

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        players = list(reader)

    # Check 1: Format validation
    for player in players:
        if not validate_id_format(player.get('player_id', '')):
            errors.append(f"Invalid ID format: {player['player_name']} -> {player.get('player_id')}")

    # Check 2: Duplicate detection
    duplicates = check_duplicates(players)
    for pid, name1, name2 in duplicates:
        errors.append(f"DUPLICATE ID: {pid} used by both '{name1}' and '{name2}'")

    # Check 3: Surname risk warnings
    warnings.extend(check_surname_risk(players))

    # Report results
    if errors:
        print("VALIDATION FAILED - Commit blocked")
        for error in errors:
            print(f"  ERROR: {error}")
        return 1

    if warnings:
        print("VALIDATION PASSED with warnings")
        for warning in warnings[:5]:  # Limit output
            print(f"  WARNING: {warning}")
        if len(warnings) > 5:
            print(f"  ... and {len(warnings) - 5} more warnings")
        return 0

    print("VALIDATION PASSED - All checks clear")
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
```

### 4.2 Validation Script Before Regeneration

**File:** `scripts/validation/pre_regeneration_check.py`

Run this script before any stat pack regeneration:

```bash
python scripts/validation/pre_regeneration_check.py
```

**Checks performed:**
1. All player_ids in squad CSV exist in dim_player (or are new)
2. No player_id appears for multiple different player names
3. Experience data matches expected range for player role
4. Cross-reference with bowler_classifications CSV

**Exit behavior:**
- Exit 0: Proceed with regeneration
- Exit 1: Block regeneration, output errors
- Exit 2: Regeneration allowed but audit log created

### 4.3 Audit Trail for ID Changes

**Audit Log Location:** `data/audit/player_id_changes.log`

**Log Format:**
```
2026-02-04T10:30:00Z | CHANGE | player_id=91e69e5b | player=Mohammed Izhar | team=MI | prev_id=2f49c897 | reason="Collision with Mohammed Siraj" | author="Brock Purdy"
2026-02-04T10:31:00Z | CREATE | player_id=f8d66d89 | player=Ravi Singh | team=RR | prev_id=null | reason="New uncapped player" | author="Brock Purdy"
```

**Audit Requirements:**
- Every player_id change must be logged
- Log retained for minimum 2 years
- Queryable by player_name, team, date range
- Included in data provenance documentation

---

## 5. Success Criteria

### Primary Success Metric
**Zero player ID mismatches in production stat packs.**

### Validation Checkpoints

| Checkpoint | Measurement | Target |
|------------|-------------|--------|
| Pre-commit validation | % commits passing on first try | > 95% |
| Duplicate detection | False negatives (missed duplicates) | 0 |
| Alert accuracy | False positive rate | < 10% |
| Review turnaround | Time to resolve flagged entries | < 24 hours |
| Regeneration confidence | Stat packs with ID issues | 0 |

### Acceptance Tests

1. **Test: Duplicate Rejection**
   - Add two players with same player_id to test CSV
   - Run validation script
   - Expected: Script exits 1, clear error message

2. **Test: Format Validation**
   - Add player with invalid ID format (9 chars, uppercase)
   - Run validation script
   - Expected: Script exits 1, format error reported

3. **Test: Surname Warning**
   - Add new player named "Deepak Singh"
   - Run validation script
   - Expected: Script exits 0 with surname collision warning

4. **Test: Audit Logging**
   - Modify existing player's ID
   - Commit change
   - Expected: Entry appears in audit log with timestamp

---

## 6. Rollout Plan

| Phase | Timeline | Deliverable |
|-------|----------|-------------|
| Phase 1 | Week 1 | Validation script (format + duplicates) |
| Phase 2 | Week 2 | Pre-commit hook integration |
| Phase 3 | Week 3 | Cross-reference validation (dim_player lookup) |
| Phase 4 | Week 4 | Manual review queue + audit logging |
| Phase 5 | Ongoing | Monitoring and alert tuning |

---

## 7. References

- [Player ID Audit Report](/analysis/player_id_audit_report.md) - Original 15 mismatches
- [Task Integrity Loop](/governance/TASK_INTEGRITY_LOOP.md) - Quality process
- [Data Provenance](/data/PROVENANCE.md) - Data lineage documentation

---

**Approval:**
- [ ] Florentino Perez (Governance)
- [ ] Andy Flower (Domain Expert)
- [ ] Tom Brady (Enforcement)

---

*Cricket Playbook - Player ID Validation Spec v1.0.0*
