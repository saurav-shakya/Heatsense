# HeatShield roadmap

Everything left after the deployed skeleton (commit `e09c6b8`). Each item below is also a GitHub issue with the same title.

**Where things stand:** all code items are done and tested (`make test`: 88 backend tests, `make test-data`). What's left needs an account, a console or real data, and is marked "(you)" below: Cloudflare deploy, real ward boundaries + rasters, Twilio sandbox, SNS sandbox number, Bedrock model access, IMD cross-check, Lighthouse run, and the demo video.

## Done

- [x] Repo layout, Makefile, docs
- [x] SAM stack deployed to `us-east-1` (`heatshield-dev`): DynamoDB tables, S3 bucket, EventBridge bus and schedules, HTTP API, 4 Lambdas
- [x] API: `GET /wards`, `GET /wards/{id}/forecast`, `POST /subscribe`, `POST /unsubscribe`, `POST /webhook/whatsapp` (stub)
- [x] Risk engine plumbing: scores every ward hourly for 4 days, writes forecasts and daily summaries, emits `RiskScoresUpdated`
- [x] Alert dispatcher plumbing: event + 07:00/19:00 IST triggers, quiet hours, picks High/Extreme wards and subscribers (logs only)
- [x] Delhi placeholder ward layer (289-cell hex grid) seeded
- [x] Web map: ward map, 4-day picker, top 10 wards, ward detail, subscribe form, English and Hindi
- [x] 24 backend tests, ruff, `sam validate --lint`, frontend build
- [x] Real hazard model, Open-Meteo pulls, IMD-tuned thresholds, replay mode
- [x] WhatsApp/SMS delivery, alert cap and de-duplication, Bedrock advisories, signed webhook with STOP/START and Ask HeatShield
- [x] Phase 1 tooling: Earth Engine export, `build_ward_layer.py`, vulnerability weights
- [x] Map code-split, Devanagari subsets only; fixed the MapLibre worker missing from production builds
- [x] Stretch: officer CSV export

## Research-led features (Oct 2026)

From [docs/research/differentiation.md](docs/research/differentiation.md). The code is done and tested (128 backend tests). Still to do:

- [x] WBGT estimate, hourly work-rest plan, tonight's low and hot nights in the risk engine
- [x] Personal level (thin roof, hot night), nearest verified cooling/water point, OK/SOS check-in with caregiver escalation, ward office checklist, `GET /resources`, `GET /officer/checkins`
- [ ] (you) `make snapshot REPLAY=2024-05-28` so the static map shows the new work plan, tonight and checklist sections (Open-Meteo was unreachable when this branch was built)
- [ ] (you) Replace `data/fixtures/delhi_resources.geojson` with DDMA/MCD cooling centres, Jal Board water points and platform rest points; set `verified: true` per point after a ward officer checks it; `make seed`
- [ ] Pull shortwave radiation and wind from Open-Meteo and switch WBGT to Liljegren (2008)
- [ ] Ward 1991–2020 minimum-temperature normals, so hot nights follow IMD's warm-night rule (≥ 4.5 °C above normal)
- [ ] Protect `GET /officer/checkins` with an officer login before real check-ins exist
- [ ] Interviews before the 2027 season: delivery riders and platform safety leads, contractors, tin-roof households, ward officers (guide in the research report)
- [ ] Validation partner: NPCCHH / IHIP heatstroke reports and 108 call data for Delhi

## Deploy

### Deploy the web map to Cloudflare Pages

Labels: `infra`, `frontend`

The frontend builds and runs locally against the live API, but it isn't published yet.

**Tasks**
- [ ] (you) `cd frontend && npx wrangler login` (one-time)
- [ ] (you) `make deploy-frontend` → Pages project `heatshield`
- [ ] (you) If the URL isn't `https://heatshield.pages.dev`, update `AllowedOrigins` in `backend/template.yaml` (or `parameter_overrides` in `samconfig.toml`) and run `make deploy-backend`
- [ ] (you) Open the live URL on a phone: map renders, day picker works, subscribe works, no CORS errors

**Done when** the live link loads the Delhi map with no console errors.

## Phase 1: data foundation

### Load real Delhi ward boundaries in place of the hex-grid fixture

Labels: `phase-1-data`, `data`

`data/fixtures/delhi_wards.geojson` is a synthetic 289-cell hex grid. Replace it with real MCD ward polygons.

**Tasks**
- [ ] (you) Source the MCD ward GeoJSON (Delhi open data / Datameet). Fall back to OSM `admin_level=10`
- [x] Normalise properties to `wardId`, `name` (keep the ward number in the name, e.g. "Ward 14 Jahangirpuri") (`build_ward_layer.py --id-field/--name-field`)
- [x] Simplify the geometry so `GET /wards` stays well under 1 MB gzipped (`--simplify`, default ~20 m)
- [x] Load it with `seed.py --file ...` and remove the "Sample data" note in the UI once all inputs are real (`make seed WARDS_FILE=...`; the note only shows for `fixture` wards)

**Done when** the map shows real ward shapes and every ward has a row in the Wards table.

### Pre-compute land surface temperature offset per ward (Landsat 8/9)

Labels: `phase-1-data`, `data`

`lstOffset` = the ward's mean summer LST minus the city mean, in °C. Hazard uses it to adjust each ward's heat index.

**Tasks**
- [x] Pull Landsat 8/9 Collection 2 Level-2 ST_B10 scenes for Apr–Jun of a recent year, cloud-masked (Earth Engine script in `data/README.md`; (you) run it)
- [x] Zonal mean per ward, then subtract the city mean (`build_ward_layer.py`)
- [x] Output into the ward GeoJSON properties (a script + Earth Engine snippet instead of a notebook)

**Fallback (PRD risk):** if processing takes too long, ship static per-ward values from MODIS LST (documented in `data/README.md`).

### Pre-compute green cover (NDVI), population density and vulnerability score per ward

Labels: `phase-1-data`, `data`

**Tasks**
- [x] Sentinel-2 L2A NDVI, same season as LST, zonal mean per ward → `ndvi`
- [x] WorldPop 100 m (India) zonal sum ÷ ward area → `popDensity` (people/km²)
- [x] `vulnerabilityScore` V in [0,1]: weighted mix of density (higher is worse) and green cover (lower is worse), plus the share of vulnerable groups where census data exists (`data/scripts/vulnerability.py`, `--groups` CSV)
- [x] Document the weights in `docs/architecture.md`

**Done when** every ward has all four attributes from real data.

## Phase 2: risk engine and map

### Risk engine: pull real Open-Meteo forecasts instead of the placeholder curve

Labels: `phase-2-risk`, `backend`

`backend/functions/risk_engine/app.py` uses `placeholder_hazard()`. Replace it with real forecasts.

**Tasks**
- [x] Fetch hourly temperature, relative humidity and apparent temperature for today + 3 days (batch ward centroids, or a coarse grid and nearest-point lookup) (temperature + humidity on a 0.1° grid; felt temperature is computed, not taken from Open-Meteo)
- [x] Compute the heat index and hazard H in [0,1], adjusted by `lstOffset`
- [x] Store the raw pull in S3 (`raw/forecasts/{date}/{hour}.json`)
- [ ] (you) Cross-check against IMD where available
- [x] Handle API failure: keep the last good scores, log, don't emit `RiskScoresUpdated`
- [x] Tests with a recorded Open-Meteo response (`tests/fixtures/open_meteo_two_points.json`)

### Tune risk level thresholds to IMD heat-index bands

Labels: `phase-2-risk`, `backend`

`heatshield/risk.py` uses placeholder thresholds (0.30 / 0.50 / 0.70).

**Tasks**
- [x] Map the IMD heatwave / severe heatwave criteria and heat-index bands onto H × V
- [x] Backtest on Delhi's hottest recent days (for example May 2024) so they land in High/Extreme (representative 28 May 2024 conditions in `test_risk.py`; (you) re-run on the replay data)
- [x] Update the tests in `backend/tests/test_risk.py`

### Replay mode: demo with a past heatwave's forecast data

Labels: `phase-2-risk`, `backend`, `frontend`

PRD risk: an off-season demo shows no heat.

**Tasks**
- [x] Store a past heatwave's hourly data (for example May 2024) in S3 (`make replay-fetch`; (you) run it, Open-Meteo is reachable from your machine)
- [x] Risk engine accepts `{"replay": "2024-05-28"}` in the event and scores from that data
- [x] `make replay DATE=...` target
- [x] UI shows a clear "Replay of <date>" notice while replay data is live

### Reduce frontend bundle size (code-split MapLibre)

Labels: `frontend`

The production JS bundle is ~1.27 MB (~355 KB gzipped), mostly maplibre-gl. Most users arrive from a WhatsApp link on a phone.

**Tasks**
- [x] Lazy-load `WardMap` with `React.lazy` so the headline and ranked list render first (first-load JS 355 → 76 KB gzipped)
- [x] Only load the Devanagari font weights actually used
- [ ] (you) Check with Lighthouse on mobile

## Phase 3: AI advisories and alerts

### Bedrock advisories per group and language

Labels: `phase-3-alerts`, `backend`

Generate short, group-specific advice in Hindi and English.

**Tasks**
- [x] Choose a model available in us-east-1: `anthropic.claude-opus-5-5` (parameter `AdvisoryModelId`); (you) enable model access in the console
- [x] Prompt constrained to a fixed safety guide and template: answer how bad, when, and what to do in **under 300 characters**, and end with how to stop alerts
- [x] Groups: outdoor worker, parent, elderly. Languages: hi, en
- [x] Cache per (ward level, peak window, group, language) so each refresh makes few Bedrock calls
- [x] Add Bedrock IAM permission to `AlertDispatcherFunction` only (plus the webhook, which the Ask HeatShield bot needs)
- [x] Human-reviewed golden examples in tests (the PRD's example alerts) (templates in `advisory.py`, golden strings in `test_alerts.py`; (you) have a native speaker review the Hindi)

### Deliver WhatsApp alerts via Twilio (sandbox for the demo)

Labels: `phase-3-alerts`, `backend`, `infra`

**Tasks**
- [ ] (you) Twilio account + WhatsApp sandbox; set its inbound URL to `<ApiUrl>/webhook/whatsapp`
- [x] Store the SID and auth token in SSM Parameter Store as SecureString (`/heatshield/dev/twilio/*`), read at cold start (`make twilio-params`)
- [x] Dispatcher sends to subscribers with `channel=whatsapp`
- [x] Record `lastAlertAt`; log the delivery status

### Deliver SMS alerts via Amazon SNS

Labels: `phase-3-alerts`, `backend`, `infra`

Target: elderly users on feature phones (Hindi SMS).

**Tasks**
- [ ] (you) SNS SMS sandbox + a verified test number (DLT rules block unregistered sender IDs for Indian numbers)
- [x] Transactional SMS type, spend limit set (`make sms-setup`)
- [x] Unicode Hindi message under 70 characters per segment, or accept 2 segments (≤ 134 chars, 2 segments)

### Alert rules: max 2 per day, quiet hours, evening + 7 AM sends

Labels: `phase-3-alerts`, `backend`

Quiet hours and evening/morning targeting already exist in `alert_dispatcher/app.py`. Still to do:

**Tasks**
- [x] Enforce at most 2 alerts per user per day using `lastAlertAt` (conditional update to avoid double sends) (`alertDate`/`alertsToday`)
- [x] Don't re-alert on every 3-hour refresh if the level hasn't changed
- [x] Every message ends with how to stop alerts
- [x] Tests for the cap and de-duplication

### WhatsApp webhook: verify Twilio signature, STOP opt-out, Ask HeatShield bot

Labels: `phase-3-alerts`, `backend`

`whatsapp_webhook/app.py` currently returns a fixed reply and must not change state until requests are verified.

**Tasks**
- [x] Validate `X-Twilio-Signature` and reject unsigned requests
- [x] `STOP` → `repo.opt_out()`; `START` → opt back in
- [x] Questions like "Can I go out at 3 PM?" → Bedrock answers using **only** that ward's current forecast + the fixed safety guide (no medical advice)
- [x] Reply in the subscriber's language
- [x] Unknown numbers get the reply: "Subscribe at <link>."

## Phase 4: polish and submission

### Submission: demo video, README, architecture diagram, cost notes

Labels: `phase-4-polish`

**Tasks**
- [ ] (you) 2-minute demo following the PRD script: map → slider to the heatwave day → tap a red ward → live subscribe → Hindi WhatsApp alert → ask the bot → architecture close
- [x] Architecture diagram in the README (Mermaid, rendered by GitHub; export a PNG for the submission form if it needs an image)
- [ ] (you) Cost notes (actual AWS bill during the hackathon); estimates are in `docs/architecture.md`
- [ ] (you) Live link + repo link on the submission form

## Stretch goals

### Stretch: cooling centre finder

Labels: `stretch`, `frontend`, `data`

Nearest shade, water point or cooling centre on the map and in alerts. Source: municipal lists or OSM (`amenity=drinking_water`, shelters).

### Stretch: officer dashboard export

Labels: `stretch`, `frontend`

Ranked ward list for tomorrow, exportable (CSV/PDF) for local authorities. **Done for CSV:** "Download ranked list (CSV)" under the top-10 exports every ward for the selected day (opens in Excel with Hindi intact). PDF not done.

### Stretch: family contact alerts for elderly subscribers

Labels: `stretch`, `backend`

Notify a relative when an elderly user's ward hits Extreme. Needs consent from both numbers and a `familyContact` field on Subscribers.

### Stretch: more languages (Bengali, Marathi, Tamil, …)

Labels: `stretch`, `frontend`, `backend`

Add more languages to `frontend/src/i18n/strings.ts`, the `Language` enum and the advisory prompts. Use matching IBM Plex / Noto fonts per script.
