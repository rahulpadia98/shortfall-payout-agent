"""Finding record and CSV output."""

import csv
from dataclasses import asdict, dataclass, fields

FINDING_TYPES = [
    "wrong_commission_rate",
    "missing_from_payout",
    "refund_deducted_twice",
    "refund_without_pos_refund",
    "commission_on_cancelled_order",
    "tip_not_fully_passed_through",
    "payout_without_pos_order",
    "unclassified",
]


@dataclass
class Finding:
    finding_id: str
    external_order_id: str
    location_id: str
    marketplace: str
    payout_id: str
    finding_type: str
    field: str
    expected_value: str
    actual_value: str
    difference: str
    contract_rule: str
    match_status: str  # matched | no_payout_row | no_pos_order


def write_findings(path, findings):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[x.name for x in fields(Finding)], lineterminator="\n")
        w.writeheader()
        for fnd in findings:
            w.writerow(asdict(fnd))
