#!/usr/bin/env python3
"""Check the discovery prompt's fallback sources without modifying whiskey data."""

import argparse
import html
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


ROOT = Path(__file__).resolve().parents[2]
PROMPT = ROOT / ".github/prompts/find-new-releases.prompt.md"
MAX_BYTES = 5_000_000
RETRIES = 3


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.text = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.hidden += 1
        if tag == "a":
            self.links.extend(value for key, value in attrs if key == "href" and value)

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.hidden = max(0, self.hidden - 1)

    def handle_data(self, data):
        if not self.hidden:
            self.text.append(data)


def load_sources(prompt):
    section = prompt.split("Reputable fallback sources (in priority order):", 1)[1]
    sources = re.findall(r"^\d+\. \[([^\]]+)\]\((https://[^)]+)\)", section, re.M)
    if not sources:
        raise ValueError("No discovery sources found in the prompt")
    return sources


def validate_content(name, url, body):
    page = Page()
    page.feed(body)
    text = " ".join(page.text).lower()
    if not page.links or not re.search(r"\b(bourbon|rye|whiskey|whisky)\b", text):
        return "No whiskey content or links found (possible soft 404 or bot challenge)"
    if urllib.parse.urlparse(url).hostname in ("breakingbourbon.com", "www.breakingbourbon.com"):
        if not any(
            re.match(r"^/bourbon-whiskey-press-releases/[^/]+", urllib.parse.urlparse(link).path)
            for link in page.links
        ):
            return "No Breaking Bourbon press-release article links found"
    return None


def check_source(name, url):
    for attempt in range(RETRIES + 1):
        transient = False
        try:
            request = urllib.request.Request(
                url, headers={"User-Agent": "WhiskeyProofs-SourceHealth/1.0"}
            )
            with urllib.request.urlopen(request, timeout=20) as response:
                if response.status != 200:
                    return f"Unexpected HTTP {response.status}"
                if response.headers.get_content_type() != "text/html":
                    return "Expected an HTML discovery page"
                body = response.read(MAX_BYTES + 1)
                if len(body) > MAX_BYTES:
                    return "Discovery page exceeds 5 MB"
                body = body.decode(response.headers.get_content_charset() or "utf-8", errors="replace")
            return validate_content(name, url, body)
        except urllib.error.HTTPError as error:
            message = f"HTTP {error.code}"
            transient = error.code == 429 or 500 <= error.code < 600
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            message = f"Network error: {error}"
            transient = True
        except (ValueError, LookupError) as error:
            return f"Invalid response: {error}"
        if not transient or attempt == RETRIES:
            return message
        time.sleep(2 ** attempt)


def run(prompt, report):
    lines = ["# Discovery source health", ""]
    failed = 0
    try:
        sources = load_sources(prompt.read_text(encoding="utf-8"))
    except (OSError, IndexError, ValueError) as error:
        sources = []
        failed = 1
        lines.append(f"Configuration error: {html.escape(str(error))}")
    for name, url in sources:
        error = check_source(name, url)
        failed += error is not None
        status = f"FAIL: {error}" if error else "OK"
        lines.append(f"- **{html.escape(name)}**: {html.escape(url)} — {html.escape(status)}")
    lines.extend(["", f"Checked: {len(sources)}; failures: {failed}."])
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 1 if failed else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt", type=Path, default=PROMPT)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    sys.exit(run(args.prompt, args.report))
