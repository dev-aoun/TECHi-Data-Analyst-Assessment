# TECHi Data Analyst Assessment
## Is TECHi Traffic Actually Up?

## 1. Project Overview

This project investigates whether TECHi's website traffic is genuinely growing and whether the reported **30% year-over-year (YoY) increase** is supported by the available evidence.

The assessment combines two separate datasets:

- **Article dataset:** 120 article-category records collected from six public TECHi website sections.
- **Traffic dataset:** A supplied assessment dataset containing monthly sessions and newsletter figures from September 2025 to August 2026.

The project uses web scraping, data preparation, exploratory analysis, visualization, and business interpretation to evaluate traffic trends and provide recommendations.

A key objective is to distinguish genuine audience growth from possible measurement changes and temporary traffic events. The project also evaluates whether TECHi should continue investing editorial resources in its Guides section.

**Important data distinction:** Article records were collected from public TECHi pages. The traffic dataset was supplied for the assessment and is not live analytics data retrieved from TECHi.

---

## 2. Project Objectives

The main objectives were to:

1. Collect the 20 newest article records from each of six TECHi sections.
2. Prepare and validate the article dataset.
3. Analyze monthly website sessions and category-level performance.
4. Identify unusual traffic movements and possible measurement issues.
5. Investigate Crypto and Guides traffic patterns.
6. Examine newsletter signup trends.
7. Evaluate whether the available evidence supports the 30% YoY growth claim.
8. Prepare a business-focused memo with recommendations and limitations.

---

## 3. Tools and Technologies

| Tool / Library | Purpose |
|---|---|
| Python 3.11 | Main programming language |
| Requests | Retrieve public website pages |
| BeautifulSoup | Parse and extract HTML content |
| Pandas | Data cleaning and analysis |
| NumPy | Numerical calculations |
| Matplotlib | Data visualization |
| OpenPyXL | Excel workbook creation and formatting |
| VS Code | Development environment |

The analysis is reproducible through Python scripts and the Excel workbook. No Jupyter notebook or Power BI file is included in the final deliverables.

---

## 4. Project Structure

The project is organized into separate folders for data, scripts, analysis outputs, charts, and final deliverables.

```text
TECHi-Data-Analyst-Assessment/
│
├── data/
│   ├── techi_articles.csv
│   ├── traffic_table.csv
│   ├── article_content.json
│   ├── collection_validation.csv
│   ├── phase2_content_review.csv
│   └── phase2_manual_review.csv
│
├── scripts/
│   ├── scrape_techi.py
│   ├── prepare_article_content.py
│   ├── finalize_phase2.py
│   ├── audit_duplicates.py
│   ├── create_review_file.py
│   ├── phase3_traffic_analysis.py
│   ├── phase4_final_memo.py
│   └── phase5_final_audit.py
│
├── analysis/
│   ├── article_section_summary.csv
│   ├── crypto_analysis.csv
│   ├── guides_analysis.csv
│   ├── monthly_traffic_analysis.csv
│   ├── newsletter_analysis.csv
│   ├── phase4_article_section_counts.csv
│   ├── phase4_format_counts.csv
│   └── section_traffic_analysis.csv
│
├── charts/
│   ├── monthly_total_sessions.png
│   └── section_traffic_trends.png
│
├── outputs/
│   ├── techi_traffic_analysis.xlsx
│   ├── phase3_analysis_summary.txt
│   ├── phase5_audit_report.csv
│   └── phase5_audit_report.txt
│
├── deliverables/
│   ├── techi_traffic_memo.md
│   ├── article_findings.csv
│   └── phase4_evidence_checklist.txt
│
├── method.txt
├── requirements.txt
└── README.md
```

**Folder descriptions:**

- `data/` contains the article dataset, supplied traffic dataset, extracted article content, and validation/review files.
- `scripts/` contains the scraping, content extraction, finalization, traffic analysis, memo generation, and audit scripts.
- `analysis/` contains detailed analysis tables exported by the scripts.
- `charts/` contains the two final traffic visualizations.
- `outputs/` contains the Excel workbook, analysis summary, and audit reports.
- `deliverables/` contains the final business memo, article findings, and evidence checklist.
- `method.txt` documents the article collection methodology and important decisions.

Temporary debugging and test files are excluded from the documented final project structure.

---

## 5. Project Workflow

The project was completed in five phases.

### Phase 1: Traffic Data Understanding

The supplied monthly traffic dataset was inspected before analysis.

It covers September 2025 to August 2026 and includes monthly sessions for:

- AI
- Markets
- Crypto
- Breakthroughs
- Policy
- Guides
- Newsletter signups

The dataset was checked for its structure, missing values, duplicate months, and numerical consistency.

The traffic dataset was kept separate from the scraped article dataset because they have different sources and purposes.

### Phase 2: Article Collection and Data Preparation

Article records were collected from six public TECHi categories:

1. AI
2. Markets
3. Crypto
4. Breakthroughs
5. Policy
6. Guides

The scraper collected 20 article records per category, producing:

- **120 total section-level records**
- **20 records per category**
- **111 unique article URLs**
- **9 URLs repeated across categories**

Repeated URLs were retained because an article can appear in more than one category. A duplicate was defined as a repeated combination of article URL and section.

The final article dataset contains nine fields:

- `url`
- `section`
- `headline`
- `author`
- `date_shown`
- `headline_word_count`
- `format`
- `names_a_company`
- `contains_a_number`

Article content was also extracted to support content checks and classification review.

The scraper uses public pages without requiring a login. Requests were kept at a controlled rate, with approximately two seconds between category requests.

Data validation checked the expected record count, category coverage, duplicate URL-section pairs, missing values, and headline word counts.

The collection process and methodological decisions are documented in `method.txt`.

**Classification limitation:** Article format and company-mention fields are automated indicators. They should be interpreted as classification results rather than guaranteed ground truth. The review files support further inspection; their existence does not mean every record has been independently human-verified.

### Phase 3: Traffic Analysis

Python and Pandas were used to analyze monthly sessions and category performance.

The analysis examined:

- Total monthly sessions.
- Month-to-month traffic changes.
- Section-level traffic trends.
- Crypto traffic around the November 2025 event.
- Guides traffic over the available period.
- Newsletter signup figures.
- The February 2026 analytics implementation change.

Two charts were generated:

1. `monthly_total_sessions.png` — overall reported monthly sessions.
2. `section_traffic_trends.png` — reported sessions across the six sections.

Supporting CSV tables were exported to `analysis/`, and the Excel workbook was created at `outputs/techi_traffic_analysis.xlsx`.

### Phase 4: Findings and Business Recommendation

The article and traffic findings were combined in the final business memo.

The memo addresses:

- Whether the 30% YoY claim can be verified.
- The best available estimate of the underlying traffic trend.
- Whether TECHi should retire the Guides section.
- Relevant article-level findings.
- Important assumptions and limitations.
- The potential cost of making the wrong decision.
- The additional information needed to improve confidence.

The final memo is available at `deliverables/techi_traffic_memo.md`.

### Phase 5: Final Quality Audit

The final audit script checked the required project files and key data conditions.

The checks covered:

- Required article dataset columns.
- Six expected sections.
- Twenty records per section.
- Duplicate URL-section combinations.
- Missing article values.
- Traffic dataset structure and monthly records.
- Required analysis tables and charts.
- Memo word count and required discussion points.
- README and supporting evidence files.

The final audit completed with:

| Audit result | Count |
|---|---:|
| PASS | 40 |
| FAIL | 0 |
| CHECK | 0 |

The audit reports are saved at:

- `outputs/phase5_audit_report.txt`
- `outputs/phase5_audit_report.csv`

This confirms that the automated project checks passed. It does not replace manual review of analytical interpretations or article classifications.

---

## 6. Main Findings

### 1. The 30% YoY claim cannot be confirmed

The supplied traffic dataset covers only September 2025 to August 2026. It does not include a comparable previous-year baseline, so the 30% YoY claim cannot be directly verified.

### 2. A major reported traffic jump occurred in February 2026

Total reported sessions increased by approximately **47.95%** between January and February 2026.

This coincided with the site-wide analytics snippet change on 1 February 2026. The increase is consistent with a possible measurement break rather than genuine audience growth, but the tracking implementation has not been independently verified.

### 3. Traffic continued to increase after February

From March to August 2026, total reported sessions increased from **96,570 to 102,805**, a change of approximately **6.46%**.

This describes the post-change trend in the supplied data. It is not a verified year-over-year growth rate.

### 4. Crypto experienced a temporary traffic spike

Crypto sessions increased from **10,100 in October 2025 to 24,800 in November 2025**.

This is consistent with the assessment note about a crypto explainer receiving aggregator front-page exposure for approximately 36 hours. The increase should not automatically be treated as evidence of sustained growth.

### 5. Guides traffic declined considerably

Guides sessions decreased from **4,930 in March 2026 to 725 in August 2026**, a decline of approximately **85.29%**.

The assessment notes that very little content has been published in this section since March 2026. Publishing activity should therefore be considered before making a final decision about the section.

### 6. Newsletter data needs clarification

The supplied newsletter figures changed from **820 in September 2025 to 1,140 in August 2026**.

However, it is unclear whether the figures represent new monthly signups or cumulative subscribers. This distinction matters when evaluating newsletter performance.

---

## 7. Business Recommendation

The available evidence does not support treating the reported 30% YoY increase as confirmed growth in real audience traffic.

The February 2026 analytics change creates a significant limitation when comparing reported traffic levels before and after that date.

TECHi should independently verify its analytics implementation and obtain comparable tracking data before making major decisions based on the reported increase.

For Guides, the recommendation is not to retire the section immediately. Instead, TECHi should review its publishing activity, evergreen content value, search contribution, and newsletter potential before making a final decision.

This approach reduces the risk of making an irreversible editorial decision using incomplete evidence.

---

## 8. Assumptions and Limitations

The following limitations should be considered when interpreting the findings:

- The supplied traffic dataset covers only 12 months.
- A comparable previous-year traffic baseline is unavailable.
- The February 2026 analytics change may have affected reported sessions.
- The tracking implementation has not been independently verified.
- The Crypto increase may be influenced by a temporary external event.
- Guides publishing activity has been limited since March 2026.
- The newsletter field is not clearly defined as monthly or cumulative.
- Automated article format and company-mention classifications may require manual review.
- Article records represent section-level appearances, not necessarily unique articles.
- The article dataset is not a direct measure of website traffic.

These limitations are documented to avoid presenting uncertain findings as confirmed facts.

---

## 9. Reproducibility and Setup

The project was developed using Python 3.11.

### Requirements

The dependencies are listed in `requirements.txt`.

From PowerShell, navigate to the project folder:

```powershell
cd E:\TECHi-Data-Analyst-Assessment
```

Install the required packages:

```powershell
python -m pip install -r requirements.txt
```

### Run the workflow

The scripts should be run from the project root in the following order:

```powershell
python scripts/scrape_techi.py
python scripts/prepare_article_content.py
python scripts/finalize_phase2.py
python scripts/phase3_traffic_analysis.py
python scripts/phase4_final_memo.py
python scripts/phase5_final_audit.py
```

Later phases use files generated by earlier phases, so the workflow order matters.

**Important notes:**

- `data/traffic_table.csv` is the supplied assessment dataset. It is not scraped from TECHi.
- The article scraper retrieves current public website content. Running it again later may produce different article records as the website changes.
- Re-running the full workflow may overwrite generated outputs.
- The final analysis can be reviewed through the Python scripts, exported CSV tables, and Excel workbook.

---

## 10. Final Deliverables

| Deliverable | Location |
|---|---|
| Article dataset | `data/techi_articles.csv` |
| Traffic dataset | `data/traffic_table.csv` |
| Article content | `data/article_content.json` |
| Collection validation | `data/collection_validation.csv` |
| Collection methodology | `method.txt` |
| Traffic analysis workbook | `outputs/techi_traffic_analysis.xlsx` |
| Monthly traffic chart | `charts/monthly_total_sessions.png` |
| Section traffic chart | `charts/section_traffic_trends.png` |
| Final business memo | `deliverables/techi_traffic_memo.md` |
| Article findings | `deliverables/article_findings.csv` |
| Evidence checklist | `deliverables/phase4_evidence_checklist.txt` |
| Final audit reports | `outputs/phase5_audit_report.txt` and `outputs/phase5_audit_report.csv` |

---

## 11. Conclusion

This project combines public website data collection, data preparation, traffic analysis, visualization, and business decision-making.

The main conclusion is that an increase in reported website sessions does not automatically mean that the real audience has grown by the same amount. Analytics implementation changes, unusual external events, and publishing activity can all influence reported numbers.

By keeping the article and traffic sources separate, validating the datasets, documenting assumptions, and explaining limitations, this project provides a cautious and evidence-based assessment of TECHi's traffic performance and editorial decisions.