# Lab 1 — Standard Image vs Docker Hardened Images

> **Goal:** Change one FROM line. Watch the CVE count collapse to 0.

## What makes a hardened image *hardened*

| Minimal | Attested | Patched |
|---------|----------|---------|
| Built from source. Only the packages your runtime actually needs. No shell, no curl, no extras. | Every image ships with an SBOM, a VEX document, SLSA provenance, and a digital signature. Verify in one command. | Continuously updated. Near-zero CVEs on day one, and Docker keeps it that way as new vulnerabilities emerge. |
| **~95% smaller** | **SBOM ✓ · VEX ✓ · SLSA L3 ✓ · Signed ✓** | **~0 CVEs on day one** |

The effect is dramatic. The hardened Ruby image, before and after:

| `standard ruby:3.3` | `docker/hardened-ruby:3.3` |
|---------------------|----------------------------|
| **193** vulnerabilities (6 Critical · 53 High · + Medium/Low) | **0** — all vulnerabilities eliminated |

And migration is **one line** — same Alpine/Debian base, same tooling, custom
certs/configs/init scripts still supported:

```diff no-copy-button
- FROM node:20-alpine
+ FROM docker/hardened-node:20-alpine
```

In this lab you'll do exactly that to the `catalog-service-node` app and measure
the result with Docker Scout.

---

## Step 1 — Scan the baseline image

```bash terminal-id=build
docker scout quickview catalog-service:baseline --org $$org$$
```

```none no-copy-button
Target     │  catalog-service:baseline  │    2C    26H    25M   122L
```

```bash terminal-id=build
docker scout cves catalog-service:baseline \
  --only-severity critical,high \
  --org $$org$$
```

Note the number of critical and high CVEs — you will eliminate all of them.

## Step 2 — Update the Dockerfile

Open :fileLink[Dockerfile]{path="catalog-service-node/Dockerfile"} and replace it
with the multi-stage DHI version below.

DHI requires multi-stage builds because the **runtime variant is distroless** —
no shell, no npm. The dev variant handles the build step.

```yaml save-as=catalog-service-node/Dockerfile
###########################################################
# Stage: base — DHI dev variant (has shell + npm for builds)
###########################################################
FROM $$dhiPrefix$$node:24-debian13-dev AS base

WORKDIR /usr/local/app
COPY package.json package-lock.json ./

###########################################################
# Stage: production-dependencies
###########################################################
FROM base AS production-dependencies
ENV NODE_ENV=production
RUN npm ci --production --ignore-scripts && npm cache clean --force

###########################################################
# Stage: final — DHI runtime (distroless, no shell)
###########################################################
FROM $$dhiPrefix$$node:24-debian13 AS final
ENV NODE_ENV=production
COPY --from=production-dependencies /usr/local/app/node_modules ./node_modules
COPY ./src ./src
EXPOSE 3000
CMD ["node", "src/index.js"]
```

```diff no-copy-button
- FROM node:20 AS base
+ FROM $$dhiPrefix$$node:24-debian13-dev AS base   # build stage
+ FROM $$dhiPrefix$$node:24-debian13 AS final      # runtime — distroless
```

## Step 3 — Build the DHI version

```bash terminal-id=build
cd catalog-service-node
docker build \
  -t catalog-service:dhi \
  --sbom=true \
  --provenance=mode=max \
  .
```

## Step 4 — Compare the images

```bash terminal-id=build
docker images catalog-service
```

```none no-copy-button
REPOSITORY        TAG        SIZE
catalog-service   dhi        191MB
catalog-service   baseline   1.62GB
```

```bash terminal-id=build
docker scout compare \
  --ignore-unchanged \
  --to catalog-service:baseline \
  catalog-service:dhi \
  --org $$org$$
```

```none no-copy-button
  vulnerabilities │  0C  0H  0M  0L  │  2C  26H  25M  122L
  size            │  40 MB (-358 MB)  │  398 MB
  packages        │  211 (-595)       │  806
```

**595 packages removed. All critical and high CVEs eliminated.**

## Step 5 — Run Scout quickview — all 7 policies green

```bash terminal-id=build
docker scout quickview catalog-service:dhi --org $$org$$
```

```none no-copy-button
Policy status  SUCCEEDED  (7/7 policies met)

  ✓  Default non-root user
  ✓  No AGPL v3 licenses
  ✓  No fixable critical or high vulnerabilities
  ✓  No high-profile vulnerabilities
  ✓  No unapproved base images
  ✓  Supply chain attestations
  ✓  No outdated base images
```

## Step 6 — Prove there is no shell (distroless demo)

```bash terminal-id=build
docker run --rm catalog-service:dhi sh
```

Expected: `exec: "sh": executable file not found in $PATH`

An attacker with code execution **cannot drop to a shell**. Compare to baseline:

```bash terminal-id=build
docker run --rm catalog-service:baseline sh -c "echo shell available"
```

## DHI vs baseline — property comparison

| Property | `node:20` | DHI runtime |
|----------|-----------|-------------|
| CVEs (critical/high) | 28+ | 0 |
| Package count | ~806 | ~211 |
| Shell in runtime | Yes | No (distroless) |
| Non-root by default | Manual | Built-in |
| SBOM | Build-time only | Cryptographically signed |
| VEX document | No | Yes |
| SLSA provenance | Build-time only | Verified |
| 7-day CVE SLA | No | Yes |
