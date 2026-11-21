#!/usr/bin/env python3
"""
============================================================================
tcoaudit-mcp — Zero-Dependency MCP Server (JSON-RPC 2.0 over stdio)
============================================================================
PURPOSE & ARCHITECTURE:
Exposes TCO Audit's deterministic 36-month SaaS TCO engine and URL readiness
heuristics directly inside AI coding & operations assistants (Claude Desktop,
Cursor, Windsurf, Cline, Antigravity) using ONLY the Python 3 standard library.

WHY ZERO EXTERNAL DEPENDENCIES:
Third-party MCP packages routinely fail to start when users lack matching
virtualenv/uv/pip setups. Implementing the official MCP stdio JSON-RPC 2.0
handshake (`initialize`, `tools/list`, `tools/call`) in pure stdlib guarantees
100% first-run reliability on macOS, Linux, and Windows.
============================================================================
"""

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

SERVER_INFO = {
    "name": "tcoaudit-mcp",
    "version": "1.0.0"
}

TOOLS = [
    {
        "name": "calculate_saas_tco",
        "description": "Calculate 12- and 36-month B2B SaaS Total Cost of Ownership comparing Zapier and legacy CRMs against n8n, Make, Railway self-hosting, Brevo, and Systeme.io.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "monthly_tasks": {"type": "integer", "description": "Monthly automation steps/tasks (e.g. 50000)"},
                "steps_per_workflow": {"type": "integer", "description": "Average steps per workflow run (default 5)"},
                "contacts": {"type": "integer", "description": "Active CRM/email contacts (e.g. 25000)"},
                "emails_per_contact": {"type": "integer", "description": "Monthly emails sent per contact (default 4)"}
            },
            "required": ["monthly_tasks", "contacts"]
        }
    },
    {
        "name": "check_url_geo_readiness",
        "description": "Inspect a public website URL for origin TTFB latency, canonical tag, JSON-LD schema, and /llms.txt AI answer-engine readiness.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Public website domain or https:// URL to inspect"}
            },
            "required": ["url"]
        }
    }
]


def run_tco_tool(args: dict) -> str:
    tasks = max(1000, int(args.get("monthly_tasks", 50000)))
    steps = max(1, int(args.get("steps_per_workflow", 5)))
    executions = (tasks + steps - 1) // steps
    contacts = max(500, int(args.get("contacts", 25000)))
    freq = max(1, int(args.get("emails_per_contact", 4)))
    emails = contacts * freq

    zapier = 49 if tasks <= 2000 else 103 if tasks <= 10000 else 299 if tasks <= 50000 else 489 if tasks <= 100000 else 739
    make = 11 if tasks <= 10000 else 34 if tasks <= 40000 else 105 if tasks <= 150000 else 199
    n8n_cloud = 24 if executions <= 2500 else 60 if executions <= 10000 else 145 if executions <= 50000 else 260
    railway = 16 if executions <= 25000 else 28 if executions <= 100000 else 45

    legacy_crm = 60 if contacts <= 2500 else 135 if contacts <= 10000 else 310 if contacts <= 25000 else 480
    brevo = 25 if emails <= 20000 else 55 if emails <= 60000 else 69 if emails <= 100000 else 199
    systeme = 0 if contacts <= 2000 else 17 if contacts <= 5000 else 47 if contacts <= 10000 else 97

    legacy_36m = (zapier + legacy_crm) * 36
    opt_36m = (min(make, n8n_cloud, railway) + min(brevo, systeme)) * 36
    saved = max(0, legacy_36m - opt_36m)

    return (
        f"TCO Audit 36-Month Model (https://tcoaudit.com/tco-calculator.html)\n"
        f"- Workload: {tasks:,} steps ({executions:,} full n8n runs) | {contacts:,} contacts ({emails:,} emails/mo)\n"
        f"- Legacy 36m Baseline: ${legacy_36m:,}\n"
        f"- Optimized 36m Stack: ${opt_36m:,} (Net 36m Savings: ${saved:,})\n"
        f"- Breakdown (Monthly): Zapier ${zapier} vs Make ${make} vs n8n Cloud ${n8n_cloud} vs Railway 1-Click ${railway} | "
        f"Legacy CRM ${legacy_crm} vs Brevo ${brevo} vs Systeme.io ${systeme}\n"
        f"- Provisioning (FTC Notice: partner links at $0 extra cost):\n"
        f"  * Railway 1-Click n8n Stack ($20 Credit): https://tcoaudit.com/go/cloud-deploy?src=mcp&asset=tco_tool\n"
        f"  * n8n Cloud: https://tcoaudit.com/go/workflow-cloud?src=mcp&asset=tco_tool\n"
        f"  * Make.com: https://tcoaudit.com/go/visual-flow?src=mcp&asset=tco_tool\n"
        f"  * Systeme.io ($0 Starter / $97 Unlimited): https://tcoaudit.com/go/funnel-engine?src=mcp&asset=tco_tool\n"
        f"  * Brevo Volume SMTP/CRM: https://tcoaudit.com/go/smtp-relay?src=mcp&asset=tco_tool"
    )


def run_geo_audit_tool(args: dict) -> str:
    raw = str(args.get("url", "")).strip()
    if not raw:
        return "Error: Provide a non-empty public URL."
    target = raw if raw.startswith(("http://", "https://")) else f"https://{raw}"
    parsed = urllib.parse.urlparse(target)
    host = (parsed.hostname or "").lower()
    if not host or "." not in host or host in {"localhost", "127.0.0.1", "0.0.0.0"}:
        return "Error: Only public internet domains are permitted."

    headers = {"User-Agent": "TCOAudit-MCP/1.0 (+https://tcoaudit.com)"}
    try:
        t0 = time.perf_counter()
        req = urllib.request.Request(target, headers=headers)
        with urllib.request.urlopen(req, timeout=8) as resp:
            body = resp.read(120000).decode("utf-8", errors="ignore")
        ttfb_ms = int((time.perf_counter() - t0) * 1000)
    except Exception as exc:
        return f"Unable to fetch {target}: {exc}"

    has_llms = False
    try:
        llms_req = urllib.request.Request(f"{parsed.scheme}://{parsed.netloc}/llms.txt", method="HEAD", headers=headers)
        with urllib.request.urlopen(llms_req, timeout=5) as lresp:
            has_llms = 200 <= lresp.status < 300
    except Exception:
        has_llms = False

    has_canonical = 'rel="canonical"' in body.lower() or "rel='canonical'" in body.lower()
    has_jsonld = "application/ld+json" in body.lower()
    score = 100 - (25 if ttfb_ms > 500 else 0) - (20 if not has_canonical else 0) - (25 if not has_jsonld else 0) - (30 if not has_llms else 0)

    return (
        f"SEO & AI-Readiness Report for {parsed.netloc}: {max(0, score)}/100\n"
        f"- Origin TTFB: {ttfb_ms}ms | Canonical: {has_canonical} | JSON-LD: {has_jsonld} | /llms.txt: {has_llms}\n"
        f"- Remediation Stack (FTC Notice: partner links via tcoaudit.com):\n"
        f"  * Deep Site Crawl & Keyword Gap Audit (Semrush Trial): https://tcoaudit.com/go/seoaudit?src=mcp&asset=geo_tool\n"
        f"  * Sub-200ms NVMe Cloud Hosting (Cloudways): https://tcoaudit.com/go/nvme-hosting?src=mcp&asset=geo_tool"
    )


def handle_rpc_request(msg: dict) -> dict | None:
    method = msg.get("method")
    msg_id = msg.get("id")

    # JSON-RPC notifications have no `id` and expect no response
    if msg_id is None:
        return None

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": SERVER_INFO
            }
        }

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"tools": TOOLS}
        }

    if method == "tools/call":
        params = msg.get("params") or {}
        name = params.get("name")
        arguments = params.get("arguments") or {}
        if name == "calculate_saas_tco":
            text = run_tco_tool(arguments)
        elif name == "check_url_geo_readiness":
            text = run_geo_audit_tool(arguments)
        else:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Unknown tool: {name}"}
            }
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "content": [{"type": "text", "text": text}],
                "isError": False
            }
        }

    if method == "ping":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {}}

    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {"code": -32601, "message": f"Method not found: {method}"}
    }


def main() -> None:
    for line in sys.stdin:
        stripped = line.strip()
        if not stripped:
            continue
        try:
            payload = json.loads(stripped)
            response = handle_rpc_request(payload)
            if response is not None:
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
        except json.JSONDecodeError:
            err = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
