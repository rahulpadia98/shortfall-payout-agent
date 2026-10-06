"""Write output/findings_report.md."""

from collections import Counter, defaultdict
from decimal import Decimal

from . import config
from .findings import FINDING_TYPES


def _money(v):
    return f"${v:,.2f}" if v >= 0 else f"-${-v:,.2f}"


def _summary_table(findings, results):
    counts = Counter(f.finding_type for f in findings)
    totals = defaultdict(Decimal)
    for f in findings:
        if f.difference:
            totals[f.finding_type] += Decimal(f.difference)
    lines = ["| Finding type | Count | Net difference (actual - expected) | Low confidence | Amount mismatches |",
             "|---|---:|---:|---:|---:|"]
    for t in FINDING_TYPES:
        n = counts.get(t, 0)
        if not n:
            continue
        rs = [results.get(f.finding_id, {}) for f in findings if f.finding_type == t]
        low = sum(1 for r in rs if r.get("confidence") == "low")
        bad = sum(1 for r in rs if r.get("explanation_check") == "mismatch")
        lines.append(f"| {t} | {n} | {_money(totals[t])} | {low} | {bad} |")
    lines.append(f"| **Total** | **{len(findings)}** | **{_money(sum(totals.values(), Decimal('0')))}** | | |")
    return "\n".join(lines)


def _evidence_block(ev):
    f = ev["finding"]
    rows = [("Field", f["field"]), ("Expected", f["expected_value"]), ("Actual", f["actual_value"]),
            ("Difference", f["difference"] or "n/a"), ("Match status", f["match_status"]),
            ("Contract rule", f["contract_rule"])]
    if ev["order"]:
        o = ev["order"]
        rows += [("POS order", f"{o['order_id']} ({o['order_type']}, {o['status']}, {o['order_datetime']})"),
                 ("POS subtotal / promo / tip / refund",
                  f"{o['subtotal']} / {o['promo_discount']} / {o['tip']} / {o['refund_amount']}"),
                 ("Contract rate on order date", ev["contract_rate"])]
    if ev["payout"]:
        p = ev["payout"]
        rows += [("Payout row", f"{p['payout_id']} (paid {p['payout_date']})"),
                 ("Payout gross / rate / commission",
                  f"{p['gross_sales']} / {p['commission_rate_applied']} / {p['commission_amount']}"),
                 ("Payout tip / refund / adjustments / net",
                  f"{p['tip_passed_through']} / {p['refund_deducted']} / {p['adjustments']} / {p['net_payout']}")]
    out = ["| | |", "|---|---|"]
    out += [f"| {k} | {str(v).replace('|', '/')} |" for k, v in rows]
    return "\n".join(out)


def write_report(findings, results, stats, model, path=config.REPORT_MD):
    parts = [f"# {config.APP_NAME} findings report", "",
             f"{len(findings)} findings. Amounts and finding types come from deterministic matching; "
             f"explanations were written by `{model}` and checked against the evidence.", "",
             "## Summary", "", _summary_table(findings, results), ""]
    if stats["errors"]:
        parts += [f"> {stats['errors']} finding(s) have no explanation because the model call failed "
                  "or returned invalid JSON.", ""]
    parts += ["## Findings", ""]
    for f in findings:
        r = results.get(f.finding_id, {})
        parts += [f"### {f.finding_id}: {f.finding_type} ({f.external_order_id})", "",
                  f"{f.marketplace}" + (f", {f.location_id}" if f.location_id else "")
                  + (f", payout {f.payout_id}" if f.payout_id else ""), "",
                  _evidence_block(r["evidence"]) if r.get("evidence") else "", ""]
        if "error" in r:
            parts += [f"**Explanation unavailable:** {r['error']}", ""]
            continue
        parts += [f"**Explanation** (confidence: {r['confidence']}): {r['explanation']}", ""]
        if f.finding_type == "unclassified" and r.get("suggested_type"):
            st = r["suggested_type"]
            parts += [f"**Suggested type:** {st['type']}. {st['reasoning']}", ""]
        if r["explanation_check"] == "mismatch":
            parts += [f"> **Check failed:** the explanation cites amounts not found in the evidence "
                      f"({', '.join('$' + a for a in r['bad_amounts'])}). Do not rely on the wording; "
                      "use the evidence table.", ""]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(parts), encoding="utf-8")
