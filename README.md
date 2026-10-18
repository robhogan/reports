# Reports

Benchmark and investigation reports, served by GitHub Pages at https://robhogan.github.io/reports/.

Each report is a static page at `<slug>/index.html`, listed in `reports.json` and on the generated index page. `.nojekyll` makes Pages serve files as they are.

To add or update a report:

```sh
tools/publish.py report.html <slug> --title "<title>" --description "<one sentence>" --date YYYY-MM-DD
```

`report.html` is a page fragment (a `<title>`, font links and `<style>`, then the body); `publish.py` wraps it in a full HTML document and regenerates `index.html`.
