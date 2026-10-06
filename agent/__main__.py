"""Command line entry point: python -m agent [--no-llm]"""

import argparse
from collections import Counter

from . import config
from .findings import FINDING_TYPES, write_findings
from .loader import load_contract_terms, load_orders, load_payouts
from .reconcile import reconcile


def main():
    parser = argparse.ArgumentParser(prog="agent", description=f"{config.APP_NAME}: payout reconciliation")
    parser.add_argument("--no-llm", action="store_true",
                        help="run only the deterministic reconciliation (no explanations)")
    args = parser.parse_args()

    orders, payouts, terms = load_orders(), load_payouts(), load_contract_terms()
    findings = reconcile(orders, payouts, terms)
    write_findings(config.FINDINGS_CSV, findings)

    print(f"{config.APP_NAME} reconciliation")
    print(f"  orders: {len(orders)}  payout rows: {len(payouts)}  findings: {len(findings)}")
    counts = Counter(f.finding_type for f in findings)
    print("\nFindings by type:")
    for t in FINDING_TYPES:
        print(f"  {t:<32}{counts.get(t, 0):>4}")
    print(f"\nWrote {config.FINDINGS_CSV}")

    if not args.no_llm:
        print("\nLLM explanations are not available yet; ran the deterministic stage only.")


if __name__ == "__main__":
    main()
