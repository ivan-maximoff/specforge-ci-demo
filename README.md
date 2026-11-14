# specforge-ci-demo

RealWorld Conduit in Go (`gin/`) with SpecForge in its pipeline: every push fuzzes the API the
job starts and fails only on a defect `.specforge/baseline.json` does not accept. A demo of
SpecForge's `ci` command, not a product.

## How it runs

`.github/workflows/specforge.yml` starts the API with `gin/compose.specforge.yml`, creates two
users with `specforge_identities.py` and runs `ci` from the SpecForge image. The report is kept
as the job's `specforge` artifact.

Secrets: `OPENAI_API_KEY`. The image is private: its package grants this repository read access.

## Running it locally

```
docker compose -f gin/compose.specforge.yml up -d --build
python3 specforge_identities.py http://localhost:8000/api
docker run --rm --network host --user "$(id -u):$(id -g)" -e HOME=/tmp -v "$PWD:/repo" \
  -e OPENAI_API_KEY -e LLM_MODEL=openai/gpt-6.1-terra ghcr.io/spec-forge-testing/specforge:ci-v1 ci
```

Accepting the defects found now: the same with `baseline update` instead of `ci`, then commit
`.specforge/`.
