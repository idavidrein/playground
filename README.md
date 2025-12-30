# Wandering Inn Volume 1 Scraper

This repo contains a small script to download the first volume of The Wandering Inn into
HTML files plus a single EPUB suitable for reading on an iPad.

## Usage

```bash
pip install -r requirements.txt
python scrape_wandering_inn.py --max-chapters 3
```

Remove `--max-chapters` to download the full volume once you confirm the output looks good.
Use `--no-proxy` if you need to bypass proxy settings in your environment.

## Output

The script writes an output folder (default: `wandering_inn_volume_1/`) containing:

- `index.html` – a table of contents
- One HTML file per chapter
- `wandering_inn_volume_1.epub`
