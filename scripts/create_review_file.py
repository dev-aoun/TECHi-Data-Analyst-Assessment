
import json
import pandas as pd
from pathlib import Path

data = Path("data")

df = pd.read_csv(
    data / "techi_articles.csv",
    dtype=str,
    keep_default_na=False
)

with open(data / "article_content.json", encoding="utf-8") as f:
    articles = json.load(f)

content_map = {
    item["url"]: item
    for item in articles
    if item.get("url")
}

review_rows = []

for _, row in df.iterrows():
    article = content_map.get(row["url"], {})

    review_rows.append({
        "section": row["section"],
        "headline": row["headline"],
        "author": row["author"],
        "date_shown": row["date_shown"],
        "format": row["format"],
        "names_a_company": row["names_a_company"],
        "contains_a_number": row["contains_a_number"],
        "article_headings": " | ".join(article.get("headings", [])),
        "article_text_preview": article.get("article_text", "")[:1200],
        "url": row["url"]
    })

review = pd.DataFrame(review_rows)

review.to_csv(
    data / "phase2_content_review.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Review records:", len(review))
print("Created: data/phase2_content_review.csv")
