#!/usr/bin/env python3
"""
Fetch completed Jira tickets for a project and generate Markdown files.

Usage:
    python3 gen_weekly_summary.py --project GENAI --output-dir ./weekly_updates --days 7

Requires JIRA_USER and JIRA_API_TOKEN env vars, or falls back to ~/.jira.d/config.yml.
"""
import argparse
import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import datetime

JIRA_BASE_URL = "https://homewardhealth.atlassian.net"
BROWSE_URL = f"{JIRA_BASE_URL}/browse"


# ---------------------------------------------------------------------------
# Jira API
# ---------------------------------------------------------------------------

def get_credentials():
    user = os.environ.get("JIRA_USER", "")
    token = os.environ.get("JIRA_API_TOKEN", "")
    if user and token:
        return user, token

    config_path = os.path.expanduser("~/.jira.d/config.yml")
    if os.path.exists(config_path):
        with open(config_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("user:"):
                    user = line.split(":", 1)[1].strip()
        if user and not token:
            try:
                result = subprocess.run(
                    ["security", "find-generic-password", "-s", "jira", "-a", user, "-w"],
                    capture_output=True, text=True, timeout=5,
                )
                if result.returncode == 0:
                    token = result.stdout.strip()
            except Exception:
                pass

    if not user or not token:
        print("ERROR: Set JIRA_USER and JIRA_API_TOKEN env vars.", file=sys.stderr)
        sys.exit(1)
    return user, token


def fetch_done_tickets(project: str, days: int) -> list[dict]:
    user, token = get_credentials()
    jql = f"project = {project} AND status = Done AND statusCategoryChangedDate >= -{days}d ORDER BY updated DESC"
    params = urllib.parse.urlencode({
        "jql": jql,
        "maxResults": 100,
        "fields": "summary,status,assignee,labels,description,updated,created,issuetype,priority,resolution,comment",
    })
    url = f"{JIRA_BASE_URL}/rest/api/3/search/jql?{params}"

    import base64
    auth = base64.b64encode(f"{user}:{token}".encode()).decode()
    req = urllib.request.Request(url, headers={
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/json",
    })

    all_issues = []
    while url:
        req = urllib.request.Request(url, headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json",
        })
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
        all_issues.extend(data.get("issues", []))
        if data.get("isLast", True):
            break
        start_at = len(all_issues)
        url = f"{JIRA_BASE_URL}/rest/api/3/search/jql?{params}&startAt={start_at}"

    return all_issues


# ---------------------------------------------------------------------------
# ADF → Markdown
# ---------------------------------------------------------------------------

def adf_to_md(node, depth=0):
    if node is None:
        return ""

    ntype = node.get("type", "")
    content = node.get("content", [])
    attrs = node.get("attrs", {})

    if ntype == "doc":
        return "\n".join(adf_to_md(c, depth) for c in content).strip()

    if ntype == "paragraph":
        if not content:
            return ""
        return "".join(adf_to_md(c, depth) for c in content) + "\n"

    if ntype == "text":
        text = node.get("text", "")
        for mark in node.get("marks", []):
            mt = mark.get("type", "")
            if mt == "strong":
                text = f"**{text}**"
            elif mt == "em":
                text = f"*{text}*"
            elif mt == "code":
                text = f"`{text}`"
            elif mt == "link":
                href = mark.get("attrs", {}).get("href", "")
                text = f"[{text}]({href})"
            elif mt == "strike":
                text = f"~~{text}~~"
        return text

    if ntype == "heading":
        level = attrs.get("level", 1)
        text = "".join(adf_to_md(c, depth) for c in content)
        return f"{'#' * level} {text}\n"

    if ntype in ("bulletList", "orderedList"):
        return "\n".join(adf_to_md(c, depth) for c in content) + "\n"

    if ntype == "listItem":
        text = "".join(adf_to_md(c, depth + 1) for c in content).strip()
        return f"{'  ' * depth}- {text}"

    if ntype == "taskList":
        return "\n".join(adf_to_md(c, depth) for c in content) + "\n"

    if ntype == "taskItem":
        check = "[x]" if attrs.get("state") == "DONE" else "[ ]"
        text = "".join(adf_to_md(c, depth + 1) for c in content).strip()
        return f"{'  ' * depth}- {check} {text}"

    if ntype == "codeBlock":
        lang = attrs.get("language", "")
        text = "".join(adf_to_md(c, depth) for c in content)
        return f"```{lang}\n{text}\n```\n"

    if ntype == "blockquote":
        text = "".join(adf_to_md(c, depth) for c in content).strip()
        return "\n".join(f"> {line}" for line in text.split("\n")) + "\n"

    if ntype == "rule":
        return "---\n"

    if ntype == "hardBreak":
        return "\n"

    if ntype == "inlineCard":
        url = attrs.get("url", "")
        return f"[{url}]({url})" if url else ""

    if ntype in ("mediaGroup", "mediaSingle"):
        return "".join(adf_to_md(c, depth) for c in content)

    if ntype == "media":
        return f"*(attachment: {attrs.get('id', 'media')})*"

    if ntype == "table":
        rows = []
        for i, c in enumerate(content):
            row = adf_to_md(c, depth)
            rows.append(row)
            if i == 0:
                cols = len(c.get("content", []))
                rows.append("| " + " | ".join(["---"] * cols) + " |")
        return "\n".join(rows) + "\n"

    if ntype == "tableRow":
        cells = [adf_to_md(c, depth) for c in content]
        return "| " + " | ".join(cells) + " |"

    if ntype in ("tableCell", "tableHeader"):
        return "".join(adf_to_md(c, depth) for c in content).strip()

    if ntype == "mention":
        return f"@{attrs.get('text', attrs.get('id', 'user'))}"

    if ntype == "emoji":
        return attrs.get("text", attrs.get("shortName", ""))

    if ntype == "panel":
        text = "".join(adf_to_md(c, depth) for c in content).strip()
        panel_type = attrs.get("panelType", "info")
        return f"> **{panel_type.upper()}:** {text}\n"

    if content:
        return "".join(adf_to_md(c, depth) for c in content)
    return ""


# ---------------------------------------------------------------------------
# Markdown generation
# ---------------------------------------------------------------------------

def format_date(iso_str):
    if not iso_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return iso_str


def comments_to_md(comments_data):
    if not comments_data:
        return ""
    comments = comments_data.get("comments", [])
    if not comments:
        return ""
    lines = ["\n## Comments\n"]
    for c in comments:
        author = c.get("author", {}).get("displayName", "Unknown")
        created = format_date(c.get("created", ""))
        body = adf_to_md(c.get("body", {}))
        lines.append(f"**{author}** ({created}):\n{body}\n")
    return "\n".join(lines)


def ticket_to_md(issue):
    key = issue["key"]
    f = issue["fields"]

    summary = f.get("summary", "No summary")
    status = (f.get("status") or {}).get("name", "Unknown")
    assignee = (f.get("assignee") or {}).get("displayName", "Unassigned")
    issue_type = (f.get("issuetype") or {}).get("name", "Unknown")
    priority = (f.get("priority") or {}).get("name", "None")
    resolution = (f.get("resolution") or {}).get("name", "None")
    labels = ", ".join(f.get("labels", [])) or "None"
    created = format_date(f.get("created"))
    updated = format_date(f.get("updated"))
    link = f"{BROWSE_URL}/{key}"

    desc_adf = f.get("description")
    description = adf_to_md(desc_adf) if desc_adf else "*No description provided.*"
    comments = comments_to_md(f.get("comment"))

    return f"""# {key}: {summary}

| Field | Value |
|-------|-------|
| **Key** | [{key}]({link}) |
| **Type** | {issue_type} |
| **Status** | {status} |
| **Resolution** | {resolution} |
| **Priority** | {priority} |
| **Assignee** | {assignee} |
| **Labels** | {labels} |
| **Created** | {created} |
| **Updated** | {updated} |

## Description

{description}
{comments}
"""


def write_summary(issues, output_dir, project, days):
    today = datetime.now().strftime("%Y-%m-%d")
    lines = [
        f"# {project} Weekly Update — Completed Tickets",
        "",
        f"**Period:** {today} (past {days} days)",
        f"**Total tickets completed:** {len(issues)}",
        "",
        "| Ticket | Summary | Assignee | Type |",
        "|--------|---------|----------|------|",
    ]
    for issue in issues:
        key = issue["key"]
        f = issue["fields"]
        summary = f.get("summary", "")
        assignee = (f.get("assignee") or {}).get("displayName", "Unassigned")
        itype = (f.get("issuetype") or {}).get("name", "")
        lines.append(f"| [{key}]({BROWSE_URL}/{key}) | {summary} | {assignee} | {itype} |")
    lines += ["", "---", "", "*Individual ticket details are in separate `jira-{project}-*.md` files in this directory.*", ""]

    path = os.path.join(output_dir, f"weekly-summary-{today}.md")
    with open(path, "w") as fp:
        fp.write("\n".join(lines))
    return path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate weekly Jira summary Markdown files.")
    parser.add_argument("--project", default="GENAI", help="Jira project key (default: GENAI)")
    parser.add_argument("--output-dir", default="homeward/projects/ai-planning/weekly_updates",
                        help="Output directory for Markdown files")
    parser.add_argument("--days", type=int, default=7, help="Lookback window in days (default: 7)")
    args = parser.parse_args()

    print(f"Fetching {args.project} tickets completed in the last {args.days} days...")
    issues = fetch_done_tickets(args.project, args.days)

    if not issues:
        print("No completed tickets found for the given period.")
        sys.exit(0)

    os.makedirs(args.output_dir, exist_ok=True)

    for issue in issues:
        key = issue["key"]
        md = ticket_to_md(issue)
        path = os.path.join(args.output_dir, f"jira-{key}.md")
        with open(path, "w") as fp:
            fp.write(md)
        print(f"  {key}: {issue['fields'].get('summary', '')}")

    summary_path = write_summary(issues, args.output_dir, args.project, args.days)
    print(f"\n{len(issues)} ticket files + summary written to {args.output_dir}")
    print(f"Summary: {summary_path}")


if __name__ == "__main__":
    main()
