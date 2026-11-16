
import pandas as pd
import requests
import time
import json
from pathlib import Path
from bs4 import BeautifulSoup

INPUT = Path("data/techi_articles.csv")
OUTPUT = Path("data/article_content.json")

df = pd.read_csv(INPUT)

# Keep one copy per article for content inspection.
articles = df.drop_duplicates(subset="url").copy()

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    )
}

session = requests.Session()
session.headers.update(headers)

results = []

for index, row in articles.iterrows():

    url = row["url"]

    print(
        f"Fetching {len(results) + 1}/{len(articles)}: {url}"
    )

    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        title = soup.select_one("h1.techi-post-hero__title")
        lead = soup.select_one("p.techi-post-lead")

        # Remove non-editorial elements.
        for element in soup.select(
            "script, style, nav, footer, header, aside"
        ):
            element.decompose()

        content = soup.select_one("article")

        if content is None:
            content = soup.body

        paragraphs = [
            p.get_text(" ", strip=True)
            for p in content.select("p")
            if p.get_text(" ", strip=True)
        ]

        headings = [
            h.get_text(" ", strip=True)
            for h in content.select("h2, h3")
            if h.get_text(" ", strip=True)
        ]

        results.append({
            "url": url,
            "headline": row["headline"],
            "section": row["section"],
            "page_title": (
                title.get_text(" ", strip=True)
                if title else ""
            ),
            "lead": (
                lead.get_text(" ", strip=True)
                if lead else ""
            ),
            "headings": headings,
            "paragraphs": paragraphs,
            "article_text": " ".join(
                [row["headline"]]
                + headings
                + paragraphs
            )
        })

    except Exception as error:
        print("ERROR:", error)

        results.append({
            "url": url,
            "headline": row["headline"],
            "section": row["section"],
            "page_title": "",
            "lead": "",
            "headings": [],
            "paragraphs": [],
            "article_text": "",
            "error": str(error)
        })

    time.sleep(2)

with open(OUTPUT, "w", encoding="utf-8") as file:
    json.dump(results, file, ensure_ascii=False, indent=2)

print("\nUNIQUE ARTICLES:", len(articles))
print("CONTENT RECORDS:", len(results))
print("FAILED FETCHES:", sum(
    not item.get("article_text") for item in results
))
print("SAVED:", OUTPUT)
