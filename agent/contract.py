"""Contract rules as code: rate lookup, rounding, and payout-week timing."""

from datetime import date, datetime, time, timedelta
from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")
LATE_SUNDAY_CUTOFF = time(23, 0)  # Sunday orders from here may settle the next week


def money(x):
    return Decimal(x).quantize(CENT, rounding=ROUND_HALF_UP)


def rate_for(terms, marketplace, order_type, on_date):
    """Latest effective_date <= on_date for the marketplace and order type."""
    applicable = [(t.effective_date, t.commission_rate) for t in terms
                  if t.marketplace == marketplace and t.order_type == order_type
                  and t.effective_date <= on_date]
    if not applicable:
        raise LookupError(f"no contract rate for {marketplace} {order_type} on {on_date}")
    return max(applicable)[1]


def week_start(d):
    return d - timedelta(days=d.weekday())


def payout_week_start(payout_date):
    """Payouts are dated the Wednesday after the week ends (Monday + 9 days)."""
    return payout_date - timedelta(days=9)


def allowed_week_starts(order_dt):
    """Payout weeks (by Monday) in which an order may legitimately appear."""
    wk = week_start(order_dt.date())
    weeks = {wk}
    if order_dt.weekday() == 6 and order_dt.time() >= LATE_SUNDAY_CUTOFF:
        weeks.add(wk + timedelta(days=7))
    return weeks


def net_payout(gross, commission, tip, refund, adjustments):
    return gross - commission + tip - refund + adjustments
