#!/usr/bin/env python3
"""Builds the reports site from each report's source and records revisions.

  tools/publish.py <slug> --title "<title>" --description "<one sentence>" --date YYYY-MM-DD   # a new report
  tools/publish.py <slug> --note "<what changed>"                                              # a new revision
  tools/publish.py <slug> --amend [--note "<what changed>"]                                    # fix the latest revision in place
  tools/publish.py --rebuild                                                                   # rebuild every live page and the index

<slug>/source.html is the report: optional <style> blocks for report-specific CSS, then the page body (<main class="page">
and anything after it, such as a <script>). This wraps it in a document that links assets/report.css and writes:

  <slug>/index.html      the live page, with a "Revisions" section listing every revision
  <slug>/v/<n>/index.html a frozen snapshot of revision n, linking a content-hashed copy of the stylesheet so later
                          theme changes don't alter it
  reports.json           the title, description, headline date and revisions of every report
  index.html             the site index

Revisions are only added by publishing a slug. --rebuild regenerates live pages and the index without touching
snapshots, e.g. after a change to this script.
"""
import argparse
import datetime
import hashlib
import html
import json
import os
import re
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_URL = 'https://github.com/robhogan/reports'
STYLESHEET = 'assets/report.css'
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500'
         '&family=IBM+Plex+Sans+Condensed:wght@500;600&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400'
         '&display=swap">')


def read(path):
    with open(os.path.join(ROOT, path)) as f:
        return f.read()


def write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w') as f:
        f.write(text)


def split_source(source):
    """Returns (leading <style> blocks, body)."""
    styles = []
    rest = source.lstrip()
    while rest.startswith('<style'):
        end = rest.index('</style>') + len('</style>')
        styles.append(rest[:end])
        rest = rest[end:].lstrip()
    return '\n'.join(styles), rest.rstrip()


def hashed_stylesheet():
    """Writes a content-hashed copy of the shared stylesheet, for snapshots, and returns its path."""
    css = read(STYLESHEET)
    path = f'assets/report-{hashlib.sha256(css.encode()).hexdigest()[:10]}.css'
    if not os.path.exists(os.path.join(ROOT, path)):
        shutil.copyfile(os.path.join(ROOT, STYLESHEET), os.path.join(ROOT, path))
    return path


def document(report, styles, body, stylesheet, extra_head=''):
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            f'<title>{html.escape(report["title"])}</title>\n'
            f'<meta name="description" content="{html.escape(report["description"])}">\n'
            f'{extra_head}{FONTS}\n<link rel="stylesheet" href="{stylesheet}">\n'
            f'{styles + chr(10) if styles else ""}</head>\n<body>\n{body}\n</body>\n</html>\n')


def with_revision_chrome(body, report):
    """Adds the latest revision to the header's .meta line and a Revisions section at the end of <main>."""
    revisions = report['revisions']
    latest = revisions[-1]
    label = f'Published {latest["date"]}' if len(revisions) == 1 else f'Revision {latest["n"]}, {latest["date"]}'
    span = f'<span><a href="#revisions">{label}</a></span>'
    meta = re.search(r'<div class="meta">.*?(?=\s*</div>)', body, re.S)
    if meta:
        body = body[:meta.end()] + span + body[meta.end():]
    rows = '\n'.join(
        f'        <tr><td><a href="v/{r["n"]}/">{r["n"]}</a></td><td>{r["date"]}</td>'
        f'<td class="l">{html.escape(r["note"], quote=False)}</td></tr>'
        for r in reversed(revisions))
    section = f"""
  <section id="revisions">
    <h2>Revisions</h2>
    <div class="scroll"><table class="revisions">
      <thead><tr><th>Revision</th><th>Date</th><th class="l">Change</th></tr></thead>
      <tbody>
{rows}
      </tbody>
    </table></div>
    <p class="note prose">Each revision links to a frozen copy of the report as it was published. The <a href="{REPO_URL}/commits/main/{report["slug"]}">commit history</a> has every edit.</p>
  </section>
"""
    end = body.rindex('</main>')
    return body[:end].rstrip() + '\n' + section + body[end:]


def snapshot_banner(report, revision):
    return (f'<div class="snapshot-banner"><div>Revision {revision["n"]} of this report, published {revision["date"]}. '
            '<a href="../../">Read the latest version</a> · <a href="../../#revisions">All revisions</a></div></div>')


def build_live(report):
    styles, body = split_source(read(f'{report["slug"]}/source.html'))
    write(f'{report["slug"]}/index.html',
          document(report, styles, with_revision_chrome(body, report), f'../{STYLESHEET}'))


def build_snapshot(report, revision):
    styles, body = split_source(read(f'{report["slug"]}/source.html'))
    write(f'{report["slug"]}/v/{revision["n"]}/index.html',
          document(report, styles, snapshot_banner(report, revision) + '\n' + body, f'../../../{hashed_stylesheet()}',
                   '<meta name="robots" content="noindex">\n'))


def write_index(reports):
    def entry(r):
        revisions = r['revisions']
        updated = (f'<span class="date">updated {html.escape(revisions[-1]["date"])}</span>'
                   if revisions[-1]['date'] != r['date'] else '')
        return (f'    <li><a href="{html.escape(r["slug"])}/">{html.escape(r["title"])}</a>'
                f'<span class="date">{html.escape(r["date"])}</span>{updated}<p>{html.escape(r["description"])}</p></li>')
    items = '\n'.join(entry(r) for r in sorted(reports, key=lambda r: r['date'], reverse=True))
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Reports</title>
<style>
  :root {{ --bg: #fbfbfa; --fg: #16181c; --muted: #6b6f77; --rule: #dddcd6; --accent: #2a5fa8; }}
  @media (prefers-color-scheme: dark) {{ :root {{ --bg: #141517; --fg: #ecebe6; --muted: #9a9b97; --rule: #2e3034; --accent: #7fb0f0; color-scheme: dark; }} }}
  body {{ margin: 0; background: var(--bg); color: var(--fg); font: 16px/1.6 system-ui, -apple-system, "Segoe UI", sans-serif; }}
  main {{ max-width: 760px; margin: 0 auto; padding: 48px 20px 80px; }}
  h1 {{ font-size: 1.8rem; margin: 0 0 8px; }}
  .lede {{ color: var(--muted); margin: 0 0 32px; }}
  ul {{ list-style: none; margin: 0; padding: 0; border-top: 1px solid var(--rule); }}
  li {{ padding: 16px 0; border-bottom: 1px solid var(--rule); }}
  a {{ color: var(--accent); font-weight: 600; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  .date {{ color: var(--muted); font-size: 0.85rem; margin-left: 12px; font-variant-numeric: tabular-nums; }}
  li p {{ margin: 4px 0 0; color: var(--muted); }}
</style>
</head>
<body>
<main>
  <h1>Reports</h1>
  <p class="lede">Benchmarks and investigations, mostly on React Native, Metro and Hermes.</p>
  <ul>
{items}
  </ul>
</main>
</body>
</html>
"""
    write('index.html', page)


def load_reports():
    path = os.path.join(ROOT, 'reports.json')
    return json.load(open(path)) if os.path.exists(path) else []


def save_reports(reports):
    write('reports.json', json.dumps(sorted(reports, key=lambda r: r['slug']), indent=2, ensure_ascii=False) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('slug', nargs='?')
    parser.add_argument('--title')
    parser.add_argument('--description')
    parser.add_argument('--date', help='headline date for the index, usually when the work was done')
    parser.add_argument('--note', help='one-line change note for this revision')
    parser.add_argument('--revised', default=datetime.date.today().isoformat(), help='revision date (default: today)')
    parser.add_argument('--amend', action='store_true', help='replace the latest revision instead of adding one')
    parser.add_argument('--rebuild', action='store_true', help='rebuild every live page and the index')
    args = parser.parse_args()
    reports = load_reports()

    if args.rebuild:
        for report in reports:
            build_live(report)
        write_index(reports)
        return

    if not args.slug:
        parser.error('a slug or --rebuild is required')
    if not os.path.exists(os.path.join(ROOT, args.slug, 'source.html')):
        parser.error(f'{args.slug}/source.html does not exist')
    report = next((r for r in reports if r['slug'] == args.slug), None)
    if report is None:
        if not (args.title and args.description and args.date):
            parser.error('a new report needs --title, --description and --date')
        if args.amend:
            parser.error('--amend needs an existing report')
        report = {'slug': args.slug, 'revisions': []}
        reports.append(report)
    elif not args.note and not args.amend:
        parser.error('a new revision of an existing report needs --note (or --amend to fix the latest one)')
    for key in ('title', 'description', 'date'):
        if getattr(args, key):
            report[key] = getattr(args, key)

    revisions = report['revisions']
    if args.amend:
        revision = revisions[-1]
        revision['date'] = args.revised
        if args.note:
            revision['note'] = args.note
    else:
        revision = {'n': len(revisions) + 1, 'date': args.revised, 'note': args.note or 'First published.'}
        revisions.append(revision)

    # Keep key order stable in reports.json.
    reports[reports.index(report)] = {k: report[k] for k in ('slug', 'title', 'description', 'date', 'revisions')}
    report = next(r for r in reports if r['slug'] == args.slug)
    save_reports(reports)
    build_snapshot(report, revision)
    build_live(report)
    write_index(reports)
    print(f'{args.slug}/index.html (revision {revision["n"]})')


if __name__ == '__main__':
    main()
