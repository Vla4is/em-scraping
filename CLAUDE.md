# Glossier scraper

- Target: https://www.glossier.com/collections/all (US locale) we start from Lithuanian locale because the task requires re-running on the US locale. The output is a CSV, they explicitly stated to **KEEP IT SIMPLE**, we respect the request and avoid complex data engineering practices and purely focus on scraping. The repo also needs `requirements.txt` and `notes.txt`.
- Shopify, **server-rendered**. A plain curl returns every product, we can use scrapy for it.
- The locality of the website is US if we access it from the link. I can purposely scrape lithuanian first and then do the us.
- Its a shopify website determined by network analysis so We **don't use `/products.json`**. The user is scraping the HTML for practice.
- `glossier/fetch-all-prod.sh` saves page 1 to `glossier/raw/all.html`, there is a commented version for Lithuania.
- On Windows, `bash` resolves to the WSL stub and fails. Use `"C:\Program Files\Git\bin\bash.exe"`.
- The CSV fields are still open, pending discussion with the user.
- I assume that when the data will be loaded it will be upsert in the system or full loading.