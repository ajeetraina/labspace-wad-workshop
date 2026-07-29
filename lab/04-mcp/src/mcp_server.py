"""
Sample MCP server for the Securing the Agentic Stack workshop.
Exposes two tools:
  - get_cve_info: fetch metadata about a CVE ID
  - check_image_security: check if an image meets security policy

Runs on SSE transport at http://0.0.0.0:8080
"""

import os
import json
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent

app = Server("workshop-mcp-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_cve_info",
            description="Return basic info about a CVE ID (severity, description).",
            inputSchema={
                "type": "object",
                "properties": {
                    "cve_id": {
                        "type": "string",
                        "description": "CVE identifier, e.g. CVE-2024-1234",
                    }
                },
                "required": ["cve_id"],
            },
        ),
        Tool(
            name="check_image_security",
            description="Check whether a container image meets security policy (zero critical CVEs, SBOM present, signed).",
            inputSchema={
                "type": "object",
                "properties": {
                    "image": {
                        "type": "string",
                        "description": "Container image reference, e.g. myorg/myapp:v1.0",
                    }
                },
                "required": ["image"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "get_cve_info":
        cve_id = arguments.get("cve_id", "")
        # In a real implementation this would call the NVD API
        result = {
            "id": cve_id,
            "note": "In production, this would query the NVD API or Docker Scout.",
            "advice": "Use `docker scout cves IMAGE` to check if this CVE affects your images.",
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    if name == "check_image_security":
        image = arguments.get("image", "")
        # In a real implementation this would call the Docker Scout API
        result = {
            "image": image,
            "note": "In production, this would call the Docker Scout API.",
            "advice": f"Run: docker scout quickview {image} --org YOUR_ORG",
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    raise ValueError(f"Unknown tool: {name}")


if __name__ == "__main__":
    import asyncio
    from starlette.applications import Starlette
    from starlette.routing import Route
    import uvicorn

    host = os.environ.get("MCP_HOST", "0.0.0.0")
    port = int(os.environ.get("MCP_PORT", "8080"))

    transport = SseServerTransport("/messages")

    async def handle_sse(request):
        async with transport.connect_sse(request.scope, request.receive, request._send) as streams:
            await app.run(streams[0], streams[1], app.create_initialization_options())

    async def health(request):
        from starlette.responses import JSONResponse
        return JSONResponse({"status": "ok", "server": "workshop-mcp-server"})

    starlette_app = Starlette(
        routes=[
            Route("/sse", endpoint=handle_sse),
            Route("/health", endpoint=health),
            Route("/messages", endpoint=transport.handle_post_message, methods=["POST"]),
        ]
    )

    print(f"MCP server listening on {host}:{port}")
    asyncio.run(uvicorn.serve(starlette_app, host=host, port=port))
