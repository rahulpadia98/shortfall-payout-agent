"""Deterministic reconciliation of POS orders against payout rows (no LLM)."""

from collections import defaultdict
from decimal import Decimal

from .contract import allowed_week_starts, money, net_payout, payout_week_start, rate_for
from .findings import Finding

ZERO = Decimal("0.00")

RULES = {
    "wrong_commission_rate": "Rule 3: commission rate is the contract rate for the marketplace and order type "
                             "with the latest effective date on or before the order date.",
    "missing_from_payout": "Rules 8-9: every completed or refunded order must appear in a payout.",
    "refund_deducted_twice": "Rule 6: a refund is deducted once, in the amount refunded to the customer.",
    "refund_without_pos_refund": "Rule 6: only refunds recorded in the POS are deducted from a payout.",
    "commission_on_cancelled_order": "Rule 9: a cancelled order has no commission and no payout row.",
    "tip_not_fully_passed_through": "Rule 5: tips pass through at 100%.",
    "payout_without_pos_order": "Rules 8-9: a payout row must correspond to a POS order.",
}
UNCLASSIFIED_RULES = {
    "gross_sales": "Rule 1: gross sales = subtotal - promo discount.",
    "commission_amount": "Rule 2: commission = gross sales x rate, rounded half-up.",
    "tip_passed_through": "Rule 5: tips pass through at 100%.",
    "refund_deducted": "Rule 6: refunds are deducted once, in the amount refunded.",
    "adjustments": "Rule 7: adjustments are zero.",
    "net_payout": "Rule 8: net = gross - commission + tip - refund + adjustments.",
    "payout_id": "Rules 10-11: an order is paid in its own week's payout, or the next week's if "
                 "placed Sunday from 11:00 PM.",
    "marketplace": "An order is paid by the marketplace it was placed through.",
    "external_order_id": "Each order appears in at most one payout row.",
}


def _fmt(v):
    return f"{v:.2f}" if isinstance(v, Decimal) else str(v)


class _Builder:
    def __init__(self):
        self.items = []

    def add(self, order, row, ftype, field, expected, actual, rule=None, status="matched"):
        diff = ""
        if isinstance(expected, Decimal) and isinstance(actual, Decimal):
            diff = _fmt(actual - expected)
        self.items.append(Finding(
            finding_id="", external_order_id=(order or row).external_order_id,
            location_id=order.location_id if order else "",
            marketplace=order.marketplace if order else row.marketplace,
            payout_id=row.payout_id if row else "", finding_type=ftype, field=field,
            expected_value=_fmt(expected), actual_value=_fmt(actual), difference=diff,
            contract_rule=rule or RULES.get(ftype) or UNCLASSIFIED_RULES[field],
            match_status=status))


def _check_order(b, order, rows, terms):
    if order.status == "cancelled":
        for row in rows:
            if row.commission_amount > 0:
                b.add(order, row, "commission_on_cancelled_order", "commission_amount",
                      ZERO, row.commission_amount)
            else:
                b.add(order, row, "unclassified", "net_payout", ZERO, row.net_payout,
                      rule="Rule 9: a cancelled order has no payout row.")
        return

    gross = order.subtotal - order.promo_discount
    rate = rate_for(terms, order.marketplace, order.order_type, order.order_datetime.date())
    commission = money(gross * rate)

    if not rows:
        net = net_payout(gross, commission, order.tip, order.refund_amount, ZERO)
        b.add(order, None, "missing_from_payout", "net_payout", net, ZERO, status="no_payout_row")
        return

    if len(rows) > 1:
        b.add(order, rows[1], "unclassified", "external_order_id", "1 payout row",
              f"{len(rows)} payout rows")
    row = rows[0]
    explained = False  # a component finding already accounts for the net difference

    if row.marketplace != order.marketplace:
        b.add(order, row, "unclassified", "marketplace", order.marketplace, row.marketplace)
    if payout_week_start(row.payout_date) not in allowed_week_starts(order.order_datetime):
        allowed = ", ".join(sorted(w.isoformat() for w in allowed_week_starts(order.order_datetime)))
        b.add(order, row, "unclassified", "payout_id", f"payout week of {allowed}",
              f"{row.payout_id} (week of {payout_week_start(row.payout_date)})")

    if row.gross_sales != gross:
        b.add(order, row, "unclassified", "gross_sales", gross, row.gross_sales)
        explained = True

    if row.commission_rate_applied != rate:
        rule = (f"{RULES['wrong_commission_rate']} Applicable rate: {rate}; applied: "
                f"{row.commission_rate_applied}.")
        b.add(order, row, "wrong_commission_rate", "commission_amount", commission,
              row.commission_amount, rule=rule)
        explained = True
    elif row.commission_amount != commission and row.gross_sales == gross:
        b.add(order, row, "unclassified", "commission_amount", commission, row.commission_amount)
        explained = True

    refund = order.refund_amount
    if row.refund_deducted != refund:
        if refund == 0 and row.refund_deducted > 0:
            ftype = "refund_without_pos_refund"
        elif refund > 0 and row.refund_deducted == refund * 2:
            ftype = "refund_deducted_twice"
        else:
            ftype = "unclassified"
        b.add(order, row, ftype, "refund_deducted", refund, row.refund_deducted)
        explained = True

    if row.tip_passed_through != order.tip:
        ftype = "tip_not_fully_passed_through" if row.tip_passed_through < order.tip else "unclassified"
        b.add(order, row, ftype, "tip_passed_through", order.tip, row.tip_passed_through)
        explained = True

    if row.adjustments != ZERO:
        b.add(order, row, "unclassified", "adjustments", ZERO, row.adjustments)
        explained = True

    own_net = net_payout(row.gross_sales, row.commission_amount, row.tip_passed_through,
                         row.refund_deducted, row.adjustments)
    if own_net != row.net_payout:
        b.add(order, row, "unclassified", "net_payout", own_net, row.net_payout,
              rule="Rule 8: net must equal the row's own gross - commission + tip - refund + adjustments.")
    elif not explained:
        expected_net = net_payout(gross, commission, order.tip, refund, ZERO)
        if row.net_payout != expected_net:
            b.add(order, row, "unclassified", "net_payout", expected_net, row.net_payout)


def reconcile(orders, payouts, terms):
    """Return the list of Findings, ids assigned in deterministic order."""
    by_order = defaultdict(list)
    for p in payouts:
        by_order[p.external_order_id].append(p)

    b = _Builder()
    known = set()
    for order in sorted(orders, key=lambda o: o.order_id):
        known.add(order.external_order_id)
        _check_order(b, order, by_order.get(order.external_order_id, []), terms)

    for p in sorted(payouts, key=lambda p: (p.payout_date, p.external_order_id)):
        if p.external_order_id not in known:
            b.add(None, p, "payout_without_pos_order", "net_payout", ZERO, p.net_payout,
                  status="no_pos_order")

    for i, f in enumerate(b.items, start=1):
        f.finding_id = f"F-{i:04d}"
    return b.items
