# CLAUDE.md — Securing the Agentic Stack

Repo context for Claude Code. Read this fully before authoring or editing content.

---

## What this repo is

An interactive Docker **labspace** for a 90-minute conference workshop at
WeAreDevelopers: *Securing the Agentic Stack — Docker Hardened Images and Supply Chain
Security*, by Ajeet Raina.

A labspace pairs markdown instructions (left panel) with a live VS Code IDE and
terminal (right panel), all inside Docker. Learners run commands directly from the
browser.

- **Workspace type:** `sdlc` (Gitea + registry + k3s + Traefik) — Lab 3 needs CI
- **Workspace image:** `dockersamples/labspace-workspace-node`
- **Sample app:** `catalog-service-node` (Docker Samples Product Catalog — Node.js + PostgreSQL)

---

## THE RULE THAT BREAKS EVERYTHING IF YOU GET IT WRONG

**`project/` in this repo IS the workspace root.**

`project/Dockerfile` here is mounted at `/home/coder/project/Dockerfile` in the
workspace, and the terminal's working directory is already `/home/coder/project/`.

| Never write | Write instead |
|-------------|---------------|
| `cd project` | *(nothing — you are already there)* |
| `project/Dockerfile` | `Dockerfile` |
| `ls project/` | `ls` |
| `save-as=project/compose.yaml` | `save-as=compose.yaml` |
| `:fileLink[x]{path="project/src/index.js"}` | `:fileLink[x]{path="src/index.js"}` |
| `git clone https://github.com/dockersamples/catalog-service-node` | *(nothing — the app is already in the workspace)* |

There is **no clone step** in this workshop. The app ships in `project/`. Any
instruction telling a learner to clone or `cd` into a subdirectory is a bug.

---

## Markdown conventions

### Fence modifiers

Every block gets a Copy button. `bash`, `shell`, `console` also get a Run button.

| Modifier | Effect |
|----------|--------|
| `no-run-button` | Show syntax without a Run button |
| `no-copy-button` | For expected output |
| `save-as=path` | Adds a Save button writing to that path (workspace-relative) |
| `terminal-id=name` | Run in a named terminal, creating it if needed |

Use the correct language tag. A Dockerfile is ```` ```dockerfile ````, never
```` ```yaml ````.

**Terminal discipline for this workshop:**

- `terminal-id=main` — setup, logins, general commands
- `terminal-id=build` — all `docker build` and `docker scout` commands
- `terminal-id=app` — long-running app processes

Each named terminal keeps its own working directory. All of them start at the
workspace root and should stay there.

### Directives

```markdown
::variableDefinition[org]{prompt="What is your Docker Organization?"}
::variableSetButton[Use the free tier (dhi.io)]{variables="tier=free,dhiPrefix=dhi.io/"}
:::conditionalDisplay{variable="tier" requiredValue="free"} ... :::
:fileLink[Dockerfile]{path="Dockerfile" line=8}
::tabLink[Open the app]{href="http://localhost:3050" id="app"}
```

Reference variables anywhere as `$$org$$`, `$$dhiPrefix$$`. Define before use.

### Style

- **Second person.** "You build the image", never "we build" / "let's build" / "our image".
- **Numbered steps** for sequential actions, with code blocks indented 4 spaces so
  they nest inside the list item.
- **Name the file and the intent** in the step text: "Create a file named `Dockerfile`
  with the following contents:", not "Create the file:".
- **Hands-on early.** No wall of text before the first command.
- Emojis sparingly — headings and key moments only.
- GitHub alerts (`> [!NOTE]`, `> [!WARNING]`) for callouts.

---

## Workshop-specific facts

### The DHI tier variables

Learners choose free or paid tier in Setup. Every DHI reference must use
`$$dhiPrefix$$`, never a hardcoded registry:

- Free tier → `dhi.io/`
- Paid tier → `$$org$$/dhi-`

So: `$$dhiPrefix$$node:24-debian13`, never `dhi.io/node:24-debian13`.

All Scout commands take `--org $$org$$`.

### DHI variants

| Variant | Tag | Use |
|---------|-----|-----|
| Dev | `$$dhiPrefix$$node:24-debian13-dev` | Build stage — has shell and npm |
| Runtime | `$$dhiPrefix$$node:24-debian13` | Production — distroless, no shell |

Because the runtime variant has no shell, the DHI Dockerfile **must** be multi-stage.

### SDLC environment (already provisioned — do not build it)

| Service | URL | Credentials |
|---------|-----|-------------|
| Gitea | `http://git.dockerlabs.xyz` | `moby` / `moby1234` |
| Registry | `http://registry.dockerlabs.xyz` | none |

**Project files are auto-committed to `moby/demo-app` at startup, and any
`.gitea/workflows/` in `project/` run automatically on that push.** Lab 3 does not
need to create a repo or configure a remote.

CI secrets auto-provisioned in `moby/demo-app`: `DOCKER_REGISTRY`, `DOCKER_USERNAME`,
`DOCKER_PASSWORD`, `DOCKERHUB_USERNAME`, `DOCKERHUB_PASSWORD`, `KUBECONFIG`.
Cosign signing needs `COSIGN_PRIVATE_KEY` and `COSIGN_PASSWORD` added by the learner.

### Signing

Use **cosign** throughout. Not Notation, not `docker trust`. The deck says cosign and
the prerequisites install cosign.

### Never use `PORT`

The workspace container owns the `PORT` environment variable. The catalog app must
hard-code its port or use `APP_PORT`.

---

## The story

One application, progressively hardened. Every lab operates on the same Product
Catalog service. Learners carry one artifact through the whole session.

### The three questions — the spine

Introduce in the Introduction, call back after every lab:

1. **What is in it?** → SBOM
2. **Where did it come from?** → SLSA provenance
3. **Can I verify that claim?** → signatures

And a fourth, once you have the first three: *which of these actually affects me?* → VEX

### Section arc

| # | Section | Format | Time |
|---|---------|--------|------|
| 01 | Introduction | read | 3 min |
| 02 | Setup | pre-work | — |
| 00 | **Demo #0 — an agent builds it** | recorded demo | 5 min |
| 03 | Lab 1 — SBOM · VEX · SLSA | hands-on | 16 min |
| 04 | Lab 2 — Migrate to DHI | hands-on | 16 min |
| 05 | Lab 3 — CI policy gate + signing | demo | 10 min |
| 06 | Lab 4 — MCP server on DHI | hands-on | 14 min |
| 07 | Conclusion + agent callback | read | 5 min |

**Concepts precede the DHI reveal.** Learners must be able to measure an image before
the numbers change, or the payoff is meaningless. Do not reorder these.

**Lab 2 is the pivot.** It is where three labs of instrumentation pay off. It must be
hands-on and it must re-run the Lab 1 measurements so learners see every number move.

### Demo #0 — the agent frames everything

The baseline image is **genuinely produced by an AI agent**, recorded in advance. Not
staged with a patch file. The narrative:

> An agent read the project, chose a base image nobody approved, resolved several
> hundred packages nobody reviewed, wrote a Dockerfile, and built successfully.
> Nothing failed. Nothing warned. You cannot answer any of the three questions about
> the result.

**The demo must not depend on the agent doing something stupid.** If it writes a good
multi-stage Dockerfile, that is a better demo — the findings live in the dependency
tree regardless, and question 3 still has no answer.

### Lab 4 must use the catalog

The MCP server exposes **the same PostgreSQL the catalog API uses** — tools like
`list_products`, `search_products`, `get_product`. A generic CVE-lookup server with
stubbed responses breaks the running example and undercuts the session's own argument
about verifying what your tools actually do.

### The callback

The Conclusion re-runs Demo #0's prompt with guardrails — DHI base pinned in the
agent's instructions, policy gate live — and the pipeline goes green. Same agent, same
prompt, different rails.

---

## Quality checklist

Before declaring any section done:

- [ ] No instruction says `cd project`, `git clone`, or uses a `project/` path prefix
- [ ] Every `save-as` path is workspace-relative and does not start with `/`
- [ ] Every DHI reference uses `$$dhiPrefix$$`; every Scout command has `--org $$org$$`
- [ ] Variables are defined before first use
- [ ] `contentPath` values in `labspace.yaml` exactly match filenames on disk
- [ ] Dockerfiles are fenced ```` ```dockerfile ````, YAML as ```` ```yaml ````
- [ ] Second person throughout — no "we", "us", "let's", "our"
- [ ] Sequential actions use numbered lists with 4-space-indented code blocks
- [ ] Every section has at least one Run, Save, or variable interaction
- [ ] The first section verifies the environment works
- [ ] Every lab ends with a callback to the three questions
- [ ] No `PORT` environment variable anywhere

---

## Known facts to verify before the workshop, not to invent

Do not fabricate figures. These need confirming against a live run:

- CVE counts for the baseline and DHI images
- Image size deltas
- The current DHI tag for `node` and `python`
- Whether a hardened MCP image exists for the comparison in Lab 4
- Whether `docker mcp gateway run --verify-signatures` works in this runtime

Where a number is needed and unverified, write `<!-- VERIFY: ... -->` inline rather
than guessing.
