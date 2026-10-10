# C. Competitor teardown: "Doesn't Google Weather already do this?"

*HeatShield: ward-level Risk = Hazard × Vulnerability, WhatsApp/SMS alerts in Hindi and English, officer map, Delhi pilot. Research date: 2026-10-10.*

> **How this was researched.** The sandbox's egress policy blocked every direct page fetch (WebFetch and curl both failed for blog.google, wmo.int, techcrunch.com, imd.gov.in and others). So every claim below comes from search-engine extracts of the cited URLs. I did not open those pages directly. Treat each claim as "reported by [n]". Items marked **(verify)** are thin or conflicting and should be checked before they go in a pitch deck.

---

## 1. Google

**Search heat alerts (2023).** Google announced in March 2023 that searches about extreme heat would show when a heat wave is predicted to start and end, plus cooling tips and health guidance, built with the Global Heat Health Information Network (GHHIN) [1]. Launch coverage named the US and parts of Europe as the first markets [1]. WMO later reported the feature as available in about 200 countries when people search for heat in their area [2]. **India status:** I found no Google announcement or press report that confirms these heat panels appear for Indian users, or that they are in Hindi **(verify by searching "heatwave Delhi" on an Indian phone)**. Google's Public Alerts help page lists India as a partner country for relaying official alerts [3], and a September 2025 Google slide claims Public Alerts cover 60+ countries, "some with only a subset of event types" [4]. If Google shows a heat alert in India, it is most likely a relay of IMD/NDMA warnings, not Google's own risk model.

**Heat Resilience tool (Sept 2024 → June 2026).** The tool uses AI on satellite and aerial imagery. It maps land-surface temperature, tree canopy and roof reflectivity, flags socially vulnerable areas, and lets officials simulate added tree canopy or cool roofs [5][6]. It launched as a pilot in 14 US communities and was not publicly available [6]. On 30 June 2026 Google Research released a building-level rooftop-albedo dataset for 50+ global cities through a "Heat Resilience Earth Engine App". It fuses Sentinel-2 with 30 cm Airbus Pléiades Neo imagery and is part of Earth AI [7]. A third-party analysis pulls **Mumbai and Kolkata** from that dataset [8]. **Delhi's inclusion is unconfirmed (verify).** The tool is for planning: it gives seasonal surface temperature and roof albedo, with no forecasts, no alerts and no channel to residents.

**AI weather models.** WeatherNext 2 (DeepMind and Google Research, 18 Nov 2025) produces 15-day hourly forecasts. It powers Search, Gemini and Pixel Weather, with Maps and the Maps Platform Weather API "coming soon", and Vertex AI early access for enterprises [9][10]. MetNet-based Nowcasting (precipitation in 5 km cells, refreshed every 15 minutes) was already running in India before its 2025 Latin American launch [11]. **I found no India-specific heat feature from Google**, such as a heat index tuned to IMD criteria or Hindi heat guidance. Pixel Weather shows a "feels like" temperature, and its AI summary on a hot day suggested sunscreen [12]. One reviewer in India found the AI summary missing in their region [12]. Google's Android-native public-safety work in India covers earthquakes (launched 2023 with NDMA) [13], not heat.

**Bottom line on Google in India.** Google offers a good forecast, a feels-like number, a probable relay of official warnings, and a planning dataset that partly covers Indian cities. It has no ward-level vulnerability, no WhatsApp/SMS push, and no tools for officers to act on.

## 2. Apple, AccuWeather, The Weather Company

- **Apple Weather.** Apple's support page lists India among the countries where severe-weather information comes from national weather services. It also shows "Feels Like" in hourly forecasts for 10 days [14]. Alerts are government warnings passed through unchanged [14].
- **AccuWeather.** The Enterprise API offers 70+ parameters, including RealFeel®, configurable threshold "alarms" for temperature and other variables, and government plus proprietary alerts. Pricing is by sales quote [15]. I found nothing India-specific.
- **The Weather Company** (weather.com, Weather Underground) has been owned by Francisco Partners since Feb 2024 [16]. I found no India heat-specific product.

## 3. Indian government stack (the real incumbent)

- **IMD.** IMD issues district-level heatwave warnings with 5-day outlooks, colour-coded Green/Yellow/Orange/Red by expected impact under NDMA guidelines. They are issued by State Met Centres [17][19]. A Dec 2025 parliamentary reply says the warnings now factor in max and min temperature, relative humidity, wind and persistence. It also says they appear on a GIS heatwave portal "at district and sub-city scales" [18]. IMD has run an experimental Heat Index (NOAA-like formula) since 2023 [17]. A July 2026 summary says impact-based forecasts are issued twice daily (secondary source) **(verify)**.
- **Mausam app** gives IMD forecasts, radar and 3-hour nowcast warnings [23]. **Meghdoot** (IMD/IITM/ICAR) gives farmers district and block forecasts with agro-advisories in English and 13 regional languages [22]. IMD also partnered with InMobi's **1Weather/Glance** to push alerts to the lock screens of 235 million phones [24].
- **SACHET (NDMA, C-DOT)** is CAP-based. It has sent 6,899 crore+ SMS in 19+ languages and is operational across all 36 States and UTs [20]. In **May 2026** it sent its first heatwave **cell-broadcast** alert ("Extremely Severe" heat wave) to five Vidarbha districts, with a loud tone, during nationwide CB testing [20][21]. Government push alerts to every phone are now real, but they are district-wide and not personalised.
- **City and state HAPs.** Ahmedabad (2013) was South Asia's first heat early-warning and preparedness plan [25]. It uses colour-coded temperature thresholds tied to response triggers, cool-roof outreach and IEC through media and health facilities [26]. Delhi's DDMA HAP 2024-25 includes a section on "identifying ward-level vulnerability" [27]. The first plan used LST maps to flag 10 wards [27]. The 2026 plan adds a proposed Cool Roof Policy, misting and cool rooms in 30+ hospitals [28]. An independent audit found it relies on fixed cooling centres and work rescheduling that miss domestic workers [29]. Telangana's HAP uses district colour-coded alerts [30]. I found **no dedicated Odisha, Telangana or Gujarat heat app** in search results **(verify)**.

## 4. Heat-health and worker-safety tools

- **OSHA-NIOSH Heat Safety Tool.** The app is free and calculates heat index plus risk level from NOAA data, with hourly planning, precautions and first aid [31]. It is US-only in its data and was built on a heat index meant for shade. NIOSH itself recommends WBGT where available [31].
- **Kestrel 5400.** This handheld WBGT meter costs USD 479–599 and has on-device alarms and the LiNK Bluetooth app [32]. It is accurate on a site but needs hardware per site and gives no area-wide view.
- **SHRAM (UC Berkeley IECC).** This is the closest Indian analogue on the worker side. It uses the EHI-N heat-stress model calibrated to work intensity, from light work up to heavy agricultural labour, with shade or sun toggles. It runs on IMD station data with 1- and 3-day forecasts for 700+ districts and offers sign-ups for personalised alerts [33]. Its resolution is the district, not the ward.
- **Gig platforms.** Eternal (Zomato/Blinkit) reported 4,500+ partner-restaurant rest points with water and charging in June 2025, open to workers from any platform [35]. Later coverage cites 5,000+ [36]. Blinkit dark stores have coolers and water and hand out glucose [36]. Swiggy Instamart runs 900+ "recharge zones" [34]. Coverage also mentions SOS support, heat-illness insurance and weather alerts [34][36]. These are physical assets that suit an "officer map" layer, but each platform's heat triggers are internal and opaque.
- **Wearables (Zephyr and others).** These were not researched (search budget) **(gap in this teardown)**.

## 5. Heat insurance (parametric)

- **SEWA with Arsht-Rock / Climate Resilience for All (CRA), Blue Marble.** In 2023, 21,000 women were covered in 5 Gujarat districts. Triggers were based on historical temperature over 10-day cycles and varied by district. The premium of about USD 10.30 was paid by Arsht-Rock, with payouts capped at about USD 85 [38]. The 2023 pilot paid nothing because thresholds were too high [40]. In 2024 coverage grew to 50,000 women in 22 districts of Gujarat, Rajasthan and Maharashtra [37]. In May 2024, 92% received Rs 400–1,600 [39]. In 2025 coverage reached about 250,000 women and became multi-hazard (heat, cyclone, rain) [40], extending to UP, Assam, J&K and Bihar [41]. The design now also considers humidity and **night-time temperature** [37].
- **Mahila Housing Trust with Go Digit (Gujarat).** No payout in 2025 because the threshold was not met. The 2026 trigger was cut to 42.74 °C, paying Rs 850–2,000 [41].
- **Go Digit with Jan Sahas (migrant workers).** Payout is Rs 3,000 when temperature exceeds about 42 °C for 5 consecutive days (up to 43.7 °C in some cities). It covers Delhi, Noida, Ghaziabad, Gurgaon, Faridabad and Lucknow, with first payouts reported in June 2025 [42][43]. J-PAL is designing a parametric product for **Delhi NCR delivery workers** [44]. I found nothing on IFFCO-Tokio heat products.
- **Implication:** Basis risk is the recurring failure mode, with zero payouts in 2023 and 2025 because thresholds were not met [40][41]. Insurers need hyper-local, validated heat indices and on-the-ground verification. That is a data-buyer opportunity for HeatShield.

## 6. Urban heat analytics, NGOs and startups

- **SEEDS with Microsoft AI for Good, "Sunny Lives".** The model takes roof type from satellite imagery, predicts indoor temperature and scores **building-level** risk on a map, built with Gramener. It covers about 125,000 slum residents in Delhi and Nagpur [45]. I found no live alerting [45]. **This is the closest technical competitor in Delhi.**
- **CEEW district heat-risk study (May 2025).** It assesses 734 districts on 35 hazard, exposure and vulnerability indicators, including night heat and humidity. It finds 57% of districts, home to 76% of people, at high or very high risk, with Delhi ranked at the top. It is published as a report plus state handbooks, not a live tool [46].
- **Sustainable Futures Collaborative (SFC).** Its March 2025 review of HAPs in 9 cities found them focused on short-term response, with poorly targeted long-term action [47]. A secondary source cites "only 2 of 37 HAPs include localized heat-risk maps" **(verify)** [47]. I found no SFC ward maps. A ward-level HVI for Jodhpur came from Drexel and NRDC India [54].
- **Mahila Housing Trust.** It runs cool roofs and women "Climate Saathis" in 100 slums across 8 Indian cities, and its community action groups relay heat early warnings [48]. MHT also co-authored Jodhpur's HAP [48]. Ahmedabad pairs cool roofs, misting bus stops and heat insurance [55].
- **Telangana Cool Roof Policy 2023-28** targets 300 km² (200 km² in Hyderabad) and mandates cool roofs on government and non-residential buildings over 600 sq yd [49].
- **CAPA Heat Watch** runs volunteer street-level temperature campaigns in 60–130+ cities, mostly in the US. I found none in India [50].
- **Chief Heat Officers** (Arsht-Rock, now City Champions for Heat Action) are in Miami-Dade, Athens, Freetown, Dhaka North, Cape Town and others. I found none in an Indian city [51].
- **Blue Sky Analytics** offers satellite-derived climate risk datasets, including heat, through an API for finance and government [52]. **Vassar Labs metWISE Heat Watch** gives block-level heat alerts from IMD and ECMWF data, aimed at government [53]. Both sell B2B or B2G data and do not reach residents.
- **Not covered:** Satellites on Fire (a wildfire product, not researched) and Climate TRACE (excluded as instructed).

---

## Comparison matrix

| Product | Target user | Spatial granularity | Metric | Personalised by vulnerability? | Actionable guidance/resources? | Channel & languages | Feedback/data loop | Business model |
|---|---|---|---|---|---|---|---|---|
| Google Search/Weather [1][2][9] | Consumers | Point forecast; alerts relayed by region | Temp, feels-like | No | Generic GHHIN tips | Search/Android, multilingual UI; India heat panel unverified | None | Ads/ecosystem |
| Google Heat Resilience + Earth Engine app [5][7] | City planners | Building-level albedo; LST | Seasonal LST, albedo | Social-vulnerability overlay | Planning scenarios (trees, roofs) | Web/Earth Engine, English | None | Free/philanthropy, Earth AI |
| Apple Weather [14] | iPhone users | Point | Temp, feels-like | No | Relays govt warnings | Push, iOS languages | None | Hardware |
| AccuWeather API [15] | Enterprises | Point | RealFeel | No | Custom thresholds | API | None | Paid API |
| IMD warnings / GIS portal [17][18] | Public, DMAs | District, sub-city | Tmax/Tmin, RH, wind, HI (exp.) | No | Impact text by colour | Web, Mausam, bulletins; EN/HI | None public | Public |
| SACHET SMS/CB [20] | All phones | District polygon | Warning level | No | Short text | SMS/CB, 19+ languages | None | Public |
| Ahmedabad / Delhi HAPs [25][27] | City depts | City; Delhi names wards | Temp thresholds | Ward vulnerability (static) | SOPs, cooling centres | Media, SMS, IEC | Annual review | Public |
| SHRAM (IECC) [33] | Outdoor workers, orgs | District | EHI-N by work intensity | By workload, not person | Risk levels | Web, alert sign-up | No | Academic |
| OSHA-NIOSH app [31] | US workers | Point | Heat index | No | Precautions, first aid | App, EN/ES | No | Public |
| Kestrel 5400 [32] | Safety officers | Site | WBGT | No | Alarms | Device + app | Logs | Hardware sale |
| Zomato/Swiggy/Blinkit [34][35] | Own riders | Rest-point network | Internal | No | Rest points, water, SOS | In-app | Internal | Cost centre |
| SEWA/CRA, Digit/Jan Sahas [37][42] | Informal women, migrants | District / city station | Tmax (+RH, night temp) | Enrolled cohort | Cash payout | Via NGOs | Payout records | Premium, philanthropy |
| SEEDS Sunny Lives [45] | NGOs, DMAs | Building | Predicted indoor temp | Yes (roof, density) | Risk map | Map | Not found | Grant |
| CEEW district risk [46] | Policymakers | District | Composite H×E×V | Yes (static) | Report recommendations | PDF | No | Think-tank |
| Blue Sky / Vassar [52][53] | Finance, govt | Grid / block | Heat indices | Partial | Dashboards | API, SMS/email (Blue Sky) | No | B2B/B2G SaaS |
| **HeatShield (as built, Oct 2026)** | Officers, outdoor workers, people at home | **Ward (Delhi ~250)** | Forecast × LST × NDVI × density; **WBGT in sun, tonight's low, roof type** | **Yes (roof, group, caregiver)** | **Hourly work-rest plan, nearest verified cooling/water point, ward office checklist** | **WhatsApp/SMS, HI/EN** | **OK/SOS check-ins → caregiver + officer counts** | B2G + B2B (platforms, insurers) |

## Where Google is genuinely as good or better

1. **Raw forecast skill and reach.** WeatherNext 2 gives 15-day hourly forecasts at global scale, already in Search and Gemini [9]. HeatShield should **consume** forecasts (IMD, or Google's Maps Weather API when it is available [10]), not build them.
2. **Building-level roof albedo** for 50+ cities, probably including Mumbai and Kolkata [7][8]. If Delhi is in the dataset, it is a free input for HeatShield's cool-roof prioritisation layer.
3. **Distribution to people who search.** Search and Android sit on almost every phone, and Google already relays official alerts in India [3].
4. **Generic health tips** reviewed by GHHIN [1].

## Gaps nobody fills well

1. **Ward-level Hazard × Vulnerability, refreshed daily.** IMD works at district and sub-city level [18]. CEEW and SHRAM work at district level [46][33]. Delhi's HAP has a static ward section [27]. Sunny Lives is building-level but covers slum pockets only, with no alerting [45]. Nobody fuses a daily forecast with LST, NDVI and population for every Delhi ward.
2. **Night-time and indoor heat as a trigger.** CEEW shows warm nights rising fastest [46], and tin roofs reach about 45 °C indoors [45]. Consumer apps show only daytime "feels like".
3. **Officer-facing action loop.** No tool tells a ward or zonal officer where to send water tankers, open cool rooms or reschedule work, or records whether they did it. HAPs are PDFs [27][29], and Google's tool is a planning tool [5].
4. **WhatsApp-first, Hindi, low-literacy push with nearby resources.** SACHET sends one district-wide SMS or CB [20]. Google waits to be searched [1]. Nobody links alerts to the nearest cooling centre, hospital cool room [28] or gig rest point [35].
5. **Ground-truth feedback.** No product collects symptom reports, outages or blocked water points from residents. Insurers suffer basis risk, with zero-payout years [40][41], and they lack hyper-local verification.
6. **Groups left out of current responses.** Examples are domestic workers missed by Delhi's HAP [29] and gig workers whose heat policy is set unilaterally by each platform [34].
7. **An evaluation layer for HAPs.** SFC finds long-term action poorly targeted [47]. Cities have no measurement of whether interventions such as cool roofs or shade cut exposure in specific wards.

## Why Google structurally won't fill them

- **Consumer, global, pull-based.** Google ships features that scale across about 200 countries [2]. Ward boundaries, IMD colour codes and NDMA SOPs are bespoke per city and change yearly [17][27].
- **Google defers to official authorities on warnings.** In India it relays government alerts [3] and builds safety features with NDMA [13]. Issuing its own vulnerability-weighted "your ward is red" alert would put it in conflict with IMD/NDMA authority and create liability.
- **Its heat work for governments is planning-grade, not operational.** It is a US pilot plus an open dataset [6][7], with no SLAs, no field workflow and no procurement presence in Indian municipalities.
- **Its products avoid personal vulnerability data.** Collecting caste or occupation proxies, health status or slum residency to personalise risk is a privacy and regulatory headache Google avoids.
- **WhatsApp is Meta's channel.** Google will not run its alerts through WhatsApp, which is the primary channel in Delhi.
- **No monetisable buyer at ward scale.** HeatShield's buyers (DDMA/MCD, insurers like Digit/CRA [42][40], and platforms [35]) want contracts, audits and custom triggers. That is services work Google does not do.

**Positioning line:** "Google tells you it's hot. HeatShield tells the officer in Ward 47 which 3 bastis need water tankers tonight, tells residents in Hindi on WhatsApp where the nearest cool room is, and reports back whether it happened."

---

## Sources
1. TechCrunch, "Google to roll out new extreme heat alerts in Search" (2023-03-29) – https://techcrunch.com/2023/03/29/google-to-roll-out-new-extreme-heat-alerts-in-search-soon/embed/
2. WMO, "Google adds health tips to extreme heat warnings" – https://wmo.int/node/24172
3. Google Public Alerts Help – https://support.google.com/publicalerts/answer/1753666?hl=en
4. Google Research slides, WMO AI Workshop (Sept 2025) – https://public.wmo.int/sites/default/files/2025-09/%5BNearing%5D%20WMO%20AI%20Workshop%202025.pdf
5. Google blog, "How we're using AI to help cities tackle extreme heat" (2024) – https://blog.google/company-news/outreach-and-initiatives/sustainability/google-ai-research-extreme-heat-resilience/
6. Smart Cities Dive, Google heat resilience mapping tool (2024) – https://smartcitiesdive.com/news/google-heat-resilience-mapping-tool-cities-trees-cool-roofs/726424
7. Google Research, "Expanding our Heat Resilience data to 50+ global cities" (2026-06-30) – https://research.google/blog/expanding-our-heat-resilience-data-to-50-global-cities/
8. M. Janosov, roof reflectivity across cities (Substack) – https://milanjanosov.substack.com/p/why-londons-rooftops-are-dark-and
9. Business Standard, WeatherNext 2 (2025-11-18) – https://www.business-standard.com/technology/tech-news/weathernext-2-google-adds-ai-weather-forecasts-to-gemini-search-pixels-125111800758_1.html
10. Android Authority, WeatherNext 2 in Pixel Weather and Maps – https://www.androidauthority.com/google-weathernext-2-pixel-weather-google-maps-3616629
11. Google blog (es-419), Nowcasting in Latin America – https://blog.google/intl/es-419/actualizaciones-de-producto/informacion/google-nowcasting-pronosticos-en-tiempo-real-para-latinoamerica/
12. Android Authority, Pixel Weather rollout (India reviewer) – https://androidauthority.com/pixel-weather-app-older-pixel-rollout-3498288
13. Moneylife, Google earthquake alerts in India with NDMA (2023) – https://moneylife.in/article/google-launches-earthquake-alert-system-in-india-for-android-smartphone-users/72107.html
14. Apple Support, Weather feature availability – https://support.apple.com/en-gb/105038
15. AccuWeather Enterprise API – https://apidev.accuweather.com/
16. Wikipedia, The Weather Company – https://en.wikipedia.org/wiki/The_Weather_Company
17. PIB/MoES, IMD Heat Index (2023) – https://moes.gov.in/sites/default/files/PIB1982978.pdf
18. PIB/MoES, heatwave reply (Dec 2025) – https://www.moes.gov.in/sites/default/files/PIB2198355.pdf
19. NCDC, heat presentation – https://ncdc.mohfw.gov.in/uploads/pdf/heat_ppt1.pdf
20. The Hitavada, first heatwave cell-broadcast in Vidarbha (2026-05-27) – https://www.thehitavada.com/Encyc/2026/5/27/vid-residents-receive-first-ever-heatwave-warning-on-cellphones.html
21. ETV Bharat, NDMA cell broadcast test (2026) – https://www.etvbharat.com/en/bharat/ndma-tests-cell-broadcast-message-to-alert-citizens-on-severe-disaster-enn26050201915
22. Down To Earth, Meghdoot app – https://www.downtoearth.org.in/news/agriculture/new-mobile-app-launched-to-assist-farmers-65994
23. UX4G, Mausam case study – https://www.ux4g.gov.in/case-studies/ux4g-mausam.php
24. InMobi, IMD and 1Weather/Glance partnership – https://advertising.inmobi.com/company/press/india-meteorological-department-and-1weather-bring-weather-alerts-to-235-million-indians-on-their-glance-lock-screen
25. NRDC, Ahmedabad Heat Action Plan – https://www.nrdc.org/experts/anjali-jaiswal/saving-lives-ahmedabad-launches-groundbreaking-heat-action-plan
26. NCDC, National Workshop report on extreme heat (2022) – https://ncdc.mohfw.gov.in/wp-content/uploads/2024/09/Report_National-Workshop_Health-Sector-Measures-to-Mitigate-and-Adapt-to-Impact-of-Extreme-Heat-_2022.pdf
27. DDMA, Delhi Heat Action Plan 2024-25 – https://ddma.delhi.gov.in/sites/default/files/ddma/generic_multiple_files/hap_6.05.2024.pdf
28. Tribune, Delhi Heat Action Plan 2026 – https://www.tribuneindia.com/news/delhi/delhi-govt-tightens-heat-action-plan-with-focus-on-thermal-hotspots-public-safety/
29. The Leaflet, audit of Delhi's HAP – https://theleaflet.in/governance-and-policy/auditing-delhis-heat-action-plan-a-ground-study-part-ii
30. Telangana Heatwave Action Plan 2021 – https://heathealth.info/wp-content/uploads/ts-heatwave-action-plan-2021-signed-compressed.pdf
31. CDC/NIOSH, Heat Safety Tool app – https://www.cdc.gov/niosh/topics/heatstress/heatapp.html
32. Kestrel 5400 Heat Stress Tracker – https://kestrelmeters.com/kestrel-5400-heat-stress-tracker
33. UC Berkeley IECC, SHRAM / EHI-N – https://iecc.gspp.berkeley.edu/tag/dashboard
34. Outlook Business, Amazon/Swiggy/Eternal heatwave aid – https://www.outlookbusiness.com/news/amazon-swiggy-eternal-heatwave-relief-delivery-partners
35. The Week (PRNewswire), Eternal heatwave initiatives (2025-06-13) – https://www.theweek.in/wire-updates/business/2025/06/13/dcm4-eternal-ltd..html
36. Free Press Journal, AC rest stops and cooling vests – https://www.freepressjournal.in/amp/tech/from-ac-rest-stops-to-cooling-vests-how-zomato-amazon-other-quick-commerce-firms-are-protecting-delivery-workers-this-very-hot-summer
37. WEF, "The heatwave that sparked a new era for women workers in India" (2025-03) – https://weforum.org/stories/2025/03/the-heatwave-that-sparked-a-new-era-for-women-workers-in-india
38. Princeton JPIA, heat-linked parametric insurance – https://jpia.princeton.edu/news/heat-linked-parametric-insurance-system-offers-climate-change-lifeline-indian-women-informal
39. CBS News, CRA payouts to Indian women – https://www.cbsnews.com/news/india-heat-wave-women-receive-insurance-cash-nonprofit-climate-resilience-for-all/
40. ILO Global Coalition for Social Justice, SEWA case – https://social-justice-coalition.ilo.org/node/773
41. Malay Mail, India's women workers turn to heat insurance (2026-05-12) – https://www.malaymail.com/amp/news/life/2026/05/12/indias-women-workers-turn-to-heat-insurance-as-soaring-temperatures-threaten-health-and-livelihoods/219526
42. Outlook Money, heatwave payouts for Noida migrant workers – https://www.outlookmoney.com/insurance/heatwave-triggers-insurance-payouts-for-noida-migrant-workers-under-new-climate-based-policy
43. Outlook Business, parametric insurance against heatwaves – https://www.outlookbusiness.com/planet/green-financing/how-parametric-insurance-could-offset-heat-linked-income-losses
44. J-PAL, parametric insurance for labour supply (Delhi NCR delivery workers) – https://www.povertyactionlab.org/initiative-project/take-and-impacts-parametric-insurance-labor-supply-under-climate-change
45. Microsoft Source Asia, SEEDS Sunny Lives – https://news.microsoft.com/source/asia/features/ai-is-helping-vulnerable-communities-in-india-better-understand-heat-wave-dangers/
46. CEEW, district-level heat risk press release (2025-05-20) – https://www.ceew.in/press-release/mapping-climate-risks-and-impacts-of-extreme-heatwave-disaster-in-indian-districts
47. Dialogue Earth, on SFC "Is India Ready for a Warming World?" – https://dialogue.earth/en/climate/as-indian-cities-struggle-to-plan-for-heat-the-most-vulnerable-suffer/
48. Mahila Housing Trust, climate burden on urban poor women – https://www.mahilahousingtrust.org/rising-temperatures-rising-inequality-the-climate-burden-on-urban-poor-women/
49. NRDC, Telangana Cool Roof Policy – https://www.nrdc.org/bio/prima-madan/telangana-announces-groundbreaking-cool-roof-policy
50. US Climate Resilience Toolkit, Heat Watch campaigns – https://toolkit.climate.gov/tool/heat-watch-campaigns
51. Context, chief heat officers – https://www.context.news/green-cities/how-chief-heat-officers-keep-cities-cool-as-the-world-warms
52. MIT Solve, Blue Sky Analytics – https://solve.mit.edu/solutions/9764
53. Vassar Labs, metWISE Heat Watch – https://vassarlabs.com/why-early-heatwave-alerts-matter-more-than-temperature-thresholds/
54. Jodhpur ward-level HVI (2025) – https://www.em-consulte.com/article/1783774/towards-climate-responsive-cities-developing-a-hea
55. Down To Earth, Ahmedabad cool roofs, misting and heat insurance – https://www.downtoearth.org.in/amp/story/climate-change/beyond-the-thermometer-ahmedabad-uses-cool-roofs-misting-bus-stops-heat-insurance-for-climate-resilience
