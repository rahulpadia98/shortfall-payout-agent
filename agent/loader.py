"""Load the agent's input CSVs. All money and rates are Decimal."""

import csv
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from . import config


@dataclass(frozen=True)
class Order:
    order_id: str
    location_id: str
    marketplace: str
    order_type: str
    external_order_id: str
    order_datetime: datetime
    subtotal: Decimal
    tax: Decimal
    tip: Decimal
    promo_discount: Decimal
    status: str
    refund_amount: Decimal


@dataclass(frozen=True)
class PayoutRow:
    payout_id: str
    payout_date: date
    marketplace: str
    external_order_id: str
    gross_sales: Decimal
    commission_rate_applied: Decimal
    commission_amount: Decimal
    tip_passed_through: Decimal
    refund_deducted: Decimal
    adjustments: Decimal
    net_payout: Decimal


@dataclass(frozen=True)
class ContractTerm:
    marketplace: str
    order_type: str
    commission_rate: Decimal
    effective_date: date


def _rows(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        yield from csv.DictReader(f)


def load_orders(path=config.POS_ORDERS_CSV):
    return [
        Order(
            order_id=r["order_id"], location_id=r["location_id"], marketplace=r["marketplace"],
            order_type=r["order_type"], external_order_id=r["external_order_id"],
            order_datetime=datetime.strptime(r["order_datetime"], "%Y-%m-%d %H:%M:%S"),
            subtotal=Decimal(r["subtotal"]), tax=Decimal(r["tax"]), tip=Decimal(r["tip"]),
            promo_discount=Decimal(r["promo_discount"]), status=r["status"],
            refund_amount=Decimal(r["refund_amount"]),
        )
        for r in _rows(path)
    ]


def load_payouts(path=config.PAYOUTS_CSV):
    return [
        PayoutRow(
            payout_id=r["payout_id"], payout_date=date.fromisoformat(r["payout_date"]),
            marketplace=r["marketplace"], external_order_id=r["external_order_id"],
            gross_sales=Decimal(r["gross_sales"]),
            commission_rate_applied=Decimal(r["commission_rate_applied"]),
            commission_amount=Decimal(r["commission_amount"]),
            tip_passed_through=Decimal(r["tip_passed_through"]),
            refund_deducted=Decimal(r["refund_deducted"]), adjustments=Decimal(r["adjustments"]),
            net_payout=Decimal(r["net_payout"]),
        )
        for r in _rows(path)
    ]


def load_contract_terms(path=config.CONTRACT_TERMS_CSV):
    return [
        ContractTerm(r["marketplace"], r["order_type"], Decimal(r["commission_rate"]),
                     date.fromisoformat(r["effective_date"]))
        for r in _rows(path)
    ]
