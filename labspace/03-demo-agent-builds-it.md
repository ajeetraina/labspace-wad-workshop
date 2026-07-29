# An Agent Built This

> [!NOTE]
> Your facilitator will play a recording of this happening. Follow along here, then
> run the measurements yourself at the end.

## The instruction it was given

That is all of it. No mention of base images, versions, security, or best practice.

```text no-copy-button
Containerise this Node.js application for production.
Add a Dockerfile and build the image as catalog-service:baseline.
```

## What it did

1. **Read `package.json`** to work out the runtime and the dependency list.

2. **Chose a base image** — from what it had seen during training, not from your
   organisation's approved list.

3. **Wrote a Dockerfile.** Open :fileLink[Dockerfile]{path="Dockerfile"} and read it.
   It may well be a good one.

4. **Ran `npm install`,** resolving several hundred transitive packages from the
   public registry.

5. **Built the image.** Successfully. No errors, no warnings, no questions.

## Freeze here. Three questions.

### What base image did it pick, and who decided that?

```bash terminal-id=build
head -20 Dockerfile
```

Nobody in your organisation chose this. The agent pattern-matched against whatever was
most common in its training data, which skews toward what was popular a year or two
ago.

### How many packages did that resolve?

```bash terminal-id=build
npm ls --all --parseable 2>/dev/null | wc -l
```

<!-- VERIFY: package count from the Phase 0 agent run -->

Every one is a package, with a version, with a vulnerability history. You reviewed
none of them. Neither did the agent — resolving a dependency and evaluating it are
different activities, and it only did the first.

### Can you prove where any of it came from?

No. Not the base image, not the packages, not the build itself.

That is the subject of the next eighty minutes.

## Measure it

This image is the baseline every later lab compares against.

1. Get the vulnerability overview:

    ```bash terminal-id=build
    docker scout quickview catalog-service:baseline --org $$org$$
    ```

    <!-- VERIFY: replace with real output from the Phase 0 run -->

2. Run the default policy evaluation:

    ```bash terminal-id=build
    docker scout policy catalog-service:baseline --org $$org$$
    ```

3. Note the size:

    ```bash terminal-id=build
    docker images catalog-service:baseline
    ```

**Write these down.** Severity counts, policy pass rate, image size. You will fill in
the second row of this table in Lab 2:

| | Critical | High | Medium | Low | Size |
|---|---|---|---|---|---|
| `catalog-service:baseline` | | | | | |
| `catalog-service:dhi` | | | | | |

## What you should be thinking

Scout is already pointing at part of the answer — it will suggest a newer base image
and show you the CVEs that would disappear. That is worth doing, and it is not
enough.

A newer base image answers *"is this old?"*. It does not answer any of the three
questions. You still cannot list what is inside, say which findings are exploitable,
or prove where the artifact came from.

Those three answers are what Lab 1 gives you.

## Checkpoint

- [ ] You have read the Dockerfile the agent wrote
- [ ] You know how many packages the image contains
- [ ] You have recorded the baseline severity counts and size
- [ ] You have seen the default policy evaluation fail
