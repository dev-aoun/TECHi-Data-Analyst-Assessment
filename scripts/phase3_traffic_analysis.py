
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter


# ============================================================
# CONFIGURATION
# ============================================================

ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT / "data"
ANALYSIS_DIR = ROOT / "analysis"
CHARTS_DIR = ROOT / "charts"
OUTPUT_DIR = ROOT / "outputs"
DELIVERABLES_DIR = ROOT / "deliverables"

TRAFFIC_FILE = DATA_DIR / "traffic_table.csv"
ARTICLE_FILE = DATA_DIR / "techi_articles.csv"

SECTIONS = [
    "AI",
    "Markets",
    "Crypto",
    "Breakthroughs",
    "Policy",
    "Guides"
]

MONTH_COLUMN = "month"
NEWSLETTER_COLUMN = "newsletter_signups"

for folder in [
    ANALYSIS_DIR,
    CHARTS_DIR,
    OUTPUT_DIR,
    DELIVERABLES_DIR
]:
    folder.mkdir(parents=True, exist_ok=True)


# ============================================================
# 1. LOAD DATA
# ============================================================

print("\n" + "=" * 65)
print("PHASE 3: TECHI TRAFFIC ANALYSIS")
print("=" * 65)

if not TRAFFIC_FILE.exists():
    raise FileNotFoundError(
        f"Traffic file not found: {TRAFFIC_FILE}"
    )

traffic = pd.read_csv(TRAFFIC_FILE)

required_columns = [
    MONTH_COLUMN,
    *SECTIONS,
    NEWSLETTER_COLUMN
]

missing_columns = [
    col for col in required_columns
    if col not in traffic.columns
]

if missing_columns:
    raise ValueError(
        f"Missing traffic columns: {missing_columns}"
    )

traffic[MONTH_COLUMN] = pd.to_datetime(
    traffic[MONTH_COLUMN],
    errors="raise"
)

traffic = traffic.sort_values(
    MONTH_COLUMN
).reset_index(drop=True)

# Validate monthly data.
if traffic[MONTH_COLUMN].duplicated().any():
    raise ValueError(
        "Duplicate months found in traffic data."
    )

if len(traffic) != 12:
    raise ValueError(
        f"Expected 12 monthly records, found {len(traffic)}."
    )

for col in SECTIONS + [NEWSLETTER_COLUMN]:
    traffic[col] = pd.to_numeric(
        traffic[col],
        errors="raise"
    )

if traffic[required_columns].isna().any().any():
    raise ValueError(
        "Missing values found in traffic data."
    )

if (traffic[SECTIONS + [NEWSLETTER_COLUMN]] < 0).any().any():
    raise ValueError(
        "Negative values found in traffic data."
    )

traffic["total_sessions"] = traffic[SECTIONS].sum(axis=1)

traffic["month_label"] = traffic[MONTH_COLUMN].dt.strftime(
    "%b %Y"
)

print("\nTRAFFIC DATA")
print(traffic.to_string(index=False))

print("\nDATA QUALITY")
print("Rows:", len(traffic))
print(
    "Duplicate months:",
    traffic[MONTH_COLUMN].duplicated().sum()
)
print(
    "Missing values:",
    traffic.isna().sum().sum()
)


# ============================================================
# 2. MONTHLY TOTALS AND MONTH-OVER-MONTH GROWTH
# ============================================================

traffic["mom_change"] = (
    traffic["total_sessions"].diff()
)

traffic["mom_growth_pct"] = (
    traffic["total_sessions"].pct_change() * 100
)

print("\nMONTHLY TRAFFIC CHANGE")

print(
    traffic[
        [
            "month_label",
            "total_sessions",
            "mom_change",
            "mom_growth_pct"
        ]
    ].to_string(index=False)
)


# ============================================================
# 3. IDENTIFY FEBRUARY MEASUREMENT BREAK
# ============================================================

jan = traffic.loc[
    traffic[MONTH_COLUMN] == pd.Timestamp("2026-01-01"),
    "total_sessions"
]

feb = traffic.loc[
    traffic[MONTH_COLUMN] == pd.Timestamp("2026-02-01"),
    "total_sessions"
]

if len(jan) != 1 or len(feb) != 1:
    raise ValueError(
        "January and February 2026 must exist exactly once."
    )

jan_value = float(jan.iloc[0])
feb_value = float(feb.iloc[0])

feb_change_pct = (
    (feb_value / jan_value) - 1
) * 100

print("\nFEBRUARY 2026 MEASUREMENT BREAK")
print("January sessions:", jan_value)
print("February sessions:", feb_value)
print(
    "January-to-February change:",
    round(feb_change_pct, 2),
    "%"
)


# ============================================================
# 4. ESTIMATE UNDERLYING TRAFFIC GROWTH
# ============================================================

pre_change = traffic[
    traffic[MONTH_COLUMN] < pd.Timestamp("2026-02-01")
].copy()

post_change = traffic[
    traffic[MONTH_COLUMN] >= pd.Timestamp("2026-02-01")
].copy()

pre_mean = pre_change["total_sessions"].mean()
post_mean = post_change["total_sessions"].mean()

pre_median = pre_change["total_sessions"].median()
post_median = post_change["total_sessions"].median()

march = traffic.loc[
    traffic[MONTH_COLUMN] == pd.Timestamp("2026-03-01"),
    "total_sessions"
]

august = traffic.loc[
    traffic[MONTH_COLUMN] == pd.Timestamp("2026-08-01"),
    "total_sessions"
]

if len(march) != 1 or len(august) != 1:
    raise ValueError(
        "March and August 2026 must exist exactly once."
    )

march_value = float(march.iloc[0])
august_value = float(august.iloc[0])

# March to August contains five monthly intervals.
post_february_growth = (
    (august_value / march_value) ** (1 / 5) - 1
) * 100

march_to_august_change = (
    (august_value / march_value) - 1
) * 100

january_to_august_reported_change = (
    (august_value / jan_value) - 1
) * 100

print("\nUNDERLYING TRAFFIC ANALYSIS")

print("Pre-February average:", round(pre_mean, 2))
print("Post-February average:", round(post_mean, 2))
print("Pre-February median:", round(pre_median, 2))
print("Post-February median:", round(post_median, 2))

print(
    "March-August change:",
    round(march_to_august_change, 2),
    "%"
)

print(
    "March-August monthly compound growth:",
    round(post_february_growth, 2),
    "%"
)

print(
    "January-August reported change:",
    round(january_to_august_reported_change, 2),
    "%"
)


# ============================================================
# 5. SECTION-LEVEL ANALYSIS
# ============================================================

section_rows = []

for section in SECTIONS:

    jan_section = traffic.loc[
        traffic[MONTH_COLUMN] == pd.Timestamp("2026-01-01"),
        section
    ]

    feb_section = traffic.loc[
        traffic[MONTH_COLUMN] == pd.Timestamp("2026-02-01"),
        section
    ]

    mar_section = traffic.loc[
        traffic[MONTH_COLUMN] == pd.Timestamp("2026-03-01"),
        section
    ]

    aug_section = traffic.loc[
        traffic[MONTH_COLUMN] == pd.Timestamp("2026-08-01"),
        section
    ]

    jan_s = float(jan_section.iloc[0])
    feb_s = float(feb_section.iloc[0])
    mar_s = float(mar_section.iloc[0])
    aug_s = float(aug_section.iloc[0])

    section_rows.append({
        "section": section,
        "jan_2026": jan_s,
        "feb_2026": feb_s,
        "feb_jump_pct": (feb_s / jan_s - 1) * 100,
        "mar_2026": mar_s,
        "aug_2026": aug_s,
        "mar_aug_change_pct": (aug_s / mar_s - 1) * 100,
        "pre_change_average": pre_change[section].mean(),
        "post_change_average": post_change[section].mean()
    })

section_analysis = pd.DataFrame(section_rows)

print("\nSECTION-LEVEL ANALYSIS")
print(section_analysis.round(2).to_string(index=False))


# ============================================================
# 6. GUIDES SECTION ANALYSIS
# ============================================================

guides = traffic[
    [
        MONTH_COLUMN,
        "month_label",
        "Guides"
    ]
].copy()

guides["mom_change_pct"] = (
    guides["Guides"].pct_change() * 100
)

guides_march = float(
    guides.loc[
        guides[MONTH_COLUMN] == pd.Timestamp("2026-03-01"),
        "Guides"
    ].iloc[0]
)

guides_august = float(
    guides.loc[
        guides[MONTH_COLUMN] == pd.Timestamp("2026-08-01"),
        "Guides"
    ].iloc[0]
)

guides_change_pct = (
    (guides_august / guides_march) - 1
) * 100

guides_pre_mean = pre_change["Guides"].mean()
guides_post_mean = post_change["Guides"].mean()

print("\nGUIDES ANALYSIS")
print("March sessions:", guides_march)
print("August sessions:", guides_august)

print(
    "March-August change:",
    round(guides_change_pct, 2),
    "%"
)

print(
    "Pre-February average:",
    round(guides_pre_mean, 2)
)

print(
    "Post-February average:",
    round(guides_post_mean, 2)
)


# ============================================================
# 7. CRYPTO NOVEMBER OUTLIER
# ============================================================

crypto = traffic[
    [
        MONTH_COLUMN,
        "month_label",
        "Crypto"
    ]
].copy()

crypto_oct = float(
    crypto.loc[
        crypto[MONTH_COLUMN] == pd.Timestamp("2025-10-01"),
        "Crypto"
    ].iloc[0]
)

crypto_nov = float(
    crypto.loc[
        crypto[MONTH_COLUMN] == pd.Timestamp("2025-11-01"),
        "Crypto"
    ].iloc[0]
)

crypto_nov_change = (
    (crypto_nov / crypto_oct) - 1
) * 100

print("\nCRYPTO NOVEMBER EVENT")
print("October:", crypto_oct)
print("November:", crypto_nov)

print(
    "October-November change:",
    round(crypto_nov_change, 2),
    "%"
)


# ============================================================
# 8. NEWSLETTER ANALYSIS
# ============================================================

newsletter = traffic[
    [
        MONTH_COLUMN,
        "month_label",
        NEWSLETTER_COLUMN
    ]
].copy()

newsletter["newsletter_mom_change"] = (
    newsletter[NEWSLETTER_COLUMN].diff()
)

newsletter["newsletter_mom_pct"] = (
    newsletter[NEWSLETTER_COLUMN].pct_change() * 100
)

print("\nNEWSLETTER SIGNUP DATA")
print(newsletter.to_string(index=False))

newsletter_note = (
    "Interpret newsletter_signups only after confirming whether "
    "the field represents new monthly signups or cumulative "
    "subscriber totals. Do not calculate acquisition growth "
    "or conversion rates until the definition is confirmed."
)


# ============================================================
# 9. ARTICLE DATA LINKAGE
# ============================================================

article_summary = pd.DataFrame()

if ARTICLE_FILE.exists():

    articles = pd.read_csv(
        ARTICLE_FILE,
        dtype=str,
        keep_default_na=False
    )

    required_article_columns = [
        "url",
        "section",
        "headline_word_count"
    ]

    missing_article_columns = [
        col for col in required_article_columns
        if col not in articles.columns
    ]

    if missing_article_columns:
        raise ValueError(
            "Missing article columns: "
            f"{missing_article_columns}"
        )

    articles["headline_word_count"] = pd.to_numeric(
        articles["headline_word_count"],
        errors="coerce"
    )

    article_summary = (
        articles.groupby("section")
        .agg(
            article_records=("url", "count"),
            unique_articles=("url", "nunique"),
            average_headline_words=(
                "headline_word_count",
                "mean"
            )
        )
        .reset_index()
    )

    print("\nARTICLE COUNTS BY SECTION")
    print(article_summary.to_string(index=False))

else:
    print("\nWARNING: Article dataset not found.")


# ============================================================
# 10. CHART 1: TOTAL MONTHLY SESSIONS
# ============================================================

plt.figure(figsize=(11, 6))

plt.plot(
    traffic["month_label"],
    traffic["total_sessions"],
    marker="o",
    linewidth=2
)

# CORRECTION: February 2026 is index 5, not index 4.
plt.axvline(
    x=5,
    linestyle="--",
    label="February 2026 measurement change"
)

plt.title("TECHi Monthly Total Sessions")
plt.xlabel("Month")
plt.ylabel("Sessions")

plt.xticks(rotation=45)
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()

plt.savefig(
    CHARTS_DIR / "monthly_total_sessions.png",
    dpi=300
)

plt.close()


# ============================================================
# 11. CHART 2: SECTION TRAFFIC TRENDS
# ============================================================

plt.figure(figsize=(11, 6))

for section in SECTIONS:

    plt.plot(
        traffic["month_label"],
        traffic[section],
        marker="o",
        label=section
    )

# CORRECTION: February 2026 is index 5, not index 4.
plt.axvline(
    x=5,
    linestyle="--",
    label="February 2026 measurement change"
)

plt.title("Monthly Sessions by TECHi Section")
plt.xlabel("Month")
plt.ylabel("Sessions")

plt.xticks(rotation=45)
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()

plt.savefig(
    CHARTS_DIR / "section_traffic_trends.png",
    dpi=300
)

plt.close()


# ============================================================
# 12. EXPORT ANALYSIS TABLES
# ============================================================

traffic.to_csv(
    ANALYSIS_DIR / "monthly_traffic_analysis.csv",
    index=False
)

section_analysis.to_csv(
    ANALYSIS_DIR / "section_traffic_analysis.csv",
    index=False
)

guides.to_csv(
    ANALYSIS_DIR / "guides_analysis.csv",
    index=False
)

crypto.to_csv(
    ANALYSIS_DIR / "crypto_analysis.csv",
    index=False
)

newsletter.to_csv(
    ANALYSIS_DIR / "newsletter_analysis.csv",
    index=False
)

if not article_summary.empty:

    article_summary.to_csv(
        ANALYSIS_DIR / "article_section_summary.csv",
        index=False
    )


# ============================================================
# 13. CREATE EXCEL WORKBOOK
# ============================================================

excel_file = (
    OUTPUT_DIR / "techi_traffic_analysis.xlsx"
)

with pd.ExcelWriter(
    excel_file,
    engine="openpyxl"
) as writer:

    traffic.to_excel(
        writer,
        sheet_name="Monthly Traffic",
        index=False
    )

    section_analysis.to_excel(
        writer,
        sheet_name="Section Analysis",
        index=False
    )

    guides.to_excel(
        writer,
        sheet_name="Guides Analysis",
        index=False
    )

    crypto.to_excel(
        writer,
        sheet_name="Crypto Analysis",
        index=False
    )

    newsletter.to_excel(
        writer,
        sheet_name="Newsletter",
        index=False
    )

    if not article_summary.empty:

        article_summary.to_excel(
            writer,
            sheet_name="Article Summary",
            index=False
        )

    pd.DataFrame({
        "Metric": [
            "January-February 2026 jump",
            "March-August total change",
            "March-August monthly compound growth",
            "January-August reported change",
            "Pre-February average sessions",
            "Post-February average sessions",
            "Guides March-August change",
            "Crypto October-November change"
        ],

        "Value": [
            feb_change_pct,
            march_to_august_change,
            post_february_growth,
            january_to_august_reported_change,
            pre_mean,
            post_mean,
            guides_change_pct,
            crypto_nov_change
        ]

    }).to_excel(
        writer,
        sheet_name="Key Metrics",
        index=False
    )


# ============================================================
# 14. EXCEL FORMATTING
# ============================================================

workbook = load_workbook(excel_file)

for worksheet in workbook.worksheets:

    worksheet.freeze_panes = "A2"
    worksheet.auto_filter.ref = worksheet.dimensions

    for cell in worksheet[1]:

        cell.font = Font(
            bold=True,
            color="FFFFFF"
        )

        cell.fill = PatternFill(
            fill_type="solid",
            fgColor="1F4E78"
        )

        cell.alignment = Alignment(
            horizontal="center"
        )

    for column_cells in worksheet.columns:

        max_length = max(
            len(str(cell.value or ""))
            for cell in column_cells
        )

        column_letter = get_column_letter(
            column_cells[0].column
        )

        worksheet.column_dimensions[
            column_letter
        ].width = min(
            max_length + 3,
            35
        )

workbook.save(excel_file)


# ============================================================
# 15. SAVE ANALYSIS SUMMARY
# ============================================================

summary = f"""
TECHI TRAFFIC ANALYSIS
======================

Data period:
{traffic['month_label'].iloc[0]} to {traffic['month_label'].iloc[-1]}

Total records:
{len(traffic)}

Total sessions in first month:
{traffic['total_sessions'].iloc[0]:,.0f}

Total sessions in final month:
{traffic['total_sessions'].iloc[-1]:,.0f}

January-February 2026 reported change:
{feb_change_pct:.2f}%

March-August 2026 traffic change:
{march_to_august_change:.2f}%

March-August monthly compound growth:
{post_february_growth:.2f}%

January-August reported change:
{january_to_august_reported_change:.2f}%

Guides March-August change:
{guides_change_pct:.2f}%

Crypto October-November change:
{crypto_nov_change:.2f}%

Newsletter definition:
{newsletter_note}

IMPORTANT LIMITATIONS:
- February 2026 is a potential measurement break.
- No complete prior-year comparison is available.
- November 2025 Crypto had an exceptional aggregator event.
- Guides publication volume must be checked before retirement.
- Newsletter metric definition must be confirmed.
- These data do not establish a causal effect of publishing changes.
"""

(
    OUTPUT_DIR / "phase3_analysis_summary.txt"
).write_text(
    summary,
    encoding="utf-8"
)


# ============================================================
# 16. FINAL OUTPUT
# ============================================================

print("\n" + "=" * 65)
print("PHASE 3 ANALYSIS COMPLETED")
print("=" * 65)

print("\nKEY METRICS")

print(
    "February jump:",
    round(feb_change_pct, 2),
    "%"
)

print(
    "March-August change:",
    round(march_to_august_change, 2),
    "%"
)

print(
    "March-August monthly compound growth:",
    round(post_february_growth, 2),
    "%"
)

print(
    "January-August reported change:",
    round(january_to_august_reported_change, 2),
    "%"
)

print(
    "Guides change:",
    round(guides_change_pct, 2),
    "%"
)

print("\nFILES CREATED:")

print("Excel:", excel_file)

print(
    "Summary:",
    OUTPUT_DIR / "phase3_analysis_summary.txt"
)

print("Charts:", CHARTS_DIR)
print("Tables:", ANALYSIS_DIR)

print("\nPHASE 3 SCRIPT FINISHED.")
