---
name: reading-confluence-pages
description: >
  Use when the user shares a Confluence URL, asks to read a Confluence page,
  search Confluence, or look up internal documentation on Confluence.
metadata:
  depends-on: "atlassian-mcp-setup"
---

# Reading Confluence Pages

**REQUIRED:** Use atlassian-mcp-setup if the Atlassian MCP is not yet authenticated.

## MCP Server

- Server: `plugin-atlassian-atlassian`
- Cloud ID: `homewardhealth.atlassian.net`

## Reading a Page by URL

Extract the numeric page ID from the URL path, then call `getConfluencePage`.

| URL pattern | Page ID |
|---|---|
| `/wiki/spaces/SD/pages/421232653/Page+Title` | `421232653` |
| `/wiki/x/Fc1bBw` | `Fc1bBw` (tiny link ID) |

```json
{
  "cloudId": "homewardhealth.atlassian.net",
  "pageId": "<extracted-id>",
  "contentFormat": "markdown"
}
```

Always use `contentFormat: "markdown"` for readable output.

## Searching for Pages

Use `searchConfluenceUsingCql` with CQL syntax:

```json
{
  "cloudId": "homewardhealth.atlassian.net",
  "cql": "title ~ \"search terms\" AND type = page",
  "limit": 10
}
```

Common CQL patterns:
- Title search: `title ~ "AWS Access"`
- Space filter: `space = \"SD\" AND title ~ \"deploy\"`
- Recent: `type = page ORDER BY lastModified DESC`
- Label: `label = \"runbook\" AND type = page`

## Browsing Spaces

Use `getConfluenceSpaces` to list available spaces, or `getPagesInConfluenceSpace` to list pages within a space.

## Auth Errors

If tools return auth errors, call `mcp_auth` on `plugin-atlassian-atlassian` to re-authenticate, then retry.
