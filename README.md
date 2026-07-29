# Securing the Agentic Stack — Labspace

Workshop labspace for **Securing the Agentic Stack: Docker Hardened Images and Supply
Chain Security** (WeAreDevelopers), by Ajeet Raina.

An AI agent containerises a real application without supervision. You spend the next
ninety minutes finding out what it shipped, and turning it into something you can
prove things about.

## Run it

```bash
bash start-labspace.sh          # then open http://localhost:3030
bash start-labspace.sh down     # stop and clean up
```

Or, once published:

```bash
docker compose -f oci://ajeetraina/labspace-wad-workshop up
```

## Structure

```
.
├── labspace/                       # Section content (left panel)
│   ├── labspace.yaml
│   ├── 01-introduction.md
│   ├── 02-setup.md
│   ├── 03-demo-agent-builds-it.md  # Recorded agent demo
│   ├── 04-lab-sbom-vex-slsa.md     # Lab 1 — vocabulary
│   ├── 05-lab-dhi-migration.md     # Lab 2 — the pivot
│   ├── 06-lab-ci-policy.md         # Lab 3 — sign and gate
│   ├── 07-lab-mcp-dhi.md           # Lab 4 — agentic stack
│   └── 08-conclusion.md
├── project/                        # THE WORKSPACE ROOT (see below)
│   ├── docker-scout-policy.yaml
│   └── mcp/                        # Catalog MCP server
├── compose.yaml                    # SDLC base
├── compose.override.yaml
└── start-labspace.sh
```

> [!IMPORTANT]
> **`project/` is the workspace root.** Files here mount at `/home/coder/project/`,
> and the terminal opens there. Instructions must never say `cd project` or reference
> a `project/` path prefix. There is no clone step in this workshop.

## Before first boot

**1. Create the app fork.** `compose.override.yaml` sets `PROJECT_CLONE_URL` to
`https://github.com/ajeetraina/catalog-service-wad`, which does not exist yet. Create
it:

```bash
git clone https://github.com/dockersamples/catalog-service-node catalog-service-wad
cd catalog-service-wad
rm -rf demo/            # the patch-based vulnerable state is not used here
```

Then run the agent (see below), commit the Dockerfile it writes, and push the fork.

Also copy `project/mcp/` and `project/docker-scout-policy.yaml` into that fork, since
the clone populates the workspace.

**2. Record the agent building the baseline.** This produces both the opening demo and
the artifact every lab measures.

```bash
cd catalog-service-wad
rm Dockerfile
# start recording, then run your coding agent with exactly:
#
#   Containerise this Node.js application for production.
#   Add a Dockerfile and build the image as catalog-service:baseline.
#
# No other instructions. Let it finish. Do not correct it.
```

Then capture the numbers that go into section 03:

```bash
docker scout quickview catalog-service:baseline
docker scout policy catalog-service:baseline
npm ls --all --parseable 2>/dev/null | wc -l
docker images catalog-service:baseline
```

> If the agent writes a *good* Dockerfile, keep it. A competent multi-stage build makes
> the demo stronger — the vulnerabilities are in the dependency tree either way, and
> "can you prove where this came from" still has no answer.

**3. Fill in the VERIFY placeholders.**

```bash
grep -rn "VERIFY" labspace/
```

Each marks a number that must come from a real run rather than an estimate.

## Facilitator checklist

- [ ] App fork created, agent's Dockerfile committed, `PROJECT_CLONE_URL` correct
- [ ] Agent run recorded, under two minutes
- [ ] All `VERIFY` placeholders replaced with measured values
- [ ] DHI tags in Labs 2 and 4 confirmed against the current catalogue
- [ ] Both tier buttons tested — free (`dhi.io/`) and paid (`$$org$$/dhi-`)
- [ ] Gitea reachable, `moby` / `moby1234` works, pipeline runs green once
- [ ] `docker mcp gateway run --verify-signatures` confirmed, or Lab 4 step demoted to demo
- [ ] Lab 3 pipeline run recorded as a fallback — the Scout gate is a live cloud call
- [ ] Day 0 state does not collide with day X

## Timing

| Section | Format | Time |
|---------|--------|------|
| Introduction | read | 3 min |
| Setup | pre-work | — |
| An Agent Built This | demo | 5 min |
| Lab 1 — SBOM, VEX, SLSA | hands-on | 16 min |
| Lab 2 — Trusted base | hands-on | 16 min |
| Lab 3 — Sign and gate | demo | 10 min |
| Lab 4 — Agentic stack | hands-on | 14 min |
| Conclusion | read | 5 min |

**69 minutes**, leaving room for overrun and transitions inside the 90.

## Authoring

`CLAUDE.md` holds the conventions. Two slash commands are available:

- `/check-labspace` — audit every file against the conventions
- `/new-section` — author a new section consistently

## Licence

Apache-2.0
