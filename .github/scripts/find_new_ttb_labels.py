#!/usr/bin/env python3
"""Discover whiskey labels and queue unfinished local downloads and OCR work."""

import argparse
import json
import re
import sys
import time
from datetime import datetime, timedelta
from html.parser import HTMLParser
from pathlib import Path

from label_state import ocr_complete

try:
    import requests
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    requests = None
    DEPENDENCIES_AVAILABLE = False


class RegistryPage(HTMLParser):
    """Read result links and visible messages without optional parser dependencies."""

    def __init__(self, content):
        super().__init__()
        self.text_parts = []
        self.links = []
        self.anchor = None
        self.hidden = 0
        self.feed(content)
        self.close()

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.hidden += 1
        if tag == "a":
            self.anchor = {"href": dict(attrs).get("href", ""), "text": []}
            self.links.append(self.anchor)

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.hidden = max(0, self.hidden - 1)
        if tag == "a":
            self.anchor = None

    def handle_data(self, data):
        if not self.hidden:
            self.text_parts.append(data)
            if self.anchor is not None:
                self.anchor["text"].append(data)


class SearchError(RuntimeError):
    def __init__(self, message, partial_ids=(), pages_completed=0):
        super().__init__(message)
        self.partial_ids = list(dict.fromkeys(partial_ids))
        self.pages_completed = pages_completed


class TTBLabelFinder:
    """Search using a single registry session; never mistake an error for no results."""

    SEARCH_URL = "https://ttbonline.gov/colasonline/publicSearchColasBasicProcess.do?action=search"
    DETAIL_URL = "https://www.ttbonline.gov/colasonline/viewColaDetails.do?action=publicFormDisplay&ttbid="
    NEXT_PAGE_URL = "https://ttbonline.gov/colasonline/publicPageBasicCola.do?action=page&pgfcn=nextset"
    MAX_PAGES = 100

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0"})

    def _request(self, method, url, **kwargs):
        # At most three retries, exclusively for transient transport/server failures.
        for attempt in range(4):
            try:
                response = getattr(self.session, method)(url, timeout=30, **kwargs)
                response.raise_for_status()
                return response
            except (requests.Timeout, requests.ConnectionError, requests.HTTPError) as exc:
                status = getattr(getattr(exc, "response", None), "status_code", None)
                transient = (isinstance(exc, (requests.Timeout, requests.ConnectionError))
                             or status in (408, 429) or (status is not None and 500 <= status < 600))
                if not transient or attempt == 3:
                    raise
                time.sleep(2 ** attempt)

    def search_ttb_registry(self, date_from, date_to, origin_code="",
                            class_type_from="100", class_type_to="150"):
        ids = []
        pages = 0
        form_data = {
            "searchCriteria.dateCompletedFrom": date_from,
            "searchCriteria.dateCompletedTo": date_to,
            "searchCriteria.productOrFancifulName": "",
            "searchCriteria.productNameSearchType": "E",
            "searchCriteria.classTypeFrom": class_type_from,
            "searchCriteria.classTypeTo": class_type_to,
            "searchCriteria.originCode": origin_code,
        }
        try:
            response = self._request("post", self.SEARCH_URL, data=form_data)
            page_ids, has_next = self._parse_search_results(response.text)
            while True:
                ids = list(dict.fromkeys(ids + page_ids))
                pages += 1
                if not has_next:
                    return ids
                if pages >= self.MAX_PAGES:
                    raise RuntimeError(f"Reached maximum page limit ({self.MAX_PAGES}); search incomplete")
                time.sleep(0.5)
                page_ids, has_next = self._fetch_next_page()
        except Exception as exc:
            raise SearchError(str(exc), ids, pages) from exc

    def _fetch_next_page(self):
        return self._parse_search_results(self._request("get", self.NEXT_PAGE_URL).text)

    def _parse_search_results(self, html_content):
        page = RegistryPage(html_content)
        text = " ".join(page.text_parts)
        if re.search(r"captcha|unable to process|access denied|session (?:has )?expired|"
                     r"unexpected error|system error", text, re.IGNORECASE):
            raise ValueError(f"Registry returned an error: {text[:200]}")
        ids = list(dict.fromkeys(
            match.group(1) for link in page.links
            if (match := re.search(r"ttbid=(\d+)", link["href"], re.IGNORECASE))))
        has_next = any(re.search(r"Next\s*>", " ".join(link["text"]), re.IGNORECASE)
                       for link in page.links)
        # Only explicit, recognized no-result responses can mean a successful empty search.
        if not ids and not re.search(
                r"no\s+(?:(?:matching|approved)\s+)?(?:records?|results?|colas?|labels?)"
                r"|(?:0|zero)\s+(?:records?|results?)|no\s+.*?found",
                text, re.IGNORECASE):
            raise ValueError("Unrecognized registry response (no result IDs or explicit no-results message)")
        if has_next and not ids:
            raise ValueError("Empty registry page advertises additional results")
        return ids, has_next

    def get_existing_ttb_ids(self, labels_dir):
        """Return only labels whose downloads AND OCR are confirmed complete."""
        path = Path(labels_dir)
        return {p.name for p in path.iterdir()
                if p.is_dir() and p.name.isdigit() and ocr_complete(p)} if path.exists() else set()

    def pending_local_ids(self, labels_dir):
        path = Path(labels_dir)
        return sorted(p.name for p in path.iterdir()
                      if p.is_dir() and p.name.isdigit() and not ocr_complete(p)) if path.exists() else []

    def work_ids(self, registry_ids, labels_dir):
        complete = self.get_existing_ttb_ids(labels_dir)
        return list(dict.fromkeys([value for value in registry_ids if value not in complete]
                                  + self.pending_local_ids(labels_dir)))

    def find_new_labels(self, date_from, date_to, labels_dir, origin_code="",
                        class_type_from="100", class_type_to="150"):
        ids = self.search_ttb_registry(date_from, date_to, origin_code, class_type_from, class_type_to)
        return self.work_ids(ids, labels_dir), len(ids)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from", dest="date_from")
    parser.add_argument("--to", dest="date_to")
    parser.add_argument("--origin", default="")
    parser.add_argument("--class-from", default="100")
    parser.add_argument("--class-to", default="150")
    parser.add_argument("--labels-dir", default="labels")
    parser.add_argument("--output")
    parser.add_argument("--max-pages", type=int, default=TTBLabelFinder.MAX_PAGES)
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()
    output = {
        "search_date": datetime.now().isoformat(), "status": "failed", "error": None,
        "new_ttb_ids": [], "count": 0, "total_registry_results": 0,
        "partial_ttb_ids": [], "partial_count": 0, "pages_completed": 0,
        "date_range": {"from": args.date_from, "to": args.date_to},
        "filters": {"origin_code": args.origin, "class_type_from": args.class_from,
                    "class_type_to": args.class_to},
    }
    finder = None
    try:
        if not DEPENDENCIES_AVAILABLE:
            raise RuntimeError("Required dependency requests is not installed")
        end = datetime.strptime(args.date_to, "%Y-%m-%d") if args.date_to else datetime.now()
        start = datetime.strptime(args.date_from, "%Y-%m-%d") if args.date_from else end - timedelta(days=7)
        if start > end or args.max_pages < 1:
            raise ValueError("Date range must be ordered and --max-pages must be positive")
        output["date_range"] = {"from": start.strftime("%Y-%m-%d"), "to": end.strftime("%Y-%m-%d")}
        finder = TTBLabelFinder(args.verbose)
        finder.MAX_PAGES = args.max_pages
        ids = finder.search_ttb_registry(start.strftime("%m/%d/%Y"), end.strftime("%m/%d/%Y"),
                                         args.origin, args.class_from, args.class_to)
        output.update(status="complete", new_ttb_ids=finder.work_ids(ids, args.labels_dir),
                      total_registry_results=len(ids))
    except SearchError as exc:
        output.update(status="partial" if exc.pages_completed else "failed", error=str(exc),
                      partial_ttb_ids=exc.partial_ids, partial_count=len(exc.partial_ids),
                      total_registry_results=len(exc.partial_ids), pages_completed=exc.pages_completed)
        output["new_ttb_ids"] = finder.work_ids(exc.partial_ids, args.labels_dir)
    except Exception as exc:
        output["error"] = str(exc)
        if finder:
            output["new_ttb_ids"] = finder.pending_local_ids(args.labels_dir)
    output["count"] = len(output["new_ttb_ids"])
    encoded = json.dumps(output, indent=2)
    if args.output:
        Path(args.output).write_text(encoded + "\n", encoding="utf-8")
    print(encoded)
    return 0 if output["status"] == "complete" else 1


if __name__ == "__main__":
    sys.exit(main())
