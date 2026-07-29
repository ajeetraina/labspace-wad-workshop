# Securing the Agentic Stack — Workshop Lab Repo

Hands-on lab materials for the **Securing the Agentic Stack** workshop.

## Structure

```
labspace-agentic-security/
├── compose.yaml                     # Labspace runtime (Gitea-enabled variant)
├── compose.override.yaml
├── docker-scout-policy.yaml         # Scout build policies
├── .gitea/workflows/
│   └── secure-build.yaml            # Secure CI pipeline (Gitea Actions)
├── labspace/                        # Step-by-step lab guides
│   ├── labspace.yaml                # Labspace manifest
│   ├── 01-introduction.md
│   ├── 02-setup.md
│   ├── 03-lab-migrate-dhi.md        # Lab 1: Migrate to DHI
│   ├── 04-lab-sbom-attestations.md  # Lab 2: SBOM + signatures
│   ├── 05-lab-ci-policy.md          # Lab 3: Gitea Actions CI pipeline
│   ├── 06-lab-mcp-dhi.md            # Lab 4: MCP server on DHI
│   └── 07-conclusion.md
└── lab/
    ├── 01-migrate/Dockerfile        # Lab 1 starting point
    ├── 02-attest/Dockerfile         # Lab 2 starting point
    ├── 03-policy/Dockerfile         # Lab 3 — standard base (will fail)
    └── 04-mcp/
        ├── Dockerfile               # MCP server on DHI
        ├── docker-compose.yml       # Hardened runtime config
        ├── requirements.txt
        └── src/mcp_server.py        # Sample MCP server

```

## Prerequisites

- Docker Desktop 4.30+
- Docker Hub account (free) with Docker Scout enabled on your org
- `cosign` CLI installed (`brew install cosign`)

> Lab 3 runs its CI pipeline on a **self-hosted Gitea** bundled in the labspace
> (`git.dockerlabs.xyz`) with a local registry (`registry.dockerlabs.xyz`) — no
> GitHub account needed.

## Quick start

```bash
git clone https://github.com/ajeetraina/labspace-agentic-security
cd labspace-agentic-security
bash start-labspace.sh          # then open http://localhost:3030
```

Or run it manually:

```bash
docker login
docker scout config organization YOUR_ORG
```

The complete workshop is also hosted at **https://dockerworkshop.vercel.app/**.

## Facilitator smoke test (run before a live workshop)

Lab 3 depends on the bundled Gitea + runner + registry from the `:dev-sdlc`
runtime variant. Verify it once before presenting — a few values (notably the
seeded Gitea repo name) come from the runtime image, not this repo:

1. **Boot it:** `bash start-labspace.sh`, then open http://localhost:3030.
2. **Gitea is up:** open http://git.dockerlabs.xyz and log in as `moby` / `moby1234`.
3. **Registry is up:** `curl -s http://registry.dockerlabs.xyz/v2/_catalog` returns JSON.
4. **Confirm the seeded repo path:** in the workspace terminal run `git remote -v`.
   Lab 3's image tag uses `${{ github.repository }}`, so it auto-follows this
   path — but confirm it resolves to `moby/<repo>` as the lab text assumes.
5. **Pre-configured secrets exist:** in the Gitea repo → Settings → Actions →
   Secrets, confirm `DOCKER_REGISTRY`, `DOCKER_USERNAME`, `DOCKER_PASSWORD`.
6. **Scout gate needs cloud auth (not offline):** the Scout step is a real cloud
   call, so add `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`, and `DOCKER_SCOUT_ORG`
   as repo secrets, plus `COSIGN_PRIVATE_KEY` / `COSIGN_PASSWORD` for signing
   (see Lab 3, Step 2). Do a full push once to confirm the pipeline goes green.

> If the seeded repo name or secret names differ in your runtime image, adjust
> Lab 3's Step 1–2 text accordingly.

## Workshop deck

The companion slide deck is **"Securing the Agentic Stack: Docker Hardened Images
and Supply Chain Security"** by Ajeet Raina. The six-part agenda maps directly to
the labspace sections:

| Deck section | Labspace |
|--------------|----------|
| 01 · Why supply chain security matters now | Introduction |
| 02 · Building blocks (SBOM · VEX · SLSA) | Lab 2 |
| 03 · Standard image vs DHI | Lab 1 |
| 04 · Securing your CI pipeline | Lab 3 |
| 05 · Securing the agentic stack | Lab 4 |
| 06 · Wrap up | Conclusion |

## Source material

Adapted from [`ajeetraina/labspace-container-security`](https://github.com/ajeetraina/labspace-container-security)
which covers 8 container security best practices using `catalog-service-node`.

## Resources

- [Docker Hardened Images](https://docs.docker.com/dhi/)
- [Docker Scout](https://docs.docker.com/scout/)
- [MCP Catalog on Docker Hub](https://hub.docker.com/mcp)
- [SLSA framework](https://slsa.dev)
- [Cosign — image signing](https://docs.sigstore.dev/cosign/)
- [State of Agentic AI Report](https://docker.com/resources/the-state-of-agentic-ai-white-paper)
