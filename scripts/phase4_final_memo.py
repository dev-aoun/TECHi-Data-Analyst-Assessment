from pathlib import Path
import pandas as pd
import re

# ============================================================
# PHASE 4: FINAL FINDINGS, EVIDENCE AND ASSESSMENT MEMO
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

TRAFFIC_FILE = ROOT / "data" / "traffic_table.csv"
ARTICLES_FILE = ROOT / "data" / "techi_articles.csv"

ANALYSIS_DIR = ROOT / "analysis"
OUTPUT_DIR = ROOT / "outputs"
DELIVERABLES_DIR = ROOT / "deliverables"

for folder in [ANALYSIS_DIR, OUTPUT_DIR, DELIVERABLES_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

MEMO_FILE = DELIVERABLES_DIR / "techi_traffic_memo.md"
FINDINGS_FILE = DELIVERABLES_DIR / "article_findings.csv"
CHECKLIST_FILE = DELIVERABLES_DIR / "phase4_evidence_checklist.txt"


def require_file(path):
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")


def as_bool(series):
    """Convert common CSV true/false representations into booleans."""
    return (
        series.astype(str)
        .str.strip()
        .str.lower()
        .isin(["true", "1", "yes", "y"])
    )


def pct_change(start, end):
    if pd.isna(start) or pd.isna(end) or start == 0:
        return float("nan")
    return (end / start - 1) * 100


def fmt_pct(value):
    return "not available" if pd.isna(value) else f"{value:.2f}%"


def word_count(text):
    return len(re.findall(r"\b[\w'-]+\b", str(text)))


# ------------------------------------------------------------
# 1. LOAD AND VALIDATE TRAFFIC DATA
# ------------------------------------------------------------

require_file(TRAFFIC_FILE)
require_file(ARTICLES_FILE)

traffic = pd.read_csv(TRAFFIC_FILE)
articles = pd.read_csv(ARTICLES_FILE)

required_traffic = {
    "month", "AI", "Markets", "Crypto",
    "Breakthroughs", "Policy", "Guides",
    "newsletter_signups"
}

required_articles = {
    "url", "section", "headline", "date_shown",
    "headline_word_count", "format",
    "names_a_company", "contains_a_number"
}

missing_traffic = required_traffic - set(traffic.columns)
missing_articles = required_articles - set(articles.columns)

if missing_traffic:
    raise ValueError(f"Traffic file is missing columns: {sorted(missing_traffic)}")

if missing_articles:
    raise ValueError(f"Article file is missing columns: {sorted(missing_articles)}")

traffic["month"] = pd.to_datetime(traffic["month"], errors="coerce")

if traffic["month"].isna().any():
    raise ValueError("Some traffic month values could not be interpreted as dates.")

if traffic["month"].duplicated().any():
    raise ValueError("Duplicate months found in traffic data.")

sections = [
    "AI", "Markets", "Crypto",
    "Breakthroughs", "Policy", "Guides"
]

for col in sections + ["newsletter_signups"]:
    traffic[col] = pd.to_numeric(traffic[col], errors="coerce")

if traffic[sections + ["newsletter_signups"]].isna().any().any():
    raise ValueError("Missing or non-numeric traffic values found.")

traffic = traffic.sort_values("month").reset_index(drop=True)
traffic["total_sessions"] = traffic[sections].sum(axis=1)

# ------------------------------------------------------------
# 2. CALCULATE KEY TRAFFIC FINDINGS
# ------------------------------------------------------------

def get_month_value(month_string, column):
    selected = traffic.loc[
        traffic["month"].dt.strftime("%Y-%m") == month_string,
        column
    ]
    if selected.empty:
        raise ValueError(f"Required month {month_string} not found.")
    return float(selected.iloc[0])


jan_total = get_month_value("2026-01", "total_sessions")
feb_total = get_month_value("2026-02", "total_sessions")
mar_total = get_month_value("2026-03", "total_sessions")
aug_total = get_month_value("2026-08", "total_sessions")

february_jump = pct_change(jan_total, feb_total)
march_august_change = pct_change(mar_total, aug_total)

march_august_monthly_growth = (
    ((aug_total / mar_total) ** (1 / 5) - 1) * 100
    if mar_total > 0 else float("nan")
)

jan_aug_change = pct_change(jan_total, aug_total)

pre_feb = traffic.loc[traffic["month"] < pd.Timestamp("2026-02-01"), "total_sessions"]
post_feb = traffic.loc[traffic["month"] >= pd.Timestamp("2026-02-01"), "total_sessions"]

pre_feb_average = pre_feb.mean()
post_feb_average = post_feb.mean()

guides_mar = get_month_value("2026-03", "Guides")
guides_aug = get_month_value("2026-08", "Guides")
guides_change = pct_change(guides_mar, guides_aug)

crypto_oct = get_month_value("2025-10", "Crypto")
crypto_nov = get_month_value("2025-11", "Crypto")
crypto_spike = pct_change(crypto_oct, crypto_nov)

newsletter_start = get_month_value("2025-09", "newsletter_signups")
newsletter_end = get_month_value("2026-08", "newsletter_signups")
newsletter_field_change = pct_change(newsletter_start, newsletter_end)

# ------------------------------------------------------------
# 3. CALCULATE ARTICLE-LEVEL EVIDENCE
# ------------------------------------------------------------

articles["headline"] = articles["headline"].fillna("").astype(str)
articles["section"] = articles["section"].fillna("").astype(str)
articles["format"] = articles["format"].fillna("Unknown").astype(str)
articles["headline_word_count"] = pd.to_numeric(
    articles["headline_word_count"], errors="coerce"
)

articles["company_flag"] = as_bool(articles["names_a_company"])
articles["number_flag"] = as_bool(articles["contains_a_number"])

article_count = len(articles)
unique_urls = articles["url"].nunique()
company_count = int(articles["company_flag"].sum())
number_count = int(articles["number_flag"].sum())

company_pct = (
    company_count / article_count * 100 if article_count else float("nan")
)
number_pct = (
    number_count / article_count * 100 if article_count else float("nan")
)

format_counts = (
    articles["format"]
    .value_counts()
    .rename_axis("format")
    .reset_index(name="article_records")
)

section_counts = (
    articles.groupby("section")
    .agg(
        article_records=("url", "size"),
        unique_urls=("url", "nunique"),
        average_headline_words=("headline_word_count", "mean")
    )
    .reset_index()
)

cross_section_urls = (
    articles.groupby("url")["section"].nunique()
)
cross_section_duplicate_count = int((cross_section_urls > 1).sum())

# Select real headline examples from the dataset (3 per category to stay under 700 words).
company_examples = (
    articles.loc[articles["company_flag"]]
    .sort_values(["section", "date_shown"])
    .drop_duplicates("url")
    .head(3)
)

number_examples = (
    articles.loc[articles["number_flag"]]
    .sort_values(["section", "date_shown"])
    .drop_duplicates("url")
    .head(3)
)

# Save article evidence tables.
article_findings = pd.DataFrame([
    {
        "finding": "Headlines flagged as mentioning a company",
        "records": company_count,
        "total_article_records": article_count,
        "percentage": round(company_pct, 2)
    },
    {
        "finding": "Headlines flagged as containing a number",
        "records": number_count,
        "total_article_records": article_count,
        "percentage": round(number_pct, 2)
    },
    {
        "finding": "Unique article URLs",
        "records": unique_urls,
        "total_article_records": article_count,
        "percentage": round(unique_urls / article_count * 100, 2)
        if article_count else 0
    },
    {
        "finding": "URLs appearing in more than one section",
        "records": cross_section_duplicate_count,
        "total_article_records": article_count,
        "percentage": round(
            cross_section_duplicate_count / article_count * 100, 2
        ) if article_count else 0
    }
])

article_findings.to_csv(FINDINGS_FILE, index=False)
format_counts.to_csv(ANALYSIS_DIR / "phase4_format_counts.csv", index=False)
section_counts.to_csv(ANALYSIS_DIR / "phase4_article_section_counts.csv", index=False)

# ------------------------------------------------------------
# 4. BUILD ARTICLE EXAMPLES FOR THE MEMO
# ------------------------------------------------------------

def example_lines(frame):
    if frame.empty:
        return "- No matching article records were found."
    lines = []
    for _, row in frame.iterrows():
        lines.append(
            f'- **{row["section"]}** — "{row["headline"]}" '
            f'({row["date_shown"]})'
        )
    return "\n".join(lines)


company_example_text = example_lines(company_examples)
number_example_text = example_lines(number_examples)

format_summary = "; ".join(
    f'{row["format"]}: {int(row["article_records"])}'
    for _, row in format_counts.iterrows()
)

# ------------------------------------------------------------
# 5. CREATE THE FINAL MEMO
# ------------------------------------------------------------

memo = f"""# TECHi Traffic Assessment: Is Traffic Actually Up?

**To:** TECHi Management  
**Subject:** Traffic growth, section performance, and measurement reliability  
**Period:** September 2025–August 2026 | **Sample:** {article_count} article records

## Executive Summary

The available data does not prove TECHi traffic is up 30% year over year (YoY). The dataset spans September 2025–August 2026 without the prior-year baseline required for a direct YoY comparison. Crucially, reported sessions jumped {february_jump:.2f}% between January and February 2026—coinciding with a site-wide analytics snippet change. This step-change is consistent with a possible measurement break rather than genuine audience growth. Until the tracking implementation is independently verified, the increase cannot confidently be attributed to real audience growth.

From March to August 2026, reported sessions grew from {mar_total:,.0f} to {aug_total:,.0f}, up {march_august_change:.2f}% ({march_august_monthly_growth:.2f}% monthly compound growth). This is the clearest post-change trend, though not a verified full-year growth estimate.

## A. Is the "Up 30% YoY" Claim True?

Unverified. Reported January–August traffic rose {jan_aug_change:.2f}%, but this crosses the February tracking change, where all six sections jumped sharply ({february_jump:.2f}% overall). Pre-February sessions averaged {pre_feb_average:,.0f}/month versus {post_feb_average:,.0f}/month afterward. Because these periods span a suspected tracking break, they cannot be treated as comparable audience levels.

## B. Best Estimate of Underlying Change

The most defensible descriptive metric is the March–August gain of {march_august_change:.2f}%, showing modest growth after the February step-change. Without a tracking audit, true underlying growth remains uncertain; report the post-February trend separately rather than citing an unverified YoY figure.

Additionally, November 2025 Crypto traffic spiked {crypto_spike:.2f}% (from {crypto_oct:,.0f} to {crypto_nov:,.0f}) due to a 36-hour aggregator front-page feature—an isolated event, not recurring growth.

## C. Should Guides Be Retired?

Not immediately. Guides fell {abs(guides_change):.2f}% from March ({guides_mar:,.0f}) to August ({guides_aug:,.0f}), alongside minimal publishing since March and negligible session-based ad revenue. However, the data lacks editorial costs, newsletter attribution, and search value.

Pause major new investment, refresh high-value evergreen guides, and measure their search and newsletter contribution before deciding on permanent closure. Keeping Guides risks ongoing editorial opportunity cost; retiring it prematurely risks losing evergreen search traffic and subscriber acquisition.

## Article Dataset Findings

Among {article_count} records, {company_count} ({company_pct:.1f}%) mention a company and {number_count} ({number_pct:.1f}%) contain a number. Format labels: {format_summary} (manual verification recommended).

**Company-mention examples:**
{company_example_text}

**Number examples:**
{number_example_text}

## Newsletter and Limitations

The `newsletter_signups` field increased {newsletter_field_change:.2f}% ({newsletter_start:,.0f} to {newsletter_end:,.0f}), but its definition (monthly new vs. cumulative) is unconfirmed. Furthermore, the current article scrape cannot verify historical monthly publishing volume.

## Recommendation and Next Evidence

Audit the February 2026 analytics change against an independent source, keep the 30% YoY claim unverified until like-for-like data exists, and place Guides under a measured review period.

**I would change my mind if...** an independently validated analytics source confirmed consistent tracking across February 1, 2026 and demonstrated at least 30% genuine YoY growth on a like-for-like basis.

**Next number requested:** Monthly section-level sessions from an independently validated tracking source spanning February 2026, paired with matching prior-year months.
"""

memo_words = word_count(memo)

if memo_words > 700:
    raise ValueError(
        f"Memo is {memo_words} words, above the 700-word limit. "
        "Shorten it before submission."
    )

MEMO_FILE.write_text(memo, encoding="utf-8")

# ------------------------------------------------------------
# 6. FINAL EVIDENCE CHECKLIST
# ------------------------------------------------------------

checklist_lines = [
    "TECHI ASSESSMENT — PHASE 4 EVIDENCE CHECKLIST",
    "=" * 55,
    "",
    f"Traffic records: {len(traffic)}",
    f"Article section-level records: {article_count}",
    f"Unique article URLs: {unique_urls}",
    f"Cross-section repeated URLs: {cross_section_duplicate_count}",
    f"Memo word count: {memo_words} (maximum 700)",
    "",
    "GENERATED IN THIS PHASE:",
    f"[PASS] {MEMO_FILE.relative_to(ROOT)}",
    f"[PASS] {FINDINGS_FILE.relative_to(ROOT)}",
    "[PASS] analysis/phase4_format_counts.csv",
    "[PASS] analysis/phase4_article_section_counts.csv",
    "",
    "IMPORTANT MANUAL CHECKS BEFORE SUBMISSION:",
    "[CHECK] Manually verify automated format classifications.",
    "[CHECK] Manually verify company-mention flags against headlines.",
    "[CHECK] Confirm whether newsletter_signups means monthly new signups or cumulative subscribers.",
    "[CHECK] Audit analytics tracking around 1 February 2026.",
    "[CHECK] Confirm whether the assignment requires a prior-year comparison dataset.",
    "[CHECK] Check the final memo and all article examples for accuracy.",
    "",
    "INTERPRETATION WARNINGS:",
    "- Do not present January-August reported growth as genuine growth.",
    "- Do not claim the 30% YoY figure is proven.",
    "- March-August growth is descriptive, not a corrected full-year estimate.",
    "- Do not claim the article sample proves historical publishing volume.",
    "- Do not invent revenue or editorial cost figures for Guides."
]

CHECKLIST_FILE.write_text(
    "\n".join(checklist_lines),
    encoding="utf-8"
)

# ------------------------------------------------------------
# 7. PRINT RESULTS
# ------------------------------------------------------------

print("\n" + "=" * 65)
print("PHASE 4: FINAL FINDINGS AND MEMO")
print("=" * 65)

print("\nTRAFFIC FINDINGS")
print(f"January-February reported jump: {february_jump:.2f}%")
print(f"March-August reported change: {march_august_change:.2f}%")
print(f"March-August monthly compound growth: {march_august_monthly_growth:.2f}%")
print(f"January-August reported change: {jan_aug_change:.2f}%")
print(f"Guides March-August change: {guides_change:.2f}%")
print(f"Crypto October-November change: {crypto_spike:.2f}%")

print("\nARTICLE FINDINGS")
print(f"Article records: {article_count}")
print(f"Unique article URLs: {unique_urls}")
print(f"Company-mention flags: {company_count}/{article_count} ({company_pct:.2f}%)")
print(f"Number flags: {number_count}/{article_count} ({number_pct:.2f}%)")
print(f"Repeated URLs across sections: {cross_section_duplicate_count}")

print("\nARTICLE FORMAT COUNTS")
print(format_counts.to_string(index=False))

print("\nMEMO")
print(f"Word count: {memo_words}")
print(f"Saved: {MEMO_FILE}")

print("\nFILES CREATED")
print(FINDINGS_FILE)
print(CHECKLIST_FILE)
print(ANALYSIS_DIR / "phase4_format_counts.csv")
print(ANALYSIS_DIR / "phase4_article_section_counts.csv")

print("\nPHASE 4 COMPLETED.")
print("Review the memo and complete the manual checks before submission.")