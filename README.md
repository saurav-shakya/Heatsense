# HeatShield

Ward-level heat risk for Indian cities, with plain-language alerts on WhatsApp and SMS in Hindi and English. Built for the WeMakeDevs x AWS hackathon, Track 02: Heat and Water. The pilot city is Delhi.

HeatShield combines the weather forecast with how exposed each ward is (surface heat, green cover, population density) and scores every ward as `Risk = Hazard × Vulnerability` every 3 hours. Residents subscribe by ward and get a short alert the evening before and the morning of a High or Extreme day. Ward officers use the map to see where water points and cooling centres matter most.

> **Status: deployed skeleton.** The infrastructure, API, map and subscribe flow work end to end. The ward layer and hazard values are placeholders until the real data pipeline (Phase 1–2) lands. See [docs/architecture.md](docs/architecture.md).

## Repository layout

```
backend/     AWS SAM app: template.yaml, 4 Python Lambdas, shared layer, tests
  functions/   api · risk_engine · alert_dispatcher · whatsapp_webhook
  layers/common/heatshield/   config, models, risk scoring, DynamoDB access
data/        ward layer fixtures + scripts (hex grid, seeding); Phase 1 pipeline notes
frontend/    React + Vite + MapLibre web map, deployed to Cloudflare Pages
docs/        architecture, data model, API contract
Makefile     every command you need
```

## Prerequisites

- AWS CLI v2 with the `saurav-cli` profile (`aws sts get-caller-identity --profile saurav-cli`)
- AWS SAM CLI (`uv tool install aws-sam-cli`), [uv](https://docs.astral.sh/uv/), Python 3.12
- Node 22+ (Wrangler is a dev dependency, so there's nothing to install globally)
- Cloudflare account: run `npx wrangler login` once inside `frontend/`

## Commands

```bash
make install          # uv sync + npm install
make test             # backend unit tests (pytest + moto)
make lint             # ruff, sam validate --lint, tsc
make deploy-backend   # sam build && sam deploy  -> stack heatshield-dev (us-east-1)
make seed             # load the Delhi ward layer into S3 + DynamoDB
make invoke-risk      # score all wards now instead of waiting for the schedule
make dev              # local map at http://localhost:5173 against the deployed API
make deploy-frontend  # build + publish to Cloudflare Pages (project "heatshield")
make deploy           # both
make logs FN=risk-engine
make destroy          # delete the stack (asks first; subscribers table is kept)
```

## Build plan

1. **Data foundation**: real MCD ward boundaries, Landsat LST, Sentinel-2 NDVI, WorldPop density per ward ([data/README.md](data/README.md))
2. **Risk engine and map**: Open-Meteo pulls, the real `H × V`, IMD-tuned thresholds, replay mode for an off-season demo
3. **AI and alerts**: Bedrock advisories per group and language, Twilio WhatsApp + SNS SMS, quiet hours and the 2-a-day cap, Ask HeatShield bot
4. **Polish**: demo video, cost notes, architecture diagram
