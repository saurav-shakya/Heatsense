# HeatShield roadmap

Everything left after the deployed skeleton (commit `e09c6b8`). Each item below is also a GitHub issue with the same title.

## Done

- [x] Repo layout, Makefile, docs
- [x] SAM stack deployed to `us-east-1` (`heatshield-dev`): DynamoDB tables, S3 bucket, EventBridge bus and schedules, HTTP API, 4 Lambdas
- [x] API: `GET /wards`, `GET /wards/{id}/forecast`, `POST /subscribe`, `POST /unsubscribe`, `POST /webhook/whatsapp` (stub)
- [x] Risk engine plumbing: scores every ward hourly for 4 days, writes forecasts and daily summaries, emits `RiskScoresUpdated`
- [x] Alert dispatcher plumbing: event + 07:00/19:00 IST triggers, quiet hours, picks High/Extreme wards and subscribers (logs only)
- [x] Delhi placeholder ward layer (289-cell hex grid) seeded
- [x] Web map: ward map, 4-day picker, top 10 wards, ward detail, subscribe form, English and Hindi
- [x] 24 backend tests, ruff, `sam validate --lint`, frontend build

## Deploy

### Deploy the web map to Cloudflare Pages

Labels: `infra`, `frontend`

The frontend builds and runs locally against the live API, but it isn't published yet.

**Tasks**
- [ ] `cd frontend && npx wrangler login` (one-time)
- [ ] `make deploy-frontend` → Pages project `heatshield`
- [ ] If the URL isn't `https://heatshield.pages.dev`, update `AllowedOrigins` in `backend/template.yaml` (or `parameter_overrides` in `samconfig.toml`) and run `make deploy-backend`
- [ ] Open the live URL on a phone: map renders, day picker works, subscribe works, no CORS errors

**Done when** the live link loads the Delhi map with no console errors.

## Phase 1: data foundation

### Load real Delhi ward boundaries in place of the hex-grid fixture

Labels: `phase-1-data`, `data`

`data/fixtures/delhi_wards.geojson` is a synthetic 289-cell hex grid. Replace it with real MCD ward polygons.

**Tasks**
- [ ] Source the MCD ward GeoJSON (Delhi open data / Datameet). Fall back to OSM `admin_level=10`
- [ ] Normalise properties to `wardId`, `name` (keep the ward number in the name, e.g. "Ward 14 Jahangirpuri")
- [ ] Simplify the geometry so `GET /wards` stays well under 1 MB gzipped
- [ ] Load it with `seed.py --file ...` and remove the "Sample data" note in the UI once all inputs are real

**Done when** the map shows real ward shapes and every ward has a row in the Wards table.

### Pre-compute land surface temperature offset per ward (Landsat 8/9)

Labels: `phase-1-data`, `data`

`lstOffset` = the ward's mean summer LST minus the city mean, in °C. Hazard uses it to adjust each ward's heat index.

**Tasks**
- [ ] Pull Landsat 8/9 Collection 2 Level-2 ST_B10 scenes for Apr–Jun of a recent year, cloud-masked
- [ ] Zonal mean per ward, then subtract the city mean
- [ ] Notebook in `data/notebooks/`; output into the ward GeoJSON properties

**Fallback (PRD risk):** if processing takes too long, ship static per-ward values from MODIS LST.

### Pre-compute green cover (NDVI), population density and vulnerability score per ward

Labels: `phase-1-data`, `data`

**Tasks**
- [ ] Sentinel-2 L2A NDVI, same season as LST, zonal mean per ward → `ndvi`
- [ ] WorldPop 100 m (India) zonal sum ÷ ward area → `popDensity` (people/km²)
- [ ] `vulnerabilityScore` V in [0,1]: weighted mix of density (higher is worse) and green cover (lower is worse), plus the share of vulnerable groups where census data exists
- [ ] Document the weights in `docs/architecture.md`

**Done when** every ward has all four attributes from real data.

## Phase 2: risk engine and map

### Risk engine: pull real Open-Meteo forecasts instead of the placeholder curve

Labels: `phase-2-risk`, `backend`

`backend/functions/risk_engine/app.py` uses `placeholder_hazard()`. Replace it with real forecasts.

**Tasks**
- [ ] Fetch hourly temperature, relative humidity and apparent temperature for today + 3 days (batch ward centroids, or a coarse grid and nearest-point lookup)
- [ ] Compute the heat index and hazard H in [0,1], adjusted by `lstOffset`
- [ ] Store the raw pull in S3 (`raw/forecasts/{date}/{hour}.json`)
- [ ] Cross-check against IMD where available
- [ ] Handle API failure: keep the last good scores, log, don't emit `RiskScoresUpdated`
- [ ] Tests with a recorded Open-Meteo response

### Tune risk level thresholds to IMD heat-index bands

Labels: `phase-2-risk`, `backend`

`heatshield/risk.py` uses placeholder thresholds (0.30 / 0.50 / 0.70).

**Tasks**
- [ ] Map the IMD heatwave / severe heatwave criteria and heat-index bands onto H × V
- [ ] Backtest on Delhi's hottest recent days (for example May 2024) so they land in High/Extreme
- [ ] Update the tests in `backend/tests/test_risk.py`

### Replay mode: demo with a past heatwave's forecast data

Labels: `phase-2-risk`, `backend`, `frontend`

PRD risk: an off-season demo shows no heat.

**Tasks**
- [ ] Store a past heatwave's hourly data (for example May 2024) in S3
- [ ] Risk engine accepts `{"replay": "2024-05-28"}` in the event and scores from that data
- [ ] `make replay DATE=...` target
- [ ] UI shows a clear "Replay of <date>" notice while replay data is live

### Reduce frontend bundle size (code-split MapLibre)

Labels: `frontend`

The production JS bundle is ~1.27 MB (~355 KB gzipped), mostly maplibre-gl. Most users arrive from a WhatsApp link on a phone.

**Tasks**
- [ ] Lazy-load `WardMap` with `React.lazy` so the headline and ranked list render first
- [ ] Only load the Devanagari font weights actually used
- [ ] Check with Lighthouse on mobile

## Phase 3: AI advisories and alerts

### Bedrock advisories per group and language

Labels: `phase-3-alerts`, `backend`

Generate short, group-specific advice in Hindi and English.

**Tasks**
- [ ] Choose a model available in us-east-1 (check model access in the console)
- [ ] Prompt constrained to a fixed safety guide and template: answer how bad, when, and what to do in **under 300 characters**, and end with how to stop alerts
- [ ] Groups: outdoor worker, parent, elderly. Languages: hi, en
- [ ] Cache per (ward level, peak window, group, language) so each refresh makes few Bedrock calls
- [ ] Add Bedrock IAM permission to `AlertDispatcherFunction` only
- [ ] Human-reviewed golden examples in tests (the PRD's example alerts)

### Deliver WhatsApp alerts via Twilio (sandbox for the demo)

Labels: `phase-3-alerts`, `backend`, `infra`

**Tasks**
- [ ] Twilio account + WhatsApp sandbox
- [ ] Store the SID and auth token in SSM Parameter Store as SecureString (`/heatshield/dev/twilio/*`), read at cold start
- [ ] Dispatcher sends to subscribers with `channel=whatsapp`
- [ ] Record `lastAlertAt`; log the delivery status

### Deliver SMS alerts via Amazon SNS

Labels: `phase-3-alerts`, `backend`, `infra`

Target: elderly users on feature phones (Hindi SMS).

**Tasks**
- [ ] SNS SMS sandbox + a verified test number (DLT rules block unregistered sender IDs for Indian numbers)
- [ ] Transactional SMS type, spend limit set
- [ ] Unicode Hindi message under 70 characters per segment, or accept 2 segments

### Alert rules: max 2 per day, quiet hours, evening + 7 AM sends

Labels: `phase-3-alerts`, `backend`

Quiet hours and evening/morning targeting already exist in `alert_dispatcher/app.py`. Still to do:

**Tasks**
- [ ] Enforce at most 2 alerts per user per day using `lastAlertAt` (conditional update to avoid double sends)
- [ ] Don't re-alert on every 3-hour refresh if the level hasn't changed
- [ ] Every message ends with how to stop alerts
- [ ] Tests for the cap and de-duplication

### WhatsApp webhook: verify Twilio signature, STOP opt-out, Ask HeatShield bot

Labels: `phase-3-alerts`, `backend`

`whatsapp_webhook/app.py` currently returns a fixed reply and must not change state until requests are verified.

**Tasks**
- [ ] Validate `X-Twilio-Signature` and reject unsigned requests
- [ ] `STOP` → `repo.opt_out()`; `START` → opt back in
- [ ] Questions like "Can I go out at 3 PM?" → Bedrock answers using **only** that ward's current forecast + the fixed safety guide (no medical advice)
- [ ] Reply in the subscriber's language
- [ ] Unknown numbers get the reply: "Subscribe at <link>."

## Phase 4: polish and submission

### Submission: demo video, README, architecture diagram, cost notes

Labels: `phase-4-polish`

**Tasks**
- [ ] 2-minute demo following the PRD script: map → slider to the heatwave day → tap a red ward → live subscribe → Hindi WhatsApp alert → ask the bot → architecture close
- [ ] Architecture diagram image in the README
- [ ] Cost notes (actual AWS bill during the hackathon)
- [ ] Live link + repo link on the submission form

## Stretch goals

### Stretch: cooling centre finder

Labels: `stretch`, `frontend`, `data`

Nearest shade, water point or cooling centre on the map and in alerts. Source: municipal lists or OSM (`amenity=drinking_water`, shelters).

### Stretch: officer dashboard export

Labels: `stretch`, `frontend`

Ranked ward list for tomorrow, exportable (CSV/PDF) for local authorities. The UI already has the ranked top-10 list to build on.

### Stretch: family contact alerts for elderly subscribers

Labels: `stretch`, `backend`

Notify a relative when an elderly user's ward hits Extreme. Needs consent from both numbers and a `familyContact` field on Subscribers.

### Stretch: more languages (Bengali, Marathi, Tamil, …)

Labels: `stretch`, `frontend`, `backend`

Add more languages to `frontend/src/i18n/strings.ts`, the `Language` enum and the advisory prompts. Use matching IBM Plex / Noto fonts per script.
