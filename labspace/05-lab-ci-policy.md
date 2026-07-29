# Lab 3 — Securing Your CI Pipeline (Gitea Actions)

> **Goal:** Wire a Docker Scout policy gate and Cosign signing into a CI pipeline.
> Watch a build **fail** on a standard base image, then **pass** with one Dockerfile
> change — all running locally, no GitHub account required.

This labspace bundles **Gitea** — a self-hosted Git service with built-in Actions
(compatible with GitHub Actions syntax) — plus a Gitea Actions **runner** and a
local **container registry** at `registry.dockerlabs.xyz`. Your app is already
checked into Gitea; you just add the secure pipeline.

## Docker Scout build policies — security as code

Define rules that **automatically fail the build** before anything insecure reaches
your registry or production.

**Policies to enforce today:**

- ✅ Block images with critical / high CVEs
- ✅ Require a valid SBOM attestation
- ✅ Require SLSA provenance
- ✅ Sign every image that passes

> Only signed, attested images reach the registry.

## Image signing with Cosign (key-based)

Docker Hardened Images are signed with **Cosign** using a key pair — the same model
you'll use here. Unlike keyless/OIDC signing, key-based signing needs no external
identity provider, so it runs fully inside the local Gitea runner.

1. Build and push the image **with attestations**
2. **Sign** with `cosign sign --key` using a private key stored as a Gitea secret
3. Signature is stored as an **OCI artifact** next to the image
4. **Verify** with `docker scout attest --verify` (Docker-native) or `cosign verify --key`

## The complete secure CI pipeline

```text no-copy-button
1. CHECKOUT      2. BUILD (DHI)     3. ATTEST         4. POLICY        5. PUSH          6. SIGN
actions/         FROM $$dhiPrefix   --sbom=true       docker/scout     docker/build-    cosign sign
checkout@v4      $$node:24...       --provenance      -action@v1       push-action@v6   --key (Gitea)
                                    =mode=max         (hard gate)
```

You'll build exactly this pipeline and watch the **POLICY** gate do its job.

---

## Step 1 — Verify the Gitea remote

Your app repo is already seeded into Gitea. Confirm the remote:

```bash terminal-id=main
git remote -v
```

You should see `origin` pointing at `http://git.dockerlabs.xyz/moby/<repo>.git`.

:tabLink[Open Gitea]{href="http://git.dockerlabs.xyz" title="Gitea" id="gitea"} and
log in with **moby** / **moby1234** if prompted, then open your repository.

## Step 2 — Add the pipeline secrets in Gitea

The local-registry secrets (`DOCKER_REGISTRY`, `DOCKER_USERNAME`, `DOCKER_PASSWORD`)
are **pre-configured**. You need to add three more for the Scout gate and signing.

First generate a Cosign key pair locally (non-interactive for the lab):

```bash terminal-id=main
export COSIGN_PASSWORD=""
cosign generate-key-pair
cat cosign.key   # copy this whole block for the secret below
```

In Gitea, go to your repo → **Settings → Actions → Secrets** and add:

| Secret | Value |
|--------|-------|
| `DOCKERHUB_USERNAME` | Your Docker Hub username |
| `DOCKERHUB_TOKEN` | A Docker Hub access token (Scout is a cloud service) |
| `DOCKER_SCOUT_ORG` | Your Scout-enabled Docker organization |
| `COSIGN_PRIVATE_KEY` | The full contents of `cosign.key` |
| `COSIGN_PASSWORD` | Empty (matches the key you just generated) |

Keep `cosign.pub` — you'll verify signatures with it later.

## Step 3 — Add the secure pipeline

Create the workflow file. Gitea reads workflows from `.gitea/workflows/`.

```yaml save-as=.gitea/workflows/secure-build.yaml
name: Secure Build

on:
  push:
    branches:
      - main

jobs:
  secure-build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
        with:
          buildkitd-config-inline: |
            [registry."registry.dockerlabs.xyz"]
              insecure = true

      - name: Install Cosign
        uses: sigstore/cosign-installer@v3

      - name: Log in to the local registry
        uses: docker/login-action@v3
        with:
          registry: ${{ secrets.DOCKER_REGISTRY }}
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Log in to Docker Hub (for Docker Scout)
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      # BUILD + ATTEST — load locally so the Scout gate runs before any push
      - name: Build with SBOM and provenance
        id: build
        uses: docker/build-push-action@v6
        with:
          context: .
          push: false
          load: true
          sbom: true
          provenance: mode=max
          tags: ${{ secrets.DOCKER_REGISTRY }}/${{ github.repository }}:${{ github.sha }}

      # POLICY — hard gate: fail on any critical/high CVE
      - name: Docker Scout policy gate
        uses: docker/scout-action@v1
        with:
          command: cves
          image: ${{ secrets.DOCKER_REGISTRY }}/${{ github.repository }}:${{ github.sha }}
          organization: ${{ secrets.DOCKER_SCOUT_ORG }}
          only-severities: critical,high
          exit-code: true

      # PUSH — only reached if the gate passed
      - name: Push image
        id: push
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          sbom: true
          provenance: mode=max
          tags: ${{ secrets.DOCKER_REGISTRY }}/${{ github.repository }}:latest

      # SIGN — key-based Cosign
      - name: Sign the image with Cosign
        env:
          COSIGN_PRIVATE_KEY: ${{ secrets.COSIGN_PRIVATE_KEY }}
          COSIGN_PASSWORD: ${{ secrets.COSIGN_PASSWORD }}
          DIGEST: ${{ steps.push.outputs.digest }}
        run: |
          cosign sign --yes \
            --key env://COSIGN_PRIVATE_KEY \
            --allow-insecure-registry --allow-http-registry \
            ${{ secrets.DOCKER_REGISTRY }}/${{ github.repository }}@${DIGEST}
```

## Step 4 — Round 1: a standard base (the gate blocks it)

Point the app's `Dockerfile` at a standard base so the Scout gate has something to
catch:

```dockerfile save-as=Dockerfile
# Round 1: standard base — will fail the Scout gate
FROM node:20

WORKDIR /usr/local/app
COPY package.json package-lock.json ./
RUN npm ci --production --ignore-scripts && npm cache clean --force
COPY ./src ./src
EXPOSE 3000
CMD ["node", "src/index.js"]
```

Commit and push:

```bash terminal-id=main
git add Dockerfile .gitea/workflows/secure-build.yaml
git commit -m "test: standard base image — should fail the gate"
git push
```

:tabLink[Open Gitea Actions]{href="http://git.dockerlabs.xyz" title="Gitea" id="gitea"}
and open your repo's **Actions** tab. The run fails at the **Docker Scout policy
gate** step:

```none no-copy-button
✗  Docker Scout policy gate
   Detected critical/high vulnerabilities — failing the build.

Error: Process completed with exit code 1
```

The image is **never pushed** — the gate stopped it.

## Step 5 — Round 2: switch to DHI (the gate passes)

Change the base to a Docker Hardened Image — a multi-stage, distroless build:

```dockerfile save-as=Dockerfile
###########################################################
# Stage: build — DHI dev variant (has shell + npm)
###########################################################
FROM $$dhiPrefix$$node:24-debian13-dev AS build

WORKDIR /usr/local/app
COPY package.json package-lock.json ./
RUN npm ci --production --ignore-scripts && npm cache clean --force

###########################################################
# Stage: final — DHI runtime (distroless, no shell)
###########################################################
FROM $$dhiPrefix$$node:24-debian13 AS final

ENV NODE_ENV=production
WORKDIR /usr/local/app
COPY --from=build /usr/local/app/node_modules ./node_modules
COPY ./src ./src
EXPOSE 3000
CMD ["node", "src/index.js"]
```

Commit and push again:

```bash terminal-id=main
git add Dockerfile
git commit -m "fix: switch to Docker Hardened Images"
git push
```

Watch the Actions tab again. Every step goes green:

```none no-copy-button
✓  Build with SBOM and provenance
✓  Docker Scout policy gate      (0 critical/high)
✓  Push image
✓  Sign the image with Cosign
```

## Step 6 — Verify the pushed, signed image

Confirm the image landed in the local registry:

```bash terminal-id=build
curl -s http://registry.dockerlabs.xyz/v2/moby/$(basename $(git rev-parse --show-toplevel))/tags/list
```

Inspect its attestations the Docker-native way — Scout verifies the Sigstore
signature and reads the attestations in one step:

```bash terminal-id=build
docker scout attest list registry.dockerlabs.xyz/moby/$(basename $(git rev-parse --show-toplevel)):latest
```

And verify the Cosign signature with the public key you kept:

```bash terminal-id=build
cosign verify \
  --key cosign.pub \
  --allow-insecure-registry --allow-http-registry \
  registry.dockerlabs.xyz/moby/$(basename $(git rev-parse --show-toplevel)):latest
```

```none no-copy-button
Verification for registry.dockerlabs.xyz/moby/<repo>:latest --
The following checks were performed on each of these signatures:
  - The cosign claims were validated
  - The signatures were verified against the specified public key
```

## What you've got

Every push to `main` now:

- **Builds** from a hardened base with a full SBOM + SLSA provenance
- **Gates** on Docker Scout — no critical/high CVE ever reaches the registry
- **Pushes** only images that passed the gate
- **Signs** every pushed image with Cosign, verifiable with a public key

> The same pipeline runs on GitHub Actions, GitLab CI, or any GitHub-Actions-
> compatible runner — swap the local registry secrets for your real registry and,
> on GitHub, you can upgrade the signing step to keyless/OIDC.
