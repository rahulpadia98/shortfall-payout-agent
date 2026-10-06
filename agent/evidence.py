"""Assemble the evidence for a finding from the POS order and payout row (data/ only)."""

from dataclasses import asdict
from decimal import Decimal

from .contract import rate_for

MONEY_FIELDS_ORDER = ("subtotal", "tax", "tip", "promo_discount", "refund_amount")
MONEY_FIELDS_PAYOUT = ("gross_sales", "commission_amount", "tip_passed_through",
                       "refund_deducted", "adjustments", "net_payout")


def _s(v):
    return f"{v:.2f}" if isinstance(v, Decimal) else str(v)


def build_evidence(finding, orders_by_ext, payouts_by_ext, terms):
    order = orders_by_ext.get(finding.external_order_id)
    rows = payouts_by_ext.get(finding.external_order_id, [])
    row = next((r for r in rows if r.payout_id == finding.payout_id), rows[0] if rows else None)

    ev = {
        "finding": {k: v for k, v in asdict(finding).items() if k != "finding_id"},
        "order": None,
        "payout": None,
        "contract_rate": None,
    }
    if order:
        ev["order"] = {
            "order_id": order.order_id, "order_type": order.order_type, "status": order.status,
            "order_datetime": order.order_datetime.strftime("%Y-%m-%d %H:%M"),
            **{k: _s(getattr(order, k)) for k in MONEY_FIELDS_ORDER},
        }
        ev["contract_rate"] = _s(rate_for(terms, order.marketplace, order.order_type,
                                          order.order_datetime.date()))
    if row:
        ev["payout"] = {
            "payout_id": row.payout_id, "payout_date": row.payout_date.isoformat(),
            "commission_rate_applied": _s(row.commission_rate_applied),
            **{k: _s(getattr(row, k)) for k in MONEY_FIELDS_PAYOUT},
        }
    return ev


def allowed_amounts(evidence):
    """Every dollar value appearing in the evidence, as absolute Decimals."""
    vals = set()

    def add(s):
        try:
            vals.add(abs(Decimal(s)))
        except Exception:
            pass

    f = evidence["finding"]
    for k in ("expected_value", "actual_value", "difference"):
        add(f[k])
    for section, fields in (("order", MONEY_FIELDS_ORDER), ("payout", MONEY_FIELDS_PAYOUT)):
        if evidence[section]:
            for k in fields:
                add(evidence[section][k])
    return vals
