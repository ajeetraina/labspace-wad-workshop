# Lab 4 — Securing the Agentic Stack

**14 minutes · hands-on**

Everything so far has been about an image *you* build and *a human* decides to deploy.

Now the catalog gets a second consumer, and the human leaves the loop entirely.

---

## Why an agent's tools are supply chain

An MCP server is an executable you hand tool-calling authority to. It gets
credentials, network reach, and often filesystem access. It is chosen from a
catalogue — sometimes by the agent itself — at run time.

Three failure modes worth naming:

| | |
|---|---|
| **Rug pull** | The server changes behaviour after you approved it |
| **Tool poisoning** | Instructions invisible to users, clear to the model |
| **Credential exfiltration** | Hardcoded environment variables are an easy target |

Every question you have asked in this workshop applies here. Almost nobody asks them.

---

## Look at the tool surface

The MCP server in this workspace exposes **the same PostgreSQL database the catalog
API uses**.

1. Open :fileLink[catalog_mcp.py]{path="mcp/src/catalog_mcp.py"}.

    Three tools: `list_products`, `search_products`, `get_product`.

2. Note what the process holds — a database connection string. That is the thing an
   attacker wants, and it is the thing you are about to hand to an agent.

---

## Build it on a hardened base

1. Create a file named `mcp/Dockerfile` with the following contents:

    ```dockerfile save-as=mcp/Dockerfile
    FROM $$dhiPrefix$$python:3.13

    WORKDIR /app
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    COPY src/ ./src/

    # No shell. No curl. No package manager.
    # Only what the server needs to answer a question about products.
    CMD ["python", "src/catalog_mcp.py"]
    ```

2. Build it:

    ```bash terminal-id=build
    docker build -t catalog-mcp:dhi ./mcp
    ```

---

## Harden the runtime too

A hardened image with a careless runtime configuration is half a job.

1. Create a file named `mcp/compose.yaml` with the following contents:

    ```yaml save-as=mcp/compose.yaml
    services:
      catalog-mcp:
        build: .
        image: catalog-mcp:dhi

        # Three lines that change what a compromised server can do next.
        read_only: true
        cap_drop: [ALL]
        security_opt: [no-new-privileges]

        environment:
          DATABASE_URL: postgres://postgres:postgres@postgres:5432/catalog
    ```

2. Start it:

    ```bash terminal-id=main
    docker compose -f mcp/compose.yaml up -d
    ```

3. Confirm the restrictions actually applied:

    ```bash terminal-id=build
    docker inspect catalog-mcp --format '{{.HostConfig.ReadonlyRootfs}} {{.HostConfig.CapDrop}}'
    ```

---

## Verify before you invoke

1. Check what you just built:

    ```bash terminal-id=build
    docker scout quickview catalog-mcp:dhi --org $$org$$
    ```

2. List its attestations:

    ```bash terminal-id=build
    docker scout attest list catalog-mcp:dhi
    ```

<!-- VERIFY: confirm a hardened MCP server image exists in the catalogue and add a
     comparison step here. Check Docker Hub -> Hardened Images before the workshop. -->

---

## Let the Gateway verify for you

Nobody verifies by hand on every invocation. The MCP Gateway performs provenance
verification on pull and run, checks for an SBOM, runs supply-chain checks, and mounts
secrets only into the target container.

```bash terminal-id=main
docker mcp gateway run --verify-signatures
```

Connect your MCP client, list the tools, and call `search_products`. Ask an agent, in
plain language, what is in the product catalog.

> [!NOTE]
> If the Gateway is not available in this environment, your facilitator will
> demonstrate this step. The rest of the lab stands on its own.

---

## Watch it refuse

Point the Gateway at an unsigned or tampered server image. It should decline to run it.

Same lesson as the broken signature in Lab 3, one layer up: **a check is only worth
something once you have seen it say no.**

---

## Checkpoint

- [ ] The catalog MCP server builds on a hardened base
- [ ] It runs read-only, with all capabilities dropped
- [ ] You have inspected its attestations
- [ ] You have seen verification reject something

## What you should be thinking

The catalog API and the catalog MCP server are the same kind of object: software you
did not write all of, pulled from a registry, running with credentials against your
data.

The only difference is that a human decided to deploy one, and an agent decides when to
invoke the other.

Which is why the answer is not a new category of tool. It is the same supply chain
controls — SBOM, VEX, provenance, signatures, policy — applied to a surface most teams
have not yet noticed is part of their supply chain.

Same three questions. Same answers. Different layer.

## Go deeper

1. Give the MCP server a read-only database role and confirm writes fail.
2. Add egress filtering so it can reach PostgreSQL and nothing else.
3. Run `catalog-mcp:dhi` through the Lab 3 policy gate.
