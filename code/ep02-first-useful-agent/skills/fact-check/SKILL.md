---
name: fact-check
description: Check each claim against its cited source and write an evidence-backed report.
---

# Fact check

Use this method for every claim you are asked to check.

1. Fetch the cited URL with the web tool. If the page can't be fetched, the verdict is **Not found**; say why.
2. Find the passage on that page that addresses the claim. Note the page's "Last updated" date if it shows one.
3. Choose one verdict:
   - **Supported**: the passage says the same thing as the claim.
   - **Contradicted**: the passage says something that conflicts with the claim.
   - **Not found**: the page doesn't address the claim.
4. Evidence: quote at most 15 words from the passage, exactly as written, in quotation marks.
5. Use only the cited page. Don't use other pages or what you already know.

## Report

Write `report.md` with:

- A title: `Fact-check report`
- The date checked (UTC)
- A table with the columns: `#`, `Claim`, `Verdict`, `Evidence`, `Source` (page title and last-updated date)
- A `Notes` line for any page that couldn't be read, or `Notes: none`
