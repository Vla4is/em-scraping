# Project for euromonitor

Two scraping exercises, one folder each.

**Glossier** (glossier.com): scraper built with Scrapy. My first ever serious project in scraping.
- **[glossier/README.md](glossier/README.md)**: setup, how to run each task, the output columns and how sets are modelled
- [glossier/notes.txt](glossier/notes.txt): assumptions, decisions, known limitations and AI usage
- [glossier/notes-on-the-way.txt](glossier/notes-on-the-way.txt): my step-by-step log while working

**Cellarbrations** (cellarbrations.com.au, whisky category): Playwright fetch + offline parsing, behind Cloudflare (needs a VPN).
- **[cellarbrations/README.md](cellarbrations/README.md)**: setup, how to run each task and the output columns
- [cellarbrations/notes.txt](cellarbrations/notes.txt): assumptions, decisions, Task 5 (browser vs HTTP) and AI usage
- [cellarbrations/my-notes.txt](cellarbrations/my-notes.txt): my step-by-step log while working

Shared:
- [requirements.txt](requirements.txt): dependencies (`pip install -r requirements.txt`, then `playwright install chromium`)
