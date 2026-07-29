# Lab 2 — Secure Software Supply Chain: SBOM · VEX · SLSA

> **Goal:** Attach a full SBOM and provenance to your image, inspect all attestations,
> and verify the digital signature.

## The building blocks — three standards every developer should understand

### SBOM — Software Bill of Materials (your ingredient list)

A complete, machine-readable list of every component in your software — packages,
libraries, versions, licenses, and their relationships.

- Know what is in every image you ship
- Respond to new CVEs in **seconds, not days**
- Required for SLSA compliance and enterprise contracts

SBOMs come in different formats — **SPDX** and **CycloneDX** — and can carry an
embedded **VEX** document.

### VEX — Vulnerability Exploitability eXchange (cutting through CVE noise)

| Without VEX | With VEX (DHI) |
|-------------|----------------|
| *"Your image has 200 CVEs."* Developer spends a week triaging. 190 are in packages not reachable by the running process. 10 are actually relevant. | *"190 not affected. 10 fixed."* Publisher attests: component not present, not reachable, or already fixed. Developer knows in seconds what actually needs action. |
| Signal-to-noise: **terrible** | Signal-to-noise: **surgical** |

VEX also comes in multiple formats: OpenVEX, the SPDX SBOM format, OASIS CSAF, and
OWASP CycloneDX.

### SLSA — Supply chain Levels for Software Artifacts (build provenance)

*Can you prove this artifact came from that source, and was not tampered with in
transit? SLSA makes that question answerable.*

| Level | What it means |
|-------|---------------|
| **L0** | No guarantees |
| **L1** | Provenance exists — build metadata documented |
| **L2** | Hosted build + signed provenance (GitHub Actions with OIDC achieves this) |
| **L3** | Hardened build, non-falsifiable provenance — **DHI target level** |

**DHI gives you:** a signed provenance envelope, hermetic/reproducible builds, and
verifiability with Cosign.

In this lab you'll produce and inspect each of these for a real image.

---

## Step 1 — Build with full attestations

```bash terminal-id=build
cd catalog-service-node
docker buildx build \
  --sbom=true \
  --provenance=mode=max \
  -t $$org$$/catalog-service:v1.0 \
  --push \
  .
```

`--sbom=true` generates a CycloneDX + SPDX bill of materials and attaches it to
the image manifest. `--provenance=mode=max` records the full build environment,
source inputs, and build parameters as a signed SLSA envelope.

## Step 2 — List all attestations

```bash terminal-id=build
docker scout attest list $$org$$/catalog-service:v1.0
```

| Attestation | What it is |
|-------------|------------|
| CycloneDX SBOM | Components, libraries, versions |
| SPDX SBOM | SBOM in SPDX format |
| Scout SBOM | SBOM generated and signed by Docker Scout |
| OpenVEX | Non-applicable CVEs with explanations |
| SLSA provenance | Source, build params, environment |
| SLSA verification summary | SLSA compliance level |

## Step 3 — View the SBOM

```bash terminal-id=build
docker scout sbom $$org$$/catalog-service:v1.0
```

Pipe to jq for a clean package list:

```bash terminal-id=build
docker scout sbom $$org$$/catalog-service:v1.0 \
  --format list
```

## Step 4 — Inspect DHI attestations (pre-built image)

DHI ships attestations that your own build inherits through the base image chain.
Inspect the upstream DHI node image directly:

```bash terminal-id=build
docker scout attest list $$dhiPrefix$$node:24-debian13
```

You will see entries including `OpenVEX`, `FIPS attestation`, `STIG attestation`,
and `Scout health` — attestations Docker generates and signs for every DHI release.

## Step 5 — View the SLSA provenance

```bash terminal-id=build
docker buildx imagetools inspect $$org$$/catalog-service:v1.0 \
  --format '{{json .Provenance}}'
```

Note the `builder.id`, `materials` (source repo + commit SHA), and
`invocation.parameters` fields. This is the non-falsifiable record of what
produced this artifact.

## Step 6 — Sign the image with Cosign

First generate a signing key pair (one time). We export an empty `COSIGN_PASSWORD`
so the keygen is non-interactive for the lab — in production you'd use a real
passphrase or a KMS/keyless flow.

```bash terminal-id=build
export COSIGN_PASSWORD=""
cosign generate-key-pair
```

This creates `cosign.key` (private — keep it safe) and `cosign.pub` (public — share
it for verification). Now sign the image:

```bash terminal-id=build
cosign sign --key cosign.key $$org$$/catalog-service:v1.0 --yes
```

The signature is stored back in the registry as an OCI artifact, right next to the
image. List everything attached to the image:

```bash terminal-id=build
cosign tree $$org$$/catalog-service:v1.0
```

## Step 7 — Verify the signature

```bash terminal-id=build
cosign verify --key cosign.pub $$org$$/catalog-service:v1.0
```

```none no-copy-button
Verification for $$org$$/catalog-service:v1.0 --
The following checks were performed on each of these signatures:
  - The cosign claims were validated
  - The signatures were verified against the specified public key
```

## Step 8 — Export VEX for use with external scanners

DHI ships VEX documents that tell external scanners which CVEs are non-applicable.
This eliminates false positives in Trivy, Grype, Wiz, and Snyk automatically.

```bash terminal-id=build
docker scout vex get $$org$$/catalog-service:v1.0 --output vex.json
cat vex.json | head -40
```

Pass to Grype:
```bash no-copy-button
grype $$org$$/catalog-service:v1.0 --vex vex.json
```

Pass to Trivy:
```bash no-copy-button
trivy image --vex vex.json $$org$$/catalog-service:v1.0
```

> **Key insight:** VEX is the signal-to-noise solution. Without it, a scanner reports
> every CVE in every package even if the vulnerable code path is never reachable.
> With VEX, you see only what actually matters.
