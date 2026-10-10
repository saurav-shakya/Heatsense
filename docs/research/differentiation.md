# What HeatShield does that Google Weather doesn't

*Synthesis of the four research reports in this folder, and what was built from it. October 2026.*

## The worry

Google already shows the temperature and "feels like", relays official heat warnings in India, runs an AI forecast (WeatherNext 2) and has a Heat Resilience dataset for city planners. A product that is "forecast + heat map + alert" competes with all of that and loses on reach. So we asked: **which heat problem in an Indian city is still unsolved, for whom, and who pays to solve it?**

## What the evidence says

**1. Temperature is the wrong number for the people who die.** ([problem-evidence.md](problem-evidence.md))

- **Humid heat.** Young, healthy people reach their limit at a wet-bulb temperature of about 31 °C, not the 35 °C once assumed (Vecellio 2022). Delhi's rising humidity has cancelled out a small fall in air temperature (CSE 2024). A 38 °C humid day is more dangerous for a worker than a 42 °C dry one, and the temperature reading hides that.
- **Hot nights.** Hot nights carry mortality risk of their own. In Ahmedabad, deaths roughly doubled on nights above 30 °C that followed days above 45 °C (secondary report, verify). Delhi's warmest night in 14 years was 32.4 °C, in May 2026.
- **Indoor heat.** Tin and asbestos roofs make homes hotter than outdoors at night, and in one Delhi trial a tin-roof room reached 45.8 °C. No weather app models the room a person is actually in.
- **Outdoor work.** India lost about 247 billion potential labour hours to heat in 2024 (Lancet Countdown). The occupational standard is WBGT with work-rest ratios (ACGIH, ISO 7243), not "avoid going out 12–4".

**2. Warnings fail when people don't see themselves at risk or don't know what to do.** ([warning-systems.md](warning-systems.md))

- **People don't feel at risk.** Only 41% of people who saw a heat alert in England acted, mostly because they didn't think heat put *them* at risk. Older people who did see themselves at risk were 3.6× more likely to act (Queensland).
- **Indian heat plans lack local data.** Only 10 of 37 plans use local thresholds and only 2 assess who is vulnerable (CPR 2023). Delhi's cooling zones went largely unused and its work-hour ban wasn't enforced.
- **The data loop is broken.** Official heat deaths are a tiny fraction of the real toll (14 confirmed deaths against 7,192 suspected heatstroke cases in 2025), so nobody can tell whether a plan worked.

**3. Google is strong where we shouldn't compete, and absent where we should.** ([competitor-teardown.md](competitor-teardown.md))

- **Where Google wins.** Google wins on forecast skill, reach, and seasonal planning data such as roof albedo and land-surface temperature. We should *use* forecasts, not build them.
- **What Google won't do.** It defers to IMD/NDMA on warnings, won't hold personal vulnerability data, won't run on WhatsApp (Meta's channel), and doesn't do city-by-city operations or procurement.
- **Closest neighbours.** These are SHRAM (worker heat risk, district-level, academic) and SEEDS/Microsoft "Sunny Lives" (building-level indoor heat for slum residents, no alerts). Government SACHET alerts now reach every phone but are district-wide and the same for everyone.

**4. Someone will pay.** ([buyers-and-market.md](buyers-and-market.md))

- **Government.** Heatwaves became a notified disaster for 2026–31, so state disaster funds can now pay for heat work.
- **Delivery platforms.** These are the readiest private buyer: Swiggy runs 900+ rest zones, Eternal (Zomato/Blinkit) 4,500+ rest points, and NDMA's 2025 advisory asks platforms to map rest zones in their apps and pause work from 11 am to 4 pm on high-alert days.
- **Insurers.** Parametric heat insurance (SEWA with ICICI Lombard and Swiss Re; Go Digit) keeps paying out nothing because its temperature triggers are set too high. Insurers need hyper-local, validated heat data.

## Segment scorecard

Scores are 1–5, judged from the reports.

| Segment | Harm | Current tools fail them | Can pay | Our data edge | Buildable now | Total |
|---|---|---|---|---|---|---|
| **Outdoor workers, sold through delivery platforms and contractors** | 5 | 5 (no ward-level work-rest advice anywhere) | 4 (platforms already spend; NDMA advisory) | 4 | 5 | **23** |
| City officials (DDMA, MCD ward offices) | 4 | 4 | 3 (new disaster-fund line, slow procurement) | 5 | 4 | 20 |
| Vulnerable people at home (elderly, tin roofs) | 5 | 5 | 1 (paid for by the city, NGOs or grants) | 4 | 4 | 19 |
| Insurers (parametric triggers) | 3 | 4 | 4 | 3 (needs a validated track record first) | 2 | 16 |

## The choice

**Lead with outdoor workers: hourly work-rest plans by ward, sold to delivery platforms and large contractors as heat-safety compliance.** It is where harm, a paying buyer and a clear gap meet, and the NDMA advisory gives platforms a reason to buy now.

**Then two follow-ons, on the same engine:**

1. **The city's heat-plan operations layer.** It gives each ward office a daily checklist (open cooling, shift work, check on people living alone, keep shelters open on hot nights, fill cooling gaps) and the check-in counts. It is funded from the new disaster-fund line and supports the "ward thresholds + vulnerability" that CPR found missing.
2. **Protection at home.** This covers tin-roof and night-heat alerts plus the elderly check-in with caregiver escalation, delivered through the city and NGOs (Mahila Housing Trust, SEWA, ASHA networks), not sold to residents.

Insurance comes last, once a season of ward-level WBGT and night-heat data exists to design triggers from.

**One line:** Google tells you it's hot. HeatShield tells a delivery rider in Jahangirpuri to stop from 11 to 5 and where the nearest water point is, tells his grandmother under a tin roof that tonight won't cool below 32 °C and checks she's OK, and tells the ward office what to open.

## What was built (this branch)

| Evidence | Change | Where |
|---|---|---|
| WBGT is the occupational standard; humidity matters | Estimated WBGT per ward-hour: Stull wet bulb, ISO 7243 shade form, +3 °C solar load | `backend/layers/common/heatshield/heat.py` (`wet_bulb_c`, `wbgt_c`) |
| ACGIH work-rest limits | Hourly work plan for moderate work (minutes of work per hour, stop hours) in each day's summary | `heat.work_minutes_per_hour`, `risk_engine/app.py` (`work_plan`) |
| Hot nights kill independently | Tonight's low per ward (with the ward's heat-island offset); ≥ 30 °C = hot night | `risk_engine/app.py` (`_night_min`), `heat.HOT_NIGHT_C` |
| Tin roofs: hotter indoors; many deaths on lower-level days | Personal level: one step up under thin roofs; hot night counts as High for elderly people, parents and thin-roof homes | `heatshield/personal.py`, alert dispatcher |
| People act when they know what to do and where to go | Nearest *verified* cooling, water or rest point, open at the peak hour, named in alerts and in the bot's SOS reply | `heatshield/resources.py`, `GET /resources`, map layer |
| Check-in systems for isolated elderly people; anti-scam | Elderly alerts on the worst days ask for OK or SOS; SOS gets 108 advice and the nearest cool place, alerts the caregiver, and counts for the ward office. Every ask says HeatShield never asks for money or OTPs | `whatsapp_webhook/app.py`, `GET /officer/checkins` |
| Heat plans lack ward-level operations | Daily ward office checklist (`open_cooling`, `shift_work`, `check_vulnerable`, `night_shelter`, `cooling_gap`) on the map and in the CSV export | `heatshield/actions.py`, `WardPanel.tsx`, `export.ts` |

Sample cooling and water points (`data/fixtures/delhi_resources.geojson`) are marked `verified: false`. The map shows them labelled "sample", and alerts never use them.

## Known limits and next steps

- **Numbers to verify.** This environment could not open web pages, so every figure in the reports comes from search-result excerpts of the cited URLs. Re-check the ones marked **[verify]** against the primary sources before using them in a pitch or a government proposal.
- **WBGT is an estimate.** It has no radiation or wind input yet. The next step is to pull shortwave radiation and wind from Open-Meteo and use Liljegren et al. (2008), which is what the OSHA calculator uses.
- **The hot-night threshold is absolute (30 °C).** IMD's warm-night rule is relative to normal (minimum ≥ 4.5 °C above normal). Add 1991–2020 ward normals.
- **Validate against outcomes.** Get 108 ambulance call data and IHIP heatstroke reports from the health department (NPCCHH) for the 2027 season, and pre-register an Ahmedabad-style evaluation.
- **Talk to users before the season** (Feb–Mar 2027): 10 delivery riders and 2 platform safety leads, 5 construction contractors, 10 elderly residents or caregivers in tin-roof homes, and 3 ward officers. The interview guide is in the shareable report.
