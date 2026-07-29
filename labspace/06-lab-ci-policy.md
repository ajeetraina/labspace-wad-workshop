# Lab 3 — Sign It, Then Gate It

**10 minutes · demo, with two hands-on steps**

You have a hardened, attested image. Nothing yet stops the next person merging a
Dockerfile that undoes it.

> Verification you run once by hand is theatre. The value only compounds when the
> check is a gate.

---

## Sign it

Hardened base images arrive signed. Yours does not — until you sign it.

1. Generate a keypair. A real pipeline would use keyless OIDC signing; a local key
   makes the mechanics visible. Press enter twice for an empty password:

    ```bash terminal-id=build
    cosign generate-key-pair
    ```

2. Tag and push to the local registry:

    ```bash terminal-id=build
    docker tag catalog-service:dhi registry.dockerlabs.xyz/catalog-service:dhi
    docker push registry.dockerlabs.xyz/catalog-service:dhi
    ```

3. Sign it:

    ```bash terminal-id=build
    cosign sign --key cosign.key registry.dockerlabs.xyz/catalog-service:dhi --yes
    ```

4. Verify:

    ```bash terminal-id=build
    cosign verify --key cosign.pub registry.dockerlabs.xyz/catalog-service:dhi
    ```

---

## Now try to fool it

This is the most useful ninety seconds in the workshop.

1. Rebuild with a trivial change and push to the **same tag**:

    ```bash terminal-id=build
    docker build -t registry.dockerlabs.xyz/catalog-service:dhi --no-cache .
    docker push registry.dockerlabs.xyz/catalog-service:dhi
    ```

2. Verify again:

    ```bash terminal-id=build
    cosign verify --key cosign.pub registry.dockerlabs.xyz/catalog-service:dhi
    ```

    ```none no-copy-button
    Error: no matching signatures
    ```

> [!IMPORTANT]
> **Tags are mutable. Digests are not. Signatures bind a claim to a digest.**
>
> Any process that trusts a tag — a Dockerfile that says `FROM node:24`, a manifest
> that says `image: catalog-service:latest` — is trusting that nobody moved it.
>
> You just watched exactly the substitution an attacker performs get caught.

3. Re-sign so the rest of the lab works:

    ```bash terminal-id=build
    cosign sign --key cosign.key registry.dockerlabs.xyz/catalog-service:dhi --yes
    ```

---

## Write the policy

You watched the default policy fail in the demo. That was an *evaluation*. Now make it
a *gate*.

1. Open :fileLink[docker-scout-policy.yaml]{path="docker-scout-policy.yaml"} — three
   rules, one per question from the spine:

    ```yaml no-copy-button
    version: "1"
    policies:
      - name: no-critical-cves
        type: vulnerability
        severity: critical
        action: fail

      - name: require-sbom
        type: attestation
        attestation: sbom
        action: fail

      - name: require-provenance
        type: attestation
        attestation: slsa-provenance
        action: fail
    ```

2. Evaluate both images and compare:

    ```bash terminal-id=build
    docker scout policy catalog-service:baseline --org $$org$$
    ```

    ```bash terminal-id=build
    docker scout policy catalog-service:dhi --org $$org$$
    ```

One fails. One passes. You now know what the pipeline will say before you push.

---

## Put it in the pipeline

> [!NOTE]
> The files in this workspace are already committed to a Gitea repository at
> :tabLink[git.dockerlabs.xyz]{href="http://git.dockerlabs.xyz" id="gitea"} — log in as
> `moby` / `moby1234`. Anything under `.gitea/workflows/` runs automatically when you
> push. There is no repository to create and no remote to configure.

1. Add the signing secrets. In Gitea, go to your repository → **Settings** →
   **Actions** → **Secrets**, and add:

    | Secret | Value |
    |--------|-------|
    | `COSIGN_PRIVATE_KEY` | contents of `cosign.key` |
    | `COSIGN_PASSWORD` | empty, if you pressed enter twice above |

    Print the key to copy it:

    ```bash terminal-id=build
    cat cosign.key
    ```

2. Create a file named `.gitea/workflows/secure-build.yaml` with the following
   contents:

    ```yaml save-as=.gitea/workflows/secure-build.yaml
    name: secure-build

    on: [push]

    env:
      IMAGE: ${{ secrets.DOCKER_REGISTRY }}/catalog-service:${{ github.sha }}

    jobs:
      build:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4

          - name: Build with attestations
            run: |
              docker build -t "$IMAGE" \
                --sbom=true \
                --provenance=mode=max .

          # The gate sits BEFORE the push.
          # An image that fails policy never reaches the registry.
          - name: Policy gate
            uses: docker/scout-action@v1
            with:
              command: policy
              image: ${{ env.IMAGE }}
              organization: ${{ secrets.DOCKER_SCOUT_ORG }}
              exit-on: policy

          - name: Sign
            env:
              COSIGN_PRIVATE_KEY: ${{ secrets.COSIGN_PRIVATE_KEY }}
              COSIGN_PASSWORD: ${{ secrets.COSIGN_PASSWORD }}
            run: cosign sign --key env://COSIGN_PRIVATE_KEY "$IMAGE" --yes

          - name: Push
            run: docker push "$IMAGE"
    ```

3. Commit and push:

    ```bash terminal-id=main
    git add .gitea/workflows/secure-build.yaml
    git commit -m "Add secure build pipeline"
    git push
    ```

4. Open :tabLink[Gitea]{href="http://git.dockerlabs.xyz" id="gitea"} and watch the run
   in the **Actions** tab.

---

## Make it fail, then make it pass

1. Revert the base image to what the agent originally chose, commit, and push. The
   policy step fails and names the failing check.

2. Restore the hardened `FROM` lines, commit, and push. Green — built, attested,
   policy-checked, signed and pushed, with nobody running a verification command by
   hand.

---

## Checkpoint

- [ ] You have signed an image with cosign
- [ ] You have watched verification fail on a moved tag
- [ ] You have evaluated the policy locally against both images
- [ ] You have watched CI fail on the gate, then pass

## Four patterns that survive contact with a real team

1. **Gate on exploitable findings, not raw CVE counts.** This is what VEX bought you
   in Lab 1. Without it a strict gate is unusable and teams switch it off within a
   month.

2. **Require provenance to a *known builder*,** not merely provenance that exists.
   "Has an attestation" is a weaker claim than it sounds.

3. **Separate base-image findings from application-layer findings.** Different owners,
   different remediation paths. Merging them makes both un-actionable.

4. **Fail closed on signature verification. Fail open with an alert on scanner
   availability.** A scanner outage should page somebody, not block every deploy.

## Go deeper

1. Add a policy that fails on any base image outside an approved list.
2. Switch to keyless signing with an OIDC identity instead of a local keypair.
3. Inspect the signature as an OCI referrer: `cosign tree registry.dockerlabs.xyz/catalog-service:dhi`
