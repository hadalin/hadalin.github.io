#!/usr/bin/env python3
"""Generate a combined GitHub + GitLab contribution heatmap SVG.

Fetches the last year of activity from the GitHub GraphQL API and the
public GitLab calendar endpoint, merges the daily counts, and renders
a GitHub-style heatmap to assets/img/contributions.svg.

Environment variables:
  GH_TOKEN     GitHub token (the Actions GITHUB_TOKEN is sufficient
               for public contribution data)
  GH_LOGIN     GitHub username
  GITLAB_USER  GitLab username

Pass --skip-github to render from GitLab data only (local preview
without a token).
"""

import json
import os
import sys
import urllib.request
from datetime import date, timedelta

OUTPUT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "assets", "img", "contributions.svg"
)

CELL = 10
GAP = 3
STEP = CELL + GAP
MARGIN_LEFT = 30
MARGIN_TOP = 20
MARGIN_BOTTOM = 24

LIGHT_PALETTE = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]
DARK_PALETTE = ["#373737", "#0e4429", "#006d32", "#26a641", "#39d353"]
LIGHT_TEXT = "#57606a"
DARK_TEXT = "#acacac"

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def http_json(request):
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def fetch_github(login, token):
    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            weeks { contributionDays { date contributionCount } }
          }
        }
      }
    }
    """
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": {"login": login}}).encode(),
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
        },
    )
    payload = http_json(request)
    if payload.get("errors"):
        raise RuntimeError(f"GitHub GraphQL errors: {payload['errors']}")
    weeks = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    counts = {}
    for week in weeks:
        for day in week["contributionDays"]:
            if day["contributionCount"]:
                counts[day["date"]] = day["contributionCount"]
    return counts


def fetch_gitlab(username):
    request = urllib.request.Request(
        f"https://gitlab.com/users/{username}/calendar.json",
        headers={"User-Agent": "contributions-graph (hadalin.me)"},
    )
    return http_json(request)


def build_weeks(today):
    """Sunday-started weeks covering the last year, like GitHub's graph."""
    start = today - timedelta(days=364)
    start -= timedelta(days=(start.weekday() + 1) % 7)  # back to Sunday
    weeks = []
    day = start
    while day <= today:
        week = []
        for _ in range(7):
            if day > today:
                break
            week.append(day)
            day += timedelta(days=1)
        weeks.append(week)
    return weeks


def level_thresholds(counts):
    values = sorted(v for v in counts.values() if v > 0)
    if not values:
        return [1, 2, 3, 4]
    return [max(1, values[min(len(values) - 1, len(values) * q // 4)]) for q in (1, 2, 3, 4)]


def level_for(count, thresholds):
    if count <= 0:
        return 0
    for level, threshold in enumerate(thresholds, start=1):
        if count <= threshold:
            return level
    return 4


def render_svg(weeks, counts):
    thresholds = level_thresholds(counts)
    total = sum(counts.get(d.isoformat(), 0) for week in weeks for d in week)

    width = MARGIN_LEFT + len(weeks) * STEP + 2
    height = MARGIN_TOP + 7 * STEP + MARGIN_BOTTOM

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img" '
        'aria-label="Combined GitHub and GitLab contributions over the last year">',
        "<style>",
        f"text {{ font: 10px -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; fill: {LIGHT_TEXT}; }}",
    ]
    for level, color in enumerate(LIGHT_PALETTE):
        parts.append(f".c{level} {{ fill: {color}; }}")
    parts.append("@media (prefers-color-scheme: dark) {")
    parts.append(f"text {{ fill: {DARK_TEXT}; }}")
    for level, color in enumerate(DARK_PALETTE):
        parts.append(f".c{level} {{ fill: {color}; }}")
    parts.append("}")
    parts.append("</style>")

    # Month labels where a new month starts; skip a cramped first label.
    labels = []
    for index, week in enumerate(weeks):
        month = week[0].month
        if index == 0 or month != weeks[index - 1][0].month:
            labels.append((index, month))
    if len(labels) > 1 and labels[1][0] - labels[0][0] < 3:
        labels = labels[1:]
    labels = [(i, m) for i, m in labels if i < len(weeks) - 2]
    for index, month in labels:
        x = MARGIN_LEFT + index * STEP
        parts.append(f'<text x="{x}" y="{MARGIN_TOP - 7}">{MONTHS[month - 1]}</text>')

    for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        y = MARGIN_TOP + row * STEP + CELL - 2
        parts.append(f'<text x="0" y="{y}">{name}</text>')

    for col, week in enumerate(weeks):
        x = MARGIN_LEFT + col * STEP
        for day in week:
            row = (day.weekday() + 1) % 7  # Sunday first
            y = MARGIN_TOP + row * STEP
            count = counts.get(day.isoformat(), 0)
            parts.append(
                f'<rect class="c{level_for(count, thresholds)}" x="{x}" y="{y}" '
                f'width="{CELL}" height="{CELL}" rx="2"><title>{day.isoformat()}: '
                f'{count} contribution{"s" if count != 1 else ""}</title></rect>'
            )

    legend_y = MARGIN_TOP + 7 * STEP + 10
    parts.append(
        f'<text x="0" y="{legend_y + CELL - 2}">{total:,} contributions in the last year</text>'
    )
    legend_x = width - 5 * STEP - 66
    parts.append(f'<text x="{legend_x - 32}" y="{legend_y + CELL - 2}">Less</text>')
    for level in range(5):
        parts.append(
            f'<rect class="c{level}" x="{legend_x + level * STEP}" y="{legend_y}" '
            f'width="{CELL}" height="{CELL}" rx="2"/>'
        )
    parts.append(f'<text x="{legend_x + 5 * STEP + 4}" y="{legend_y + CELL - 2}">More</text>')

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main():
    skip_github = "--skip-github" in sys.argv

    counts = {}

    if skip_github:
        print("Skipping GitHub (preview mode)", file=sys.stderr)
    else:
        token = os.environ["GH_TOKEN"]
        login = os.environ["GH_LOGIN"]
        github = fetch_github(login, token)
        print(f"GitHub: {sum(github.values())} contributions", file=sys.stderr)
        for day, count in github.items():
            counts[day] = counts.get(day, 0) + count

    gitlab = fetch_gitlab(os.environ["GITLAB_USER"])
    print(f"GitLab: {sum(gitlab.values())} contributions", file=sys.stderr)
    for day, count in gitlab.items():
        counts[day] = counts.get(day, 0) + count

    svg = render_svg(build_weeks(date.today()), counts)
    output = os.path.normpath(OUTPUT_PATH)
    with open(output, "w") as f:
        f.write(svg)
    print(f"Wrote {output}", file=sys.stderr)


if __name__ == "__main__":
    main()
