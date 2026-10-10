import type { ActionCode, Group, Home, Language, PlaceKind, RiskLevel } from "../api/client";

export interface Strings {
  city: string;
  levels: Record<RiskLevel, string>;
  levelAdvice: Record<RiskLevel, string>;
  dayToday: string;
  dayTomorrow: string;
  headline: (dayLabel: string, count: number, total: number) => string;
  headlineCalm: (dayLabel: string) => string;
  standfirst: string;
  chooseDay: string;
  topWards: string;
  topWardsNote: string;
  legend: string;
  backToList: string;
  peakAt: (heatIndex: number, time: string) => string;
  hourByHour: string;
  whyTitle: string;
  surfaceHeat: string;
  surfaceHeatValue: (offset: number) => string;
  greenCover: string;
  greenCoverValue: (ndvi: number) => string;
  density: string;
  densityValue: (n: number) => string;
  subscribeTitle: string;
  subscribeNote: string;
  phone: string;
  phoneHint: string;
  whoFor: string;
  groups: Record<Group, string>;
  alertLanguage: string;
  channel: string;
  subscribe: string;
  subscribing: string;
  subscribed: string;
  loading: string;
  loadFailed: string;
  retry: string;
  sampleData: string;
  noForecast: string;
  replayNotice: (date: string) => string;
  snapshotNotice: (when: string) => string;
  subscribeOffline: string;
  exportCsv: string;
  csvHeaders: string[];
  mapLoading: string;
  workTitle: string;
  workStop: (window: string) => string;
  workRatio: (window: string, work: number) => string;
  workSafe: string;
  wbgtNote: (wbgt: number) => string;
  nightTitle: string;
  nightValue: (low: number, hot: boolean) => string;
  placesTitle: string;
  placeKinds: Record<PlaceKind, string>;
  placeSample: string;
  placeHours: (open: string, close: string) => string;
  alwaysOpen: string;
  noPlaces: string;
  placesSampleNote: string;
  actionsTitle: string;
  actions: Record<ActionCode, string>;
  roofQuestion: string;
  roofs: Record<Home, string>;
  roofHint: string;
  caregiver: string;
  caregiverHint: string;
  placesLegend: string;
}

const en: Strings = {
  city: "Delhi",
  levels: { low: "Low", moderate: "Moderate", high: "High", extreme: "Extreme" },
  levelAdvice: {
    low: "Normal precautions.",
    moderate: "Drink water often, rest in shade.",
    high: "Avoid outdoor work 12 to 4 pm.",
    extreme: "Stay indoors in the afternoon. Check on elderly neighbours.",
  },
  dayToday: "Today",
  dayTomorrow: "Tomorrow",
  headline: (day, count, total) => `${day}, ${count} of ${total} wards reach high or extreme heat risk`,
  headlineCalm: (day) => `${day}, no ward reaches high heat risk`,
  standfirst: "Risk combines the heat forecast with how exposed each ward is: built-up surfaces, green cover and how many people live there.",
  chooseDay: "Forecast day",
  topWards: "Highest risk wards",
  topWardsNote: "Where water points and cooling centres matter most.",
  legend: "Risk levels",
  backToList: "All wards",
  peakAt: (hi, time) => `Feels like ${Math.round(hi)}°C at the hottest hour, around ${time}.`,
  hourByHour: "Hour by hour",
  whyTitle: "Why this ward scores this way",
  surfaceHeat: "Surface heat",
  surfaceHeatValue: (o) => `${o >= 0 ? "+" : "−"}${Math.abs(o).toFixed(1)}°C against the city average`,
  greenCover: "Green cover",
  greenCoverValue: (n) => (n < 0.15 ? "Very little" : n < 0.3 ? "Some" : "Plenty") + ` (NDVI ${n.toFixed(2)})`,
  density: "People",
  densityValue: (n) => `${Math.round(n).toLocaleString("en-IN")} per km²`,
  subscribeTitle: "Get heat alerts for this ward",
  subscribeNote: "At most two messages a day, never between 10 pm and 6 am. Reply STOP to any alert to stop.",
  phone: "Mobile number",
  phoneHint: "10-digit Indian mobile number",
  whoFor: "Who are the alerts for?",
  groups: { worker: "Someone who works outdoors", parent: "A parent of young children", elderly: "An elderly person" },
  alertLanguage: "Alert language",
  channel: "Send by",
  subscribe: "Get alerts",
  subscribing: "Signing up…",
  subscribed: "You're signed up. Alerts will come when this ward reaches high risk.",
  loading: "Loading the latest forecast…",
  loadFailed: "The forecast couldn't be loaded. Check your connection and try again.",
  retry: "Try again",
  sampleData: "Sample wards. The grid and ward attributes are placeholders until real ward boundaries are loaded; the heat forecast is live.",
  noForecast: "No forecast yet for this ward. The next update runs within three hours.",
  snapshotNotice: (when) => `Saved forecast from ${when}. The live service is not connected, so these scores are not updating.`,
  subscribeOffline: "Alerts need the live service, which is not connected right now.",
  replayNotice: (date) => `Replay of ${date}. These scores use a past heatwave's weather, not today's forecast.`,
  exportCsv: "Download ranked list (CSV)",
  csvHeaders: [
    "Rank", "Ward ID", "Ward", "Date", "Risk level", "Risk score", "Feels like (°C)", "Peak hour (IST)",
    "WBGT in sun, max (°C)", "Stop heavy work (IST)", "Tonight's low (°C)", "Ward actions",
  ],
  mapLoading: "Loading map…",
  workTitle: "For outdoor workers",
  workStop: (w) => `Stop heavy outdoor work ${w}.`,
  workRatio: (w, m) => `${w}: work ${m} min, rest ${60 - m} min in shade each hour.`,
  workSafe: "Normal work hours are fine today for workers used to the heat. Drink water every 20 minutes.",
  wbgtNote: (x) => `Heat stress in the sun (WBGT) peaks near ${Math.round(x)}°C. Above 31.5°C, steady moderate work is unsafe.`,
  nightTitle: "Tonight",
  nightValue: (low, hot) =>
    hot
      ? `Stays above ${Math.round(low)}°C, so the body gets no rest overnight. Elderly people and infants need a cool place to sleep.`
      : `Cools to about ${Math.round(low)}°C.`,
  placesTitle: "Nearest cool places and water",
  placeKinds: { cooling: "Cooling centre", water: "Drinking water", rest: "Shaded rest point" },
  placeSample: "sample",
  placeHours: (a, b) => `${a} to ${b}`,
  alwaysOpen: "Open all day",
  noPlaces: "No cooling centre or water point listed within 2 km.",
  placesSampleNote: "Sample points, not yet checked by the ward office. Alerts never send people to them.",
  actionsTitle: "Ward office checklist",
  actions: {
    open_cooling: "Open cooling centres and water points through the risky hours.",
    shift_work: "Move municipal and site outdoor work out of the stop-work hours.",
    check_vulnerable: "Send ASHA workers or volunteers to elderly people who live alone.",
    night_shelter: "Keep cooling spaces open tonight: the ward won't cool down.",
    cooling_gap: "Nothing verified within 1 km: set up a temporary water or shade point.",
  },
  roofQuestion: "Roof over the home",
  roofs: { pucca: "Brick or concrete", tin: "Tin, asbestos or plastic sheet" },
  roofHint: "Rooms under thin roofs get hotter than outside, so alerts start one level earlier.",
  caregiver: "Family member or neighbour to tell (optional)",
  caregiverHint: "On the worst days the alert asks for an OK. If the reply is SOS, we message this number.",
  placesLegend: "Cooling centres and water points",
};

const hi: Strings = {
  city: "दिल्ली",
  levels: { low: "कम", moderate: "मध्यम", high: "ज़्यादा", extreme: "बहुत ज़्यादा" },
  levelAdvice: {
    low: "सामान्य सावधानी रखें।",
    moderate: "बार-बार पानी पिएं, छांव में आराम करें।",
    high: "दोपहर 12 से 4 बजे तक बाहर काम न करें।",
    extreme: "दोपहर में घर के अंदर रहें। बुज़ुर्ग पड़ोसियों का हाल पूछें।",
  },
  dayToday: "आज",
  dayTomorrow: "कल",
  headline: (day, count, total) => `${day} ${total} में से ${count} वार्डों में गर्मी का ख़तरा ज़्यादा या बहुत ज़्यादा`,
  headlineCalm: (day) => `${day} किसी वार्ड में गर्मी का ख़तरा ज़्यादा नहीं`,
  standfirst: "ख़तरा गर्मी के पूर्वानुमान और हर वार्ड की स्थिति से तय होता है: पक्की सतह, हरियाली और आबादी।",
  chooseDay: "पूर्वानुमान का दिन",
  topWards: "सबसे ज़्यादा ख़तरे वाले वार्ड",
  topWardsNote: "जहां पानी और ठंडी जगहों की सबसे ज़्यादा ज़रूरत है।",
  legend: "ख़तरे के स्तर",
  backToList: "सभी वार्ड",
  peakAt: (hi, time) => `सबसे गर्म समय, लगभग ${time}, ${Math.round(hi)}°C जैसा महसूस होगा।`,
  hourByHour: "घंटे के हिसाब से",
  whyTitle: "इस वार्ड का ख़तरा ऐसा क्यों है",
  surfaceHeat: "सतह की गर्मी",
  surfaceHeatValue: (o) => `शहर के औसत से ${o >= 0 ? "+" : "−"}${Math.abs(o).toFixed(1)}°C`,
  greenCover: "हरियाली",
  greenCoverValue: (n) => (n < 0.15 ? "बहुत कम" : n < 0.3 ? "कुछ" : "काफ़ी") + ` (NDVI ${n.toFixed(2)})`,
  density: "आबादी",
  densityValue: (n) => `${Math.round(n).toLocaleString("en-IN")} प्रति वर्ग किमी`,
  subscribeTitle: "इस वार्ड के लिए गर्मी की चेतावनी पाएं",
  subscribeNote: "दिन में ज़्यादा से ज़्यादा दो संदेश, रात 10 से सुबह 6 बजे के बीच कभी नहीं। बंद करने के लिए STOP लिखें।",
  phone: "मोबाइल नंबर",
  phoneHint: "10 अंकों का भारतीय मोबाइल नंबर",
  whoFor: "चेतावनी किसके लिए है?",
  groups: { worker: "बाहर काम करने वाले", parent: "छोटे बच्चों के माता-पिता", elderly: "बुज़ुर्ग व्यक्ति" },
  alertLanguage: "चेतावनी की भाषा",
  channel: "कैसे भेजें",
  subscribe: "चेतावनी पाएं",
  subscribing: "जोड़ रहे हैं…",
  subscribed: "आप जुड़ गए हैं। वार्ड में ख़तरा बढ़ने पर संदेश आएगा।",
  loading: "ताज़ा पूर्वानुमान आ रहा है…",
  loadFailed: "पूर्वानुमान नहीं मिल सका। इंटरनेट जांचें और फिर कोशिश करें।",
  retry: "फिर कोशिश करें",
  sampleData: "नमूना वार्ड। असली वार्ड सीमाएं जुड़ने तक ग्रिड और वार्ड की जानकारी अस्थायी है; गर्मी का पूर्वानुमान असली है।",
  noForecast: "इस वार्ड का पूर्वानुमान अभी नहीं है। अगला अपडेट तीन घंटे में आएगा।",
  snapshotNotice: (when) => `${when} का सहेजा गया पूर्वानुमान। लाइव सेवा जुड़ी नहीं है, इसलिए ये स्कोर अपडेट नहीं हो रहे।`,
  subscribeOffline: "अलर्ट के लिए लाइव सेवा चाहिए, जो अभी जुड़ी नहीं है।",
  replayNotice: (date) => `${date} का रीप्ले। ये स्कोर आज के पूर्वानुमान से नहीं, एक पुरानी लू के मौसम से बने हैं।`,
  exportCsv: "रैंक सूची डाउनलोड करें (CSV)",
  csvHeaders: [
    "रैंक", "वार्ड ID", "वार्ड", "तारीख", "ख़तरे का स्तर", "ख़तरे का स्कोर", "महसूस तापमान (°C)", "सबसे गर्म समय (IST)",
    "धूप में WBGT, अधिकतम (°C)", "भारी काम बंद (IST)", "आज रात न्यूनतम (°C)", "वार्ड के काम",
  ],
  mapLoading: "नक्शा आ रहा है…",
  workTitle: "बाहर काम करने वालों के लिए",
  workStop: (w) => `${w} बाहर भारी काम बंद रखें।`,
  workRatio: (w, m) => `${w}: हर घंटे ${m} मिनट काम, ${60 - m} मिनट छांव में आराम।`,
  workSafe: "गर्मी के आदी कामगारों के लिए आज सामान्य काम ठीक है। हर 20 मिनट पानी पिएं।",
  wbgtNote: (x) => `धूप में गर्मी का तनाव (WBGT) लगभग ${Math.round(x)}°C तक जाएगा। 31.5°C से ऊपर लगातार मध्यम काम सुरक्षित नहीं।`,
  nightTitle: "आज रात",
  nightValue: (low, hot) =>
    hot
      ? `तापमान ${Math.round(low)}°C से नीचे नहीं जाएगा, रात में शरीर को आराम नहीं मिलेगा। बुज़ुर्गों और छोटे बच्चों को ठंडी जगह सुलाएं।`
      : `लगभग ${Math.round(low)}°C तक ठंडा होगा।`,
  placesTitle: "सबसे पास ठंडी जगहें और पानी",
  placeKinds: { cooling: "ठंडी जगह", water: "पीने का पानी", rest: "छांव में आराम" },
  placeSample: "नमूना",
  placeHours: (a, b) => `${a} से ${b}`,
  alwaysOpen: "पूरे दिन खुला",
  noPlaces: "2 किमी के अंदर कोई ठंडी जगह या पानी केंद्र दर्ज नहीं।",
  placesSampleNote: "नमूना जगहें, वार्ड कार्यालय ने अभी जांची नहीं हैं। अलर्ट कभी इनका नाम नहीं भेजते।",
  actionsTitle: "वार्ड कार्यालय के काम",
  actions: {
    open_cooling: "ख़तरे के घंटों में ठंडी जगहें और पानी केंद्र खुले रखें।",
    shift_work: "नगर निगम और साइट का बाहरी काम काम-बंद घंटों से हटाएं।",
    check_vulnerable: "अकेले रहने वाले बुज़ुर्गों के पास आशा कार्यकर्ता या स्वयंसेवक भेजें।",
    night_shelter: "आज रात ठंडी जगहें खुली रखें: वार्ड रात में ठंडा नहीं होगा।",
    cooling_gap: "1 किमी में कोई जांची हुई जगह नहीं: अस्थायी पानी या छांव केंद्र लगाएं।",
  },
  roofQuestion: "घर की छत",
  roofs: { pucca: "ईंट या कंक्रीट", tin: "टीन, एस्बेस्टस या प्लास्टिक शीट" },
  roofHint: "पतली छत के नीचे कमरा बाहर से ज़्यादा गर्म होता है, इसलिए चेतावनी एक स्तर पहले आएगी।",
  caregiver: "परिवार या पड़ोसी जिसे बताना हो (वैकल्पिक)",
  caregiverHint: "सबसे गर्म दिनों में अलर्ट OK पूछेगा। जवाब SOS आया तो हम इस नंबर पर संदेश भेजेंगे।",
  placesLegend: "ठंडी जगहें और पानी केंद्र",
};

export const STRINGS: Record<Language, Strings> = { en, hi };
