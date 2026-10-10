import type { Group, Language, RiskLevel } from "../api/client";

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
  sampleData: "Sample data. The grid and scores are placeholders until real ward boundaries and forecasts are connected.",
  noForecast: "No forecast yet for this ward. The next update runs within three hours.",
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
  sampleData: "नमूना डेटा। असली वार्ड सीमाएं और पूर्वानुमान जुड़ने तक ग्रिड और स्कोर अस्थायी हैं।",
  noForecast: "इस वार्ड का पूर्वानुमान अभी नहीं है। अगला अपडेट तीन घंटे में आएगा।",
};

export const STRINGS: Record<Language, Strings> = { en, hi };
