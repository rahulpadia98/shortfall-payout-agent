"""Sanity checks for the generated data in data/ and eval/.

Recomputes expected payout values from pos_orders.csv and contract_terms.csv
independently of the generator, then checks them against payouts.csv and the
answer key. This is a data-validation script, not agent code, so it may read eval/.

Usage: python scripts/check_data.py   (exits 1 if any check fails)
"""

import csv
import hashlib
import subprocess
import sys
import tempfile
from collections import Counter
from datetime import date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CENT = Decimal("0.01")
MONEY_FIELDS = ["gross_sales", "commission_amount", "tip_passed_through", "refund_deducted",
                "adjustments", "net_payout"]
OUTPUT_FILES = ["data/pos_orders.csv", "data/payouts.csv", "data/contract_terms.csv",
                "eval/seeded_errors.csv", "eval/edge_cases.csv"]

failures = []


def check(name, problems):
    problems = list(problems)
    print(f"[{'PASS' if not problems else 'FAIL'}] {name}")
    for p in problems[:10]:
        print(f"       - {p}")
    if len(problems) > 10:
        print(f"       ... and {len(problems) - 10} more")
    if problems:
        failures.append(name)


def read(rel):
    with open(ROOT / rel, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def money(x):
    return Decimal(x).quantize(CENT, rounding=ROUND_HALF_UP)


def week_start(d):
    return d - timedelta(days=d.weekday())


pos = read("data/pos_orders.csv")
payouts = read("data/payouts.csv")
terms = read("data/contract_terms.csv")
errors = read("eval/seeded_errors.csv")
edges = read("eval/edge_cases.csv")

pos_by_id = {o["external_order_id"]: o for o in pos}
payout_by_id = {}
for p in payouts:
    payout_by_id.setdefault(p["external_order_id"], []).append(p)
error_by_id = {e["external_order_id"]: e for e in errors}
edge_ids = {e["external_order_id"] for e in edges}


def contract_rate(marketplace, order_type, on_date):
    applicable = [(date.fromisoformat(t["effective_date"]), Decimal(t["commission_rate"]))
                  for t in terms
                  if t["marketplace"] == marketplace and t["order_type"] == order_type
                  and date.fromisoformat(t["effective_date"]) <= on_date]
    return max(applicable)[1]


def expected_row(o):
    order_date = datetime.fromisoformat(o["order_datetime"]).date()
    gross = Decimal(o["subtotal"]) - Decimal(o["promo_discount"])
    rate = contract_rate(o["marketplace"], o["order_type"], order_date)
    commission = money(gross * rate)
    tip, refund = Decimal(o["tip"]), Decimal(o["refund_amount"])
    return {"gross_sales": gross, "commission_rate_applied": rate, "commission_amount": commission,
            "tip_passed_through": tip, "refund_deducted": refund, "adjustments": Decimal("0.00"),
            "net_payout": gross - commission + tip - refund}


# 1. Row counts --------------------------------------------------------------
print("Row counts")
for rel, rows in [("data/pos_orders.csv", pos), ("data/payouts.csv", payouts),
                  ("data/contract_terms.csv", terms), ("eval/seeded_errors.csv", errors),
                  ("eval/edge_cases.csv", edges)]:
    print(f"  {rel:26} {len(rows):5}")
print("  orders by marketplace:", dict(sorted(Counter(o["marketplace"] for o in pos).items())))
print("  orders by status:     ", dict(sorted(Counter(o["status"] for o in pos).items())))
print("  orders by type:       ", dict(sorted(Counter(o["order_type"] for o in pos).items())))
print("  payouts (weekly ids): ", len({p["payout_id"] for p in payouts}))
print("  errors by type:")
for t, n in sorted(Counter(e["error_type"] for e in errors).items()):
    print(f"    {t:32} {n}")
dates = sorted(datetime.fromisoformat(o["order_datetime"]).date() for o in pos)
print(f"  order dates: {dates[0]} .. {dates[-1]} ({(dates[-1] - dates[0]).days + 1} days)")
print()

check("about 2,000 orders (1,800-2,200)", [] if 1800 <= len(pos) <= 2200 else [f"{len(pos)} orders"])
check("about 40 seeded errors (36-44), all six types present",
      ([] if 36 <= len(errors) <= 44 else [f"{len(errors)} errors"])
      + [f"missing type {t}" for t in ["wrong_commission_rate", "missing_from_payout",
                                         "refund_deducted_twice", "refund_without_pos_refund",
                                         "commission_on_cancelled_order", "tip_not_fully_passed_through"]
         if t not in {e["error_type"] for e in errors}])
check("8-10 edge cases", [] if 8 <= len(edges) <= 10 else [f"{len(edges)} edge cases"])
check("unique ids in POS, error key and edge key",
      [f"duplicate {k}" for k, n in Counter(o["order_id"] for o in pos).items() if n > 1]
      + [f"duplicate {k}" for k, n in Counter(o["external_order_id"] for o in pos).items() if n > 1]
      + [f"duplicate error id {k}" for k, n in Counter(e["external_order_id"] for e in errors).items() if n > 1]
      + [f"duplicate edge id {k}" for k, n in Counter(e["external_order_id"] for e in edges).items() if n > 1])

# 2. Seeded error ids exist ----------------------------------------------------
problems = []
for e in errors:
    eid = e["external_order_id"]
    if eid not in pos_by_id:
        problems.append(f"{eid} not in pos_orders.csv")
    if e["error_type"] == "missing_from_payout":
        if eid in payout_by_id:
            problems.append(f"{eid} is missing_from_payout but appears in payouts.csv")
    elif eid not in payout_by_id:
        problems.append(f"{eid} ({e['error_type']}) not in payouts.csv")
check("every seeded error id exists in the data", problems)
check("every edge case id exists in pos_orders.csv", [f"{i} not in POS" for i in edge_ids if i not in pos_by_id])

# 3. Net formula on every payout row ------------------------------------------
problems = []
for p in payouts:
    v = {k: Decimal(p[k]) for k in MONEY_FIELDS}
    net = v["gross_sales"] - v["commission_amount"] + v["tip_passed_through"] - v["refund_deducted"] + v["adjustments"]
    if net != v["net_payout"]:
        problems.append(f"{p['external_order_id']}: formula gives {net}, row says {v['net_payout']}")
check("every payout row satisfies the net_payout formula exactly", problems)

# 4. Clean rows match independent recomputation ------------------------------
problems = []
clean_count = 0
for o in pos:
    eid = o["external_order_id"]
    if eid in error_by_id:
        continue
    rows = payout_by_id.get(eid, [])
    if o["status"] == "cancelled":
        if rows:
            problems.append(f"{eid}: cancelled clean order has a payout row")
        continue
    if len(rows) != 1:
        problems.append(f"{eid}: expected 1 payout row, found {len(rows)}")
        continue
    p, exp = rows[0], expected_row(o)
    clean_count += 1
    if p["marketplace"] != o["marketplace"]:
        problems.append(f"{eid}: marketplace mismatch")
    for k, want in exp.items():
        if Decimal(p[k]) != want:
            problems.append(f"{eid}: {k} is {p[k]}, expected {want}")
    order_wk = week_start(datetime.fromisoformat(o["order_datetime"]).date())
    paid_wk = date.fromisoformat(p["payout_date"]) - timedelta(days=9)
    allowed = {order_wk} | ({order_wk + timedelta(days=7)} if eid in edge_ids else set())
    if paid_wk not in allowed:
        problems.append(f"{eid}: paid for week of {paid_wk}, ordered week of {order_wk}")
check(f"clean rows match POS + contract exactly ({clean_count} paid clean rows)", problems)
check("payout rows all trace to a POS order", [f"orphan {i}" for i in payout_by_id if i not in pos_by_id])
check("each payout_id has a single date and marketplace",
      [f"{pid} inconsistent" for pid in {p["payout_id"] for p in payouts}
       if len({(p["payout_date"], p["marketplace"]) for p in payouts if p["payout_id"] == pid}) != 1])

# Answer key values agree with the data.
problems = []
for e in errors:
    eid, t = e["external_order_id"], e["error_type"]
    o, exp = pos_by_id[eid], expected_row(pos_by_id[eid])
    p = payout_by_id.get(eid, [None])[0]
    if t == "wrong_commission_rate":
        want = (exp["commission_amount"], Decimal(p["commission_amount"]))
        if Decimal(p["commission_rate_applied"]) == exp["commission_rate_applied"]:
            problems.append(f"{eid}: rate applied is actually correct")
    elif t == "missing_from_payout":
        want = (exp["net_payout"], Decimal("0.00"))
    elif t == "refund_deducted_twice":
        want = (Decimal(o["refund_amount"]), Decimal(p["refund_deducted"]))
        if Decimal(p["refund_deducted"]) != 2 * Decimal(o["refund_amount"]):
            problems.append(f"{eid}: refund not doubled")
    elif t == "refund_without_pos_refund":
        want = (Decimal("0.00"), Decimal(p["refund_deducted"]))
        if o["status"] != "completed" or Decimal(o["refund_amount"]) != 0:
            problems.append(f"{eid}: POS does show a refund")
    elif t == "commission_on_cancelled_order":
        want = (Decimal("0.00"), Decimal(p["commission_amount"]))
        if o["status"] != "cancelled":
            problems.append(f"{eid}: POS order not cancelled")
    elif t == "tip_not_fully_passed_through":
        want = (Decimal(o["tip"]), Decimal(p["tip_passed_through"]))
    else:
        problems.append(f"{eid}: unknown error type {t}")
        continue
    got = (Decimal(e["expected_value"]), Decimal(e["actual_value"]))
    if got != want:
        problems.append(f"{eid} ({t}): key says {got}, data says {want}")
    if got[0] == got[1]:
        problems.append(f"{eid} ({t}): expected equals actual, not an error")
check("answer key expected/actual values agree with the data", problems)

# 5. Edge cases do not overlap errors ------------------------------------------
check("no edge case id overlaps a seeded error id",
      [f"{i} is both an edge case and an error" for i in edge_ids & set(error_by_id)])

# 6. Determinism ---------------------------------------------------------------
def digests(root):
    return {rel: hashlib.sha256((root / rel).read_bytes()).hexdigest() for rel in OUTPUT_FILES}

with tempfile.TemporaryDirectory() as t1, tempfile.TemporaryDirectory() as t2:
    for out in (t1, t2):
        subprocess.run([sys.executable, str(ROOT / "scripts" / "generate_data.py"), "--out", out],
                       check=True, capture_output=True)
    d1, d2, current = digests(Path(t1)), digests(Path(t2)), digests(ROOT)
    check("generator is deterministic (two fresh runs + checked-in files identical)",
          [f"{rel} differs" for rel in OUTPUT_FILES if not d1[rel] == d2[rel] == current[rel]])

print()
if failures:
    print(f"{len(failures)} check(s) FAILED")
    sys.exit(1)
print("All checks passed.")
