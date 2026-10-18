#!/usr/bin/env python3
"""Adds or updates a report on the site.

  tools/publish.py <fragment.html> <slug> --title "<title>" --description "<one sentence>" --date YYYY-MM-DD

<fragment.html> is a report page as written for Claude artifacts: a <title>, font links and a <style> block followed
by the page body, without a document skeleton. This wraps it in a full HTML document at <slug>/index.html, records
it in reports.json, and regenerates the index page.
"""
import argparse
import html
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SKELETON_STYLE = """<style>
  :root { color-scheme: light; padding-top: env(safe-area-inset-top, 0px); padding-bottom: env(safe-area-inset-bottom, 0px); }
  body { margin: 0; font: 14px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; }
  img { max-width: 100%; }
  [hidden] { display: none !important; }
</style>"""


def wrap(fragment):
    # Everything up to the end of the first <style> block belongs in <head>.
    split = fragment.find('</style>')
    head, body = (fragment[:split + len('</style>')], fragment[split + len('</style>'):]) if split != -1 else ('', fragment)
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            f'{SKELETON_STYLE}\n{head.strip()}\n</head>\n<body>\n{body.strip()}\n</body>\n</html>\n')


def write_index(reports):
    items = '\n'.join(
        f'    <li><a href="{html.escape(r["slug"])}/">{html.escape(r["title"])}</a>'
        f'<span class="date">{html.escape(r["date"])}</span><p>{html.escape(r["description"])}</p></li>'
        for r in sorted(reports, key=lambda r: r['date'], reverse=True))
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
    open(os.path.join(ROOT, 'index.html'), 'w').write(page)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('fragment')
    parser.add_argument('slug')
    parser.add_argument('--title', required=True)
    parser.add_argument('--description', required=True)
    parser.add_argument('--date', required=True)
    args = parser.parse_args()
    os.makedirs(os.path.join(ROOT, args.slug), exist_ok=True)
    open(os.path.join(ROOT, args.slug, 'index.html'), 'w').write(wrap(open(args.fragment).read()))
    path = os.path.join(ROOT, 'reports.json')
    reports = json.load(open(path)) if os.path.exists(path) else []
    reports = [r for r in reports if r['slug'] != args.slug]
    reports.append({'slug': args.slug, 'title': args.title, 'description': args.description, 'date': args.date})
    json.dump(sorted(reports, key=lambda r: r['slug']), open(path, 'w'), indent=2)
    open(path, 'a').write('\n')
    write_index(reports)
    print(f'{args.slug}/index.html')


if __name__ == '__main__':
    main()
