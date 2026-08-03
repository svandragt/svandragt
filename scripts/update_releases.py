#!/usr/bin/env python3
"""Update the RELEASES-LIST block in README.md with the latest GitHub
releases across all public, non-fork repos owned by the user. Uses the
`gh` CLI (already authenticated in the GitHub Actions runner).
"""
import json
import re
import subprocess

USER = "svandragt"
README = "README.md"
START = "<!-- RELEASES-LIST:START -->"
END = "<!-- RELEASES-LIST:END -->"
MAX_RELEASES = 5

QUERY = """
query {
  user(login: "%s") {
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC) {
      nodes {
        name
        releases(first: 1, orderBy: {field: CREATED_AT, direction: DESC}) {
          nodes { name tagName url createdAt }
        }
      }
    }
  }
}
""" % USER


def md_escape(s):
    return s.replace("[", "\\[").replace("]", "\\]")


def main():
    out = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={QUERY}"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    repos = json.loads(out)["data"]["user"]["repositories"]["nodes"]

    releases = []
    for repo in repos:
        nodes = repo["releases"]["nodes"]
        if nodes:
            releases.append((repo["name"], nodes[0]))
    releases.sort(key=lambda r: r[1]["createdAt"], reverse=True)
    releases = releases[:MAX_RELEASES]

    lines = []
    for name, rel in releases:
        date = rel["createdAt"][:10]
        label = md_escape(f"{name} {rel['name'] or rel['tagName']}")
        lines.append(f"- {date} — [{label}]({rel['url']})")
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
