# Lab 4 — Securing the Agentic Stack: MCP Server on DHI

> **Goal:** Build a Python MCP server on a hardened base, run it with full runtime
> hardening, verify its attestations, and connect an MCP client.

## The better the agent, the bigger the blast radius

MCP servers execute code, call APIs, and access filesystems autonomously — often
with real credentials. One compromised MCP server can:

- **Rug pull** — the server changes behavior after you approved it
- **Tool poisoning** — malicious prompts invisible to users, clear to the AI
- **Credential exfiltration** — hardcoded env vars are an easy target

### Container isolation = blast radius boundary

Run MCP servers in containers. Even a **fully compromised** MCP server cannot reach
beyond its container boundary — no host filesystem, no sibling services, no
credentials it was not explicitly given.

> *"Containers brought order to app deployment. They can do the same for agentic AI."*

### What you get for free with an MCP server on DHI

- 📦 An **SBOM** of every package in your MCP server
- ✍️ A **digital signature** — verify before invoking
- 🧱 **Container isolation** — blast radius bounded
- 🚫 **No shell, no curl** — reduced attack vectors

Running the server with `read_only + cap_drop: ALL + no-new-privileges` bounds the
blast radius: even fully compromised, it cannot write files, escalate privileges,
or reach outside its declared network scope.

---

## Step 1 — Review the sample MCP server

Open :fileLink[Dockerfile]{path="lab/04-mcp/Dockerfile"}.

```yaml save-as=lab/04-mcp/Dockerfile
###########################################################
# Stage: build
###########################################################
FROM $$dhiPrefix$$python:3.12-slim-dev AS build

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --target /app/deps

###########################################################
# Stage: final — distroless runtime
###########################################################
FROM $$dhiPrefix$$python:3.12-slim AS final

ENV PYTHONPATH=/app/deps
WORKDIR /app
COPY --from=build /app/deps ./deps
COPY ./src ./src

# No shell. No curl. No wget. Only what the MCP server needs.
EXPOSE 8080
CMD ["python", "src/mcp_server.py"]
```

```diff no-copy-button
- FROM python:3.12-slim
+ FROM $$dhiPrefix$$python:3.12-slim-dev AS build   # build stage
+ FROM $$dhiPrefix$$python:3.12-slim AS final        # distroless runtime
```

## Step 2 — Build with attestations

```bash terminal-id=build
cd lab/04-mcp
docker buildx build \
  --sbom=true \
  --provenance=mode=max \
  -t $$org$$/mcp-server:v1 \
  --push \
  .
```

## Step 3 — Scan the MCP server image

```bash terminal-id=build
docker scout quickview $$org$$/mcp-server:v1 --org $$org$$
```

```none no-copy-button
Target     │  $$org$$/mcp-server:v1  │    0C     0H     0M     0L

Policy status  SUCCEEDED  (7/7 policies met)
```

## Step 4 — Sign the MCP server image

Reuse the Cosign key pair from Lab 2 (or run `cosign generate-key-pair` again):

```bash terminal-id=build
cosign sign --key cosign.key $$org$$/mcp-server:v1 --yes
cosign verify --key cosign.pub $$org$$/mcp-server:v1
```

## Step 5 — Run with runtime hardening flags

Open :fileLink[docker-compose.yml]{path="lab/04-mcp/docker-compose.yml"}.

```yaml save-as=lab/04-mcp/docker-compose.yml
services:
  mcp-server:
    image: $$org$$/mcp-server:v1
    ports:
      - "8080:8080"
    read_only: true
    cap_drop:
      - ALL
    security_opt:
      - no-new-privileges:true
    tmpfs:
      - /tmp:noexec,nosuid,size=32m
    environment:
      MCP_TRANSPORT: sse
      MCP_HOST: "0.0.0.0"
      MCP_PORT: "8080"
```

```bash terminal-id=build
docker compose up -d
docker ps
```

## Step 6 — Verify the runtime hardening

```bash terminal-id=build
docker inspect lab04-mcp-server-1 \
  --format 'ReadOnly={{.HostConfig.ReadonlyRootfs}} CapDrop={{.HostConfig.CapDrop}}'
```

```none no-copy-button
ReadOnly=true CapDrop=[ALL]
```

Attempt a write — it must fail:

```bash terminal-id=build
docker exec lab04-mcp-server-1 sh -c "echo pwned > /app/test.txt" 2>&1 || echo "Write blocked"
```

```none no-copy-button
Write blocked
```

## Step 7 — Verify the SBOM

```bash terminal-id=build
docker scout attest list $$org$$/mcp-server:v1
docker scout sbom $$org$$/mcp-server:v1 --format list
```

Compare the package count to a standard Python image:

```bash terminal-id=build
docker scout cves python:3.12-slim --only-severity critical,high --org $$org$$
docker scout cves $$org$$/mcp-server:v1 --only-severity critical,high --org $$org$$
```

## Step 8 — Connect an MCP client (optional)

The server exposes SSE transport at `http://localhost:8080/sse`.

**Claude Desktop** — add to `claude_desktop_config.json`:
```json no-copy-button
{
  "mcpServers": {
    "workshop-mcp": {
      "url": "http://localhost:8080/sse"
    }
  }
}
```

**Docker MCP CLI:**
```bash terminal-id=main
docker mcp client connect workshop-mcp http://localhost:8080
```

## Step 9 — Clean up

```bash terminal-id=build
docker compose down
```

---

## Summary — what hardening buys you

| Control | Attacker capability without it | With it |
|---------|-------------------------------|---------|
| `read_only` | Drop payloads, modify app files | Cannot write anywhere |
| `cap_drop: ALL` | Change UIDs, raw sockets, chroot | No Linux privilege escalation |
| `no-new-privileges` | Gain privs via SUID binaries | SUID bits ignored |
| Distroless base | `curl` payloads, shell pivoting | No shell, no curl |
| Signed SBOM | Unknown dependencies | Full audit trail |

---

## The complete agentic supply chain

You have now built every link in this chain. **Every step is verifiable. Every
artifact is trusted.**

```text no-copy-button
 BASE               BUILD              POLICY            SIGN             REGISTRY          DEPLOY
 DHI Python/Node →  Docker Buildx  →   Scout Check  →    Cosign       →   Docker Hub    →  MCP Container
 0 CVEs · SLSA L3   SBOM+Provenance    No critical CVEs  OCI signature    Signed image     Verified · Isolated

                          Agent / MCP client  --invokes-->  Verified MCP server in a DHI container
```
