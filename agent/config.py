"""Settings shared across the agent."""

import os
from pathlib import Path

from dotenv import load_dotenv

APP_NAME = "Shortfall"

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"

POS_ORDERS_CSV = DATA_DIR / "pos_orders.csv"
PAYOUTS_CSV = DATA_DIR / "payouts.csv"
CONTRACT_TERMS_CSV = DATA_DIR / "contract_terms.csv"
CONTRACT_RULES_MD = DATA_DIR / "contract_rules.md"

FINDINGS_CSV = OUTPUT_DIR / "findings.csv"
LLM_CACHE_JSON = OUTPUT_DIR / "llm_cache.json"
REPORT_MD = OUTPUT_DIR / "findings_report.md"

DEFAULT_MODEL = "claude-sonnet-5-5"

load_dotenv(ROOT / ".env")
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL") or DEFAULT_MODEL
