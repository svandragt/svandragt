# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

GitHub profile README repo (`svandragt/svandragt`) — the special repo whose `README.md` renders on the GitHub profile page. There is no app or build; the only logic is a script that keeps the "Latest from my blog" section fresh.

## Architecture

- `README.md` — the profile page content. Two blocks are generated, not hand-edited: `<!-- RELEASES-LIST:START/END -->` and `<!-- BLOG-POST-LIST:START/END -->`.
- `scripts/update_releases.py` — queries the GitHub GraphQL API (via `gh api graphql`) for the latest release across all public, non-fork repos owned by `svandragt`, takes the 5 most recent, and rewrites the releases block in place.
- `scripts/update_blog_posts.py` — fetches `https://vandragt.com/feed` (Atom, falls back to RSS), takes the latest 5 entries, and rewrites the blog block in place. For posts without a title (micro.blog status updates), it falls back to a trimmed excerpt of the body text.
- `.github/workflows/blog-post-workflow.yml` — runs both scripts daily via cron (06:00 UTC) and on manual dispatch, then auto-commits any change to `README.md` via `stefanzweifel/git-auto-commit-action`. `update_releases.py` needs `GH_TOKEN` set (from `secrets.GITHUB_TOKEN`) for the `gh` CLI.
- `.github/workflows/dependabot-auto-merge.yml` + `.github/dependabot.yml` — Dependabot watches GitHub Actions versions weekly; PRs from `dependabot[bot]` get auto-merged (squash) via `gh pr merge --auto`.

## Working on the scripts

Run locally to test against live data:

```bash
python3 scripts/update_releases.py    # needs `gh` authenticated locally
python3 scripts/update_blog_posts.py
```

Both are single-file, stdlib-only scripts (no dependencies to install, no test suite) that edit `README.md` directly, so check `git diff` after running one.

## Git workflow

Push straight to `main` — no PRs for changes in this repo.
