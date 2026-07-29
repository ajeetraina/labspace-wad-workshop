# Conclusion & Next Steps

🎉 You have completed all four labs. Here is what you just did:

---

## What you built

| Lab | What you proved |
|-----|-----------------|
| **Lab 1** | One FROM change eliminates 190+ CVEs and 595 packages |
| **Lab 2** | SBOM, VEX, SLSA provenance, and digital signature are inspectable and verifiable |
| **Lab 3** | A CI pipeline that blocks any image not meeting all seven Scout policies |
| **Lab 4** | A fully attested, signed MCP server running with zero-write, zero-capability isolation |

---

## Your security framework — do this Monday

```
1. Know what is in your images          →  SBOM + VEX
2. Verify where they came from          →  SLSA provenance + image signing
3. Start from a trusted base            →  Docker Hardened Images
4. Enforce at the pipeline              →  Docker Scout build policies
5. Isolate your agents                  →  MCP servers in hardened containers
```

---

## The bigger picture

Coding stopped being human-paced. Your developers are already shipping with
agents — the only question is whether your platform ships with them, safely.

> **One continuous trust chain. From source to production. From human developer to
> autonomous agent.**

Here in the agentic era, **speed and safety isn't a tradeoff**:

- **For developers** — agents run without asking permission at every step. The work
  happens, and nothing escapes the sandbox.
- **For the platform team** — the safe path is the fast path. Developers stop routing
  around you because what you ship is what they would have built themselves — only governed.
- **For security** — become a policy authority, not the inbox. Write the rails once;
  the runtime enforces them and the audit log writes itself.

---

## Key commands cheat sheet

```bash
# Scan an image
docker scout quickview IMAGE --org YOUR_ORG
docker scout cves IMAGE --only-severity critical,high

# Compare two images
docker scout compare --ignore-unchanged --to BASELINE IMAGE

# Inspect attestations
docker scout attest list IMAGE
docker scout sbom IMAGE --format list

# Sign and verify (key-based)
cosign generate-key-pair
cosign sign --key cosign.key IMAGE --yes
cosign verify --key cosign.pub IMAGE

# Build with full attestations
docker buildx build --sbom=true --provenance=mode=max -t IMAGE --push .
```

---

## Resources

| Resource | URL |
|----------|-----|
| Lab repo | github.com/ajeetraina/labspace-agentic-security |
| Full workshop | dockerworkshop.vercel.app |
| Docker Hardened Images | hub.docker.com → Trusted Content → Hardened Images |
| Docker Scout docs | docs.docker.com/scout |
| MCP Catalog | hub.docker.com/mcp |
| SLSA framework | slsa.dev |
| VEX specification | openvex.dev |
| Cosign (image signing) | docs.sigstore.dev/cosign |
| MCP specification | modelcontextprotocol.io |
| State of Agentic AI Report | docker.com/resources/the-state-of-agentic-ai-white-paper |

---

> *Securing your containers is step one.*
> *Securing your supply chain is the rest.*
>
> [Get started with DHI →](https://docs.docker.com/dhi/get-started/)
