#!/usr/bin/env python3
"""
Comprehensive DuckDB Analytics View Validator
Andy Flower — Cricket Domain Expert
Validates ALL 132 views in cricket_playbook.duckdb
"""

import duckdb
import sys
import time
from datetime import datetime

DB_PATH = "/Users/dwijeshreddy/cricket-playbook/data/cricket_playbook.duckdb"
SINCE2023_CUTOFF_YEAR = 2023  # Data should start from 2023 onwards


def get_all_views(con):
    """Get all views from the database."""
    rows = con.execute(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_type = 'VIEW' ORDER BY table_name"
    ).fetchall()
    return [r[0] for r in rows]


def get_view_columns(con, view_name):
    """Get column names for a view."""
    try:
        cols = con.execute(
            f"SELECT column_name FROM information_schema.columns WHERE table_name = '{view_name}'"
        ).fetchall()
        return [c[0] for c in cols]
    except Exception:
        # Fallback: query one row
        try:
            row = con.execute(f"SELECT * FROM {view_name} LIMIT 0").description
            return [d[0] for d in row]
        except Exception:
            return []


def get_row_count(con, view_name):
    """Get row count for a view. Returns (count, error_msg)."""
    try:
        result = con.execute(f"SELECT COUNT(*) FROM {view_name}").fetchone()
        return result[0], None
    except Exception as e:
        return -1, str(e)


def check_date_range_via_match_id(con, view_name, columns):
    """If view has match_id, join dim_match to get date range."""
    if "match_id" not in columns:
        return None, None, None
    try:
        result = con.execute(f"""
            SELECT
                MIN(dm.match_date) as min_date,
                MAX(dm.match_date) as max_date,
                MIN(dm.season) as min_season
            FROM {view_name} v
            JOIN dim_match dm ON v.match_id = dm.match_id
        """).fetchone()
        return result[0], result[1], result[2]
    except Exception:
        return None, None, None


def check_season_range(con, view_name, columns):
    """Check season column range if it exists."""
    season_cols = [c for c in columns if c.lower() in ("season", "ipl_season", "year")]
    if not season_cols:
        return None, None
    col = season_cols[0]
    try:
        result = con.execute(f"SELECT MIN({col}), MAX({col}) FROM {view_name}").fetchone()
        return result[0], result[1]
    except Exception:
        return None, None


def check_match_date_direct(con, view_name, columns):
    """Check match_date column directly if it exists."""
    date_cols = [c for c in columns if c.lower() in ("match_date", "date")]
    if not date_cols:
        return None, None
    col = date_cols[0]
    try:
        result = con.execute(f"SELECT MIN({col}), MAX({col}) FROM {view_name}").fetchone()
        return result[0], result[1]
    except Exception:
        return None, None


def identify_dual_pairs(views):
    """Identify alltime/since2023 pairs."""
    pairs = {}
    for v in views:
        if v.endswith("_alltime"):
            base = v[:-8]  # strip _alltime
            since_name = base + "_since2023"
            if since_name in views:
                pairs[base] = {"alltime": v, "since2023": since_name}
            else:
                pairs[base] = {"alltime": v, "since2023": None}
        elif v.endswith("_since2023"):
            base = v[:-10]  # strip _since2023
            alltime_name = base + "_alltime"
            if base not in pairs:
                if alltime_name in views:
                    pairs[base] = {"alltime": alltime_name, "since2023": v}
                else:
                    pairs[base] = {"alltime": None, "since2023": v}
    return pairs


def main():
    start_time = time.time()
    con = duckdb.connect(DB_PATH, read_only=True)

    all_views = get_all_views(con)
    print("=" * 120)
    print("  CRICKET PLAYBOOK — COMPREHENSIVE VIEW VALIDATION REPORT")
    print(f"  Database: {DB_PATH}")
    print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Total Views Found: {len(all_views)}")
    print("=" * 120)

    # =========================================================================
    # SECTION 1: Row counts for ALL views
    # =========================================================================
    print("\n" + "=" * 120)
    print("  SECTION 1: ROW COUNTS FOR ALL VIEWS")
    print("=" * 120)

    view_data = {}  # view_name -> {count, columns, error, ...}
    zero_row_views = []
    error_views = []

    for i, v in enumerate(all_views, 1):
        count, err = get_row_count(con, v)
        columns = get_view_columns(con, v)
        view_data[v] = {
            "count": count,
            "error": err,
            "columns": columns,
        }
        status = "OK" if count > 0 else ("ERROR" if err else "EMPTY")
        if count == 0 and not err:
            zero_row_views.append(v)
        if err:
            error_views.append((v, err))

        count_str = f"{count:>12,}" if count >= 0 else "     ERROR"
        print(f"  {i:>3}. {v:<70s} | Rows: {count_str} | Cols: {len(columns):>3} | {status}")

    # =========================================================================
    # SECTION 2: Dual-scope pair validation
    # =========================================================================
    print("\n" + "=" * 120)
    print("  SECTION 2: DUAL-SCOPE PAIR VALIDATION (alltime vs since2023)")
    print("=" * 120)

    pairs = identify_dual_pairs(all_views)
    print(f"\n  Found {len(pairs)} dual-scope base names.\n")

    pair_results = []

    for base_name in sorted(pairs.keys()):
        pair = pairs[base_name]
        alltime_view = pair["alltime"]
        since_view = pair["since2023"]

        result = {
            "base": base_name,
            "alltime_view": alltime_view,
            "since2023_view": since_view,
            "alltime_count": None,
            "since2023_count": None,
            "subset_ok": None,
            "alltime_min_date": None,
            "alltime_max_date": None,
            "alltime_min_season": None,
            "alltime_max_season": None,
            "since2023_min_date": None,
            "since2023_max_date": None,
            "since2023_min_season": None,
            "since2023_max_season": None,
            "date_filter_ok": None,
            "alltime_goes_back": None,
            "issues": [],
        }

        # Row counts
        if alltime_view and alltime_view in view_data:
            result["alltime_count"] = view_data[alltime_view]["count"]
        if since_view and since_view in view_data:
            result["since2023_count"] = view_data[since_view]["count"]

        # Missing pair member
        if not alltime_view:
            result["issues"].append("MISSING alltime view")
        if not since_view:
            result["issues"].append("MISSING since2023 view")

        # Subset check: alltime >= since2023
        if result["alltime_count"] is not None and result["since2023_count"] is not None:
            if result["alltime_count"] >= 0 and result["since2023_count"] >= 0:
                if result["alltime_count"] >= result["since2023_count"]:
                    result["subset_ok"] = True
                else:
                    result["subset_ok"] = False
                    result["issues"].append(
                        f"SUBSET VIOLATION: alltime ({result['alltime_count']:,}) < since2023 ({result['since2023_count']:,})"
                    )

        # Date range checks for ALLTIME view
        if alltime_view and alltime_view in view_data:
            cols = view_data[alltime_view]["columns"]

            # Try match_id join
            min_d, max_d, min_s = check_date_range_via_match_id(con, alltime_view, cols)
            if min_d is not None:
                result["alltime_min_date"] = str(min_d)
                result["alltime_max_date"] = str(max_d)
            if min_s is not None:
                result["alltime_min_season"] = min_s

            # Try direct season column
            min_season, max_season = check_season_range(con, alltime_view, cols)
            if min_season is not None:
                result["alltime_min_season"] = min_season
                result["alltime_max_season"] = max_season

            # Try direct date column
            min_date, max_date = check_match_date_direct(con, alltime_view, cols)
            if min_date is not None and result["alltime_min_date"] is None:
                result["alltime_min_date"] = str(min_date)
                result["alltime_max_date"] = str(max_date)

            # Verify alltime goes back before 2023
            goes_back = False
            if result["alltime_min_season"] is not None:
                try:
                    if int(result["alltime_min_season"]) < SINCE2023_CUTOFF_YEAR:
                        goes_back = True
                except (ValueError, TypeError):
                    pass
            if result["alltime_min_date"] is not None:
                try:
                    year = int(str(result["alltime_min_date"])[:4])
                    if year < SINCE2023_CUTOFF_YEAR:
                        goes_back = True
                except (ValueError, TypeError):
                    pass
            result["alltime_goes_back"] = goes_back
            if not goes_back and result["alltime_count"] and result["alltime_count"] > 0:
                # Only flag if we actually found date/season info
                if (
                    result["alltime_min_season"] is not None
                    or result["alltime_min_date"] is not None
                ):
                    result["issues"].append(
                        f"WARNING: alltime view does NOT go back before 2023 "
                        f"(min_season={result['alltime_min_season']}, min_date={result['alltime_min_date']})"
                    )

        # Date range checks for SINCE2023 view
        if since_view and since_view in view_data:
            cols = view_data[since_view]["columns"]

            # Try match_id join
            min_d, max_d, min_s = check_date_range_via_match_id(con, since_view, cols)
            if min_d is not None:
                result["since2023_min_date"] = str(min_d)
                result["since2023_max_date"] = str(max_d)
            if min_s is not None:
                result["since2023_min_season"] = min_s

            # Try direct season column
            min_season, max_season = check_season_range(con, since_view, cols)
            if min_season is not None:
                result["since2023_min_season"] = min_season
                result["since2023_max_season"] = max_season

            # Try direct date column
            min_date, max_date = check_match_date_direct(con, since_view, cols)
            if min_date is not None and result["since2023_min_date"] is None:
                result["since2023_min_date"] = str(min_date)
                result["since2023_max_date"] = str(max_date)

            # Verify since2023 does NOT have data before 2023
            has_old_data = False
            if result["since2023_min_season"] is not None:
                try:
                    if int(result["since2023_min_season"]) < SINCE2023_CUTOFF_YEAR:
                        has_old_data = True
                except (ValueError, TypeError):
                    pass
            if result["since2023_min_date"] is not None:
                try:
                    year = int(str(result["since2023_min_date"])[:4])
                    if year < SINCE2023_CUTOFF_YEAR:
                        has_old_data = True
                except (ValueError, TypeError):
                    pass

            result["date_filter_ok"] = not has_old_data
            if has_old_data:
                result["issues"].append(
                    f"DATE LEAK: since2023 view contains pre-2023 data! "
                    f"(min_season={result['since2023_min_season']}, min_date={result['since2023_min_date']})"
                )

        # Zero row checks
        if result["alltime_count"] == 0:
            result["issues"].append("EMPTY: alltime view returns 0 rows")
        if result["since2023_count"] == 0:
            result["issues"].append("EMPTY: since2023 view returns 0 rows")
        if result["alltime_count"] is not None and result["alltime_count"] < 0:
            result["issues"].append("ERROR querying alltime view")
        if result["since2023_count"] is not None and result["since2023_count"] < 0:
            result["issues"].append("ERROR querying since2023 view")

        pair_results.append(result)

    # Print pair results
    for r in pair_results:
        at_count = (
            f"{r['alltime_count']:>12,}"
            if r["alltime_count"] is not None and r["alltime_count"] >= 0
            else "    N/A"
        )
        s23_count = (
            f"{r['since2023_count']:>12,}"
            if r["since2023_count"] is not None and r["since2023_count"] >= 0
            else "    N/A"
        )
        subset_str = "YES" if r["subset_ok"] else ("NO" if r["subset_ok"] is False else "N/A")
        date_ok_str = (
            "YES" if r["date_filter_ok"] else ("LEAK" if r["date_filter_ok"] is False else "N/A")
        )
        goes_back_str = (
            "YES"
            if r["alltime_goes_back"]
            else ("NO" if r["alltime_goes_back"] is False else "N/A")
        )

        verdict = "PASS"
        if r["issues"]:
            if any(
                kw in iss
                for iss in r["issues"]
                for kw in ["DATE LEAK", "SUBSET VIOLATION", "ERROR"]
            ):
                verdict = "FAIL"
            elif any("EMPTY" in iss for iss in r["issues"]):
                verdict = "WARN"
            elif any("WARNING" in iss for iss in r["issues"]):
                verdict = "WARN"
            elif any("MISSING" in iss for iss in r["issues"]):
                verdict = "WARN"

        print(f"\n  --- {r['base']} ---")
        print(f"  Alltime view:     {r['alltime_view'] or 'MISSING'}")
        print(f"  Since2023 view:   {r['since2023_view'] or 'MISSING'}")
        print(f"  Alltime rows:     {at_count}")
        print(f"  Since2023 rows:   {s23_count}")
        print(f"  Subset OK:        {subset_str}")
        print(f"  Date filter OK:   {date_ok_str}")
        print(f"  Alltime pre-2023: {goes_back_str}")

        if r["alltime_min_season"] or r["alltime_min_date"]:
            print(
                f"  Alltime range:    season={r['alltime_min_season']}-{r.get('alltime_max_season', '?')} | date={r['alltime_min_date']} to {r['alltime_max_date']}"
            )
        if r["since2023_min_season"] or r["since2023_min_date"]:
            print(
                f"  Since2023 range:  season={r['since2023_min_season']}-{r.get('since2023_max_season', '?')} | date={r['since2023_min_date']} to {r['since2023_max_date']}"
            )

        if r["issues"]:
            for iss in r["issues"]:
                print(f"  ** {iss}")
        print(f"  VERDICT: {verdict}")

    # =========================================================================
    # SECTION 3: Standalone views (no pair)
    # =========================================================================
    print("\n" + "=" * 120)
    print("  SECTION 3: STANDALONE VIEWS (no alltime/since2023 pair)")
    print("=" * 120)

    paired_views = set()
    for base_name, pair in pairs.items():
        if pair["alltime"]:
            paired_views.add(pair["alltime"])
        if pair["since2023"]:
            paired_views.add(pair["since2023"])

    standalone = [v for v in all_views if v not in paired_views]
    print(f"\n  Found {len(standalone)} standalone views.\n")

    for v in standalone:
        d = view_data[v]
        count = d["count"]
        status = "PASS" if count > 0 else ("ERROR" if d["error"] else "WARN (0 rows)")
        count_str = f"{count:>12,}" if count >= 0 else "     ERROR"
        print(f"  {v:<70s} | Rows: {count_str} | {status}")
        if d["error"]:
            print(f"    ERROR: {d['error']}")

    # =========================================================================
    # SECTION 4: SQL quoting check (look at view definitions)
    # =========================================================================
    print("\n" + "=" * 120)
    print("  SECTION 4: SQL DEFINITION CHECKS (quoting issues)")
    print("=" * 120)

    quoting_issues = []
    try:
        # Get view SQL definitions
        view_defs = con.execute("""
            SELECT view_name, sql
            FROM duckdb_views()
            WHERE NOT internal
            ORDER BY view_name
        """).fetchall()

        for vname, vsql in view_defs:
            if vsql:
                # Check for common quoting issues
                # Single quotes around identifiers (should be double quotes)
                # This is a heuristic check
                issues = []

                # Check for WHERE conditions with potential quoting issues
                # e.g., WHERE column = 'value' is fine, but WHERE 'column' = something is wrong
                if "WHERE" in vsql.upper():
                    # Look for unusual patterns
                    pass  # Basic SQL quoting is fine in DuckDB

                # Check for unbalanced quotes
                single_count = vsql.count("'")
                if single_count % 2 != 0:
                    issues.append(f"Unbalanced single quotes ({single_count} found)")

                double_count = vsql.count('"')
                if double_count % 2 != 0:
                    issues.append(f"Unbalanced double quotes ({double_count} found)")

                if issues:
                    quoting_issues.append((vname, issues))
    except Exception as e:
        print(f"  Could not inspect view definitions: {e}")

    if quoting_issues:
        for vname, issues in quoting_issues:
            print(f"  {vname}:")
            for iss in issues:
                print(f"    ** {iss}")
    else:
        print("\n  No SQL quoting issues detected.")

    # =========================================================================
    # SECTION 5: Deep date-filter verification via match_id join
    # =========================================================================
    print("\n" + "=" * 120)
    print("  SECTION 5: DEEP DATE-FILTER VERIFICATION (match_id join)")
    print("=" * 120)

    # For each since2023 view that has match_id, do the join check
    since2023_views = [v for v in all_views if v.endswith("_since2023")]
    print(f"\n  Checking {len(since2023_views)} since2023 views via dim_match join...\n")

    for v in since2023_views:
        cols = view_data[v]["columns"]
        if "match_id" in cols:
            try:
                result = con.execute(f"""
                    SELECT
                        MIN(dm.match_date) as min_date,
                        MAX(dm.match_date) as max_date,
                        MIN(dm.season) as min_season,
                        MAX(dm.season) as max_season,
                        COUNT(DISTINCT dm.season) as n_seasons
                    FROM {v} vw
                    JOIN dim_match dm ON vw.match_id = dm.match_id
                """).fetchone()
                min_date, max_date, min_season, max_season, n_seasons = result

                leak = False
                if min_season is not None and int(min_season) < 2023:
                    leak = True
                if min_date is not None and str(min_date)[:4] < "2023":
                    leak = True

                status = "LEAK!" if leak else "OK"
                print(
                    f"  {v:<65s} | {status} | seasons: {min_season}-{max_season} ({n_seasons}) | dates: {min_date} to {max_date}"
                )
                if leak:
                    print("    ** DATE LEAK DETECTED: data before 2023 present!")
            except Exception as e:
                print(f"  {v:<65s} | SKIP (join failed: {str(e)[:60]})")
        else:
            # Try season column
            min_s, max_s = check_season_range(con, v, cols)
            if min_s is not None:
                leak = False
                try:
                    if int(min_s) < 2023:
                        leak = True
                except (ValueError, TypeError):
                    pass
                status = "LEAK!" if leak else "OK"
                print(f"  {v:<65s} | {status} | season col: {min_s}-{max_s} (no match_id)")
                if leak:
                    print("    ** DATE LEAK DETECTED via season column!")
            else:
                print(f"  {v:<65s} | NO DATE INFO (no match_id or season column)")

    # =========================================================================
    # SECTION 6: Deep date-filter verification for alltime views
    # =========================================================================
    print("\n" + "=" * 120)
    print("  SECTION 6: ALLTIME VIEWS — HISTORICAL DEPTH CHECK")
    print("=" * 120)

    alltime_views = [v for v in all_views if v.endswith("_alltime")]
    print(f"\n  Checking {len(alltime_views)} alltime views for pre-2023 data...\n")

    for v in alltime_views:
        cols = view_data[v]["columns"]
        if "match_id" in cols:
            try:
                result = con.execute(f"""
                    SELECT
                        MIN(dm.match_date) as min_date,
                        MAX(dm.match_date) as max_date,
                        MIN(dm.season) as min_season,
                        MAX(dm.season) as max_season,
                        COUNT(DISTINCT dm.season) as n_seasons
                    FROM {v} vw
                    JOIN dim_match dm ON vw.match_id = dm.match_id
                """).fetchone()
                min_date, max_date, min_season, max_season, n_seasons = result

                has_old = False
                if min_season is not None and int(min_season) < 2023:
                    has_old = True

                status = "OK (has history)" if has_old else "WARNING (no pre-2023)"
                print(
                    f"  {v:<65s} | {status} | seasons: {min_season}-{max_season} ({n_seasons}) | dates: {min_date} to {max_date}"
                )
            except Exception as e:
                print(f"  {v:<65s} | SKIP (join failed: {str(e)[:60]})")
        else:
            min_s, max_s = check_season_range(con, v, cols)
            if min_s is not None:
                has_old = False
                try:
                    if int(min_s) < 2023:
                        has_old = True
                except (ValueError, TypeError):
                    pass
                status = "OK (has history)" if has_old else "WARNING (no pre-2023)"
                print(f"  {v:<65s} | {status} | season col: {min_s}-{max_s} (no match_id)")
            else:
                print(f"  {v:<65s} | NO DATE INFO (no match_id or season column)")

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 120)
    print("  FINAL SUMMARY")
    print("=" * 120)

    total = len(all_views)
    ok_count = sum(1 for v in all_views if view_data[v]["count"] > 0)
    empty_count = len(zero_row_views)
    error_count = len(error_views)

    print(f"\n  Total views:              {total}")
    print(f"  Views with data:          {ok_count}")
    print(f"  Views with 0 rows:        {empty_count}")
    print(f"  Views with errors:        {error_count}")

    if zero_row_views:
        print("\n  EMPTY VIEWS (0 rows):")
        for v in zero_row_views:
            print(f"    - {v}")

    if error_views:
        print("\n  ERROR VIEWS:")
        for v, err in error_views:
            print(f"    - {v}: {err[:100]}")

    # Pair summary
    pair_pass = 0
    pair_warn = 0
    pair_fail = 0
    failed_pairs = []
    warned_pairs = []

    for r in pair_results:
        has_fail = any(
            kw in iss for iss in r["issues"] for kw in ["DATE LEAK", "SUBSET VIOLATION", "ERROR"]
        )
        has_warn = any(kw in iss for iss in r["issues"] for kw in ["EMPTY", "WARNING", "MISSING"])
        if has_fail:
            pair_fail += 1
            failed_pairs.append(r)
        elif has_warn:
            pair_warn += 1
            warned_pairs.append(r)
        else:
            pair_pass += 1

    print(f"\n  Dual-scope pairs:         {len(pair_results)}")
    print(f"    PASS:                   {pair_pass}")
    print(f"    WARN:                   {pair_warn}")
    print(f"    FAIL:                   {pair_fail}")

    if failed_pairs:
        print("\n  FAILED PAIRS:")
        for r in failed_pairs:
            print(f"    - {r['base']}")
            for iss in r["issues"]:
                print(f"      ** {iss}")

    if warned_pairs:
        print("\n  WARNED PAIRS:")
        for r in warned_pairs:
            print(f"    - {r['base']}")
            for iss in r["issues"]:
                print(f"      ** {iss}")

    # Overall verdict
    print("\n" + "-" * 120)
    if pair_fail > 0 or error_count > 0:
        overall = "FAIL"
    elif pair_warn > 0 or empty_count > 0:
        overall = "PASS WITH WARNINGS"
    else:
        overall = "PASS"

    elapsed = time.time() - start_time
    print(f"\n  OVERALL VERDICT: {overall}")
    print(f"  Validation completed in {elapsed:.1f}s")
    print("=" * 120)

    con.close()
    return 0 if overall != "FAIL" else 1


if __name__ == "__main__":
    sys.exit(main())
