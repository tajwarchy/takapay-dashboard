"""
data_prep.py
Cleans takapay_sample_data.csv into data.json for the DeepDive dashboard.

Data-quality decisions made here (explained in README):
  1. brand_mention is True for all 660 rows -> dropped, it carries no signal.
  2. ~60 posts are tagged topic=off_topic (traffic, food, weather, unrelated
     shopping chatter) but still carry a sentiment score near the neutral
     line. They are KEPT in the dataset (so the dashboard can show them if a
     user filters for them, for transparency) but EXCLUDED from all headline
     sentiment/topic aggregates computed on the frontend, since they are not
     actually about the brand and would quietly dilute the real signal.
  3. 10 pairs of rows (20 rows) are exact duplicate posts (same text, same
     sentiment, different id/platform) - almost certainly injected/repost
     noise rather than genuinely independent opinions. One copy of each is
     kept, the newer duplicate id is dropped.
  4. Within topic=failed_transaction (the single largest bucket, a third of
     all posts) we tag a root-cause subtype using simple keyword rules so a
     brand manager can see WHY people are unhappy, not just that they are:
       - "Deducted but recharge failed": mentions a telco name or recharge
       - "Money sent but stuck / not received": pending/stuck transfer language
       - "Other": doesn't match either pattern
  5. The competitor name mentioned throughout topic=competitor posts is
     NgoodPay - every single one of these 81 posts is negative toward
     TakaPay, so it's surfaced as its own panel.
"""

import pandas as pd
import json

SRC = "takapay_sample_data.csv"
OUT = "data.json"

df = pd.read_csv(SRC)

raw_total = len(df)

# --- 2. drop exact duplicate posts, keep the lowest id ---
df = df.sort_values("id")
dup_mask = df.duplicated(subset="text", keep="first")
duplicates_removed = int(dup_mask.sum())
df = df[~dup_mask].copy()

# --- 4. root-cause subtype for failed_transaction ---
TELCOS = ["grameenphone", "banglalink", "airtel", "robi", "teletalk"]


def tag_subtype(row):
    if row["topic"] != "failed_transaction":
        return None
    t = row["text"].lower()
    if any(tc in t for tc in TELCOS) or "রিচার্জ" in row["text"] or "recharge" in t:
        return "Deducted but recharge failed"
    if (
        "pending" in t
        or "পৌঁছায়নি" in row["text"]
        or "atke ache" in t
        or "receiver pay nai" in t
    ):
        return "Money sent but stuck / not received"
    return "Other"


df["subtype"] = df.apply(tag_subtype, axis=1)
df["subtype"] = df["subtype"].astype(object).where(df["subtype"].notna(), None)
df["is_off_topic"] = df["topic"] == "off_topic"

records = df[
    [
        "id",
        "platform",
        "timestamp",
        "author",
        "text",
        "language",
        "sentiment",
        "sentiment_score",
        "topic",
        "subtype",
        "is_off_topic",
        "reactions",
        "comments",
    ]
].to_dict(orient="records")

meta = {
    "raw_total": raw_total,
    "duplicates_removed": duplicates_removed,
    "clean_total": len(df),
    "off_topic_count": int(df["is_off_topic"].sum()),
    "date_min": df["timestamp"].min(),
    "date_max": df["timestamp"].max(),
    "competitor_name": "NgoodPay",
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump({"meta": meta, "records": records}, f, ensure_ascii=False, indent=1)

print(f"raw={raw_total} duplicates_removed={duplicates_removed} clean={len(df)}")
print(f"off_topic={meta['off_topic_count']}")
print("wrote", OUT)
