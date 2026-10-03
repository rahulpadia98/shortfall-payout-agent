"""Generate synthetic data for the delivery payout reconciliation project.

Everything here is fictional: "Harbor Taco Co." (locations LOC-1..LOC-3) selling
through two made-up marketplaces, "Marketplace A" and "Marketplace B".

Output (deterministic: fixed seed, so every run writes identical files):
    data/pos_orders.csv       POS order log (source of truth for what was sold)
    data/payouts.csv          marketplace payout line items, one per order
    data/contract_terms.csv   commission rates by marketplace/order_type/date
    eval/seeded_errors.csv    answer key: injected payout errors
    eval/edge_cases.csv       answer key: suspicious-looking rows that are correct

BUSINESS RULES FOR CLEAN (NON-ERROR) PAYOUT ROWS
------------------------------------------------
- gross_sales = subtotal - promo_discount. Promos are merchant-funded, so they
  lower both the merchant's sales and the commission base.
- commission_rate_applied = the contract rate for the order's marketplace and
  order_type with the latest effective_date <= the order's date (local time).
- commission_amount = gross_sales * commission_rate_applied, rounded half-up
  to the cent.
- Tax is remitted by the marketplace and is not part of the payout.
- tip_passed_through = tip (tips pass through 100%).
- refund_deducted = POS refund_amount. Refunds (full or partial) do not reverse
  the commission.
- adjustments = 0.00.
- net_payout = gross_sales - commission_amount + tip_passed_through
               - refund_deducted + adjustments
- Cancelled orders have no payout row.
- Payouts are weekly per marketplace. Weeks run Monday to Sunday; the payout is
  dated the Wednesday after the week ends. An order is paid in the payout for
  the week of its order date, except that a few late Sunday-night orders are
  legitimately paid in the following week's payout (see eval/edge_cases.csv).

Seeded errors violate exactly one of these rules per order. The marketplace's
own row stays arithmetically consistent (net_payout matches the formula on the
row's own fields), so errors show up only against the POS and the contract.

Usage: python scripts/generate_data.py [--out DIR]   (DIR defaults to repo root)
"""

import argparse
import csv
import random
from datetime import date, datetime, time, timedelta
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

SEED = 42
START_DATE = date(2026, 6, 1)  # a Monday
NUM_DAYS = 60
RATE_CHANGE_DATE = date(2026, 7, 1)

LOCATIONS = {"LOC-1": Decimal("1.2"), "LOC-2": Decimal("1.0"), "LOC-3": Decimal("0.8")}
BASE_ORDERS_PER_DAY = 10.0
WEEKEND_FACTOR = 1.25  # Fri, Sat, Sun
TAX_RATE = Decimal("0.0825")

MARKETPLACES = {"A": "Marketplace A", "B": "Marketplace B"}

# (marketplace, order_type, commission_rate, effective_date)
CONTRACT_TERMS = [
    ("Marketplace A", "delivery", Decimal("0.25"), START_DATE),
    ("Marketplace A", "delivery", Decimal("0.22"), RATE_CHANGE_DATE),
    ("Marketplace A", "pickup", Decimal("0.10"), START_DATE),
    ("Marketplace B", "delivery", Decimal("0.20"), START_DATE),
    ("Marketplace B", "pickup", Decimal("0.08"), START_DATE),
]

CENT = Decimal("0.01")
ZERO = Decimal("0.00")


def money(x):
    return Decimal(x).quantize(CENT, rounding=ROUND_HALF_UP)


def contract_rate(marketplace, order_type, on_date):
    applicable = [
        (eff, rate)
        for mp, ot, rate, eff in CONTRACT_TERMS
        if mp == marketplace and ot == order_type and eff <= on_date
    ]
    return max(applicable)[1]


def week_start(d):
    return d - timedelta(days=d.weekday())


def payout_key(marketplace, wk_start):
    """(payout_id, payout_date) for a marketplace's payout covering one week."""
    iso_year, iso_week, _ = wk_start.isocalendar()
    letter = "A" if marketplace == "Marketplace A" else "B"
    return f"P{letter}-{iso_year}W{iso_week:02d}", wk_start + timedelta(days=9)


# --------------------------------------------------------------------------
# Orders
# --------------------------------------------------------------------------

def random_order_time(rng):
    r = rng.random()
    if r < 0.40:
        lo, hi = 11 * 60, 14 * 60  # lunch
    elif r < 0.90:
        lo, hi = 17 * 60, 21 * 60 + 30  # dinner
    elif r < 0.95:
        lo, hi = 14 * 60, 17 * 60  # afternoon
    else:
        lo, hi = 21 * 60 + 30, 24 * 60  # late night
    minute = rng.randrange(lo, hi)
    return time(minute // 60, minute % 60)


def generate_orders(rng):
    orders = []
    for day in range(NUM_DAYS):
        d = START_DATE + timedelta(days=day)
        weekend = d.weekday() >= 4
        for loc, weight in LOCATIONS.items():
            mean = BASE_ORDERS_PER_DAY * float(weight) * (WEEKEND_FACTOR if weekend else 1.0)
            count = max(0, round(rng.gauss(mean, mean ** 0.5)))
            for _ in range(count):
                orders.append(make_order(rng, loc, datetime.combine(d, random_order_time(rng))))
    return orders


def make_order(rng, location_id, order_dt):
    marketplace = "Marketplace A" if rng.random() < 0.55 else "Marketplace B"
    order_type = "delivery" if rng.random() < 0.85 else "pickup"
    subtotal = money(Decimal(rng.randint(1200, 9000)) / 100)
    tax = money(subtotal * TAX_RATE)

    tip = ZERO
    if order_type == "delivery" and rng.random() < 0.75:
        tip = money(subtotal * Decimal(rng.choice([10, 15, 18, 20, 25])) / 100)

    promo = ZERO
    if rng.random() < 0.20:
        promo = money(rng.choice([3, 4, 5, 6, 8, 10]))

    r = rng.random()
    status, refund = "completed", ZERO
    if r < 0.03:
        status = "cancelled"
    elif r < 0.07:
        status = "refunded"
        gross = subtotal - promo
        refund = gross if rng.random() < 0.5 else money(gross * Decimal(rng.randint(15, 60)) / 100)

    return {
        "order_id": None,
        "location_id": location_id,
        "marketplace": marketplace,
        "order_type": order_type,
        "external_order_id": None,
        "order_datetime": order_dt,
        "subtotal": subtotal,
        "tax": tax,
        "tip": tip,
        "promo_discount": promo,
        "status": status,
        "refund_amount": refund,
    }


def assign_ids(orders):
    orders.sort(key=lambda o: (o["order_datetime"], o["location_id"]))
    counters = {"Marketplace A": 100001, "Marketplace B": 500001}
    for i, o in enumerate(orders, start=1):
        o["order_id"] = f"HTC-{i:06d}"
        letter = "A" if o["marketplace"] == "Marketplace A" else "B"
        o["external_order_id"] = f"MP{letter}-{counters[o['marketplace']]}"
        counters[o["marketplace"]] += 1


# --------------------------------------------------------------------------
# Legitimate edge cases (reshaped before ids are assigned)
# --------------------------------------------------------------------------

def pick(rng, orders, used, predicate):
    candidates = [o for o in orders if id(o) not in used and predicate(o)]
    if not candidates:
        raise RuntimeError("no candidate order for edge case / error")
    chosen = rng.choice(candidates)
    used.add(id(chosen))
    return chosen


def plant_edge_cases(rng, orders, used):
    """Return [(order, description_fn)] and the set of orders paid a week late."""
    edges, late = [], set()

    def is_clean_delivery(o):
        return o["status"] == "completed" and o["order_type"] == "delivery"

    # 1-2. Large merchant-funded promo lowers the commission base.
    for _ in range(2):
        o = pick(rng, orders, used, lambda o: is_clean_delivery(o) and o["subtotal"] >= 50)
        o["promo_discount"] = money(int(o["subtotal"] * Decimal("0.45")))
        edges.append((o, lambda o: (
            f"Merchant-funded promo of ${o['promo_discount']} (about 45% of subtotal ${o['subtotal']}) "
            f"correctly lowers the commission base; commission looks low vs. subtotal but is correct")))

    # 3-4. Orders on either side of Marketplace A's delivery rate change.
    boundary = RATE_CHANGE_DATE - timedelta(days=1)
    o = pick(rng, orders, used, lambda o: is_clean_delivery(o) and o["marketplace"] == "Marketplace A"
             and o["order_datetime"].date() == boundary)
    o["order_datetime"] = datetime.combine(boundary, time(23, 52))
    edges.append((o, lambda o: (
        f"Ordered {o['order_datetime']:%Y-%m-%d %H:%M}, minutes before the {RATE_CHANGE_DATE} rate "
        f"change; correctly charged the old 25% delivery rate")))

    o = pick(rng, orders, used, lambda o: is_clean_delivery(o) and o["marketplace"] == "Marketplace A"
             and o["order_datetime"].date() == RATE_CHANGE_DATE)
    o["order_datetime"] = datetime.combine(RATE_CHANGE_DATE, time(0, 7))
    edges.append((o, lambda o: (
        f"Ordered {o['order_datetime']:%Y-%m-%d %H:%M}, just after the rate change took effect; "
        f"correctly charged the new 22% delivery rate")))

    # 5-6. Partial refund deducted exactly once.
    for _ in range(2):
        o = pick(rng, orders, used, lambda o: is_clean_delivery(o) and o["subtotal"] - o["promo_discount"] >= 30)
        o["status"] = "refunded"
        o["refund_amount"] = money((o["subtotal"] - o["promo_discount"]) * Decimal(rng.randint(20, 40)) / 100)
        edges.append((o, lambda o: (
            f"Partial refund of ${o['refund_amount']} on gross sales of "
            f"${o['subtotal'] - o['promo_discount']}, deducted once at the correct amount")))

    # 7-8. Late Sunday-night order paid in the following week's payout.
    last_full_sunday = week_start(START_DATE + timedelta(days=NUM_DAYS - 1)) - timedelta(days=1)
    for minute in (44, 57):
        o = pick(rng, orders, used, lambda o: is_clean_delivery(o) and o["order_datetime"].weekday() == 6
                 and o["order_datetime"].date() <= last_full_sunday)
        o["order_datetime"] = datetime.combine(o["order_datetime"].date(), time(23, minute))
        late.add(id(o))
        edges.append((o, lambda o: (
            f"Placed Sunday {o['order_datetime']:%Y-%m-%d %H:%M}, end of the payout week; appears in "
            f"the following week's payout with correct amounts")))

    # 9. Cancelled order correctly absent from payouts.
    o = pick(rng, orders, used, lambda o: o["status"] == "cancelled")
    edges.append((o, lambda o: "Cancelled order; correctly has no payout row"))

    # 10. Pickup order at the lower pickup rate.
    o = pick(rng, orders, used, lambda o: o["status"] == "completed" and o["order_type"] == "pickup"
             and o["marketplace"] == "Marketplace A" and o["promo_discount"] == 0)
    edges.append((o, lambda o: "Pickup order charged the contracted 10% pickup rate, lower than delivery"))

    return edges, late


# --------------------------------------------------------------------------
# Payouts
# --------------------------------------------------------------------------

def clean_payout_row(o, late):
    order_date = o["order_datetime"].date()
    wk = week_start(order_date) + timedelta(days=7 if id(o) in late else 0)
    payout_id, payout_date = payout_key(o["marketplace"], wk)
    gross = o["subtotal"] - o["promo_discount"]
    rate = contract_rate(o["marketplace"], o["order_type"], order_date)
    row = {
        "payout_id": payout_id,
        "payout_date": payout_date,
        "marketplace": o["marketplace"],
        "external_order_id": o["external_order_id"],
        "gross_sales": gross,
        "commission_rate_applied": rate,
        "commission_amount": money(gross * rate),
        "tip_passed_through": o["tip"],
        "refund_deducted": o["refund_amount"],
        "adjustments": ZERO,
    }
    return recompute_net(row)


def recompute_net(row):
    row["net_payout"] = (row["gross_sales"] - row["commission_amount"] + row["tip_passed_through"]
                         - row["refund_deducted"] + row["adjustments"])
    return row


def inject_errors(rng, orders, payouts, used):
    """Mutate payouts in place; return answer-key rows."""
    errors = []

    def record(o, error_type, expected, actual):
        errors.append({"external_order_id": o["external_order_id"], "error_type": error_type,
                       "expected_value": expected, "actual_value": actual})

    def completed(o):
        return o["status"] == "completed"

    # wrong_commission_rate: 4 stale pre-change A delivery rates, 3 pickups billed at delivery rate.
    wrong_rates = []
    for _ in range(4):
        o = pick(rng, orders, used, lambda o: completed(o) and o["marketplace"] == "Marketplace A"
                 and o["order_type"] == "delivery" and o["order_datetime"].date() >= RATE_CHANGE_DATE)
        wrong_rates.append((o, contract_rate(o["marketplace"], "delivery", RATE_CHANGE_DATE - timedelta(days=1))))
    for _ in range(3):
        o = pick(rng, orders, used, lambda o: completed(o) and o["order_type"] == "pickup")
        wrong_rates.append((o, contract_rate(o["marketplace"], "delivery", o["order_datetime"].date())))
    for o, wrong_rate in wrong_rates:
        row = payouts[o["external_order_id"]]
        expected = row["commission_amount"]
        row["commission_rate_applied"] = wrong_rate
        row["commission_amount"] = money(row["gross_sales"] * wrong_rate)
        recompute_net(row)
        record(o, "wrong_commission_rate", expected, row["commission_amount"])

    # missing_from_payout
    for _ in range(7):
        o = pick(rng, orders, used, completed)
        row = payouts.pop(o["external_order_id"])
        record(o, "missing_from_payout", row["net_payout"], ZERO)

    # refund_deducted_twice
    for _ in range(7):
        o = pick(rng, orders, used, lambda o: o["status"] == "refunded")
        row = payouts[o["external_order_id"]]
        row["refund_deducted"] = o["refund_amount"] * 2
        recompute_net(row)
        record(o, "refund_deducted_twice", o["refund_amount"], row["refund_deducted"])

    # refund_without_pos_refund
    for _ in range(7):
        o = pick(rng, orders, used, completed)
        row = payouts[o["external_order_id"]]
        row["refund_deducted"] = money(row["gross_sales"] * Decimal(rng.randint(20, 100)) / 100)
        recompute_net(row)
        record(o, "refund_without_pos_refund", ZERO, row["refund_deducted"])

    # commission_on_cancelled_order: marketplace bills commission on a cancelled order.
    for _ in range(6):
        o = pick(rng, orders, used, lambda o: o["status"] == "cancelled")
        row = clean_payout_row(o, late=set())
        row["commission_amount"] = money((o["subtotal"] - o["promo_discount"]) * row["commission_rate_applied"])
        row["gross_sales"] = ZERO
        row["tip_passed_through"] = ZERO
        payouts[o["external_order_id"]] = recompute_net(row)
        record(o, "commission_on_cancelled_order", ZERO, row["commission_amount"])

    # tip_not_fully_passed_through
    for _ in range(6):
        o = pick(rng, orders, used, lambda o: completed(o) and o["tip"] > 0)
        row = payouts[o["external_order_id"]]
        row["tip_passed_through"] = money(o["tip"] * Decimal(rng.choice([0, 50, 70, 80])) / 100)
        recompute_net(row)
        record(o, "tip_not_fully_passed_through", o["tip"], row["tip_passed_through"])

    return errors


# --------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------

def fmt(v):
    if isinstance(v, datetime):
        return v.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(v, date):
        return v.isoformat()
    if isinstance(v, Decimal):
        return f"{v:.2f}"
    return v


def write_csv(path, fieldnames, rows, rate_fields=()):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: (str(row[k]) if k in rate_fields else fmt(row[k])) for k in fieldnames})


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()

    rng = random.Random(SEED)
    orders = generate_orders(rng)

    used = set()
    edges, late = plant_edge_cases(rng, orders, used)
    assign_ids(orders)

    payouts = {o["external_order_id"]: clean_payout_row(o, late)
               for o in orders if o["status"] != "cancelled"}
    errors = inject_errors(rng, orders, payouts, used)

    write_csv(args.out / "data" / "pos_orders.csv",
              ["order_id", "location_id", "marketplace", "order_type", "external_order_id",
               "order_datetime", "subtotal", "tax", "tip", "promo_discount", "status", "refund_amount"],
              orders)
    write_csv(args.out / "data" / "payouts.csv",
              ["payout_id", "payout_date", "marketplace", "external_order_id", "gross_sales",
               "commission_rate_applied", "commission_amount", "tip_passed_through",
               "refund_deducted", "adjustments", "net_payout"],
              sorted(payouts.values(), key=lambda r: (r["payout_date"], r["marketplace"], r["external_order_id"])),
              rate_fields={"commission_rate_applied"})
    write_csv(args.out / "data" / "contract_terms.csv",
              ["marketplace", "order_type", "commission_rate", "effective_date"],
              [dict(zip(["marketplace", "order_type", "commission_rate", "effective_date"], t))
               for t in CONTRACT_TERMS],
              rate_fields={"commission_rate"})
    write_csv(args.out / "eval" / "seeded_errors.csv",
              ["external_order_id", "error_type", "expected_value", "actual_value"],
              sorted(errors, key=lambda e: (e["error_type"], e["external_order_id"])))
    write_csv(args.out / "eval" / "edge_cases.csv",
              ["external_order_id", "description"],
              sorted(({"external_order_id": o["external_order_id"], "description": describe(o)}
                      for o, describe in edges), key=lambda e: e["external_order_id"]))

    print(f"orders={len(orders)} payout_rows={len(payouts)} errors={len(errors)} edge_cases={len(edges)}")
    print(f"wrote data/ and eval/ under {args.out}")


if __name__ == "__main__":
    main()
