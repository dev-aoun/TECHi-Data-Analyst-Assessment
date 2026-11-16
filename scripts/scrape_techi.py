
import re
import time
import requests
import pandas as pd

from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "https://www.techi.com"

OUTPUT_FILE = Path("data/techi_articles.csv")
VALIDATION_FILE = Path("data/collection_validation.csv")

TARGET_PER_SECTION = 20

CATEGORIES = {
    "AI": "/category/ai-intelligence/",
    "Markets": "/category/markets-equities/",
    "Crypto": "/category/crypto-defi/",
    "Breakthroughs": "/category/tech-breakthroughs/",
    "Policy": "/category/policy-impact/",
    "Guides": "/category/research-tools-guides/"
}

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
# HTTP SESSION WITH RETRIES
# ============================================================

session = requests.Session()

retry_strategy = Retry(
    total=4,
    connect=4,
    read=4,
    backoff_factor=2,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"]
)

adapter = HTTPAdapter(max_retries=retry_strategy)

session.mount("https://", adapter)
session.mount("http://", adapter)

session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    )
})


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def count_words(headline):
    return len(re.findall(r"\b[\w’'-]+\b", headline))


def detect_number(headline):
    return bool(re.search(r"\d", headline))


def detect_company(headline):
    for company in COMPANIES:
        pattern = r"(?<!\w)" + re.escape(company) + r"(?!\w)"

        if re.search(pattern, headline, re.IGNORECASE):
            return True

    return False


def classify_format(headline):
    """
    Preliminary headline-based classification.
    Review against article content before final submission.
    """

    title = headline.lower()

    if any(x in title for x in [
        "how to", "guide", "tips", "checklist",
        "what to look for", "step-by-step"
    ]):
        return "Guide"

    if any(x in title for x in [
        "review", "tested", "comparison", "versus"
    ]):
        return "Review"

    if any(x in title for x in [
        "what is", "how does", "explained",
        "understanding", "breakdown"
    ]):
        return "Explainer"

    if any(x in title for x in [
        "analysis", "outlook", "forecast",
        "implications", "what it means"
    ]):
        return "Analysis"

    return "News"


def get_text(element):
    if element is None:
        return ""

    return element.get_text(" ", strip=True)


# ============================================================
# SCRAPE ONE CATEGORY
# ============================================================

def scrape_category(section, category_path):

    category_url = urljoin(BASE_URL, category_path)

    print("\n" + "=" * 60)
    print("SECTION:", section)
    print("URL:", category_url)

    response = session.get(category_url, timeout=60)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")

    cards = soup.select("article.techi-article-card")

    print("Article cards found:", len(cards))

    records = []

    # IMPORTANT:
    # Deduplicate only inside this section.
    # Do NOT remove URLs appearing in another category.
    seen_in_section = set()

    for card in cards:

        link = card.select_one(
            'a[href*="/"]'
        )

        headline_element = card.select_one(
            "h2.techi-archive-title"
        )

        author_element = card.select_one(
            'a[href^="/@"]'
        )

        date_element = card.select_one("time")

        headline = get_text(headline_element)

        if not headline:
            continue

        href = None

        # Prefer the link containing the article headline.
        if headline_element:
            headline_link = headline_element.find_parent("a")

            if headline_link:
                href = headline_link.get("href")

        # Fallback to another link in the card.
        if not href and link:
            href = link.get("href")

        if not href:
            continue

        article_url = urljoin(BASE_URL, href)

        # Ignore repeated cards in the same section only.
        if article_url in seen_in_section:
            continue

        seen_in_section.add(article_url)

        author = get_text(author_element)
        date_shown = get_text(date_element)

        record = {
            "url": article_url,
            "section": section,
            "headline": headline,
            "author": author,
            "date_shown": date_shown,
            "headline_word_count": count_words(headline),
            "format": classify_format(headline),
            "names_a_company": detect_company(headline),
            "contains_a_number": detect_number(headline)
        }

        records.append(record)

        if len(records) == TARGET_PER_SECTION:
            break

    print("Unique records extracted:", len(records))

    if len(records) != TARGET_PER_SECTION:
        print(
            f"WARNING: {section} has {len(records)} records; "
            f"expected {TARGET_PER_SECTION}."
        )

    return records


# ============================================================
# MAIN SCRAPING PROCESS
# ============================================================

def main():

    all_records = []

    for section, category_path in CATEGORIES.items():

        try:
            section_records = scrape_category(
                section,
                category_path
            )

            all_records.extend(section_records)

        except requests.RequestException as error:

            print("\nERROR collecting", section)
            print(error)

        except Exception as error:

            print("\nUNEXPECTED ERROR:", section)
            print(error)

        # Respect the site's request limit.
        time.sleep(2)

    # ========================================================
    # CREATE DATAFRAME
    # ========================================================

    columns = [
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

    df = pd.DataFrame(all_records, columns=columns)

    # CRITICAL:
    # Do not use df.drop_duplicates(subset="url") here.
    # Cross-category repeats are valid records.

    # Remove duplicates only within the same section.
    df = df.drop_duplicates(
        subset=["url", "section"],
        keep="first"
    )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    # ========================================================
    # VALIDATION
    # ========================================================

    print("\n" + "=" * 60)
    print("FINAL DATASET VALIDATION")
    print("=" * 60)

    print("\nTOTAL ROWS:", len(df))

    print("\nSECTION COUNTS:")
    print(df["section"].value_counts().sort_index())

    print("\nUNIQUE ARTICLE URLS:", df["url"].nunique())

    print("\nCROSS-SECTION DUPLICATE URLS:",
          df[df.duplicated("url", keep=False)]["url"].nunique())

    print("\nMISSING VALUES:")
    print(df.isna().sum())

    checks = [
        ("Expected 120 rows", len(df) == 120),
        ("All six sections present", df["section"].nunique() == 6),
        (
            "20 records per section",
            bool((df.groupby("section").size() == 20).all())
        ),
        (
            "No duplicate URLs within a section",
            not df.duplicated(["url", "section"]).any()
        ),
        (
            "No missing required values",
            not df[
                ["url", "section", "headline", "author", "date_shown"]
            ].eq("").any().any()
            and not df[
                ["url", "section", "headline", "author", "date_shown"]
            ].isna().any().any()
        ),
        (
            "Positive headline word counts",
            bool((df["headline_word_count"] > 0).all())
        )
    ]

    validation = pd.DataFrame(
        [
            {
                "check": name,
                "result": "PASS" if passed else "FAIL"
            }
            for name, passed in checks
        ]
    )

    validation.to_csv(
        VALIDATION_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nVALIDATION CHECKS:")
    for name, passed in checks:
        print(
            ("PASS" if passed else "FAIL") + " - " + name
        )

    print("\nFILES CREATED:")
    print(OUTPUT_FILE)
    print(VALIDATION_FILE)

    if all(passed for _, passed in checks):
        print("\nSUCCESS: ARTICLE COLLECTION VALIDATED.")
    else:
        print("\nWARNING: COLLECTION NEEDS ATTENTION.")


if __name__ == "__main__":
    main()
