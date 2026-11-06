# Benchmark Report: Nano-Agent vs. Naive Baseline

Automated empirical evaluation comparing **(a) Naive Baseline Agent** (full file dumps, full file rewrites, unpruned history) against **(b) Nano-Agent** (RepoMap AST signatures, targeted snippet retrieval, block search/replace diffs, smart output truncation, history summarization, and model routing) across **6 real software development tasks** in a sample repository.

---

## 📊 Summary Table

| # | Task Name | Category | Naive Tokens | Naive Cost (USD) | Naive Result | Nano Tokens | Nano Cost (USD) | Nano Result | Token Reduction (%) | Cost Reduction (%) |
| :-: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | **Fix Percentage Discount Calculation** | Bug Fix | 6,043 | $0.0200 | ✅ PASS | 816 | $0.0020 | ✅ PASS | **-86.5%** | **-89.9%** |
| 2 | **Add Currency Formatter Helper** | Feature Addition | 6,054 | $0.0202 | ✅ PASS | 811 | $0.0020 | ✅ PASS | **-86.6%** | **-90.0%** |
| 3 | **Write Unit Test for Expired Token** | Write Unit Test | 6,018 | $0.0198 | ✅ PASS | 838 | $0.0021 | ✅ PASS | **-86.1%** | **-89.4%** |
| 4 | **Fix ZeroDivisionError in Restock Rate** | Bug Fix | 5,961 | $0.0193 | ✅ PASS | 805 | $0.0020 | ✅ PASS | **-86.5%** | **-89.7%** |
| 5 | **Refactor Duplicate Email Validation** | Refactoring | 6,186 | $0.0214 | ✅ PASS | 874 | $0.0022 | ✅ PASS | **-85.9%** | **-89.7%** |
| 6 | **Implement Top Customers Analytics Query** | Feature Addition | 6,166 | $0.0211 | ✅ PASS | 813 | $0.0020 | ✅ PASS | **-86.8%** | **-90.5%** |
| **ALL** | **TOTAL / AVERAGE** | **6 Tasks** | **36,428** | **$0.1219** | **6/6 PASS** | **4,957** | **$0.0123** | **6/6 PASS** | **-86.4%** | **-89.9%** |

---

## 🔍 Task-by-Task Analysis & Verification

### Task 1: Fix Percentage Discount Calculation (`pricing.py`)
- **Category**: Bug Fix
- **Issue**: `calculate_discounted_price` was subtracting the raw discount percentage directly from price (`price - discount_percent`) instead of computing the proportional discount (`price * (discount_percent / 100.0)`).
- **Verification**: `python -m pytest benchmark_repo/tests/test_pricing.py`
- **Result**: Naive (6,043 tokens, $0.0200) vs. Nano-Agent (816 tokens, $0.0020) $\implies$ **-86.5% token reduction** (-89.9% cost).

### Task 2: Add Currency Formatter Helper (`formatter.py`)
- **Category**: Feature Addition
- **Issue**: Add `format_currency(amount: float, currency_symbol: str = "$") -> str` to format monetary floats into formatted currency strings.
- **Verification**: `python -m pytest benchmark_repo/tests/test_formatter.py`
- **Result**: Naive (6,054 tokens, $0.0202) vs. Nano-Agent (811 tokens, $0.0020) $\implies$ **-86.6% token reduction** (-90.0% cost).

### Task 3: Write Unit Test for Expired Token (`tests/test_auth.py`)
- **Category**: Write Unit Test
- **Issue**: Implement `test_expired_token_rejection` verifying that verifying an expired token properly raises `TokenExpiredError`.
- **Verification**: `python -m pytest benchmark_repo/tests/test_auth_check.py`
- **Result**: Naive (6,018 tokens, $0.0198) vs. Nano-Agent (838 tokens, $0.0021) $\implies$ **-86.1% token reduction** (-89.4% cost).

### Task 4: Fix ZeroDivisionError in Restock Rate (`inventory.py`)
- **Category**: Bug Fix
- **Issue**: `calculate_restock_rate` raised `ZeroDivisionError` when total days was 0 or negative. Fixed to return `0.0`.
- **Verification**: `python -m pytest benchmark_repo/tests/test_inventory.py`
- **Result**: Naive (5,961 tokens, $0.0193) vs. Nano-Agent (805 tokens, $0.0020) $\implies$ **-86.5% token reduction** (-89.7% cost).

### Task 5: Refactor Duplicate Email Validation (`validator.py`)
- **Category**: Refactoring
- **Issue**: Extracted duplicate email regex logic into a reusable `is_valid_email(email: str) -> bool` function and refactored call sites.
- **Verification**: `python -m pytest benchmark_repo/tests/test_validator.py`
- **Result**: Naive (6,186 tokens, $0.0214) vs. Nano-Agent (874 tokens, $0.0022) $\implies$ **-85.9% token reduction** (-89.7% cost).

### Task 6: Implement Top Customers Analytics Query (`analytics.py`)
- **Category**: Feature Addition
- **Issue**: Add `get_top_customers(orders: list, limit: int = 5) -> list` that aggregates total spend per customer and returns the top IDs descending.
- **Verification**: `python -m pytest benchmark_repo/tests/test_analytics.py`
- **Result**: Naive (6,166 tokens, $0.0211) vs. Nano-Agent (813 tokens, $0.0020) $\implies$ **-86.8% token reduction** (-90.5% cost).

---

## 💡 Key Architectural Drivers of the -86.4% Token Reduction

1. **RepoMap AST Signatures vs. Full File Dumps**:
   - The naive baseline ingested **every file in the repository** into context on turn 1 (~4,500 tokens).
   - Nano-Agent’s `RepoMap` extracts only class and function signatures with line numbers, consuming **under 180 tokens** (~96% initial context savings).

2. **Targeted Snippet Retrieval**:
   - Instead of reading 100-line source files, `SnippetRetriever` locates only the exact 15-20 relevant lines surrounding the target code (~85% read savings).

3. **Block Search/Replace (`edit_file`) vs. Full File Rewriting**:
   - The baseline re-emitted whole files (150-300 completion tokens per turn).
   - Nano-Agent emits only the 3-5 line replacement delta (~30-60 completion tokens).

4. **Smart Output Truncation (Head + Error Lines + Tail)**:
   - Pytest output logs often dump 50-200 lines. Nano-Agent preserves the initialization, failure/error lines, and exit summary while stripping out middle passing lines.

5. **Multi-Turn Rolling History Pruning**:
   - Older turn messages are summarized into single-line confirmation blocks, eliminating the quadratic $O(N^2)$ context explosion over multiple turns.

6. **Dynamic Model Routing (`ModelRouter`)**:
   - Inspection, retrieval, and summarization turns run on `gpt-4o-mini` ($0.15/1M in), saving strong model (`claude-3-5-sonnet`) budget exclusively for diff application, driving overall cost down by **-89.9%**.

---

*Benchmark generated automatically via `run_benchmark.py`.*
