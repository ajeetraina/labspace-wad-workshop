# Lab 2 — Start From a Trusted Base

**16 minutes · hands-on**

This is the pivot of the workshop. You spent Lab 1 learning to measure an image. Now
you change one thing about where it starts, and measure it again.

---

## Two variants, and why it matters

Docker Hardened Images come in two flavours, and you need both:

| Variant | Tag | What it has |
|---------|-----|-------------|
| Dev | `$$dhiPrefix$$node:24-debian13-dev` | A shell and npm — for building |
| Runtime | `$$dhiPrefix$$node:24-debian13` | Distroless — no shell, no package manager |

Because the runtime variant has no shell, you cannot run `npm install` in it. That
forces a multi-stage build: the dev image installs dependencies, the runtime image
receives only the output.

That constraint is doing real work. An image with no shell is one an attacker cannot
drop into.

---

## Migrate

1. Replace the Dockerfile with a multi-stage build on hardened bases. Create a file
   named `Dockerfile` with the following contents:

    ```dockerfile save-as=Dockerfile
    ###########################################################
    # Stage: base — DHI dev variant, has shell and npm
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
    # Stage: final — DHI runtime variant, distroless
    ###########################################################
    FROM $$dhiPrefix$$node:24-debian13 AS final
    ENV NODE_ENV=production
    WORKDIR /usr/local/app

    COPY --from=production-dependencies /usr/local/app/node_modules ./node_modules
    COPY ./src ./src

    EXPOSE 3000
    CMD ["node", "src/index.js"]
    ```

2. That is the entire migration. Here is what actually changed:

    ```diff no-copy-button
    - FROM node:<whatever the agent picked>
    + FROM $$dhiPrefix$$node:24-debian13-dev AS base    # build
    + FROM $$dhiPrefix$$node:24-debian13 AS final       # runtime, distroless
    ```

3. Build it:

    ```bash terminal-id=build
    docker build -t catalog-service:dhi --sbom=true --provenance=mode=max .
    ```

---

## Confirm it still works

A hardened image that breaks your application is not a security win.

```bash terminal-id=build
docker run --rm catalog-service:dhi node --version
```

Same runtime, same app.

---

## Now measure it

1. The overview:

    ```bash terminal-id=build
    docker scout quickview catalog-service:dhi --org $$org$$
    ```

    <!-- VERIFY: real quickview output for the DHI build -->

2. The direct comparison:

    ```bash terminal-id=build
    docker scout compare --to catalog-service:baseline catalog-service:dhi --org $$org$$
    ```

3. The size difference:

    ```bash terminal-id=build
    docker images catalog-service
    ```

4. Fill in your table from the demo:

    | | Critical | High | Medium | Low | Size |
    |---|---|---|---|---|---|
    | `catalog-service:baseline` | | | | | |
    | `catalog-service:dhi` | | | | | |

---

## Where did the CVEs go?

This is the part people misunderstand. They were not patched.

1. Count the packages again and compare with Lab 1:

    ```bash terminal-id=build
    docker scout sbom --format spdx --output dhi.spdx.json catalog-service:dhi
    jq '.packages | length' dhi.spdx.json
    ```

2. Try to get a shell:

    ```bash terminal-id=build
    docker run --rm catalog-service:dhi sh -c "echo hello" || echo "No shell in this image."
    ```

The vulnerable packages are **gone**, not fixed. There is no shell to drop into, no
package manager to install with, and no `curl` to fetch a second stage.

---

## Re-run Lab 1 against the base

Everything you learned now returns a different answer.

```bash terminal-id=build
docker scout attest list $$dhiPrefix$$node:24-debian13
```

An SBOM, a VEX document, SLSA provenance and a signature — all shipped with the base
image, all verifiable, none of which you had to produce.

Compare that with the agent's image, which shipped nothing but itself.

---

## Checkpoint

- [ ] `catalog-service:dhi` builds from the same source
- [ ] The runtime still works
- [ ] You have recorded the severity and size deltas
- [ ] You have confirmed there is no shell in the final image
- [ ] You have listed the attestations that arrived with the base

## What you should be thinking

Two things changed, and they are worth separating.

**The attack surface shrank.** Fewer packages means fewer vulnerabilities, and no
shell means a compromised process has far less to work with.

**The evidence burden moved.** In Lab 1 you generated an SBOM, hunted for provenance
and had nothing to verify. Starting from a hardened base, all of that arrives with the
image, signed by somebody whose job is keeping it current.

You still own your application layer. You are no longer responsible for proving things
about an operating system you did not assemble.

Back to the three questions: you can now answer all of them about the base. Lab 3 is
about making sure that stays true.

## Go deeper

1. Add a custom CA certificate to the runtime stage and confirm the app still trusts it.
2. Build a third image on `node:24-slim` and compare — how much of the win is just
   "slim", and how much is hardening?
3. Inspect the layers: `docker history catalog-service:dhi`
