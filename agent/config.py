"""Settings shared across the agent."""

from pathlib import Path

APP_NAME = "Shortfall"

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"

POS_ORDERS_CSV = DATA_DIR / "pos_orders.csv"
PAYOUTS_CSV = DATA_DIR / "payouts.csv"
CONTRACT_TERMS_CSV = DATA_DIR / "contract_terms.csv"
CONTRACT_RULES_MD = DATA_DIR / "contract_rules.md"

FINDINGS_CSV = OUTPUT_DIR / "findings.csv"
