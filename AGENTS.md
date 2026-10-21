# Reports: working guide

This repo is Rob Hogan's public reports site, https://robhogan.github.io/reports/: benchmarks, safety reviews and investigations, mostly on React Native, Metro and Hermes. This file is the source of truth for how a report looks and reads. `README.md` covers the file layout and `tools/publish.py`.

Version control is Sapling (`sl`). Work goes directly on `main`, with no PRs. Pages serves `main`'s root, so a push is a publish.

## Workflow

1. **Write** `<slug>/source.html`: optional `<style>` blocks for report-specific CSS, then `<main class="page">…</main>`, then anything after it, such as a `<script>` for a chart. No `<html>`, `<head>`, `<title>` or font links: the publish tool adds them and links `assets/report.css`.
2. **Publish** with `tools/publish.py` (see `README.md`). A new report needs `--title`, `--description` and `--date`. A change to a report that has been pushed is a new revision and needs `--note`. Use `--amend` only to fix a revision that hasn't been pushed yet.
3. **Look at it.** Render light and dark, and read the screenshots:

   ```sh
   chrome="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
   "$chrome" --headless=new --hide-scrollbars --virtual-time-budget=5000 --window-size=1200,9000 --screenshot=/tmp/light.png "file://$PWD/<slug>/index.html"
   "$chrome" --headless=new --hide-scrollbars --virtual-time-budget=5000 --window-size=1200,9000 --blink-settings=preferredColorScheme=0 --screenshot=/tmp/dark.png "file://$PWD/<slug>/index.html"
   ```

   Headless Chrome won't lay out narrower than 500px, so check phone width by loading the page in a 390px-wide `<iframe>`. Nothing outside a `.scroll` frame or a `<pre>` may overflow horizontally.
4. **Commit and push:** `sl commit -m "<sentence-case summary>"`, then `sl push --to main`. Commit `source.html` together with everything the tool generated.
5. **Check the live site.** Pages takes a minute or two. Fetch the live URL until the new text appears.

Never hand-edit generated files: `<slug>/index.html`, `<slug>/v/`, `reports.json`, `index.html` and `assets/report-<hash>.css`. Edit `source.html` or `assets/report.css` and republish.

Slugs name the repo, then the PR number or topic: `react-native-58965-destructuring`, `metro-1676-safety-review`, `react-native-regenerator-removal`.

## Audience

Reports are public, and are read by maintainers and contributors who weren't there when the work was done.

- **Nothing private or local.** No local paths, machine names, devroot, PR queue or session references, and no detail that is internal to Meta or any other company. Apps that aren't public are anonymised: "Private Expo SDK 58 game app".
- **Describe the method as it stands, not the path to it.** No "a first pass got this wrong" stories and no notes about runs that were discarded. If a pitfall matters to the result, state it as part of the method ("The lowered side of every comparison uses the CommonJS helpers apps really get").
- **Only claims that were checked.** State measured facts plainly. Label inferences and estimates as such, and say what they rest on ("derived from opcode counts and encodings, not from a prototype"). Drop anything that can't be supported, rather than hedging it into vagueness.
- **Credit people** by name with a link to their GitHub profile: Michael Leon (`<a href="https://github.com/micleo2">@micleo2</a>`).

## Writing

- **British English** in all report text: "behaviour", "analysed", "initialiser", "colour". (Some earlier report text mixes in American spellings. Leave it unless revising that passage.)
- **Verdict first, then evidence, then method.** The summary says what the reader should conclude. Each section opens with its finding, numbers included, then backs it up.
- **Short sentences and short paragraphs.** One or two paragraphs after the verdict cards, a single paragraph introducing most sections.
- **Specifics over adjectives.** "5–11× slower", "about 90–130 ns per execution", "2,302,951 files", never "much slower" or "many files". State units and sample sizes ("median of 40 per variant", "95% CI").
- **Vocabulary.** "Tradeoff", not "trade-off". Don't use "would" to describe behaviour: use "can" or "will". Avoid "actual". After a label-colon lede, capitalise the next word ("Fix before landing: Keep…").
- **Numbers.** Thousands separators (`2,982`). En dash for ranges (`45–55%`, `0.1–0.5%`). A true minus sign in verdict values and deltas meant to be read as signed numbers (`−2.4%`). A space before units (`56.8 s`, `1.23 ms`, `+7.8 KiB`).
- **References.** GitHub items as `owner/repo#123` (`react/metro#2040`), linked where a reader is likely to click through. Commits and versions in `<span class="mono">`. Code, flags, file names and identifiers in `<code>`.
- **HTML source.** Don't hard-wrap: each paragraph or list item is a single line.

## Page structure

Every report follows the same order. Optional sections are marked.

1. **Header**: eyebrow, `h1`, lede, meta line.
2. **Summary**: verdict cards, then one or two paragraphs.
3. **Tradeoffs** (optional, often second): what gets worse, ranked by severity.
4. **Evidence sections**: one `<section>` per question, each with an `h2` that states the topic ("Why the crawler can't run out of file descriptors", "Bundle size in real apps").
5. **Recommendation** (or "Before landing"): a short `ul.tight` of actions.
6. **Method**: how everything was measured, with scripts and repros in `<details>`.
7. **Follow-ups** (optional): sections added in later revisions, titled "Follow-up: <topic>" with an `id`, after Method.
8. **Revisions**: added by the publish tool. Don't write it.

## Visual style

The theme is `assets/report.css`. Report-specific CSS (a chart, a one-off layout) goes in a `<style>` block at the top of `source.html` and uses the theme's variables. Anything a second report needs moves into the shared theme.

- **Fonts:** IBM Plex Sans for body text, IBM Plex Sans Condensed for headings and verdict values, IBM Plex Mono for code, eyebrows, labels and table headers.
- **Colours:** always the variables, never literal colours, so dark mode works. `--bg`, `--surface` (table headers, group rows), `--fg`, `--fg-2` (secondary text), `--fg-3` (labels, meta), `--rule` (borders), `--accent` (links), `--code-bg`. `--faster` (blue) and `--slower` (red) mean good and bad, via `.pos` and `.neg`, and are the only data colours. Dark mode follows `prefers-color-scheme`, and `<html data-theme="light|dark">` forces either.
- **Layout:** `.page` is a 1040px grid with 56px between sections. Text blocks get `.prose` (72ch). Tables, charts, verdict cards and tradeoffs run full width. Wide tables scroll inside a `.scroll` frame, never the page.

## Components

### Header

```html
<main class="page">
  <header>
    <div class="eyebrow">react/metro #1676 · safety review</div>
    <h1>Dropping graceful-fs from Metro</h1>
    <p class="lede">What <code>metro</code> loses when <code>graceful-fs</code> is replaced with plain <code>node:fs</code>, checked against its source and measured under a 256-fd hard limit.</p>
    <div class="meta">
      <span>PR head <span class="mono">d5ca710</span></span><span>graceful-fs 4.2.11</span><span>Node 26.11.1, macOS</span><span>Reviewed 2026-10-18</span>
    </div>
  </header>
```

The eyebrow is `<repo> #<PR> · <kind>` or `<package> · <kind>`, where the kind is "benchmark", "safety review" or "investigation". The lede is one sentence: the question, and how it was answered. The meta line lists what the results depend on (commits, versions, devices, platform), ending with "Measured", "Reviewed" or "Investigated" and the date. The publish tool appends the revision link.

### Summary

```html
<section>
  <h2>Summary</h2>
  <div class="verdict">
    <div><span class="k">Verdict</span><span class="v pos">Safe to land</span><span class="d">One sentence on why.</span></div>
    <div><span class="k">Re-render 40 cards</span><span class="v pos">−2.1 to −2.4%</span><span class="d">What was measured, and where.</span></div>
    <div><span class="k">Bytecode size</span><span class="v neg">−0.25 to +0.49%</span><span class="d">…</span></div>
    <div><span class="k">Cold start</span><span class="v">No change</span><span class="d">…</span></div>
  </div>
  <div class="prose stack">
    <p>The finding, and the reason for it.</p>
    <p>What the catch is, and how much it matters.</p>
  </div>
</section>
```

Four cards is the norm. `.k` is a short label, `.v` a value or a two-to-four-word verdict (`.pos`, `.neg` or neither), `.d` one or two sentences. `.stack` spaces consecutive paragraphs. Use it on any `.prose` block that holds more than one element.

### Tradeoffs

```html
<div class="tradeoffs">
  <div class="tradeoff"><span class="sev high">Breaks</span><div><span class="t">What gets worse, as a statement</span><span class="b">The mechanism, the measured size, how common it is, and the fix or mitigation.</span></div></div>
  <div class="tradeoff"><span class="sev med">1.7–2.2× slower</span><div><span class="t">…</span><span class="b">…</span></div></div>
  <div class="tradeoff"><span class="sev low">Neutral</span><div><span class="t">…</span><span class="b">…</span></div></div>
</div>
```

The `.sev` text is a short label or a measured magnitude ("Breaks", "5–11× slower", "+31 B per site", "Edge case", "Negligible", "Small gain"). `high`, `med` and `low` set its colour. Order from most to least severe.

### Tables

```html
<div class="scroll"><table>
  <thead><tr><th>Scenario</th><th>Lowered</th><th>Native</th><th>Δ (95% CI)</th><th class="l">Notes</th></tr></thead>
  <tbody>
    <tr class="group"><td colspan="5">Typical patterns</td></tr>
    <tr><td>const [a, b] = pair</td><td>287.9</td><td>128.8</td><td class="pos">−55.2%</td><td class="l">Free text wraps.</td></tr>
  </tbody>
</table></div>
<p class="note prose">What the numbers are, how many samples, and anything that qualifies them.</p>
```

Numbers are right-aligned with tabular figures. The first column is monospace, for code and identifiers. Add `class="sans"` to first-column cells that hold names or prose instead. `td.l`/`th.l` are left-aligned, wrapping text columns. `.pos`/`.neg` colour a cell that is better or worse. `tr.group` heads a group of rows. A `.note` caption under a table carries the sample sizes and caveats. Put a CI on its own line in a muted mono span: `<br><span class="mono" style="color:var(--fg-3)">-6.8 … +6.2</span>`.

### Other blocks

- `<h3>` subsections inside a section, grouped with their table: `<div style="display:grid;gap:10px"><h3>…</h3><div class="scroll">…</div></div>`.
- `ul.tight` for lists of findings or recommendations, with a bold lead-in where items have a topic: `<li><strong>Expo has shipped this already.</strong> …</li>`.
- `.grid2` for two blocks side by side that stack on narrow screens.
- `<pre>` for code and bytecode listings. Long scripts and repros go in `<details class="prose"><summary>Crawler stress script</summary><pre>…</pre></details>`, with `<`, `>` and `&` escaped.
- Charts are report-specific: inline SVG or HTML built by a `<script>` after `</main>`, styled in the report's own `<style>`, coloured only with `--faster`, `--slower`, `--fg-3` and `--rule`, with an `aria-label`, and backed by a full table of the same data in `<details>`. `react-native-58965-destructuring/source.html` is the reference.
