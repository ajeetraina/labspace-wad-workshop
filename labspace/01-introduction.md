# Introduction

👋 Welcome to **Securing the Agentic Stack: Docker Hardened Images & Supply Chain Security**!

This workshop walks you through supply chain security fundamentals and applies
them to real workloads — both a traditional Node.js service and a Python MCP server
that an AI agent calls at runtime.

---

## Why supply chain security matters now

> *Especially when agents are doing the pulling.*

Agentic AI systems pull dependencies, invoke tools, and build environments
**autonomously** — without a human reviewing each step. One compromised base image
or MCP server can give an attacker access to production credentials, filesystems,
and external APIs with no human in the loop.

> *"The better the agent, the bigger the blast radius."*

### Agents expand your attack surface, automatically

| Traditional workflow | Agentic workflow |
|----------------------|------------------|
| Developer pulls base image — manually, with intent | Agent pulls base image — **autonomously** |
| Developer installs dependencies — reviewed in a PR | Agent installs packages — **no human review** |
| CI pipeline runs — with human-authored config | Agent invokes external tools — **with real credentials** |
| | Agent modifies the Dockerfile — **mid-pipeline** |

---

## Three problems every security team knows

| Integrity | Excessive attack surface | Operational overhead |
|-----------|--------------------------|----------------------|
| How do you know every component is exactly what it claims to be and has not been tampered with in transit? | General-purpose base images ship 500+ packages, most unused by your app. Every package is a potential CVE. | Security teams flooded with CVEs. Developers spend more time patching than building. Real work grinds to a halt. |

---

## The security gap is already here

**Docker State of Agentic AI Report — 800+ developers & tech leaders:**

| Stat | Figure |
|------|--------|
| Already have AI agents in production | **60%** |
| Cite security as the #1 challenge scaling agentic AI | **40%** |
| Know MCP but can't deploy it securely at scale | **85%** |
| Use containers for agent development or production | **94%** |
| Call agentic AI a strategic priority | 94% |
| Can't ensure the tools their agents use are secure | 45% |

*Source: Docker State of Agentic AI Report · docker.com/resources/the-state-of-agentic-ai-white-paper*

And the broader software supply chain is under the same pressure:

| Stat | Figure |
|------|--------|
| Applications that include open source components | **96%** |
| Share of a typical application's code that is open source | **70–90%** |
| New malicious packages identified in 2025 alone | **454,648** |
| Open-source malware packages logged since 2019 | **123,219** |

*Source: The State of Software Supply Chain Report 2026 by Sonatype*

---

## The "software supply chain" in practice

- Software is built from multiple parts, dependencies, and open source components.
- All software contains vulnerabilities — both known and unknown.
- Software development involves multiple developers, teams, and systems.
- Components are created by contributors both inside and outside your organization.
- Attackers target components with vulnerabilities to gain access and insert
  malicious code into an organization's software.

Given all that, **every company needs to:**

1. **Know what software they're running.**
2. **Know what risks that software has.**
3. **Fix those risks quickly.**

Every stage of the chain — from **Producer → Source → Build → Package → Consumer** —
is a place an artifact can be compromised, manipulated, tampered with, or served
stale. The questions you need answerable at each hop:

| Producer | Source | Build | Dependencies | Package | Consumer |
|----------|--------|-------|--------------|---------|----------|
| Who? | Compromised? | Tampered? | Genuine? | Altered? | Old? |

*Adapted from slsa.dev/spec/v1.0/threats-overview*

---

## The three standards you need to know

Three attestations make those questions answerable:

| Standard | The question it answers | What it solves |
|----------|------------------------|----------------|
| **SBOM** | What's in this software artifact? | Know every component in every image |
| **VEX** | Which CVEs actually affect me? | Cut CVE noise to the reachable few |
| **SLSA** | Where did it come from — can I verify it? | Prove provenance wasn't tampered with |

Docker Hardened Images ship all three, plus a digital signature, out of the box.
You'll generate, inspect, and verify each of them in the labs.

---

## What you will do in this workshop

| Lab | Task | Time |
|-----|------|------|
| **Lab 1** | Migrate `catalog-service-node` from `node:20` to DHI — watch the CVE count collapse | ~20 min |
| **Lab 2** | Generate an SBOM, inspect VEX + SLSA attestations, verify the digital signature | ~20 min |
| **Lab 3** | Wire Docker Scout + Cosign into a Gitea Actions pipeline — watch a build fail, then pass | ~45 min |
| **Lab 4** | Build a Python MCP server on `hardened-python`, run it hardened, verify it | ~30 min |

> **Key numbers you will reproduce:**
> - `node:20` → ~140+ CVEs, 700+ packages
> - DHI node runtime → **0 critical/high CVEs, ~12 packages**
> - Image size: **up to 95% smaller**

Let's get started. 🚀
