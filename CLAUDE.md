# Delivery Payout Reconciliation Agent

Portfolio project: an agent that reconciles a restaurant's POS delivery orders
against marketplace payout reports and flags discrepancies.

## Standing rules

- All data is synthetic and fictional. Never reference real companies, real
  restaurants, or the user's employer. The business is "Harbor Taco Co." and the
  marketplaces are "Marketplace A" and "Marketplace B".
- Agent code must never read anything in `eval/`. `eval/` is the answer key and
  is used for scoring only.
- Arithmetic (matching, commissions, totals) is done in deterministic Python,
  never by an LLM.
- Ask before deleting or overwriting any existing file.
- Branding: this is a standalone portfolio product called "Shortfall", not tied
  to any real company. Never mention Loop or any real company in code, comments,
  docs, reports, or terminal output. The product name lives in a single setting,
  `APP_NAME = "Shortfall"` in `agent/config.py`; use it everywhere a product name
  appears in user-facing output.
- Never open, read, or print `.env`. During build phases, never open anything in
  `eval/` (scoring happens in a separate phase).

## Layout

- `data/`: agent inputs (`pos_orders.csv`, `payouts.csv`, `contract_terms.csv`).
- `eval/`: answer key (`seeded_errors.csv`, `edge_cases.csv`). Scoring only.
- `scripts/`: data generator and sanity checks. These are not agent code.
- `agent/`: the Shortfall agent. `reconcile.py` does all matching and math
  (Decimal, no LLM); `llm.py` only writes explanations and checks their dollar
  amounts against the evidence; `report.py` writes the markdown report.
- `output/`: agent output (gitignored except `findings_report.md`):
  `findings.csv`, `llm_cache.json`, `findings_report.md`.
- `data/contract_rules.md`: plain-English contract rules, read by the agent and
  sent to the model with each finding.

`data/` and `eval/` are generated output. `scripts/generate_data.py` rewrites
them deterministically (fixed seed), so a rerun reproduces identical files. The
business rules for clean rows are documented at the top of that script.

## Commands

```
.venv\Scripts\python scripts\generate_data.py   # regenerate data/ and eval/
.venv\Scripts\python scripts\check_data.py      # verify the generated data

.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m agent --no-llm          # deterministic stage only -> output/findings.csv
.venv\Scripts\python -m agent                   # plus LLM explanations -> output/findings_report.md
```

The LLM stage needs `ANTHROPIC_API_KEY` (and optionally `ANTHROPIC_MODEL`,
default `claude-sonnet-5-5`) in `.env` or the environment. Responses are cached in
`output/llm_cache.json`, so reruns only pay for new or changed findings.
