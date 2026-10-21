# Reports

Benchmark and investigation reports, served by GitHub Pages at https://robhogan.github.io/reports/.

Each report lives in its own directory. `<slug>/source.html` is what gets written and edited, and `tools/publish.py` builds everything else from it:

```
assets/report.css          shared theme: fonts, colours, light and dark, components
assets/report-<hash>.css   frozen copies of the theme, linked by snapshots
<slug>/source.html         the report body, plus optional report-specific <style>
<slug>/index.html          the live page (generated)
<slug>/v/<n>/index.html    a frozen snapshot of revision n (generated)
reports.json               every report's title, description, date and revisions (generated)
index.html                 the site index (generated)
```

## Publishing

```sh
# A new report: write <slug>/source.html, then
tools/publish.py <slug> --title "<title>" --description "<one sentence>" --date YYYY-MM-DD

# A new revision: edit <slug>/source.html, then
tools/publish.py <slug> --note "<what changed, one sentence>"

# Fix the latest revision before it has been pushed
tools/publish.py <slug> --amend

# Rebuild every live page and the index, e.g. after changing publish.py
tools/publish.py --rebuild
```

`.nojekyll` makes Pages serve files as they are.

## Revisions

Every publish of a slug records a revision with a date and a change note, and writes a snapshot of the report to `<slug>/v/<n>/`. The live page shows the latest revision in its header and lists every revision in a "Revisions" section at the end. Snapshots carry a banner that links back to the latest version.

Live pages link `assets/report.css`, so a theme change applies to them straight away. Snapshots link the content-hashed copy that was current when they were published, so a later theme change doesn't alter them. Never edit a snapshot or a hashed stylesheet.

`AGENTS.md` describes the visual and writing style and the component catalogue.
