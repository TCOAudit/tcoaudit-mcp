# tcoaudit-mcp



[![TCOAudit/tcoaudit-mcp MCP server](https://glama.ai/mcp/servers/TCOAudit/tcoaudit-mcp/badges/score.svg)](https://glama.ai/mcp/servers/TCOAudit/tcoaudit-mcp)

Zero-dependency Python 3 Model Context Protocol (MCP) server for 36-month B2B SaaS Total Cost of Ownership modeling and website AI-search readiness checks. Built with the Python standard library only.

> **Disclosure:** Maintained by [TCO Audit](https://tcoaudit.com). Optional provisioning links routed through `tcoaudit.com/go/*` may earn a partner commission at no extra cost to you.

## Why Standard Library Only

MCP servers that pull in heavy package trees break when a local `uv`, `pip`, or virtualenv setup drifts. `server.py` implements the MCP stdio JSON-RPC 2.0 handshake (`initialize`, `tools/list`, `tools/call`, `ping`) directly on Python 3 stdlib. Clone it, point your client at `server.py`, and it runs.

## Requirements

- Python 3.10 or newer
- No external dependencies

## Tools

### `calculate_saas_tco`

Models 12- and 36-month costs across Zapier, Make.com, n8n Cloud, Railway 1-Click n8n clusters, legacy CRMs, Brevo, and Systeme.io.

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :---: | :--- |
| `monthly_tasks` | integer | Yes | — | Monthly automation steps/tasks (e.g., `50000`) |
| `contacts` | integer | Yes | — | Active CRM or email contacts (e.g., `25000`) |
| `steps_per_workflow` | integer | No | `5` | Average steps per workflow execution |
| `emails_per_contact` | integer | No | `4` | Monthly emails sent per contact |

### `check_url_geo_readiness`

Fetches a public URL and scores technical AI-search readiness out of 100 based on origin TTFB, canonical link tag, `application/ld+json` structured data, and `/llms.txt` availability.

| Parameter | Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `url` | string | Yes | Public domain or `https://` URL to inspect (blocks `localhost` and private loopback hosts) |

## Installation & Client Configuration

Clone the repository and note the absolute path to `server.py`:

```bash
git clone https://github.com/TCOAudit/tcoaudit-mcp.git
cd tcoaudit-mcp
```

Add the server to your MCP client config (`claude_desktop_config.json`, `.cursor/mcp.json`, Windsurf, Cline, or Antigravity):

```json
{
  "mcpServers": {
    "tcoaudit": {
      "command": "python3",
      "args": ["/ABSOLUTE/PATH/TO/tcoaudit-mcp/server.py"]
    }
  }
}
```

## Verify Locally

Send an `initialize` and `tools/list` request over stdio:

```bash
printf '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}\n{"jsonrpc":"2.0","id":2,"method":"tools/list"}\n' | python3 server.py
```

Both responses return valid JSON-RPC 2.0 payloads with `tcoaudit-mcp` and the two registered tools.

## Web Calculators

For interactive charts, scenario exports, and full methodology breakdowns, use the browser suite at [tcoaudit.com](https://tcoaudit.com):

- [SaaS & Automation 36-Month TCO Calculator](https://tcoaudit.com/tco-calculator)
- [B2B Cross-Border FX & Wire TCO Calculator](https://tcoaudit.com/fx-tco-calculator)
- [SEO & AI-Search (`/llms.txt`) Readiness Grader](https://tcoaudit.com/seo-ai-grader)
- [Cold Outbound Stack & Inbox Sizer](https://tcoaudit.com/outbound-stack-builder)

## License

MIT — see [LICENSE](./LICENSE).
