
from pathlib import Path
import pandas as pd
import re

ROOT = Path(__file__).resolve().parents[1]

# ------------------------------------------------------------
# REQUIRED PROJECT FILES
# ------------------------------------------------------------

required_files = {
    "Scraped article dataset": "data/techi_articles.csv",
    "Traffic dataset": "data/traffic_table.csv",
    "Collection validation": "data/collection_validation.csv",
    "Article content data": "data/article_content.json",
    "Methodology": "method.txt",
    "Traffic Excel workbook": "outputs/techi_traffic_analysis.xlsx",
    "Traffic analysis summary": "outputs/phase3_analysis_summary.txt",
    "Monthly traffic analysis": "analysis/monthly_traffic_analysis.csv",
    "Section traffic analysis": "analysis/section_traffic_analysis.csv",
    "Guides analysis": "analysis/guides_analysis.csv",
    "Crypto analysis": "analysis/crypto_analysis.csv",
    "Newsletter analysis": "analysis/newsletter_analysis.csv",
    "Article section summary": "analysis/article_section_summary.csv",
    "Phase 4 memo": "deliverables/techi_traffic_memo.md",
    "Article findings": "deliverables/article_findings.csv",
    "Phase 4 checklist": "deliverables/phase4_evidence_checklist.txt",
    "Monthly traffic chart": "charts/monthly_total_sessions.png",
    "Section traffic chart": "charts/section_traffic_trends.png",
}

optional_files = {
    "README": "README.md",
    "Requirements": "requirements.txt",
    "Scraper script": "scripts/scrape_techi.py",
    "Content extraction script": "scripts/prepare_article_content.py",
    "Phase 2 finalization script": "scripts/finalize_phase2.py",
    "Phase 3 analysis script": "scripts/phase3_traffic_analysis.py",
    "Phase 4 memo script": "scripts/phase4_final_memo.py",
    "Phase 5 audit script": "scripts/phase5_final_audit.py",
}

results = []


def record(name, status, detail):
    results.append({
        "item": name,
        "status": status,
        "detail": detail
    })


print("\n" + "=" * 70)
print("PHASE 5: FINAL PROJECT AUDIT")
print("=" * 70)

# ------------------------------------------------------------
# 1. CHECK REQUIRED FILES
# ------------------------------------------------------------

print("\n1. REQUIRED FILES")

for name, relative_path in required_files.items():
    path = ROOT / relative_path

    if path.is_file() and path.stat().st_size > 0:
        record(name, "PASS", f"Found ({path.stat().st_size:,} bytes)")
        print(f"[PASS] {name}")
    else:
        record(name, "FAIL", f"Missing or empty: {relative_path}")
        print(f"[FAIL] {name}: {relative_path}")

# ------------------------------------------------------------
# 2. CHECK OPTIONAL EVIDENCE
# ------------------------------------------------------------

print("\n2. OPTIONAL / SUPPORTING EVIDENCE")

for name, relative_path in optional_files.items():
    path = ROOT / relative_path

    if path.exists():
        if path.is_dir():
            count = sum(1 for item in path.rglob("*") if item.is_file())
            detail = f"Directory exists; {count} files"
        else:
            detail = f"Found ({path.stat().st_size:,} bytes)"

        record(name, "PASS", detail)
        print(f"[PASS] {name}: {detail}")
    else:
        record(name, "CHECK", f"Not found: {relative_path}")
        print(f"[CHECK] {name}: not found")

# ------------------------------------------------------------
# 3. VALIDATE ARTICLE DATASET
# ------------------------------------------------------------

print("\n3. ARTICLE DATASET VALIDATION")

article_file = ROOT / "data/techi_articles.csv"

if article_file.exists():
    articles = pd.read_csv(article_file)

    required_columns = [
        "url", "section", "headline", "author", "date_shown",
        "headline_word_count", "format",
        "names_a_company", "contains_a_number"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in articles.columns
    ]

    if not missing_columns:
        record(
            "Article required columns",
            "PASS",
            "All nine required columns exist"
        )
        print("[PASS] All nine required columns exist")
    else:
        record(
            "Article required columns",
            "FAIL",
            f"Missing: {missing_columns}"
        )
        print(f"[FAIL] Missing columns: {missing_columns}")

    expected_sections = {
        "AI", "Markets", "Crypto",
        "Breakthroughs", "Policy", "Guides"
    }

    actual_sections = set(articles["section"].dropna().unique())

    if actual_sections == expected_sections:
        record("Six article sections", "PASS", "All six sections found")
        print("[PASS] All six sections found")
    else:
        record(
            "Six article sections",
            "FAIL",
            f"Found: {sorted(actual_sections)}"
        )
        print(f"[FAIL] Unexpected sections: {sorted(actual_sections)}")

    counts = articles.groupby("section").size()

    if len(counts) == 6 and (counts == 20).all():
        record("Twenty records per section", "PASS", "20 per section")
        print("[PASS] Exactly 20 records per section")
    else:
        record(
            "Twenty records per section",
            "FAIL",
            counts.to_dict().__str__()
        )
        print("[FAIL] Unexpected section counts")
        print(counts)

    duplicate_pairs = articles.duplicated(
        subset=["url", "section"]
    ).sum()

    if duplicate_pairs == 0:
        record(
            "Duplicate URL-section pairs",
            "PASS",
            "No duplicate pairs"
        )
        print("[PASS] No duplicate URL-section pairs")
    else:
        record(
            "Duplicate URL-section pairs",
            "FAIL",
            f"{duplicate_pairs} duplicates"
        )
        print(f"[FAIL] {duplicate_pairs} duplicate pairs")

    missing_values = articles[required_columns].isna().sum().sum()

    if missing_values == 0:
        record("Article missing values", "PASS", "No missing required values")
        print("[PASS] No missing required values")
    else:
        record(
            "Article missing values",
            "FAIL",
            f"{missing_values} missing cells"
        )
        print(f"[FAIL] Missing required cells: {missing_values}")

    unique_urls = articles["url"].nunique()

    print(f"Article records: {len(articles)}")
    print(f"Unique URLs: {unique_urls}")
    print(f"Cross-section repeated URLs: {len(articles) - unique_urls}")

# ------------------------------------------------------------
# 4. VALIDATE TRAFFIC DATASET
# ------------------------------------------------------------

print("\n4. TRAFFIC DATA VALIDATION")

traffic_file = ROOT / "data/traffic_table.csv"

if traffic_file.exists():
    traffic = pd.read_csv(traffic_file)

    traffic_columns = [
        "month", "AI", "Markets", "Crypto",
        "Breakthroughs", "Policy", "Guides",
        "newsletter_signups"
    ]

    missing_columns = [
        col for col in traffic_columns
        if col not in traffic.columns
    ]

    if not missing_columns:
        record("Traffic required columns", "PASS", "All eight columns exist")
        print("[PASS] All eight required columns exist")
    else:
        record(
            "Traffic required columns",
            "FAIL",
            f"Missing: {missing_columns}"
        )
        print(f"[FAIL] Missing columns: {missing_columns}")

    if not missing_columns:
        traffic["month"] = pd.to_datetime(
            traffic["month"], errors="coerce"
        )

        duplicate_months = traffic["month"].duplicated().sum()
        missing_cells = traffic[traffic_columns].isna().sum().sum()

        if len(traffic) == 12 and duplicate_months == 0:
            record(
                "Traffic monthly coverage",
                "PASS",
                "12 unique monthly records"
            )
            print("[PASS] 12 unique monthly records")
        else:
            record(
                "Traffic monthly coverage",
                "FAIL",
                f"Rows={len(traffic)}, duplicate months={duplicate_months}"
            )
            print("[FAIL] Monthly coverage issue")

        if missing_cells == 0:
            record("Traffic missing values", "PASS", "No missing values")
            print("[PASS] No missing traffic values")
        else:
            record(
                "Traffic missing values",
                "FAIL",
                f"{missing_cells} missing cells"
            )
            print(f"[FAIL] Missing traffic cells: {missing_cells}")

# ------------------------------------------------------------
# 5. CHECK MEMO
# ------------------------------------------------------------

print("\n5. MEMO VALIDATION")

memo_file = ROOT / "deliverables/techi_traffic_memo.md"

if memo_file.exists():
    memo = memo_file.read_text(encoding="utf-8")

    words = re.findall(r"\b[\w'-]+\b", memo)
    word_total = len(words)

    if word_total <= 700:
        record("Memo word limit", "PASS", f"{word_total} words")
        print(f"[PASS] Memo word count: {word_total}")
    else:
        record("Memo word limit", "FAIL", f"{word_total} words")
        print(f"[FAIL] Memo exceeds limit: {word_total}")

    required_phrases = [
        "30% YoY",
        "Guides",
        "I would change my mind if",
        "Next number"
    ]

    memo_lower = memo.lower()

    for phrase in required_phrases:
        if phrase.lower() in memo_lower:
            record(
                f"Memo includes: {phrase}",
                "PASS",
                "Phrase found"
            )
            print(f"[PASS] Memo includes: {phrase}")
        else:
            record(
                f"Memo includes: {phrase}",
                "FAIL",
                "Phrase not found"
            )
            print(f"[FAIL] Missing memo phrase: {phrase}")

# ------------------------------------------------------------
# 6. CHECK README
# ------------------------------------------------------------

print("\n6. README CHECK")

readme_file = ROOT / "README.md"

if readme_file.exists():
    readme = readme_file.read_text(
        encoding="utf-8",
        errors="replace"
    )

    if len(readme.strip()) > 100:
        record("README content", "PASS", "README has content")
        print("[PASS] README exists and has content")
    else:
        record("README content", "CHECK", "README needs more detail")
        print("[CHECK] README is too short")
else:
    record("README content", "FAIL", "README.md not found")
    print("[FAIL] README.md not found")

# ------------------------------------------------------------
# 7. CREATE AUDIT REPORT
# ------------------------------------------------------------

report = pd.DataFrame(results)

audit_dir = ROOT / "outputs"
audit_dir.mkdir(exist_ok=True)

csv_path = audit_dir / "phase5_audit_report.csv"
txt_path = audit_dir / "phase5_audit_report.txt"

report.to_csv(csv_path, index=False)

passed = int((report["status"] == "PASS").sum())
failed = int((report["status"] == "FAIL").sum())
check_items = int((report["status"] == "CHECK").sum())

lines = [
    "TECHI DATA ANALYST ASSESSMENT",
    "PHASE 5 FINAL AUDIT REPORT",
    "=" * 60,
    "",
    f"Passed checks: {passed}",
    f"Failed checks: {failed}",
    f"Manual checks required: {check_items}",
    "",
    report.to_string(index=False),
    "",
    "IMPORTANT:",
    "A PASS means a file or structural check succeeded.",
    "It does not mean all manual content reviews are complete.",
    "Review the CHECK items before final submission."
]

txt_path.write_text("\n".join(lines), encoding="utf-8")

print("\n" + "=" * 70)
print("PHASE 5 AUDIT SUMMARY")
print("=" * 70)

print(f"PASS: {passed}")
print(f"FAIL: {failed}")
print(f"CHECK: {check_items}")

print("\nREPORTS CREATED:")
print(csv_path)
print(txt_path)

print("\nPHASE 5 AUDIT FINISHED.")
