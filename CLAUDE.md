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

## Layout

- `data/`: agent inputs (`pos_orders.csv`, `payouts.csv`, `contract_terms.csv`).
- `eval/`: answer key (`seeded_errors.csv`, `edge_cases.csv`). Scoring only.
- `scripts/`: data generator and sanity checks. These are not agent code.

`data/` and `eval/` are generated output. `scripts/generate_data.py` rewrites
them deterministically (fixed seed), so a rerun reproduces identical files. The
business rules for clean rows are documented at the top of that script.

## Commands

```
.venv\Scripts\python scripts\generate_data.py   # regenerate data/ and eval/
.venv\Scripts\python scripts\check_data.py      # verify the generated data
```
