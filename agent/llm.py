"""LLM layer: plain-English explanations of findings.

The model only explains. It never changes amounts or finding_type; dollar amounts
in its text are checked against the evidence and mismatches are flagged.
"""

import hashlib
import json
import re
from decimal import Decimal, InvalidOperation

import anthropic

from . import config
from .evidence import allowed_amounts, build_evidence
from .findings import FINDING_TYPES

PROMPT_VERSION = 1
CONFIDENCE = {"high", "medium", "low"}
SUGGESTABLE = [t for t in FINDING_TYPES if t != "unclassified"] + ["other"]

SYSTEM = f"""You are the explanation writer inside {config.APP_NAME}, a tool that checks a restaurant's \
marketplace payouts against its point-of-sale records. A deterministic program has already found a \
discrepancy and computed every number. Your job is only to explain it.

Rules:
- Write for a restaurant finance manager: plain English, no jargon, 2 to 3 sentences.
- Use only dollar amounts that appear in the evidence. Never compute new amounts, totals, or percentages of money.
- Do not change or dispute the finding's amounts or its finding_type.
- Respond with a single JSON object and nothing else."""


def _user_prompt(rules_md, evidence):
    unclassified = evidence["finding"]["finding_type"] == "unclassified"
    schema = ('{"explanation": "<2-3 sentences>", "confidence": "high|medium|low"'
              + (', "suggested_type": {"type": "<one of: ' + ", ".join(SUGGESTABLE)
                 + '>", "reasoning": "<1-2 sentences>"}' if unclassified else "")
              + "}")
    extra = ("This finding is unclassified: the program could not match it to a known pattern. "
             "Include suggested_type with your best reading of what happened.\n\n" if unclassified else "")
    return (f"CONTRACT RULES\n{rules_md}\n\nEVIDENCE (JSON)\n{json.dumps(evidence, indent=2)}\n\n"
            f"{extra}Return JSON in exactly this shape: {schema}")


def _parse(text, unclassified):
    """Return a validated result dict, or raise ValueError."""
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < start:
        raise ValueError("no JSON object in response")
    data = json.loads(text[start:end + 1])
    expl = data.get("explanation")
    if not isinstance(expl, str) or not expl.strip():
        raise ValueError("missing explanation")
    conf = str(data.get("confidence", "")).lower()
    if conf not in CONFIDENCE:
        raise ValueError(f"bad confidence: {data.get('confidence')!r}")
    result = {"explanation": expl.strip(), "confidence": conf}
    if unclassified:
        st = data.get("suggested_type")
        if not (isinstance(st, dict) and isinstance(st.get("type"), str)
                and isinstance(st.get("reasoning"), str) and st["reasoning"].strip()):
            raise ValueError("unclassified finding needs suggested_type {type, reasoning}")
        result["suggested_type"] = {"type": st["type"], "reasoning": st["reasoning"].strip()}
    return result  # suggested_type from the model is dropped for classified findings


AMOUNT_RE = re.compile(r"\$\s?(\d[\d,]*(?:\.\d+)?)")


def check_amounts(explanation, evidence):
    """Compare $ amounts in the explanation with the evidence. Returns (status, bad_amounts)."""
    found = AMOUNT_RE.findall(explanation)
    if not found:
        return "no_amounts", []
    allowed = allowed_amounts(evidence)
    bad = []
    for raw in found:
        try:
            val = Decimal(raw.replace(",", "").rstrip("."))
        except InvalidOperation:
            bad.append(raw)
            continue
        if val not in allowed:
            bad.append(raw)
    return ("mismatch" if bad else "ok"), bad


def _cache_key(evidence, model, rules_md):
    blob = json.dumps({"evidence": evidence, "model": model, "v": PROMPT_VERSION,
                       "rules": hashlib.sha256(rules_md.encode()).hexdigest()}, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()


def _load_cache():
    try:
        return json.loads(config.LLM_CACHE_JSON.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_cache(cache):
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    config.LLM_CACHE_JSON.write_text(json.dumps(cache, indent=1, sort_keys=True), encoding="utf-8")


def _ask(client, model, rules_md, evidence):
    unclassified = evidence["finding"]["finding_type"] == "unclassified"
    last_err = None
    for _ in range(2):  # one retry on malformed output
        resp = client.messages.create(
            model=model, max_tokens=2000, system=SYSTEM,
            output_config={"effort": "low"},
            messages=[{"role": "user", "content": _user_prompt(rules_md, evidence)}],
        )
        if resp.stop_reason == "refusal":
            raise ValueError("model declined to answer")
        text = "".join(b.text for b in resp.content if b.type == "text")
        try:
            return _parse(text, unclassified)
        except (ValueError, json.JSONDecodeError) as e:
            last_err = e
    raise ValueError(f"invalid JSON from model: {last_err}")


def explain_findings(findings, orders, payouts, terms, log=print):
    """Return {finding_id: {...result, explanation_check, bad_amounts, error}} and usage stats."""
    rules_md = config.CONTRACT_RULES_MD.read_text(encoding="utf-8")
    orders_by_ext = {o.external_order_id: o for o in orders}
    payouts_by_ext = {}
    for p in payouts:
        payouts_by_ext.setdefault(p.external_order_id, []).append(p)

    model = config.ANTHROPIC_MODEL
    cache = _load_cache()
    client = anthropic.Anthropic()
    results, stats = {}, {"cached": 0, "called": 0, "errors": 0}

    for i, f in enumerate(findings, start=1):
        evidence = build_evidence(f, orders_by_ext, payouts_by_ext, terms)
        key = _cache_key(evidence, model, rules_md)
        entry = {"evidence": evidence}
        if key in cache:
            entry.update(cache[key])
            stats["cached"] += 1
        else:
            try:
                res = _ask(client, model, rules_md, evidence)
            except anthropic.AuthenticationError:
                raise SystemExit("Anthropic authentication failed. Set ANTHROPIC_API_KEY in .env "
                                 "or your environment, or run with --no-llm.")
            except (anthropic.APIError, ValueError) as e:
                stats["errors"] += 1
                entry["error"] = f"{type(e).__name__}: {e}"
                log(f"  [{i}/{len(findings)}] {f.finding_id} failed: {entry['error']}")
                results[f.finding_id] = entry
                continue
            cache[key] = res
            _save_cache(cache)
            entry.update(res)
            stats["called"] += 1
            log(f"  [{i}/{len(findings)}] {f.finding_id} explained")
        status, bad = check_amounts(entry["explanation"], evidence)
        entry["explanation_check"], entry["bad_amounts"] = status, bad
        results[f.finding_id] = entry
    return results, stats
