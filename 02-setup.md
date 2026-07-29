# Setup

Five minutes of configuration, then you never touch it again.

## 1. Your Docker organisation

Docker Scout needs to know which organisation to analyse under.

::variableDefinition[org]{prompt="What is your Docker Organization?"}

:::conditionalDisplay{variable="org" hasNoValue}
> [!WARNING]
> Set your organisation above before continuing. Every Scout command in this workshop
> uses it.
:::

## 2. Choose your DHI tier

Docker Hardened Images are available two ways, and the commands differ slightly.
Pick one now and the rest of the workshop adapts.

::variableSetButton[Use the free tier (dhi.io)]{variables="tier=free,dhiPrefix=dhi.io/"}

::variableSetButton[Use the paid tier ($$org$$)]{variables="tier=paid,dhiPrefix=$$org$$/dhi-"}

> [!TIP]
> **Free tier** pulls straight from the `dhi.io` registry and needs no Docker Hub
> subscription. **Paid tier** uses images mirrored into your own organisation.
>
> Choose free unless you have a paid plan with `node` already mirrored.

:::conditionalDisplay{variable="tier" hasNoValue}
> [!WARNING]
> Pick a tier above before continuing.
:::

## 3. Log in

1. Log in to Docker Hub:

    ```bash terminal-id=main
    docker login
    ```

:::conditionalDisplay{variable="tier" requiredValue="free"}
2. Also log in to the hardened image registry:

    ```bash terminal-id=main
    docker login dhi.io
    ```
:::

3. Point Scout at your organisation:

    ```bash terminal-id=main
    docker scout config organization $$org$$
    ```

## 4. Check cosign

You will sign an image in Lab 3 using [cosign](https://docs.sigstore.dev/cosign/),
from the Sigstore project.

```bash terminal-id=main
cosign version
```

If that fails, install it:

```bash terminal-id=main no-run-button
# macOS
brew install cosign

# Linux
curl -Lo cosign https://github.com/sigstore/cosign/releases/latest/download/cosign-linux-amd64
chmod +x cosign && sudo mv cosign /usr/local/bin/
```

## 5. Preflight

Run all four. Each should print a version.

```bash terminal-id=main
docker --version
docker scout version
cosign version
git --version
```

## 6. Confirm the agent's image is here

The image an agent built is already in this workspace. Confirm it:

```bash terminal-id=build
docker images catalog-service:baseline
```

> [!NOTE]
> If that returns nothing, build it now — it takes about a minute:
>
> ```bash terminal-id=build no-run-button
> docker build -t catalog-service:baseline --sbom=true --provenance=mode=max .
> ```
>
> This uses the Dockerfile exactly as the agent wrote it. You are not fixing anything
> yet.

You are ready. Continue to **An Agent Built This**.
