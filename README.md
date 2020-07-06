# CoronaUpdate
Daily update of corona virus in public transportation

Needed to run this script:
  1. geckodriver-v0.26.0-win64.
  2. Mozilla Firefox (too big to add here, please download online)
  3. the added files here.

Explanation:
1. The script goes to https://coronaupdates.health.gov.il/corona-updates/grid/public-transport than scraping all of its pages.
2. parsing all of the rides available in the website to a list
3. comparing with most recent list
4. showing diff = new rides
