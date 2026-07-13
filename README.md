# DeepDive · TakaPay Social Listening Dashboard

**Live demo:** _add your deployed link here before submitting_
**Repo:** _this repo_

A single-page dashboard that turns 660 raw social posts about TakaPay (a
fictional mobile wallet) into something a non-technical brand manager can
act on in under a minute.

## What I built

- **Overall sentiment picture** — a sentiment split (donut) and a daily
  average-sentiment-score trend across June, so a brand manager can see both
  "how are we doing" and "is it getting better or worse."
- **Topic breakdown** — post volume per topic plus the sentiment mix within
  each topic, so it's clear at a glance which topics are big *and* which are
  actually driving negativity (volume alone would be misleading here).
- **My product call — a root-cause breakdown of failed transactions.**
  `failed_transaction` is the single largest topic (a third of all posts)
  and it's overwhelmingly negative, but "failed transaction" isn't one
  problem. I split it into two patterns using keyword rules:
  - *Money sent but stuck / not received* (162 posts) — a transfer sits
    pending for hours or days.
  - *Deducted but recharge failed* (44 posts) — money is taken but a mobile
    recharge (Grameenphone/Banglalink/Airtel/Robi/Teletalk) never lands.

  I chose this over a generic "top negative topic" callout because a brand
  manager can't act on "failed_transaction is bad" — but they can route
  "stuck transfers" to the payments/ops team and "recharge deductions
  without delivery" to the telco-integration team. That's a different fix
  and likely a different owner for each, so collapsing them into one number
  would hide the actionable part. I paired the breakdown with a rotating
  strip of real (sample) post text, in the original Bangla/English mix, so
  the percentages stay grounded in what people are actually saying.
- **Competitor spotlight** — the data has 81 posts naming a competitor
  (NgoodPay), and every single one is negative toward TakaPay: cheaper
  cash-out fees, a bigger agent network, faster app, better customer care.
  I surfaced this as its own panel since it's a very concrete, well-
  supported signal and doubles as the brief's "compare against the
  competitor" stretch idea.
- **Filters** — sentiment, topic, and date range, all live-updating the KPIs
  and every chart.

## What I noticed about the data

- **`brand_mention` is `True` for all 660 rows.** It looks like a
  pre-filter field that isn't doing any filtering here — it carries no
  signal, so I dropped it rather than pretend it was meaningful.
- **~60 posts are off-topic** (traffic complaints, biryani recommendations,
  "anyone know a phone offer?") but still carry a `topic: off_topic` label
  and a sentiment score sitting right near the neutral boundary. Left in,
  these would quietly dilute the real brand sentiment toward "less
  negative" without saying anything about the brand. I kept them in the
  underlying dataset (visible via the Topic filter, for transparency) but
  excluded them from every headline sentiment/topic figure.
- **10 pairs of posts (20 rows) are exact duplicates** — identical text and
  sentiment, different id/platform. That reads like injected or reposted
  noise rather than 20 independent opinions, so I deduplicated before
  computing anything, keeping the lower id of each pair.
- Sentiment **labels and scores agree closely** with each other (negative
  ≈ 6–30, neutral ≈ 45–60, positive ≈ 46–94), so I used the provided
  sentiment/sentiment_score as-is rather than re-deriving it.

## What I'd improve with another week

- Do the failed-transaction and competitor sub-tagging with an actual
  classifier (or an LLM pass with a few-shot prompt) instead of keyword
  rules — the rules work well on this sample because the synthetic data is
  fairly templated, but real text would break them.
- Add per-platform breakdown (TikTok vs. Facebook vs. Reddit skew quite
  differently in volume) since a brand manager may care where the noise is
  loudest, not just what it's about.
- Add a lightweight backend (or a scheduled script) so the dashboard can
  ingest a live feed instead of a static JSON snapshot.
- Surface the actual off-topic and duplicate posts in an inspectable list
  (not just a count) so someone can audit the cleaning decisions themselves.

## Where AI helped, and where I overrode it

- I used Claude to help me quickly profile the CSV (null/duplicate/topic/
  sentiment distributions) and to draft the first pass of the HTML/JS/Chart.js
  dashboard and the keyword rules for the failed-transaction subtypes.
- I overrode the first version of the root-cause tagging, which lumped
  everything mentioning a telco name into the same bucket as the "stuck
  transfer" pattern — I re-split it because the two are different failure
  modes with different fixes, which is the whole point of the insight.
- I checked the JSON output for validity before trusting it (an early
  version wrote `NaN` for the empty subtype field, which is not valid JSON
  and would have silently broken the page's `fetch().json()` call in a
  strict parser — I caught this by testing the output file directly rather
  than assuming it'd work).
- The 15-word micro-copy in the "our product call" section is mine — I
  rewrote the AI's first draft, which was longer and read more like a
  report than something a brand manager would actually skim.

## Tech

Plain HTML/CSS/JS + Chart.js (via CDN), no build step, reading a static
`data.json` produced by `data_prep.py` from the provided CSV. Chosen
deliberately over a framework for this scope: nothing to build, nothing to
break between now and the review, deploys as-is to GitHub Pages.

## Running locally

```bash
python3 data_prep.py   # regenerates data.json from takapay_sample_data.csv
python3 -m http.server 8000
# open http://localhost:8000
```

