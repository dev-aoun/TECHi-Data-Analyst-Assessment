
import re
import json
import pandas as pd

from pathlib import Path


# ============================================================
# 1. PROJECT PATHS
# ============================================================

DATA = Path("data")

ARTICLES_FILE = DATA / "techi_articles.csv"
CONTENT_FILE = DATA / "article_content.json"
VALIDATION_FILE = DATA / "collection_validation.csv"
REVIEW_FILE = DATA / "phase2_manual_review.csv"
METHOD_FILE = Path("method.txt")


# ============================================================
# 2. COMPANY LIST
# ============================================================

COMPANIES = [
    "OpenAI", "Google", "Microsoft", "Nvidia", "Anthropic",
    "Apple", "Meta", "Amazon", "SpaceX", "Tesla", "DeepSeek",
    "IBM", "Intel", "AMD", "Qualcomm", "Samsung", "Oracle",
    "Palantir", "Ciena", "Astera Labs", "Pax8", "NoRedInk",
    "IXL", "TikTok", "ByteDance", "xAI", "Perplexity",
    "Mistral", "Cohere", "Adobe", "Salesforce", "Cisco",
    "Huawei", "Sony", "Netflix", "Uber", "Airbnb"
]


# ============================================================
# 3. HEADLINE WORD COUNT
# ============================================================

def word_count(headline):
    """
    Count headline words consistently.
    Supports ordinary and curly apostrophes.
    """

    return len(
        re.findall(r"\b[\w’'-]+\b", str(headline))
    )


# ============================================================
# 4. COMPANY MENTION DETECTION
# ============================================================

def company_flag(headline):
    """
    Check whether a headline contains a company
    from the predefined company list.

    Case-insensitive matching with word boundaries
    helps avoid partial-word matches.
    """

    headline = str(headline)

    for company in COMPANIES:

        pattern = (
            r"(?<!\w)"
            + re.escape(company)
            + r"(?!\w)"
        )

        if re.search(pattern, headline, re.IGNORECASE):
            return True

    return False


# ============================================================
# 5. NUMBER DETECTION
# ============================================================

def number_flag(headline):
    """
    Return True if the headline contains at least
    one numeric digit.
    """

    return bool(
        re.search(r"\d", str(headline))
    )


# ============================================================
# 6. ARTICLE FORMAT CLASSIFICATION
# ============================================================

def classify_format(headline, article_text):
    """
    Assign one of five preliminary article formats:

    News
    Analysis
    Explainer
    Guide
    Review

    Classification is conservative:
    - Strong headline phrases are prioritized.
    - Article text is used for numbered instructions.
    - Unclear articles default to News.

    Automated classifications require manual review.
    """

    title = str(headline).lower()
    text = str(article_text).lower()

    # --------------------------------------------------------
    # A. GUIDE
    # --------------------------------------------------------

    guide_patterns = [
        r"\bhow to\b",
        r"\bstep-by-step\b",
        r"\bchecklist\b",
        r"\btips for\b",
        r"\bguide to\b",
        r"\bguide for\b",
        r"\bbuyer's guide\b",
        r"\bbuyer’s guide\b",
        r"\bwhat to look for\b"
    ]

    if any(
        re.search(pattern, title)
        for pattern in guide_patterns
    ):
        return "Guide"

    # --------------------------------------------------------
    # B. REVIEW
    # --------------------------------------------------------

    review_patterns = [
        r"\breview\b",
        r"\bhands-on review\b",
        r"\btested\b",
        r"\bcomparison\b",
        r"\bversus\b"
    ]

    if any(
        re.search(pattern, title)
        for pattern in review_patterns
    ):
        return "Review"

    # --------------------------------------------------------
    # C. EXPLAINER
    # --------------------------------------------------------

    explainer_patterns = [
        r"\bwhat is\b",
        r"\bwhat are\b",
        r"\bhow does\b",
        r"\bhow do\b",
        r"\bexplained\b",
        r"\bunderstanding\b",
        r"\bbreakdown\b"
    ]

    if any(
        re.search(pattern, title)
        for pattern in explainer_patterns
    ):
        return "Explainer"

    # --------------------------------------------------------
    # D. ANALYSIS
    # --------------------------------------------------------

    analysis_patterns = [
        r"\banalysis\b",
        r"\bforecast\b",
        r"\boutlook\b",
        r"\bimplications\b",
        r"\bwhat it means\b"
    ]

    if any(
        re.search(pattern, title)
        for pattern in analysis_patterns
    ):
        return "Analysis"

    # --------------------------------------------------------
    # E. ARTICLE CONTENT: NUMBERED INSTRUCTIONS
    # --------------------------------------------------------

    numbered_steps = re.findall(
        r"(?im)^\s*(?:step\s+\d+\s*[:.)-]?|\d+[.)]\s+)",
        text
    )

    if len(numbered_steps) >= 2:
        return "Guide"

    # --------------------------------------------------------
    # F. DEFAULT CATEGORY
    # --------------------------------------------------------

    return "News"


# ============================================================
# 7. CONTENT VALIDATION
# ============================================================

def load_article_content():

    if not CONTENT_FILE.exists():
        raise FileNotFoundError(
            f"Article content file not found: {CONTENT_FILE}"
        )

    with open(
        CONTENT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        articles = json.load(file)

    if not isinstance(articles, list):
        raise ValueError(
            "article_content.json must contain a JSON list."
        )

    content_by_url = {}

    for item in articles:

        if not isinstance(item, dict):
            continue

        url = item.get("url", "").strip()

        if url:
            content_by_url[url] = item

    return articles, content_by_url


# ============================================================
# 8. MAIN PROCESSING
# ============================================================

def main():

    print("=" * 65)
    print("TECHi ARTICLE DATA FINALIZATION")
    print("=" * 65)

    # --------------------------------------------------------
    # A. CHECK REQUIRED FILES
    # --------------------------------------------------------

    if not ARTICLES_FILE.exists():
        raise FileNotFoundError(
            f"Article CSV not found: {ARTICLES_FILE}"
        )

    DATA.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------------
    # B. LOAD ARTICLE DATA
    # --------------------------------------------------------

    df = pd.read_csv(
        ARTICLES_FILE,
        dtype=str,
        keep_default_na=False
    )

    required_columns = [
        "url",
        "section",
        "headline",
        "author",
        "date_shown"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required CSV columns: {missing_columns}"
        )

    print("\nARTICLE DATA LOADED")
    print("Section-level records:", len(df))
    print("Unique article URLs:", df["url"].nunique())

    # --------------------------------------------------------
    # C. LOAD EXTRACTED ARTICLE CONTENT
    # --------------------------------------------------------

    articles, content_by_url = load_article_content()

    unique_urls = df["url"].nunique()

    failed_records = [
        item
        for item in articles
        if (
            item.get("error")
            or not str(item.get("article_text", "")).strip()
        )
    ]

    available_urls = [
        url
        for url in df["url"].unique()
        if (
            url in content_by_url
            and str(
                content_by_url[url].get("article_text", "")
            ).strip()
        )
    ]

    missing_content_urls = [
        url
        for url in df["url"].unique()
        if url not in available_urls
    ]

    print("\nARTICLE CONTENT STATUS")
    print("Content records:", len(articles))
    print("Unique content URLs:", len(content_by_url))
    print("Available article pages:", len(available_urls))
    print("Failed or empty records:", len(failed_records))
    print("Missing article URLs:", len(missing_content_urls))

    # Do not silently classify articles without their content.
    if missing_content_urls:
        raise ValueError(
            "Some article pages have missing or empty content. "
            "Please investigate article_content.json before "
            "finalizing the dataset."
        )

    # --------------------------------------------------------
    # D. RECALCULATE HEADLINE FIELDS
    # --------------------------------------------------------

    print("\nRECALCULATING HEADLINE FIELDS...")

    df["headline_word_count"] = (
        df["headline"].apply(word_count)
    )

    df["names_a_company"] = (
        df["headline"].apply(company_flag)
    )

    df["contains_a_number"] = (
        df["headline"].apply(number_flag)
    )

    # --------------------------------------------------------
    # E. CLASSIFY ARTICLE FORMATS
    # --------------------------------------------------------

    print("CLASSIFYING ARTICLE FORMATS...")

    formats = []

    for _, row in df.iterrows():

        article = content_by_url.get(
            row["url"],
            {}
        )

        article_text = article.get(
            "article_text",
            ""
        )

        article_format = classify_format(
            row["headline"],
            article_text
        )

        formats.append(article_format)

    df["format"] = formats

    # --------------------------------------------------------
    # F. FINAL COLUMN ORDER
    # --------------------------------------------------------

    final_columns = [
        "url",
        "section",
        "headline",
        "author",
        "date_shown",
        "headline_word_count",
        "format",
        "names_a_company",
        "contains_a_number"
    ]

    df = df[final_columns]

    # --------------------------------------------------------
    # G. CREATE MANUAL REVIEW FILE
    # --------------------------------------------------------

    review = df.copy()

    review["article_text_available"] = review["url"].apply(
        lambda url: bool(
            str(
                content_by_url.get(
                    url,
                    {}
                ).get("article_text", "")
            ).strip()
        )
    )

    review["review_required"] = True

    review["review_note"] = (
        "Automated preliminary classification; "
        "check against the article content."
    )

    review.to_csv(
        REVIEW_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    # --------------------------------------------------------
    # H. SAVE FINAL ARTICLE CSV
    # --------------------------------------------------------

    df.to_csv(
        ARTICLES_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    # --------------------------------------------------------
    # I. VALIDATION CHECKS
    # --------------------------------------------------------

    checks = [

        (
            "120 section-level records",
            len(df) == 120
        ),

        (
            "Six sections",
            df["section"].nunique() == 6
        ),

        (
            "20 records per section",
            bool(
                (df.groupby("section").size() == 20).all()
            )
        ),

        (
            "111 unique article URLs",
            df["url"].nunique() == 111
        ),

        (
            "No duplicate URL within a section",
            not df.duplicated(
                ["url", "section"]
            ).any()
        ),

        (
            "No missing required values",
            not df[
                [
                    "url",
                    "section",
                    "headline",
                    "author",
                    "date_shown"
                ]
            ].eq("").any().any()
        ),

        (
            "Positive headline word counts",
            bool(
                (df["headline_word_count"] > 0).all()
            )
        ),

        (
            "All formats assigned correctly",
            bool(
                df["format"].isin(
                    [
                        "News",
                        "Analysis",
                        "Explainer",
                        "Guide",
                        "Review"
                    ]
                ).all()
            )
        ),

        (
            "Content available for all unique URLs",
            len(available_urls) == unique_urls
        ),

        (
            "No missing article content",
            len(missing_content_urls) == 0
        )

    ]

    validation = pd.DataFrame(
        [
            {
                "check": name,
                "result": (
                    "PASS" if passed else "FAIL"
                )
            }
            for name, passed in checks
        ]
    )

    validation.to_csv(
        VALIDATION_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    # --------------------------------------------------------
    # J. WRITE METHODOLOGY
    # --------------------------------------------------------

    method = """TECHi Article Collection and Preparation Method
Collection date: 16 November 2026

1. Article Collection

Article listings were collected from six public TECHi categories: AI, Markets, Crypto, Breakthroughs, Policy and Guides. Python 3.11, Requests and BeautifulSoup were used to retrieve and parse the category pages.

Article cards were selected using the article.techi-article-card CSS selector. Headlines were extracted from h2.techi-archive-title, authors from links beginning with /@, dates from the time element, and URLs from article links. Relative URLs were converted to absolute URLs.

The first 20 valid article cards in each category were retained in displayed order, producing 120 section-level records.

2. Article Content Extraction

A separate script visited each unique article URL and extracted the page title, lead, headings and paragraphs. Non-editorial elements such as scripts, navigation, headers, footers and sidebars were removed before paragraph extraction.

The extracted content was saved in data/article_content.json. Requests were made sequentially with a two-second delay. Failed or empty extractions were recorded for review.

3. Data Preparation and Classification

The finalization script recalculated headline word counts using a regular-expression word-token method.

contains_a_number is TRUE when a headline contains at least one digit. names_a_company uses case-insensitive matching against a predefined list of 37 company names. Organizations absent from this list may be missed.

Article formats are assigned to five working categories: News, Analysis, Explainer, Guide and Review. Classification uses headline keyword patterns, with numbered instructional steps in article text as additional evidence. These automated labels are preliminary and require manual review.

4. Duplicate Handling and Validation

Content extraction uses one copy of each unique article URL. The final article dataset retains separate records when an article appears in different categories.

The expected dataset contains 120 section-level records and 111 unique article URLs. Nine URLs appear in more than one category. These records are retained because category membership is meaningful. Duplicate URL-section combinations are not allowed.

Validation checks cover record counts, category coverage, duplicate pairs, required fields, headline word counts, format labels and article-content availability.

5. Data Limitations

The article dataset represents public TECHi listings at the collection date and may change as the website is updated. Automated company and format classifications may contain errors.

The monthly traffic table is a separate assessment-provided dataset. It was not collected by the article scraper and was analyzed independently.
"""

    METHOD_FILE.write_text(
        method,
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # K. DISPLAY RESULTS
    # --------------------------------------------------------

    print("\n" + "=" * 65)
    print("FINAL VALIDATION RESULTS")
    print("=" * 65)

    print(
        validation.to_string(index=False)
    )

    passed = (
        validation["result"] == "PASS"
    ).sum()

    failed = (
        validation["result"] == "FAIL"
    ).sum()

    print("\nVALIDATION SUMMARY")
    print("Passed:", passed)
    print("Failed:", failed)

    print("\nFORMAT COUNTS")
    print(
        df["format"].value_counts().to_string()
    )

    print("\nCOMPANY FLAGS")
    print(
        df["names_a_company"].value_counts().to_string()
    )

    print("\nNUMBER FLAGS")
    print(
        df["contains_a_number"].value_counts().to_string()
    )

    print("\nSECTION COUNTS")
    print(
        df["section"].value_counts().to_string()
    )

    print("\nFILES CREATED / UPDATED")
    print(ARTICLES_FILE)
    print(REVIEW_FILE)
    print(VALIDATION_FILE)
    print(METHOD_FILE)

    print("\n" + "=" * 65)

    if failed == 0:
        print("SUCCESS: ALL VALIDATION CHECKS PASSED")
    else:
        print("WARNING: SOME VALIDATION CHECKS FAILED")

    print("=" * 65)


# ============================================================
# 9. RUN SCRIPT
# ============================================================

if __name__ == "__main__":
    main()
