
import pandas as pd

df = pd.read_csv("data/techi_articles.csv")

duplicates = df[df.duplicated("url", keep=False)].sort_values(
    ["url", "section"]
)

print("DUPLICATE ROWS:", len(duplicates))
print("\nDUPLICATE ARTICLE DETAILS:")

print(
    duplicates[
        ["url", "section", "headline", "author", "date_shown"]
    ].to_string(index=False)
)

print("\nDUPLICATE URL SUMMARY:")

print(
    duplicates.groupby("url").agg(
        sections=("section", lambda x: ", ".join(sorted(set(x)))),
        occurrences=("url", "size"),
        headline=("headline", "first")
    ).to_string()
)

print("\nBLANK FORMAT VALUES:")
print(df["format"].fillna("").str.strip().eq("").sum())

print("\nDUPLICATES WITHIN SAME SECTION:")
print(
    df.duplicated(["url", "section"]).sum()
)
