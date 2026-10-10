# A. Health Evidence: Who Urban Heat Harms in India, and How

*Research brief for HeatShield (ward-level heat-risk alerts, pilot Delhi). Compiled 2026-10-10.*

> **Method note (read first).** In this research environment, the network policy blocked direct page fetches (WebFetch/curl were denied for pmc.ncbi.nlm.nih.gov, mausam.imd.gov.in, ndma.gov.in, wikipedia, CDC, BoM and others). Every figure below comes from web-search extracts that quote the listed URL. I did not read any of these sources in full. I dropped figures that the search results flagged as unverifiable or contradictory, or I flag them inline. Before any number goes into investor, government or clinical material, check it against the primary PDF. Items marked **[verify]** most need that check.

---

## 1. Heat mortality and morbidity in India

**Ahmedabad Heat Action Plan (HAP) evaluation.** Hess et al. (2018, *J. Environ. Public Health*, DOI 10.1155/2018/7973519) compared summer all-cause mortality in 2014–2015 (after the HAP) with a 2007–2010 baseline. They used distributed-lag nonlinear models and incidence-rate ratios on HAP warning days [1]. After the HAP, extreme heat and HAP warnings were linked to lower summertime all-cause mortality, and the largest declines came at the highest temperatures [1]. The headline estimate is **~1,190 avoided deaths per year** [1][2], with a reported 95% CI of 162–2,218 [2]. The Ahmedabad HAP document cites **2,380 deaths avoided over the whole post-HAP period** [3]. This is consistent with ~1,190/yr × 2 years, but treat that reconciliation as **[verify]**. Critics note that the study cannot fully separate the HAP's effect from other factors [4].

**Long-run trend.** Mazdiyasni et al. (2017, *Science Advances*) used IMD data for 1960–2009. They found that mean summer temperatures in India rose by more than 0.5 °C, and that this went with a **146% increase in the probability of heat-wave mortality events killing more than 100 people** [5][6]. Over the same period, heat-wave days increased by about 25% across most of India [6]. The study defined a heat wave as three or more consecutive days above the 85th percentile of the hottest month's temperature [5].

**National burden context.** Fu et al. (2018, *PLoS Medicine*) used Million Death Study data for 2001–2013. They found that heat's excess mortality appears within **0–1 days**, while cold effects last up to two weeks [7][8]. The lag matters for alert timing. In that study most temperature-attributable deaths came from moderate cold, not extreme heat [8].

**2024–2025 counts and under-counting.**
- **2024:** NCDC data obtained under the RTI Act recorded **~48,000 heatstroke cases and 159 deaths** [9]. The Health Ministry told the Lok Sabha **360 deaths** in 17 states (1 March–25 July). HeatWatch's analysis of news reports counted **733 heatstroke deaths** in the same 17 states between March and June [10].
- **2025:** NCDC/IDSP recorded **7,192 suspected heatstroke cases and 14 confirmed deaths** (1 March–24 June) [11]. HeatWatch counted **at least 84 deaths** from media reports (Feb–Jul), led by Maharashtra (17), Uttar Pradesh (15) and Telangana (15) [12].
- **Why the counts diverge:** IDSP depends on hospital reporting, so it misses deaths outside facilities and deaths not diagnosed as heat-related [11]. Heat is often left off death certificates. NCRB (police inquest) figures run higher because they need no clinical confirmation [10]. India has no nationally representative source for heat deaths [12].

*Takeaway:* Official "heatstroke deaths" undercount the true heat toll by a large factor. Most heat mortality appears as excess all-cause deaths (cardiovascular, renal, respiratory), not as coded heatstroke. Do not use official death counts to calibrate the product.

---

## 2. Humid heat, physiology and the right index

**Theoretical ceiling.** Sherwood & Huber (2010, *PNAS*) argued that sustained wet-bulb temperature (Tw) above **35 °C** causes hyperthermia, because the body can no longer shed metabolic heat. They noted that observed peak Tw at the time never exceeded **31 °C** [13].

**Empirical limits are lower.** Vecellio et al. (PSU HEAT Project, *J. Appl. Physiol.* 2022, e-pub Dec 2021) tested young, healthy adults doing light activity. **No subject's critical Tw reached 35 °C.** In warm-humid conditions (36–40 °C air) the critical Tw averaged **30.55 ± 0.98 °C** [14][15]. Penn State reported critical Tw of **30–31 °C in warm-humid** air and **25–28 °C in hot-dry** air [15]. The authors expect older adults' limits to be lower still [15]. In other words, dry heat can also be dangerous at a low Tw.

**Why air temperature or "feels like" misses risk.**
- The **Heat Index** uses only temperature and humidity and is calculated **for shade** [16].
- **WBGT** also accounts for **sun, wind and cloud**. More cloud or wind lowers WBGT, while the heat index stays the same [16]. NWS advises using WBGT for outdoor work or vigorous activity in full sun [16].
- WBGT still leaves out workload, acclimatization and clothing [17]. That is why occupational tables pair WBGT with work intensity.
- **Delhi-specific:** CSE's 2001–2024 analysis found rising humidity in Delhi **cancelled out a small fall in air temperature**, so heat stress rose even where air temperature did not [18]. In summer 2023 Delhi had **14 days with daily-average heat index above 41 °C** [18].

**WBGT work/rest thresholds: ACGIH TLV screening table (WBGT °C)** [19][20]. The table assumes an 8-hour day, a 5-day week and normal work clothing. The values are screening limits, not prescriptions.

| Work share of each hour | Acclimatized TLV: Light | Moderate | Heavy | Very heavy | Unacclimatized Action Limit: Light | Moderate |
|---|---|---|---|---|---|---|
| 75–100% | 31.0 | 28.0 | — | — | 28.0 | 25.0 |
| 50–75% | 31.0 | 29.0 | 27.5 | — | — | — |
| 25–50% | 32.0 | 30.0 | 29.0 | 28.0 | — | — |
| 0–25% | 32.5 | 31.5 | 30.5 | 30.0 | — | — |

"—" means no screening value is given, so a detailed analysis or physiological monitoring is needed [19][20]. The unacclimatized cells for the lower rows were not retrieved and are left blank rather than guessed. Clothing adjustments apply; for example, about +3 °C for double-layer woven clothing [19]. The acclimatized values match across the 2016–2023 editions quoted by secondary sources. Check the current ACGIH booklet **[verify]**.

**ISO 7243:2017 reference WBGT values (°C), by metabolic class** [21]:

| Class (metabolic rate) | Example | Acclimatized | Unacclimatized |
|---|---|---|---|
| 0 Rest (≤65 W/m²) | resting | 33 | 32 |
| 1 Low (65–130) | light assembly | 30 | 29 |
| 2 Moderate (130–200) | handling, operating | 28 | 26 |
| 3 High (200–260) | sustained construction | 26 / 25 (air movement / none) | 23 / 22 |
| 4 Very high (>260) | — | 25 / 23 | 20 / 18 |

These values come from a French calculator citing NF EN ISO 7243:2017, not from the ISO text itself **[verify]**. A 2023 *J. Appl. Physiol.* study supports a roughly constant **3 °C** reduction in the WBGT limit for unacclimatized workers [22].

**WBGT approximations from temperature and humidity.**
- **Simplified WBGT (sWBGT, the "Australian BoM" approximation):**
  **WBGT ≈ 0.567·Ta + 0.393·e + 3.94**, where Ta is air temperature in °C and *e* is vapour pressure in hPa [23][24].
  The commonly paired vapour-pressure formula is **e = (RH/100) × 6.105 × exp(17.27·Ta / (237.7 + Ta))** [25]. That pairing was confirmed only through a third-party API's documentation, so treat the BoM attribution as **[verify]**.
  Limitations: sWBGT ignores radiation and wind and assumes moderately high sun and light wind. It can overestimate stress in windy or cloudy conditions and underestimate it in hot, dry, sunny conditions [24]. A study also found that it greatly overestimates heat stress in hot-humid areas [25].
- **Liljegren et al. (2008, *JOEH* 5(10):645–655):** a physically based heat- and mass-transfer model. Inputs are temperature, RH, wind speed, pressure, and date/time/location (for solar radiation). OSHA's outdoor WBGT calculator uses it [26]. A methods comparison recommends it for population-level work [26]. The original paper reports predictions within ±1 °C of measured WBGT **91–100%** of the time [26].

---

## 3. Night-time heat

- **IMD "warm night":** declared when a station's maximum is at least 40 °C (plains), 37 °C (coastal) or 30 °C (hills) **and** the minimum temperature departs from normal by **≥4.5 °C** [27]. (One secondary source also cites a "very warm night" at a departure above 6.4 °C. That is unverified, so it is not used here.)
- **Mortality evidence:** In 28 East Asian cities, mortality risk on days with hot nights was up to **50% higher** than on days without them (He et al., *Lancet Planetary Health* 2022) [28]. A 2025 study of 178 locations using hourly temperatures found that controlling for daily minimum temperature left the hot-night association almost unchanged. This suggests hot nights carry risk of their own [29].
- **India:** National India studies use daily mean temperature, not minimum temperature [29]. An IIPH study of Ahmedabad (2001–2016), reported second-hand, found mortality **roughly doubled** on nights above 30 °C that followed days above 45 °C, compared with 28–30 °C nights [29] **[verify primary paper]**.
- **Delhi is losing night cooling:** Average land-surface cooling from day peak to night low fell from **12.3 °C (2001–10) to 11.2 °C (2014–23)**. The urban core cools about **3.8 °C less** than the peri-urban fringe [30]. CSE reported that on 25 May 2026 Delhi had its **warmest night in 14 years (32.4 °C)** [30].

---

## 4. Indoor heat in informal housing

- **Houses stay hotter than outdoors at night.** A multi-site South Asian logger dataset (Delhi, Yavatmal, Jalna, Dhaka, Faisalabad; *Scientific Data* 2022) found that indoor temperatures track outdoor ones by day. Houses then **cool more slowly in the evening and night**, so mean indoor temperature **exceeds** outdoor. In April, **tin-roof homes averaged 33.4 °C indoors versus 32.8 °C outdoors** [31]. The authors argue that outdoor-station data underestimate chronic heat stress, especially at night, in dense informal neighbourhoods [32].
- **Ahmedabad slums by roof type** (mean indoor ambient temperature): **asbestos sheet 36.83 ± 2.08 °C**, **tin 35.8 ± 1.02 °C**, RCC 33.75 ± 0.76 °C, ModRoof 33.8 ± 1.03 °C [31]. The same study found an outdoor-minus-indoor gap of **5.39 °C with cool roofs versus 4.20 °C without** (daytime) [33].
- **Delhi community cool-roof trial:** the tin-roof control building reached **45.8 °C** indoors, while the cool-roof models reached **33.1–33.8 °C** [32].
- **Mahila Housing Trust (MHT):** reports that solar-reflective paint lowers indoor temperature by **5–6 °C** and lower-cost options by **2–5 °C** [34]. Another account found paint on tin cut peaks by only **about 1 °C**, compared with up to **4.5 °C** for ModRoof [31]. These figures are NGO or secondary reports, not controlled trials. MHT and the University of Chicago are testing reflective roofs in Delhi informal settlements [32].
- **Kolkata:** in 123 slum dwellings, indoor heat stress was **greater and lasted longer** than in rural houses under similar outdoor conditions. The hottest homes had cement walls with tin or clay-tile roofs [31].

*Takeaway:* Roof material is a first-order modifier of exposure. A tin or asbestos roof can add several °C, and these homes stay hot through the night, when outdoor readings suggest relief.

---

## 5. Outdoor workers

- **ILO (2019), *Working on a Warmer Planet*:** India lost **4.3% of working hours in 1995** and is projected to lose **5.8% in 2030**, equivalent to **34 million full-time jobs**. Agriculture takes most of the loss, with construction a growing share [35].
- **Lancet Countdown:** the 2024 India data sheet reported **181 billion potential labour hours lost in 2023** (50% above the 1990s average) and **US$141 billion in potential income loss** [36]. The 2025 report found **247 billion hours lost in 2024** [36]. It also reported **419 hours lost per person per year** (124% above the 1990s) and 366 more hours per person of heat stressful enough to affect outdoor work [37]. Press coverage reported US$194 billion in income loss for 2024, from a single source **[verify]** [36].
- **Kidney injury:** Venugopal et al. (*Kidney Int. Rep.*) studied salt-pan workers in Tamil Nadu. Earlier work at the same pans found **~90% of workers** worked above international heat-exposure limits, with a median water intake of **1 litre per 8-hour shift** [38]. In Odisha, a study of 1,136 agricultural workers found **157 potential heat-stress nephropathy cases** [38]. A review lists acute kidney injury, kidney stones and chronic kidney disease (CKD) among heat-driven hospital admissions [38].
- **Gig and delivery riders:** In a 2024 TGPWU–HeatWatch survey (Telangana), **52% reported heat exhaustion and 30% heat-stroke symptoms** [39][40]. A randomised trial in **Delhi and Gurugram (May–June 2025, n = 276 delivery workers)** tests heatwave-triggered cash transfers against symptoms such as headache, vomiting and fatigue; its results were not found [41]. Earnings fall in heat: Bengaluru riders reportedly dropped from 20–25 orders per day to 15 or fewer [40].

---

## 6. Vulnerable groups

- **Older adults:** have a reduced ability to sweat and regulate body temperature, and more often have heart, lung or kidney disease [42][43]. Between 2014 and 2023, each Indian adult over 65 had **8.4 heatwave days per year**, **58% more** than in 1990–99 [44].
- **Infants and children:** have immature thermoregulation [42]. Under-5s absorb heat more readily and produce more metabolic heat [43]. Each Indian infant had **7.7 heatwave days per year**, **47% more** than in 1990–99 [44].
- **Pregnancy:** a meta-analysis of 70 studies in 27 countries (Chersich et al., *BMJ* 2020) found the odds of **preterm birth rise 5% per 1 °C** (OR 1.05, 1.03–1.07) and **16% during heatwaves** (OR 1.16, 1.10–1.23). **Stillbirth rises 5% per 1 °C** (1.01–1.08). The largest effects were in lower socioeconomic groups [45].
- **Medications (CDC clinical guidance):**
  - **Reduced thirst:** diuretics, ACE inhibitors, ARBs.
  - **Impaired thermoregulation:** antipsychotics, anticholinergics, stimulants.
  - **Reduced sweating:** TCAs, antipsychotics, anticholinergics.
  - **Highest-risk combination:** an ACE inhibitor or ARB taken with a diuretic.

  CDC describes this as expert opinion [46]. Beta-blockers and antiplatelet drugs have been linked to a higher risk of heart attack in heat (small German study) [46].
- **Chronic disease and isolation:** cardiovascular, respiratory and kidney disease and social isolation all raise risk [43].

---

## 7. Indian official definitions

- **IMD heat wave (plains):** maximum temperature **≥40 °C** and departure from normal **4.5–6.4 °C** = heat wave; departure **>6.4 °C** = severe heat wave. Absolute criteria: **≥45 °C** = heat wave, **≥47 °C** = severe [27]. Coastal stations use 37 °C and hills 30 °C as the base threshold [27]. For declaration, the criteria must be met at **at least 2 stations in a sub-division on 2 consecutive days**, and the heat wave is declared on day 2 [27].
- **NDMA:** guidelines on heat wave action plans were issued in 2016 and revised in 2017 and **2019** (the version in force). They require states and cities to carry out vulnerability and risk assessment and to set departmental roles, communication strategy, hospital preparedness and awareness campaigns. The 2019 revision added emphasis on **worker acclimatisation** [47]. All of this NDMA material is secondary; the primary text could not be opened **[verify]**.
- **The gap:** IMD criteria use **station air temperature only**. They take no account of humidity, night-time minimum (outside the separate warm-night rule), solar load or indoor conditions. That leaves out several of the pathways in sections 2–4.

---

## Implications for product

1. **Use WBGT, not air temperature or heat index, as the core hazard metric.** Compute outdoor WBGT with Liljegren (sun and wind aware) where radiation and wind data exist. Fall back to sWBGT only with known bias. Map alerts to **ACGIH/ISO work-intensity thresholds** (e.g., moderate work, acclimatized: caution at 28 °C, stop or rest from about 30–31.5 °C), not to IMD's ≥40 °C [16][19][21][26]. Delhi's humidity trend means air-temperature alerts will miss dangerous humid days [18].
2. **Make night-time heat its own alert.** Track Tmin and evening cooling, and alert on IMD warm-night conditions (Tmin departure ≥4.5 °C) and consecutive hot nights. Hot nights carry independent mortality risk, and Delhi's core cools less every decade [27][28][29][30].
3. **Estimate indoor heat, not just outdoor.** Add a roof-type and housing modifier, using ward slum share or self-reported roof type (tin, asbestos, RCC). Asbestos and tin homes run about 2–3 °C hotter than RCC and stay above outdoor temperature at night [31]. Advice should cover what to do *inside* the home.
4. **Personalise thresholds by vulnerability.** Let users flag age over 65, infants under 5, pregnancy, chronic disease and medications. Lower their trigger thresholds; ISO suggests about 3 °C lower for unacclimatized people as one anchor [22]. Send medication-specific prompts, for example on diuretics plus ACE inhibitors or ARBs [45][46].
5. **Build worker mode around work/rest schedules, not "stay indoors".** For construction, street-vending and gig workers, push hour-by-hour rest and water guidance (a median of ~1 L per 8-hour shift, as observed among salt-pan workers, is far too little [38]). Offer advice employers and platforms can act on. Heat costs workers wages, so the advice needs to be affordable [35][36][38][39].
6. **Alert early and respond on the same day.** Heat mortality appears within 0–1 days [8]. Send next-day forecasts the evening before and hour-level warnings in the morning.
7. **Do not validate against official death counts.** They miss most deaths (14 confirmed deaths in 2025 against 7,192 suspected cases) [11]. Track outcomes with all-cause excess mortality, hospital and ambulance data, and user-reported symptoms. Pre-register evaluation in the Ahmedabad style, measuring avoided deaths before and after, to build credibility with municipal buyers [1].
8. **Speak the official language but go beyond it.** Map HeatShield levels to IMD and city heat action plan color codes so authorities can adopt them. Make clear where ward-level WBGT, night-time and indoor signals add warning that IMD's station-based criteria lack [27][47].

---

## Sources

1. Hess JJ, Lm S, Knowlton K, et al. "Building Resilience to Climate Change: Pilot Evaluation of the Impact of India's First Heat Action Plan on All-Cause Mortality." *J Environ Public Health* 2018:7973519. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6236972/ (abstract via https://www.preventionweb.net/publication/building-resilience-climate-change-pilot-evaluation-impact-indias-first-heat-action)
2. University of Washington Emergency Medicine news; Mavalankar D (IIPH-G), "Ahmedabad Heat Action Plan," GIZ webinar slides, 2024. https://em.uw.edu/node/344 ; https://community.connective-cities.net/system/files/2024-12/giz%20final%20Dr%20Dileep%20Mavalankar%20IIPHG%20for%20%20GIZ%20webinar%2019-4-2024.pdf
3. Ahmedabad Municipal Corporation. *Ahmedabad Heat Action Plan 2018/2019.* https://heathealth.info/wp-content/uploads/ahmedabad-heat-action-plan-2018.pdf
4. "Message Sent, Now What? A Critical Analysis of the Heat Action Plan in Ahmedabad, India." *Urban Science* 4(4):53, 2020. https://www.mdpi.com/2413-8851/4/4/53
5. Mazdiyasni O, AghaKouchak A, et al. "Increasing probability of mortality during Indian heat waves." *Science Advances* 3(6), 2017. https://repository.library.noaa.gov/view/noaa/24732 ; summary https://journalistsresource.org/?p=54109
6. UC Irvine Engineering news / Associated Press, 2017. https://engineering.uci.edu/node/10108 ; https://www.washingtontimes.com/news/2017/jun/7/study-indias-rising-temperatures-are-already-deadl/
7. Fu SH, Gasparrini A, Rodriguez PS, Jha P. "Mortality attributable to hot and cold ambient temperatures in India: a nationally representative case-crossover study." *PLoS Med* 15(7):e1002619, 2018. https://journals.plos.org/plosmedicine/article?id=10.1371%2Fjournal.pmed.1002619
8. Science Trends summary of Fu et al., 2018. https://sciencetrends.com/hot-temperature-has-highest-mortality-risk-but-moderately-cold-temperature-contributed-to-the-most-deaths-in-india
9. PTI / The Tribune; Deccan Herald, 2025 (NCDC RTI data). https://www.tribuneindia.com/news/science-technology/india-recorded-over-7000-suspected-heatstroke-cases-14-deaths-in-march-june-period-rti/amp
10. HeatWatch India. "Struck by Heat: A News Analysis of Heatstroke Deaths in India in 2024." https://www.heatwatch.in/report/press-release-new-report-struck-by-heat-a-news-analysis-of-heatstroke-deaths-in-india-in-2024/ ; Down To Earth https://www.downtoearth.org.in/climate-change/seeing-red-india-had-over-700-heat-deaths-in-2024-much-higher-than-official-toll-claim-scientists ; The Quint https://www.thequint.com/climate-change/india-heatwave-heatstroke-deaths-mortality-data
11. Deccan Herald (PTI), "India recorded over 7,000 suspected heatstroke cases," 28 Jul 2025. https://www.deccanherald.com/dhie/news-and-trends/2025/07/28/india-recorded-over-7000-suspected-heatstroke-cases
12. Assam Tribune, "India recorded 84 heatstroke deaths in 2025 summer, true toll likely higher," 2025 (HeatWatch). https://assamtribune.com/national/india-recorded-84-heatstroke-deaths-in-2025-summer-true-toll-likely-higher-report-1589006
13. Sherwood SC, Huber M. "An adaptability limit to climate change due to heat stress." *PNAS* 107(21):9552–9555, 2010. https://docs.lib.purdue.edu/easpubs/79 ; https://www.purdue.edu/newsroom/research/2010/100504HuberLimits.html
14. Vecellio DJ, Wolf ST, Cottle RM, Kenney WL. "Evaluating the 35 °C wet-bulb temperature adaptability threshold for young, healthy subjects (PSU HEAT Project)." *J Appl Physiol* 132(2), 2022. https://pure.psu.edu/en/publications/evaluating-the-35c-wet-bulb-temperature-adaptability-threshold-fo/
15. Penn State News, "Humans can't endure temperatures and humidities as high as previously thought," 2022. https://psu.edu/news/research/story/humans-cant-endure-temperatures-and-humidities-high-previously-thought
16. US National Weather Service, "Wet Bulb Globe Temperature." https://www.weather.gov/gid/WBGT ; https://www.weather.gov/mpx/wbgt
17. Klimo Insights, "Heat Index vs WBGT." https://klimoinsights.com/resources/heat-index-vs-wbgt/
18. Centre for Science and Environment, "Decoding the Urban Heat Stress among Indian cities," 2024. https://cseindia.org/cse-study-tracks-heat-wave-exposes-dangerous-trends-in-india-s-biggest-cities-12205 ; https://www.downtoearth.org.in/amp/story/urbanisation/indian-cities-no-longer-cooling-down-at-night-finds-cse-study
19. Canadian Centre for Occupational Health and Safety (CCOHS), "Hot Environments – Control Measures" (reproduces ACGIH TLV screening table). https://ccohs.gc.ca/oshanswers/phys_agents/heat_control.html ; reprint https://ilt.safetynow.com/hot-environments-control-measures-fact-sheets/?print=pdf
20. Minnesota DLI, STD 5-1.3 (ACGIH 2023 criteria notes). https://www.dli.mn.gov/sites/default/files/pdf/STD_5-1.3_indoor_ventilation_and_temperature.pdf
21. Travail-Industrie, WBGT calculator citing NF EN ISO 7243:2017 / INRS ED 6373. https://travail-industrie.com/outils/calculateur-wbgt-stress-thermique-chaleur
22. "Distribution of upper limit of the prescriptive zone values for acclimatized and unacclimatized individuals." *J Appl Physiol* 2023, DOI 10.1152/japplphysiol.00724.2022. https://pure.psu.edu/en/publications/distribution-of-upper-limit-of-the-prescriptive-zone-values-for-a/
23. "Key role of the Madden-Julian Oscillation on tropical and subtropical humid heat and heatwaves," arXiv 2509.17526, 2025. https://arxiv.org/pdf/2509.17526
24. *Nature Communications* table of heat-stress indices (PMC7695704, Table 1). https://pmc.ncbi.nlm.nih.gov/articles/PMC7695704/table/Tab1
25. Oanor WBGT API documentation; review table PMC9206009. https://oanor.com/api/wbgt-api/openapi.json ; https://pmc.ncbi.nlm.nih.gov/articles/PMC9206009/table/Tab1
26. Liljegren JC, Carhart RA, Lawday P, Tschopp S, Sharp R. "Modeling the wet bulb globe temperature using standard meteorological measurements." *JOEH* 5(10):645–655, 2008. Via OSHA Outdoor WBGT Calculator https://www.osha.gov/heat-exposure/wbgt-calculator ; Lemke & Kjellstrom, *Ind Health* 50(4):267–278, 2012 https://dx.doi.org/10.2486/indhealth.ms1352 ; ECU thesis https://thescholarship.ecu.edu/items/8798c067-e098-4d70-849e-17cd59da74ee
27. India Meteorological Department, Morning Heat Bulletin (definitions). https://mausam.imd.gov.in/pdfs/heatcolduser/morning_heat_bulletin.pdf ; persistence rule via Business Today 2024 https://www.businesstoday.in/amp/india/story/imd-red-alert-weather-update-heatwave-severe-heat-wave-delhi-uttar-pradesh-punjab-chandigarh-haryana-madhya-pradesh-rajasthan-430333-2024-05-21
28. He C, Kan H, et al. "The effects of night-time warming on mortality burden under future climate change scenarios: a modelling study." *Lancet Planetary Health* 6(8):e648–e657, 2022. https://www.preventionweb.net/news/risk-death-rises-climate-change-causes-nighttime-temperatures-climb ; https://sdgresources.relx.com/node/16439
29. Royé D, et al. "Short-term association between hot nights and mortality: a multicountry analysis in 178 locations considering hourly ambient temperature." *Environment International*, 2025. https://www.sciencedirect.com/science/article/pii/S0160412025004702 ; Ahmedabad hot-night finding via Medindia https://www.medindia.net/news/healthwatch/heatwave-havoc-hot-nights-increase-mortality-rates-in-india-217009-1.htm
30. CSE, "Warm nights: Delhi is losing its capacity to cool down during summer nights," 2026. https://www.cseindia.org/warm-nights-delhi-is-losing-its-capacity-to-cool-down-during-summer-nights-says-new-cse-report-13137 ; Down To Earth https://www.downtoearth.org.in/amp/story/environment/record-night-warming-in-delhi-worsening-heat-stress-here-are-some-policy-suggestions
31. "Indoor heat measurement data from low-income households in rural and urban South Asia." *Scientific Data* 9, 2022. https://www.nature.com/articles/s41597-022-01314-5 ; AIDMI, "Keeping Maharashtra's Slums Cool: What the Evidence Says" https://aidmi.org/blog/keeping-maharashtras-slums-cool-what-the-evidence-says/ ; "Indoor heat conditions measured in urban slum and rural village housing in West Bengal, India," *Building and Environment*, 2021 https://www.sciencedirect.com/science/article/abs/pii/S0360132320309343
32. Multi-city South Asia indoor/outdoor study (PMC9184534) https://pmc.ncbi.nlm.nih.gov/articles/PMC9184534 ; India Water Portal, "Inside Delhi's urban heat island" https://www.indiawaterportal.org/climate-change/inside-delhis-urban-heat-island-how-ai-and-community-action-are-combating-the-crisis ; Mongabay India 2025 https://india.mongabay.com/2025/01/when-heat-rises-incomes-fall-for-the-informal-workforce/
33. "Combating climate change-induced heat stress: Assessing cool roofs and its impact on the indoor ambient temperature of the households in the urban slums of Ahmedabad." https://www.researchgate.net/publication/340017377
34. The Better India, "How One Simple Initiative Is Cooling Down Homes for 20,000 Women in Slums" (Mahila Housing Trust). https://thebetterindia.com/353012/heatwave-mahila-housing-trust-reflective-solar-paint-ahmedabad-ignas-park-slum-homes/ ; Citizen Matters https://citizenmatters.in/women-at-the-forefront-of-bringing-climate-resilience-to-ahmedabads-slums/
35. International Labour Organization. *Working on a Warmer Planet: The Impact of Heat Stress on Labour Productivity and Decent Work*, 2019. https://indiaenvironmentportal.org.in/reports-and-documents/working-on-a-warmer-planet-the-effect-of-heat-stress-on-productivity-and-decent-work ; The Quint https://www.thequint.com/news/environment/india-may-lose-34-million-jobs-due-to-global-warming-2030-un
36. Lancet Countdown. *2024 India Data Sheet.* https://lancetcountdown.org/wp-content/uploads/2024/10/Lancet-Countdown-2024_INDIA.pdf ; press coverage https://www.policycircle.org/environment/extreme-heat-productivity-loss/ ; https://www.etvbharat.com/en/health/lancet-countdown-climate-change-india-biggest-health-threat-enn25102804239
37. Business Standard / Tribune coverage of the 2025 Lancet Countdown report. https://www.business-standard.com/india-news/indians-faced-nearly-20-heatwave-days-in-2024-on-average-lancet-report-125102900069_1.html ; https://www.tribuneindia.com/news/weather/people-in-india-each-saw-20-heatwave-days-in-2024-6-5-linked-with-climate-change-lancet-report/amp
38. Yale Environment 360, "India kidney disease, climate and outdoor workers" https://e360.yale.edu/features/india-kidney-disease-climate-outdoor-workers ; "Heat Stress: A Hazardous Occupational Risk for Vulnerable Workers" (PMC10334395) https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10334395/ ; "Heat Stress Nephropathy in CKDu Hotspots of Bargarh District, Odisha" (PMC12546656) https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12546656/
39. Telangana Gig and Platform Workers Union & HeatWatch. *Impact of Extreme Heat on Gig Workers: A Survey Report*, 2024. https://tgpwu.org/wp-content/uploads/2024/08/Impact_of_Extreme_Heat_on_Gig_Workers_A_Survey_Report-1.pdf
40. WRI India, "Rising heat's invisible burden on delivery workers"; Rest of World 2024. https://wri-india.org/perspectives/rising-heats-invisible-burden-delivery-workers ; https://restofworld.org/2024/india-heat-wave-delivery-workers/
41. AEA RCT Registry, "Scorching Streets: Heatwaves and Gig Workers in India." https://www.socialscienceregistry.org/trials/15839
42. WHO Regional Office for Europe, "How summer heat impacts health and how to #KeepCool," 23 Jun 2025. https://www.who.int/europe/news/item/23-06-2025-how-summer-heat-impacts-health-and-how-to--keepcool
43. Minnesota Department of Health, "Extreme Heat." https://www.health.state.mn.us/communities/environment/climate/extremeheat.html
44. Lancet Countdown 2024 India data sheet (via coverage). https://lancetcountdown.org/wp-content/uploads/2024/10/Lancet-Countdown-2024_INDIA.pdf ; https://www.etvbharat.com/amp/en/health/lancet-countdown-climate-change-india-biggest-health-threat-enn25102804239
45. Chersich MF, et al. "Associations between high temperatures in pregnancy and risk of preterm birth, low birth weight, and stillbirths: systematic review and meta-analysis." *BMJ* 371:m3811, 2020. https://researchonline.lshtm.ac.uk/4659047 ; https://www.burnet.edu.au/knowledge-and-media/research-articles/associations-between-high-temperatures-in-pregnancy-and-risk-of-preterm-birth-low-birth-weight-and
46. US CDC, "Heat and Medications – Guidance for Clinicians." https://www.cdc.gov/heat-health/hcp/heat-and-medications-guidance-for-clinicians.html ; Scientific American https://www.scientificamerican.com/article/how-some-common-medications-can-make-people-more-vulnerable-to-heat/
47. IMPRI, "Heat Action Plans in India (2013 Onwards)" (NDMA 2016/2017/2019 guidelines summary) https://www.impriindia.com/insights/heat-action-plans-in-india-2013-onwards-from-reactive-emergency-response-to-proactive-climate-adaptation/ ; Vikaspedia, "Guidelines on management of heat wave" https://en.vikaspedia.in/viewcontent/social-welfare/disaster-management-1/guidelines-on-disaster-management/heat-wave/guidelines-on-management-of-heat-wave?lgn=en
