#!/usr/bin/env python3
"""Update the BLOG-POST-LIST block in README.md from an Atom/RSS feed.

For posts with a title, show the title. For titleless posts (micro.blog
status updates), show the post text instead — the whole thing if short,
or a trimmed excerpt if long.
"""
import html
import re
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

FEED = "https://vandragt.com/feed"
README = "README.md"
START = "<!-- BLOG-POST-LIST:START -->"
END = "<!-- BLOG-POST-LIST:END -->"
MAX_POSTS = 5
EXCERPT_LEN = 150

ATOM = "http://www.w3.org/2005/Atom"


def strip_html(s):
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def excerpt(text):
    if len(text) <= EXCERPT_LEN:
        return text
    return text[:EXCERPT_LEN].rstrip(" .,;:") + "…"


def md_escape(s):
    return s.replace("[", "\\[").replace("]", "\\]")


def parse_atom(root):
    ns = {"a": ATOM}
    items = []
    for e in root.findall("a:entry", ns):
        title = (e.findtext("a:title", default="", namespaces=ns) or "").strip()
        url = ""
        for link in e.findall("a:link", ns):
            if link.get("rel", "alternate") == "alternate":
                url = link.get("href") or url
                break
            url = url or link.get("href", "")
        body = strip_html(
            e.findtext("a:content", default="", namespaces=ns)
            or e.findtext("a:summary", default="", namespaces=ns)
        )
        date = (
            e.findtext("a:published", default="", namespaces=ns)
            or e.findtext("a:updated", default="", namespaces=ns)
        )[:10]
        items.append((title, url, body, date))
    return items


def parse_rss(root):
    items = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        url = (item.findtext("link") or "").strip()
        body = strip_html(item.findtext("description") or "")
        date = (item.findtext("pubDate") or "").strip()
        if date:
            date = parsedate_to_datetime(date).strftime("%Y-%m-%d")
        items.append((title, url, body, date))
    return items


def main():
    req = urllib.request.Request(FEED, headers={"User-Agent": "blog-post-updater"})
    data = urllib.request.urlopen(req, timeout=30).read()
    root = ET.fromstring(data)

    items = parse_atom(root) or parse_rss(root)
    items = items[:MAX_POSTS]

    lines = []
    for title, url, body, date in items:
        label = title if title else excerpt(body)
        label = md_escape(label) or url
        prefix = f"{date} — " if date else ""
        lines.append(f"- {prefix}[{label}]({url})")
    block = "\n".join(lines)

    with open(README, encoding="utf-8") as f:
        content = f.read()
    new = re.sub(
        re.escape(START) + r".*?" + re.escape(END),
        START + "\n" + block + "\n" + END,
        content,
        flags=re.S,
    )
    with open(README, "w", encoding="utf-8") as f:
        f.write(new)
    print(new[new.index(START) : new.index(END) + len(END)])


if __name__ == "__main__":
    main()
