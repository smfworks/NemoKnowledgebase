# Capture a published test

Do this the same day a Clearinghouse test post goes live. A post without a row here is unfinished.

## When

After Step 8 in the Clearinghouse publish skill: the post URL returns HTTP 200.

Skip this file for week-in-reviews, setup recipes, release analyses of models we did not run, and essays. Those do not get a row.

## What to add

1. `published/YYYY-MM-DD-slug.md`

```markdown
# Title, copied from the post

- **Date:** YYYY-MM-DD
- **Author:** Nemo
- **Suite:** name the battery. Cold Iron is `strict_v01`, 157, thinking off.
- **Write-up:** https://www.smfclearinghouse.com/blog/YYYY-MM-DD-slug
- **Artifacts:** `benchmarks/<name>/` or "Not checked into this repo."

## Published line

> The post's own excerpt. Do not tighten it into a new claim.

This entry records that Clearinghouse post. It does not re-score the run.
```

2. A new first row in the conducted-tests table in `README.md`. Newest stays on top. Shift nothing else up by rewriting history. Insert.

3. Scripts and JSON, if you have them, under `benchmarks/<name>/`. Link that directory from the entry. If you do not have the JSON, say so. Do not point at a path that is not in git.

## Git

Use the clone whose `origin` is `https://github.com/smfworks/NemoKnowledgebase.git`.

```bash
git add README.md published/YYYY-MM-DD-slug.md benchmarks/<name>
git commit -m "Add YYYY-MM-DD-slug to the published test index"
git push origin main
```

`git add` those paths only. A dirty worktree here often holds notes that are not public. `git add -A` will publish them.

## Check

- The new row is the first data row under "Conducted tests".
- The published line matches the live post's excerpt.
- Every artifact link resolves to files in this commit.
- You did not invent a score that the post does not state.
