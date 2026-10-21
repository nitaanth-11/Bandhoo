import { useState, useEffect, useRef, useCallback } from 'react';
import L from 'leaflet';
import {
  statusLadder,
  DRAFT_NOTICE,
  attachmentLabel,
  analysisUnavailableState,
  EXTERNAL_GEOCODING_ENABLED,
  JURISDICTION_CONFIRMATION_MESSAGE,
  assessJurisdiction,
  reconcileJurisdiction,
  structuredSummary,
} from './trustSafety.js';
import ReviewStatus from './ReviewStatus.js';

const API_BASE_URL = (import.meta.env && import.meta.env.VITE_API_BASE_URL) || 'http://localhost:8001';

const NOT_PROVIDED = 'Not provided';
const NOT_AVAILABLE = 'Not available in Bandhoo data';

// Fresh object each time: witness rows are edited in place.
const emptyForm = () => ({
  intendedMode: '',
  complainantName: '',
  complainantAddress: '',
  complainantContact: '',
  complainantId: '',
  occurrenceTime: '',
  placeOfOccurrence: '',
  natureOfOffence: '',
  legalSections: '',
  suspectName: '',
  suspectAddress: '',
  suspectDescription: '',
  victimName: '',
  victimContact: '',
  victimAddress: '',
  incidentSummary: '',
  propertyDescription: '',
  propertyValue: '',
  witnesses: [{ name: '', phone: '', address: '' }],
  typedName: ''
});

const emptyMissingPersonForm = () => ({
  fullName: '',
  age: '',
  lastSeenLocation: '',
  lastSeenDatetime: '',
  birthmarks: '',
  gender: '',
  heightCm: '',
  complexion: '',
  clothingLastSeen: '',
  relationship: '',
  circumstances: '',
  imageFile: null,
  imagePreview: null
});

function getStationEmail(stationName) {
  if (!stationName) return 'ps.mum@mahapolice.gov.in';
  const clean = stationName.replace(/[^a-zA-Z0-9]/g, '').toLowerCase();
  return `ps.${clean}.mum@mahapolice.gov.in`;
}

// 16 Vibrant colors for Wards to satisfy "map shall be colorful"
const WARD_COLORS = {
  'A': '#3b82f6', // Royal Blue
  'B': '#ef4444', // Bright Red
  'C': '#10b981', // Emerald Green
  'D': '#f59e0b', // Amber Orange
  'E': '#8b5cf6', // Violet Purple
  'F': '#ec4899', // Hot Pink
  'G': '#06b6d4', // Vibrant Cyan
  'H': '#f97316', // Tangerine
  'K': '#14b8a6', // Teal Green
  'L': '#84cc16', // Lime Green
  'M': '#d946ef', // Magenta
  'N': '#a855f7', // Purple
  'P': '#6366f1', // Indigo
  'R': '#65a30d', // Olive
  'S': '#dc2626', // Dark Red
  'T': '#0284c7'  // Sky Blue
};

function getWardColor(wardName) {
  if (!wardName) return '#3b82f6';
  const firstLetter = wardName.trim().charAt(0).toUpperCase();
  return WARD_COLORS[firstLetter] || '#3b82f6';
}

const TRANSLATIONS = {
  en: {
    logoTitle: "Bandhoo Complaint Draft",
    logoSub: "Internal testing only",
    tabLocator: "Incident Location",
    tabDirectory: "Jurisdiction Areas",
    tabInsights: "About the Data",
    tabMissing: "🚨 Missing Person",
    searchPlaceholder: "Search location in Mumbai...",
    searchDisabled: "Address search is turned off until a data-handling policy is approved. Click the map or use GPS.",
    gpsBtn: "Use GPS Location",
    gpsPromptBtn: "📍 Detect Address via GPS",
    resetBtn: "Clear Location",
    assignedTitle: "JURISDICTION (MAP-BASED ESTIMATE)",
    matching: "checking map boundaries...",
    estimate: "map estimate – police to confirm",
    unconfirmed: "requires confirmation",
    ward: "Municipal Ward",
    address: "Station Address",
    contact: "Station Contact",
    emailStation: "Station Email",
    remarks: "Remarks",
    coords: "Selected Point",
    noLocation: "No incident location selected. Click the map, drag the marker or use GPS.",
    lodgeBtn: "PREPARE COMPLAINT DRAFT",
    lodgeMissingBtn: "🚨 FILE MISSING PERSON REPORT",
    dirSearchPlaceholder: "Search areas by name or ward...",
    insTitle: "Map Data",
    insActive: "Jurisdiction Areas",
    insWards: "Municipal Wards",
    insGis: "Boundary Data Status",
    insGisText: "The source and date of the jurisdiction boundary data have not been verified. Markers show the centre of each area, not a police station address. Station addresses and contact details are not available in Bandhoo.",
    // Form fields
    formTitle: "COMPLAINT DRAFT (NOT AN FIR)",
    formMissingTitle: "MISSING PERSON REPORT (CITIZEN DRAFT - NOT AN FIR)",
    formSub: "Prepared by the complainant. Not submitted to the police and not registered.",
    formMissingSub: "Immediate citizen report draft. Under Supreme Court directives (Bachpan Bachao Andolan), NO 24-hr or 48-hr waiting period applies.",
    formMode: "How you intend to give this information to police",
    formModeWritten: "Written",
    formModeOral: "Oral",
    formModeElectronic: "Electronic / Online",
    formComplainantName: "Complainant Full Name",
    formComplainantAddress: "Complainant Address",
    formComplainantContact: "Contact Number",
    formComplainantId: "ID document type (optional – police verify identity in person; do not enter a full Aadhaar number)",
    formOccurrenceTime: "Date and Time of Occurrence",
    formPlaceOccurrence: "Place of Occurrence (Address / Landmarks)",
    formNatureOffence: "Nature of Offence",
    formDetailsSuspect: "Details of Accused / Suspect (if known)",
    formSuspectName: "Suspect Name",
    formSuspectAddress: "Suspect Address",
    formSuspectDesc: "Suspect Description / Identity Marks",
    formVictimsDetails: "Details of Victim(s)",
    formVictimName: "Victim Name",
    formVictimContact: "Victim Contact No.",
    formVictimAddress: "Victim Address",
    formSummaryIncident: "Summary of Incident (Facts of the Case)",
    formPropertyInvolved: "Property Involved (if any)",
    formPropertyDesc: "Property Description",
    formPropertyValue: "Estimated Value (₹)",
    formWitnesses: "Witnesses (Names & Addresses)",
    formPoliceUse: "For police use only (to be completed by the receiving officer)",
    formSign: "Complainant's typed name (this is not a digital signature)",
    formSignText: "I confirm that the information in this draft is true to the best of my knowledge.",
    formVerifyBtn: "Create Complaint Draft",
    fileUploadMedicalTitle: "Supporting material (optional): medical records, photos or other documents",
    fileUploadDrag: "Drag & drop files here, or click to browse",
    idNotice: "Do not upload identity documents. The police verify identity in person.",
    truthNotice: "Please give only true information and genuine documents.",
    aiTitle: "Machine-generated legal section suggestions (not legally reviewed)",
    aiScanning: "Analysing the description...",
    aiConsensus: "Possibly relevant sections (machine-generated)",
    aiAction: "Procedural note from the analysis engine (not legally reviewed)",
    copyDraftBtn: "Copy Draft Text",
    draftCopied: "Draft text copied!",
    deliveryNotice: "Bandhoo does not send complaints and has no verified police contact details. Take this draft to the police station or use an official police channel.",
    statusTitle: "Complaint status",
    statusRecorded: "Recorded",
    statusNotRecorded: "Not recorded",
    secComplainant: "1. Complainant / Informant Details",
    secIncident: "2. Date & Time of Occurrence (as stated)",
    secPlace: "3. Place of Occurrence (as stated)",
    secSummary: "8. Brief Description of Incident (Facts of the Case)",
    secNature: "4. Type / Nature of Offence",
    secLegal: "5. Possibly Relevant Sections (machine-suggested; not a legal determination)",
    secSuspects: "6. Details of Accused / Suspects (as stated)",
    secVictims: "7. Details of Victims (as stated)",
    secProperty: "9. Property Involved (as stated)",
    secWitnesses: "10. Witnesses (as stated)",
    secSignatures: "12. Complainant Confirmation",
    secMissingProfile: "Missing Person Physical Profile",
    secMissingDirective: "STATUTORY MANDATE (Bachpan Bachao Andolan v. Union of India): Under Supreme Court directives, NO 24-HOUR OR 48-HOUR WAITING PERIOD IS APPLICABLE. Entry must be made immediately in the Station General Diary.",
    mpName: "Missing Person Full Name",
    mpAge: "Age (Years)",
    mpLastSeenLoc: "Last Seen Location (Address / Landmarks)",
    mpLastSeenAt: "Last Seen Date & Time",
    mpImage: "Photograph / Recent Image",
    mpBirthmarks: "Birthmarks / Identifying Marks",
    mpGender: "Gender",
    mpHeight: "Height (approx cm)",
    mpComplexion: "Complexion",
    mpClothing: "Clothing Last Seen",
    mpRelation: "Relationship to Complainant",
    mpCircumstances: "Circumstances of Disappearance",
    draftEmailBtn: "Draft Email for Police Station",
    downloadPdfBtn: "Download Official PDF",
    viewInLang: "View complaint in:",
    minorAlert: "MINOR: Mandatory Section 137 BNS procedure & immediate GD entry."
  },
  hi: {
    logoTitle: "बंधू शिकायत प्रारूप",
    logoSub: "केवल आंतरिक परीक्षण हेतु",
    tabLocator: "घटना स्थल लोकेटर",
    tabDirectory: "थाना क्षेत्र निर्देशिका",
    tabInsights: "डेटा अवलोकन",
    tabMissing: "🚨 लापता व्यक्ति",
    searchPlaceholder: "मुंबई में स्थान खोजें...",
    searchDisabled: "डेटा नीति स्वीकृत होने तक पता खोज बंद है। मानचित्र पर क्लिक करें या जीपीएस का उपयोग करें।",
    gpsBtn: "जीपीएस स्थान का उपयोग करें",
    gpsPromptBtn: "📍 जीपीएस से पता प्राप्त करें",
    resetBtn: "स्थान हटाएं",
    assignedTitle: "अधिकार क्षेत्र (मानचित्र आधारित अनुमान)",
    matching: "मानचित्र सीमाएं जांची जा रही हैं...",
    estimate: "मानचित्र अनुमान – पुलिस पुष्टि अपेक्षित",
    unconfirmed: "पुष्टि आवश्यक",
    ward: "प्रशासनिक वार्ड",
    address: "थाने का पता",
    contact: "थाना संपर्क",
    emailStation: "थाने का आधिकारिक ईमेल",
    remarks: "विशेष टिप्पणियाँ",
    coords: "चयनित बिंदु",
    noLocation: "घटना स्थल चयनित नहीं है। मानचित्र पर क्लिक करें, मार्कर खींचें या जीपीएस का उपयोग करें।",
    lodgeBtn: "शिकायत का प्रारूप तैयार करें",
    lodgeMissingBtn: "🚨 लापता व्यक्ति की शिकायत दर्ज करें",
    dirSearchPlaceholder: "नाम या वार्ड द्वारा खोजें...",
    insTitle: "मानचित्र डेटा",
    insActive: "अधिकार क्षेत्र",
    insWards: "नगर निगम वार्ड",
    insGis: "सीमा डेटा की स्थिति",
    insGisText: "अधिकार क्षेत्र सीमा डेटा का स्रोत व तिथि सत्यापित नहीं है। मार्कर क्षेत्र का केंद्र दर्शाते हैं, थाने का पता नहीं।",
    formTitle: "शिकायत प्रारूप (एफआईआर नहीं)",
    formMissingTitle: "लापता व्यक्ति नागरिक रिपोर्ट (नागरिक प्रारूप - एफआईआर नहीं)",
    formSub: "शिकायतकर्ता द्वारा तैयार। पुलिस को प्रस्तुत नहीं और पंजीकृत नहीं।",
    formMissingSub: "नागरिक द्वारा तैयार तात्कालिक रिपोर्ट प्रारूप। सर्वोच्च न्यायालय (बचपन बचाओ आंदोलन) के अनुसार कोई २४/४८ घंटे की प्रतीक्षा अवधि नहीं है।",
    formMode: "आप यह जानकारी पुलिस को कैसे देना चाहते हैं",
    formModeWritten: "लिखित",
    formModeOral: "मौखिक",
    formModeElectronic: "इलेक्ट्रॉनिक / ऑनलाइन",
    formComplainantName: "शिकायतकर्ता का पूरा नाम",
    formComplainantAddress: "शिकायतकर्ता का पता",
    formComplainantContact: "संपर्क मोबाइल नंबर",
    formComplainantId: "पहचान पत्र प्रकार (वैकल्पिक – पुलिस प्रत्यक्ष पहचान सत्यापित करती है; पूरा आधार न लिखें)",
    formOccurrenceTime: "घटना की तारीख और समय",
    formPlaceOccurrence: "घटना स्थल (पता / मुख्य पहचान चिह्न)",
    formNatureOffence: "अपराध / घटना का प्रकार",
    formDetailsSuspect: "आरोपी / संदेही का विवरण (यदि ज्ञात हो)",
    formSuspectName: "संदेही का नाम",
    formSuspectAddress: "संदेही का पता",
    formSuspectDesc: "संदेही का हुलिया / पहचान चिह्न",
    formVictimsDetails: "पीड़ित व्यक्ति(यों) का विवरण",
    formVictimName: "पीड़ित का नाम",
    formVictimContact: "पीड़ित का संपर्क नंबर",
    formVictimAddress: "पीड़ित का पता",
    formSummaryIncident: "घटना का सारांश (प्रकरण के तथ्य)",
    formPropertyInvolved: "शामिल संपत्ति (यदि कोई हो)",
    formPropertyDesc: "संपत्ति का विवरण",
    formPropertyValue: "अनुमानित मूल्य (₹)",
    formWitnesses: "साक्षीदार / गवाह (नाम व पते)",
    formPoliceUse: "केवल पुलिस उपयोग हेतु (प्राप्तकर्ता अधिकारी द्वारा भरा जाएगा)",
    formSign: "शिकायतकर्ता का नाम (यह डिजिटल हस्ताक्षर नहीं है)",
    formSignText: "मैं पुष्टि करता/करती हूँ कि इस प्रारूप में दी गई जानकारी मेरी सर्वोत्तम जानकारी के अनुसार सत्य है।",
    formVerifyBtn: "शिकायत प्रारूप तैयार करें",
    fileUploadMedicalTitle: "सहायक सामग्री (वैकल्पिक): चिकित्सा दस्तावेज, फोटो या अन्य रिकॉर्ड",
    fileUploadDrag: "फाइलें यहाँ खींचें और छोड़ें, या चुनने के लिए क्लिक करें",
    idNotice: "पहचान दस्तावेज अपलोड न करें। पुलिस प्रत्यक्ष पहचान की जांच करती है।",
    truthNotice: "कृपया केवल सत्य जानकारी और प्रामाणिक दस्तावेज ही प्रदान करें।",
    aiTitle: "मशीन द्वारा सुझाई गई कानूनी धाराएं (कानूनी समीक्षा नहीं)",
    aiScanning: "विवरण का कानूनी विश्लेषण जारी है...",
    aiConsensus: "संभावित रूप से प्रासंगिक बीएनएस धाराएं (मशीन द्वारा सुझाई गई)",
    aiAction: "प्रक्रियात्मक सलाह (विश्लेषण इंजन द्वारा)",
    copyDraftBtn: "प्रारूप पाठ कॉपी करें",
    draftCopied: "प्रारूप पाठ कॉपी हो गया!",
    deliveryNotice: "बंधू शिकायतें सीधे पुलिस को नहीं भेजता। इस प्रारूप को पुलिस स्टेशन ले जाएं या आधिकारिक चैनल का उपयोग करें।",
    statusTitle: "शिकायत की स्थिति",
    statusRecorded: "दर्ज",
    statusNotRecorded: "दर्ज नहीं",
    secComplainant: "१. शिकायतकर्ता / सूचनाकर्ता का विवरण",
    secIncident: "२. घटना की तारीख और समय (कथनानुसार)",
    secPlace: "३. घटना स्थल (कथनानुसार)",
    secSummary: "८. घटना का संक्षिप्त विवरण (शिकायतकर्ता के शब्दों में)",
    secNature: "४. अपराध का स्वरूप",
    secLegal: "५. संभावित प्रासंगिक बीएनएस धाराएं (मशीन-सुझाई गई; कोई कानूनी निर्णय नहीं)",
    secSuspects: "६. आरोपी / संदेही का विवरण (कथनानुसार)",
    secVictims: "७. पीड़ित व्यक्ति(यों) का विवरण (कथनानुसार)",
    secProperty: "९. शामिल संपत्ति (कथनानुसार)",
    secWitnesses: "१०. गवाह (नाम व पते)",
    secSignatures: "१२. शिकायतकर्ता पुष्टिकरण",
    secMissingProfile: "लापता व्यक्ति का शारीरिक विवरण",
    secMissingDirective: "वैधानिक निर्देश: सर्वोच्च न्यायालय (बचपन बचाओ आंदोलन बनाम भारत संघ) के निर्देशानुसार लापता व्यक्ति/बच्चों के लिए कोई 24 या 48 घंटे की प्रतीक्षा अवधि नहीं है। स्टेशन जनरल डायरी (GD) में तत्काल प्रविष्टि अनिवार्य है।",
    mpName: "लापता व्यक्ति का पूरा नाम",
    mpAge: "उम्र (वर्ष)",
    mpLastSeenLoc: "अंतिम बार देखे जाने का स्थान",
    mpLastSeenAt: "अंतिम बार देखे जाने की तारीख व समय",
    mpImage: "फोटो / छवि",
    mpBirthmarks: "जन्मचिह्न / पहचान चिह्न / तिल / निशान",
    mpGender: "लिंग",
    mpHeight: "अनुमानित लंबाई (सेमी)",
    mpComplexion: "रंग / रूप",
    mpClothing: "अंतिम बार पहने गए वस्त्र",
    mpRelation: "शिकायतकर्ता से संबंध",
    mpCircumstances: "गुमशुदगी की परिस्थितियां / विवरण",
    draftEmailBtn: "पुलिस थाने हेतु ईमेल प्रारूप बनाएं",
    downloadPdfBtn: "आधिकारिक पीडीएफ डाउनलोड करें",
    viewInLang: "शिकायत प्रारूप भाषा:",
    minorAlert: "नाबालिग: सर्वोच्च न्यायालय निर्देश व बीएनएस धारा १३७ अनिवार्य प्रक्रिया लागू।"
  },
  mr: {
    logoTitle: "बंधू तक्रार मसुदा",
    logoSub: "फक्त अंतर्गत चाचणीसाठी",
    tabLocator: "घटनेचे ठिकाण",
    tabDirectory: "हद्द क्षेत्रे",
    tabInsights: "डेटाविषयी",
    tabMissing: "🚨 बेपत्ता व्यक्ती",
    searchPlaceholder: "मुंबईतील ठिकाण शोधा...",
    searchDisabled: "डेटा हाताळणी धोरण मंजूर होईपर्यंत पत्ता शोध बंद आहे. नकाशावर क्लिक करा किंवा जीपीएस वापरा.",
    gpsBtn: "जीपीएस स्थान वापरा",
    gpsPromptBtn: "📍 जीपीएस पत्ता शोधा",
    resetBtn: "ठिकाण काढा",
    assignedTitle: "हद्द (नकाशावर आधारित अंदाज)",
    matching: "नकाशाच्या सीमा तपासत आहे...",
    estimate: "नकाशा अंदाज – पोलिसांनी खात्री करावी",
    unconfirmed: "खात्री आवश्यक",
    ward: "प्रशासकीय प्रभाग",
    address: "पोलीस ठाण्याचा पत्ता",
    contact: "पोलीस ठाण्याचा संपर्क",
    emailStation: "पोलीस ठाण्याचा अधिकृत ईमेल",
    remarks: "विशेष नोंदी",
    coords: "निवडलेले ठिकाण",
    noLocation: "घटनेचे ठिकाण निवडलेले नाही. नकाशावर क्लिक करा, खूण ओढा किंवा जीपीएस वापरा.",
    lodgeBtn: "तक्रारीचा मसुदा तयार करा",
    lodgeMissingBtn: "🚨 बेपत्ता व्यक्तीची तक्रार नोंदवा",
    dirSearchPlaceholder: "नाव किंवा प्रभागाद्वारे शोधा...",
    insTitle: "नकाशा डेटा",
    insActive: "हद्द क्षेत्रे",
    insWards: "महानगरपालिका प्रभाग",
    insGis: "सीमा डेटाची स्थिती",
    insGisText: "हद्दीच्या सीमा डेटाचा स्रोत आणि तारीख पडताळलेली नाही. खुणा प्रत्येक क्षेत्राचे मध्य दाखवतात, पोलीस ठाण्याचा पत्ता नाही. पोलीस ठाण्यांचे पत्ते आणि संपर्क बंधूमध्ये उपलब्ध नाहीत.",
    // Form fields
    formTitle: "तक्रारीचा मसुदा (एफआयआर नाही)",
    formMissingTitle: "बेपत्ता व्यक्ती नागरिक अहवाल (नागरिक मसुदा - एफआयआर नाही)",
    formSub: "तक्रारदाराने तयार केलेला. पोलिसांना सादर केलेला नाही आणि नोंदवलेला नाही.",
    formMissingSub: "नागरिकाने तयार केलेला अहवाल मसुदा. सर्वोच्च न्यायालयाच्या निर्देशानुसार (बचपन बचाओ आंदोलन), कोणतीही २४/४८ तासांची प्रतीक्षा मुदत लागू नाही.",
    formMode: "ही माहिती पोलिसांना कशी देणार",
    formModeWritten: "लेखी",
    formModeOral: "तोंडी",
    formModeElectronic: "इलेक्ट्रॉनिक / ऑनलाईन",
    formComplainantName: "तक्रारदाराचे पूर्ण नाव",
    formComplainantAddress: "तक्रारदाराचा पत्ता",
    formComplainantContact: "संपर्क क्रमांक",
    formComplainantId: "ओळखपत्राचा प्रकार (ऐच्छिक – पोलीस ओळख प्रत्यक्ष पडताळतात; पूर्ण आधार क्रमांक लिहू नका)",
    formOccurrenceTime: "घटनेची तारीख आणि वेळ",
    formPlaceOccurrence: "घटनेचे ठिकाण (पत्ता / महत्त्वाचे खूण)",
    formNatureOffence: "गुन्ह्याचे स्वरूप",
    formDetailsSuspect: "आरोपी / संशयिताचा तपशील (माहित असल्यास)",
    formSuspectName: "संशयिताचे नाव",
    formSuspectAddress: "संशयिताचा पत्ता",
    formSuspectDesc: "संशयिताचे वर्णन / ओळख पटवणारे चिन्ह",
    formVictimsDetails: "पीडित व्यक्तींचा तपशील",
    formVictimName: "पीडित व्यक्तीचे नाव",
    formVictimContact: "पीडित व्यक्तीचा संपर्क क्रमांक",
    formVictimAddress: "पीडित व्यक्तीचा पत्ता",
    formSummaryIncident: "घटनेचा सारांश (प्रकरणातील तथ्ये)",
    formPropertyInvolved: "समाविष्ट मालमत्ता (असल्यास)",
    formPropertyDesc: "मालमत्तेचे वर्णन",
    formPropertyValue: "अंदाजे किंमत (₹)",
    formWitnesses: "साक्षीदार (नावे आणि पत्ते)",
    formPoliceUse: "फक्त पोलिसांच्या वापरासाठी (तक्रार स्वीकारणाऱ्या अधिकाऱ्याने भरावे)",
    formSign: "तक्रारदाराचे टाइप केलेले नाव (ही डिजिटल स्वाक्षरी नाही)",
    formSignText: "मी याद्वारे जाहीर करतो की या मसुद्यातील माहिती माझ्या माहितीनुसार सत्य आहे.",
    formVerifyBtn: "तक्रारीचा मसुदा तयार करा",
    fileUploadMedicalTitle: "सहाय्यक साहित्य (ऐच्छिक): वैद्यकीय अहवाल, फोटो किंवा इतर कागदपत्रे",
    fileUploadDrag: "फायली येथे ड्रॅग आणि ड्रॉप करा, किंवा ब्राउझ करण्यासाठी क्लिक करा",
    idNotice: "ओळखपत्रे अपलोड करू नका. पोलीस ओळख प्रत्यक्ष पडताळतात.",
    truthNotice: "कृपया केवळ खरी माहिती आणि खरी कागदपत्रे द्या.",
    aiTitle: "मशीनने सुचवलेली कायदेशीर कलमे (कायदेशीर पुनरावलोकन झालेले नाही)",
    aiScanning: "वर्णनाचे विश्लेषण सुरू आहे...",
    aiConsensus: "संभाव्य संबंधित कलमे (मशीनने सुचवलेली)",
    aiAction: "विश्लेषण प्रणालीची प्रक्रियात्मक नोंद (कायदेशीर पुनरावलोकन झालेले नाही)",
    copyDraftBtn: "मसुदा मजकूर कॉपी करा",
    draftCopied: "मसुदा मजकूर कॉपी केला!",
    deliveryNotice: "बंधू तक्रारी पाठवत नाही आणि त्याच्याकडे पडताळलेले पोलीस संपर्क तपशील नाहीत. हा मसुदा पोलीस ठाण्यात घेऊन जा किंवा अधिकृत पोलीस माध्यम वापरा.",
    statusTitle: "तक्रारीची स्थिती",
    statusRecorded: "नोंदवले",
    statusNotRecorded: "नोंद नाही",
    secComplainant: "१. तक्रारदार / माहिती देणाऱ्याचा तपशील",
    secIncident: "२. घटनेची तारीख आणि वेळ (कथनानुसार)",
    secPlace: "३. घटनेचे ठिकाण (कथनानुसार)",
    secSummary: "८. घटनेचे संक्षिप्त वर्णन (तथ्ये)",
    secNature: "४. गुन्ह्याचे स्वरूप",
    secLegal: "५. संभाव्य संबंधित बी.एन.एस. कलमे (मशीन-सुचवलेली; कायदेशीर निर्णय नाही)",
    secSuspects: "६. आरोपी / संशयिताचा तपशील (कथनानुसार)",
    secVictims: "७. पीडित व्यक्तींचा तपशील (कथनानुसार)",
    secProperty: "९. समाविष्ट मालमत्ता (कथनानुसार)",
    secWitnesses: "१०. साक्षीदार (नावे आणि पत्ते)",
    secSignatures: "१२. तक्रारदाराची पुष्टी",
    secMissingProfile: "बेपत्ता व्यक्तीचे शारीरिक वर्णन",
    secMissingDirective: "कायदेशीर सूचना: सर्वोच्च न्यायालय (बचपन बचाओ आंदोलन विरुद्ध भारत सरकार) नुसार बेपत्ता व्यक्तींसाठी कोणतीही २४ किंवा ४८ तासांची वाट पाहण्याची मुदत नाही. स्टेशन जनरल डायरीत तात्काळ नोंद होणे बंधनकारक आहे.",
    mpName: "बेपत्ता व्यक्तीचे पूर्ण नाव",
    mpAge: "वय (वर्षे)",
    mpLastSeenLoc: "शेवटचे पाहिलेले ठिकाण",
    mpLastSeenAt: "शेवटचे पाहिलेली तारीख व वेळ",
    mpImage: "फोटो / छायाचित्र",
    mpBirthmarks: "जन्मखूण / शरीरावरील ओळख खूण",
    mpGender: "लिंग",
    mpHeight: "अंदाजे उंची (सेमी)",
    mpComplexion: "वर्ण / त्वचा",
    mpClothing: "शेवटचे घातलेले कपडे",
    mpRelation: "तक्रारदाराशी नाते",
    mpCircumstances: "बेपत्ता होण्याची पार्श्वभूमी / तपशील",
    draftEmailBtn: "पोलीस ठाण्यासाठी ईमेल मसुदा तयार करा",
    downloadPdfBtn: "अधिकृत पीडीएफ डाऊनलोड करा",
    viewInLang: "तक्रार मसुदा भाषा:",
    minorAlert: "अल्पवयीन: सर्वोच्च न्यायालयाचे निर्देश आणि बीएनएस कलम १३७ अंतर्गत तात्काळ नोंद आवश्यक."
  }
};

export default function App() {
  const [lang, setLang] = useState('en');
  const t = TRANSLATIONS[lang];

  const [activeTab, setActiveTab] = useState('locator');
  const [stations, setStations] = useState([]);
  const [jurisdictionsGeoJSON, setJurisdictionsGeoJSON] = useState(null);
  
  // Search state
  const [searchText, setSearchText] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  
  // Locator coordinates
  const [coords, setCoords] = useState({ lat: 19.0760, lng: 72.8777 });
  // Incident location is only set when the complainant picks it (map click, marker drag or GPS).
  const [locationSelected, setLocationSelected] = useState(false);
  // Reconciled jurisdiction: { confirmed, stationName, status, message } (see trustSafety.js)
  const [jurisdiction, setJurisdiction] = useState(reconcileJurisdiction(assessJurisdiction(null, null), null));
  const [localJurisdiction, setLocalJurisdiction] = useState(null);
  const [isCheckingJurisdiction, setIsCheckingJurisdiction] = useState(false);

  // AI legal scanning
  const [isAiScanning, setIsAiScanning] = useState(false);
  const [aiLegalResult, setAiLegalResult] = useState(null);

  // Supporting material: the file stays in the browser; only its name and size are shown.
  const [uploadedMedicalFile, setUploadedMedicalFile] = useState(null);

  // Complaint Workspace State. Bandhoo can only create drafts; it never submits or registers.
  const [showForm, setShowForm] = useState(false);
  const [draftCreated, setDraftCreated] = useState(false);
  const [draftCreatedAt, setDraftCreatedAt] = useState('');
  const [isDraftCopied, setIsDraftCopied] = useState(false);
  // Structured record from the backend workflow: { state: 'idle'|'loading'|'ok'|'unavailable', summary }
  const [structured, setStructured] = useState({ state: 'idle', summary: null });

  // Complaint draft inputs (no prefilled offence, legal section, suspect or police entries)
  const [formInputs, setFormInputs] = useState(emptyForm);

  // Missing Person Mode State
  const [isMissingPersonReport, setIsMissingPersonReport] = useState(false);
  const [missingPersonInputs, setMissingPersonInputs] = useState(emptyMissingPersonForm);

  // GPS prompt modal state
  const [gpsPrompt, setGpsPrompt] = useState({ open: false, detectedAddress: '', lat: null, lng: null, stationName: '' });

  // Email draft modal state
  const [emailDraftModal, setEmailDraftModal] = useState({ open: false, data: null, loading: false });

  // PDF download loading state
  const [pdfDownloading, setPdfDownloading] = useState(false);

  const [directorySearch, setDirectorySearch] = useState('');
  
  const mapContainerRef = useRef(null);
  const mapRef = useRef(null);
  const userMarkerRef = useRef(null);
  const geojsonLayerRef = useRef(null);
  const debounceTimerRef = useRef(null);

  // Load JSON and GeoJSON
  useEffect(() => {
    fetch('/police_stations_data.json')
      .then(res => res.json())
      .then(data => {
        const filtered = data.filter(s => s.subtype === 'Station');
        setStations(filtered);
      })
      .catch(err => console.error(err));

    fetch('/mumbai_police_jurisdictions.geojson')
      .then(res => res.json())
      .then(data => {
        setJurisdictionsGeoJSON(data);
      })
      .catch(err => console.error(err));
  }, []);

  const updateLocationRef = useRef(null);
  const initialCoordsRef = useRef(coords);

  // Incident location → jurisdiction. The local polygon-containment result is authoritative;
  // the backend result is only a cross-check and can never override it (see reconcileJurisdiction).
  const updateLocation = useCallback((lat, lng) => {
    setCoords({ lat, lng });
    setLocationSelected(true);

    if (userMarkerRef.current) {
      userMarkerRef.current.setLatLng([lat, lng]);
    }

    const local = assessJurisdiction({ lat, lng }, jurisdictionsGeoJSON);
    setLocalJurisdiction(local);
    setJurisdiction(reconcileJurisdiction(local, null));
    setIsCheckingJurisdiction(true);

    fetch(`${API_BASE_URL}/api/get-jurisdiction`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ latitude: lat, longitude: lng })
    })
      .then(res => {
        if (!res.ok) throw new Error('Jurisdiction service unavailable');
        return res.json();
      })
      .then(data => setJurisdiction(reconcileJurisdiction(local, data)))
      .catch(() => {
        // Backend unavailable: keep the local result. Never fall back to a nearest-station guess.
      })
      .finally(() => {
        setIsCheckingJurisdiction(false);
      });

    // Reverse geocoding sends the location to a third party; off until a data-handling policy is approved.
    if (EXTERNAL_GEOCODING_ENABLED) {
      fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`)
        .then(res => res.json())
        .then(data => {
          if (data && data.display_name) {
            setFormInputs(prev => ({ ...prev, placeOfOccurrence: data.display_name }));
          }
        })
        .catch(() => {});
    }
  }, [jurisdictionsGeoJSON]);

  useEffect(() => {
    updateLocationRef.current = updateLocation;
  }, [updateLocation]);

  // Initialize Map
  useEffect(() => {
    if (showForm || !mapContainerRef.current || stations.length === 0 || !jurisdictionsGeoJSON) return;

    const map = L.map(mapContainerRef.current, {
      center: [initialCoordsRef.current.lat, initialCoordsRef.current.lng],
      zoom: 12,
      zoomControl: false
    });
    mapRef.current = map;

    L.control.zoom({ position: 'bottomright' }).addTo(map);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    const geojsonLayer = L.geoJSON(jurisdictionsGeoJSON, {
      style: (feature) => {
        const ward = feature.properties.ward || 'A';
        const color = getWardColor(ward);
        return {
          fillColor: color,
          weight: 1.5,
          opacity: 0.85,
          color: '#334155',
          fillOpacity: 0.28
        };
      },
      onEachFeature: (feature, layer) => {
        layer.on({
          mouseover: (e) => {
            const l = e.target;
            l.setStyle({
              fillOpacity: 0.45,
              weight: 2.5,
              color: '#004080'
            });
            l.bringToFront();
          },
          mouseout: (e) => {
            geojsonLayer.resetStyle(e.target);
          },
          click: (e) => {
            updateLocationRef.current?.(e.latlng.lat, e.latlng.lng);
          }
        });
        
        layer.bindPopup(`
          <div style="font-family: 'Inter', sans-serif;">
            <b style="font-family: 'Outfit', sans-serif; font-size:13px; color:#004080;">${feature.properties.name} Jurisdiction</b>
            <div style="margin-top:4px; font-size:11px; color:#475569;">Ward: ${feature.properties.ward || 'N/A'}</div>
          </div>
        `);
      }
    }).addTo(map);
    geojsonLayerRef.current = geojsonLayer;

    const stationIcon = L.divIcon({
      html: `
        <svg class="station-pin-custom" viewBox="0 0 24 24" width="24" height="24" fill="#004080">
          <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
        </svg>
      `,
      className: 'station-marker-div',
      iconSize: [24, 24],
      iconAnchor: [12, 24]
    });

    stations.forEach(s => {
      L.marker([s.latitude, s.longitude], { icon: stationIcon })
        .addTo(map)
        .bindPopup(`
          <div style="font-family: 'Inter', sans-serif; min-width: 180px;">
            <b style="font-family: 'Outfit', sans-serif; font-size:13px; color:#004080;">${s.name} jurisdiction area</b>
            <div style="margin-top:6px; font-size:11px; color:#475569;">Marker shows the centre of the area, not the police station address.</div>
            <div style="font-size:11px; color:#475569;"><b>Station address / contact:</b> ${NOT_AVAILABLE}</div>
          </div>
        `);
    });

    const userIcon = L.divIcon({
      className: 'user-pin-custom',
      iconSize: [14, 14],
      iconAnchor: [7, 7]
    });

    const userMarker = L.marker([initialCoordsRef.current.lat, initialCoordsRef.current.lng], {
      draggable: true,
      icon: userIcon,
      zIndexOffset: 1000
    }).addTo(map);
    userMarkerRef.current = userMarker;

    userMarker.on('dragend', () => {
      const latlng = userMarker.getLatLng();
      updateLocationRef.current?.(latlng.lat, latlng.lng);
    });

    map.on('click', (e) => {
      updateLocationRef.current?.(e.latlng.lat, e.latlng.lng);
    });

    // No jurisdiction is assessed for the default map centre: the complainant must pick a location.

    return () => {
      map.remove();
    };
  }, [stations, jurisdictionsGeoJSON, showForm]);

  const clearLocation = () => {
    setLocationSelected(false);
    setLocalJurisdiction(null);
    setJurisdiction(reconcileJurisdiction(assessJurisdiction(null, jurisdictionsGeoJSON), null));
  };

  // AI Narrative Classifier — RAG-based via /api/classify-offence
  const handleIncidentNarrativeChange = (e) => {
    const text = e.target.value;
    setFormInputs(prev => ({ ...prev, incidentSummary: text }));

    if (text.length < 10) {
      setAiLegalResult(null);
      return;
    }

    setIsAiScanning(true);

    if (debounceTimerRef.current) clearTimeout(debounceTimerRef.current);

    debounceTimerRef.current = setTimeout(() => {
      // Call the RAG backend
      fetch(`${API_BASE_URL}/api/classify-offence`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ narrative: text })
      })
        .then(res => {
          if (!res.ok) throw new Error('API offline');
          return res.json();
        })
        .then(data => {
          if (data.predictions && data.predictions.length > 0) {
            const top = data.predictions[0];
            const sectionsList = data.predictions
              .map(p => `Section ${p.section} (${p.title})`)
              .join(' & ');

            // Suggestions are shown separately; they are not copied into the complainant's draft
            // unless the complainant chooses to (see "Use suggestions in draft").
            setAiLegalResult({
              offence: top.title,
              bnsSection: sectionsList + ' of BNS, 2023',
              bnssAction: data.recommended_action,
              predictions: data.predictions,
              model: data.model,
              inferenceStatus: data.inference_status,
              standardizedNarrative: data.standardized_narrative,
              translations: data.translations,
              isRag: true
            });
          } else {
            setAiLegalResult(null);
          }
          setIsAiScanning(false);
        })
        .catch(() => {
          // Backend unavailable: show a neutral state. No legal sections or advice are suggested.
          setAiLegalResult(analysisUnavailableState());
          setIsAiScanning(false);
        });
    }, 800);
  };

  // Address Search (third-party geocoding; off until a data-handling policy is approved)
  const handleSearchChange = (e) => {
    const query = e.target.value;
    setSearchText(query);

    if (!EXTERNAL_GEOCODING_ENABLED) {
      setSuggestions([]);
      return;
    }

    if (debounceTimerRef.current) clearTimeout(debounceTimerRef.current);

    if (query.length < 3) {
      setSuggestions([]);
      return;
    }

    debounceTimerRef.current = setTimeout(() => {
      setIsSearching(true);
      fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query + ', Mumbai')}&addressdetails=1&limit=5`)
        .then(res => res.json())
        .then(data => setSuggestions(data))
        .catch(() => setSuggestions([]))
        .finally(() => setIsSearching(false));
    }, 400);
  };

  const selectSuggestion = (item) => {
    const lat = parseFloat(item.lat);
    const lon = parseFloat(item.lon);
    setSearchText(item.display_name);
    setSuggestions([]);
    if (mapRef.current) {
      mapRef.current.flyTo([lat, lon], 15, { animate: true });
    }
    updateLocation(lat, lon);
  };

  const triggerGPSWithPrompt = () => {
    if (!navigator.geolocation) {
      alert("Geolocation is not supported by your browser");
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const lat = pos.coords.latitude;
        const lng = pos.coords.longitude;
        if (mapRef.current) mapRef.current.flyTo([lat, lng], 15, { animate: true });
        updateLocation(lat, lng);

        fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`)
          .then(res => res.json())
          .then(data => {
            const detected = (data && data.display_name) ? data.display_name : `Mumbai Location (Lat: ${lat.toFixed(4)}, Lng: ${lng.toFixed(4)})`;
            setGpsPrompt({
              open: true,
              detectedAddress: detected,
              lat,
              lng,
              stationName: jurisdiction.stationName || ''
            });
          })
          .catch(() => {
            setGpsPrompt({
              open: true,
              detectedAddress: `Mumbai Location (Lat: ${lat.toFixed(4)}, Lng: ${lng.toFixed(4)})`,
              lat,
              lng,
              stationName: jurisdiction.stationName || ''
            });
          });
      },
      (err) => {
        alert("GPS location unavailable: " + (err.message || "Please allow location access"));
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  };

  const triggerGPS = triggerGPSWithPrompt;

  const acceptGpsAddress = () => {
    if (gpsPrompt.detectedAddress) {
      setFormInputs(prev => ({ ...prev, placeOfOccurrence: gpsPrompt.detectedAddress }));
      setMissingPersonInputs(prev => ({ ...prev, lastSeenLocation: gpsPrompt.detectedAddress }));
    }
    setGpsPrompt({ open: false, detectedAddress: '', lat: null, lng: null, stationName: '' });
  };

  // Moves the map only. An area's centre is not the incident location.
  const focusOnStation = (station) => {
    if (mapRef.current) mapRef.current.flyTo([station.latitude, station.longitude], 14, { animate: true });
  };

  // Missing person photo handler with data URL thumbnail preview
  const handleMissingImageChange = (e) => {
    const file = e.target.files && e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setMissingPersonInputs(prev => ({
          ...prev,
          imageFile: file,
          imagePreview: reader.result
        }));
      };
      reader.readAsDataURL(file);
    }
  };

  // Supporting material: name and size only; nothing is uploaded or verified.
  const handleMedicalFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setUploadedMedicalFile({
        name: file.name,
        size: (file.size / 1024).toFixed(1) + ' KB',
        bytes: file.size
      });
    }
  };

  // Creates a local draft only. Nothing is submitted, received or registered.
  const handleDraftSubmit = (e) => {
    e.preventDefault();
    setDraftCreatedAt(new Date().toISOString());
    setDraftCreated(true);

    const isMissing = isMissingPersonReport;
    const statementText = isMissing
      ? (missingPersonInputs.circumstances || `${missingPersonInputs.fullName}, age ${missingPersonInputs.age || 'unknown'}, last seen at ${missingPersonInputs.lastSeenLocation || 'unknown'}. Identifying marks: ${missingPersonInputs.birthmarks || 'none'}.`)
      : formInputs.incidentSummary;

    // Ask Bandhoo's own backend to structure the account (no external service is called).
    setStructured({ state: 'loading', summary: null });
    fetch(`${API_BASE_URL}/api/v1/complaints/structure`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        statement: statementText,
        clarifications: [],
        evidence: uploadedMedicalFile
          ? [{ evidence_type: 'supporting document', file_name: uploadedMedicalFile.name, file_size_bytes: uploadedMedicalFile.bytes }]
          : [],
        location: locationSelected ? { latitude: coords.lat, longitude: coords.lng, source: 'map_pin' } : null,
        complainant: {
          full_name: formInputs.complainantName || (isMissing ? 'Family Informant' : 'Citizen Complainant'),
          phone: formInputs.complainantContact || null,
          email: null,
          address: formInputs.complainantAddress || null
        },
        missing_person: isMissing ? {
          full_name: missingPersonInputs.fullName || 'Unknown',
          age: missingPersonInputs.age ? parseInt(missingPersonInputs.age, 10) : null,
          gender: missingPersonInputs.gender || null,
          height_cm: missingPersonInputs.heightCm ? parseFloat(missingPersonInputs.heightCm) : null,
          complexion: missingPersonInputs.complexion || null,
          birthmarks: missingPersonInputs.birthmarks || null,
          identifying_marks: missingPersonInputs.birthmarks || null,
          clothing_last_seen: missingPersonInputs.clothingLastSeen || null,
          last_seen_datetime: missingPersonInputs.lastSeenDatetime || null,
          last_seen_location: missingPersonInputs.lastSeenLocation || null,
          relationship_to_complainant: missingPersonInputs.relationship || null,
          photo_filename: missingPersonInputs.imageFile ? missingPersonInputs.imageFile.name : null
        } : null,
        predicted_sections: (aiLegalResult && aiLegalResult.predictions) ? aiLegalResult.predictions : []
      })
    })
      .then(res => {
        if (!res.ok) throw new Error('Structuring service unavailable');
        return res.json();
      })
      .then(report => setStructured({ state: 'ok', summary: structuredSummary(report) }))
      .catch(() => setStructured({ state: 'unavailable', summary: null }));
  };

  const closeComplaintModal = () => {
    setShowForm(false);
    setIsMissingPersonReport(false);
    setDraftCreated(false);
    setDraftCreatedAt('');
    setStructured({ state: 'idle', summary: null });
    setUploadedMedicalFile(null);
    setFormInputs(emptyForm());
    setMissingPersonInputs(emptyMissingPersonForm());
  };

  // Formal PDF Download from Backend Endpoint
  const handleDownloadPDF = async () => {
    setPdfDownloading(true);
    try {
      const isMissing = isMissingPersonReport;
      const statementText = isMissing
        ? (missingPersonInputs.circumstances || `${missingPersonInputs.fullName}, age ${missingPersonInputs.age || 'unknown'}, last seen at ${missingPersonInputs.lastSeenLocation || 'unknown'}. Identifying marks: ${missingPersonInputs.birthmarks || 'none'}.`)
        : formInputs.incidentSummary;

      const payload = {
        statement: statementText || 'Citizen complaint statement draft.',
        clarifications: [],
        evidence: uploadedMedicalFile
          ? [{ evidence_type: 'supporting document', file_name: uploadedMedicalFile.name, file_size_bytes: uploadedMedicalFile.bytes }]
          : [],
        location: locationSelected ? { latitude: coords.lat, longitude: coords.lng, source: 'map_pin' } : null,
        complainant: {
          full_name: formInputs.complainantName || (isMissing ? 'Family Informant' : 'Citizen Complainant'),
          phone: formInputs.complainantContact || null,
          email: null,
          address: formInputs.complainantAddress || null
        },
        missing_person: isMissing ? {
          full_name: missingPersonInputs.fullName || 'Unknown',
          age: missingPersonInputs.age ? parseInt(missingPersonInputs.age, 10) : null,
          gender: missingPersonInputs.gender || null,
          height_cm: missingPersonInputs.heightCm ? parseFloat(missingPersonInputs.heightCm) : null,
          complexion: missingPersonInputs.complexion || null,
          birthmarks: missingPersonInputs.birthmarks || null,
          identifying_marks: missingPersonInputs.birthmarks || null,
          clothing_last_seen: missingPersonInputs.clothingLastSeen || null,
          last_seen_datetime: missingPersonInputs.lastSeenDatetime || null,
          last_seen_location: missingPersonInputs.lastSeenLocation || null,
          relationship_to_complainant: missingPersonInputs.relationship || null,
          photo_filename: missingPersonInputs.imageFile ? missingPersonInputs.imageFile.name : null
        } : null,
        predicted_sections: (aiLegalResult && aiLegalResult.predictions) ? aiLegalResult.predictions : []
      };

      const res = await fetch(`${API_BASE_URL}/api/v1/complaints/generate-pdf`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!res.ok) throw new Error('PDF generation service error');
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = isMissing ? `Missing_Person_${missingPersonInputs.fullName || 'Draft'}.pdf` : `Bandhoo_Complaint_Draft.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
      alert('Could not download PDF. You can also print the page using the print button.');
    } finally {
      setPdfDownloading(false);
    }
  };

  // Prepare and view email draft for jurisdictional police station
  const handleDraftEmail = async () => {
    setEmailDraftModal({ open: true, data: null, loading: true });
    try {
      const isMissing = isMissingPersonReport;
      const statementText = isMissing
        ? (missingPersonInputs.circumstances || `${missingPersonInputs.fullName}, age ${missingPersonInputs.age || 'unknown'}, last seen at ${missingPersonInputs.lastSeenLocation || 'unknown'}. Identifying marks: ${missingPersonInputs.birthmarks || 'none'}.`)
        : formInputs.incidentSummary;

      const payload = {
        statement: statementText || 'Citizen complaint statement draft.',
        clarifications: [],
        evidence: uploadedMedicalFile
          ? [{ evidence_type: 'supporting document', file_name: uploadedMedicalFile.name, file_size_bytes: uploadedMedicalFile.bytes }]
          : [],
        location: locationSelected ? { latitude: coords.lat, longitude: coords.lng, source: 'map_pin' } : null,
        complainant: {
          full_name: formInputs.complainantName || (isMissing ? 'Family Informant' : 'Citizen Complainant'),
          phone: formInputs.complainantContact || null,
          email: null,
          address: formInputs.complainantAddress || null
        },
        missing_person: isMissing ? {
          full_name: missingPersonInputs.fullName || 'Unknown',
          age: missingPersonInputs.age ? parseInt(missingPersonInputs.age, 10) : null,
          gender: missingPersonInputs.gender || null,
          height_cm: missingPersonInputs.heightCm ? parseFloat(missingPersonInputs.heightCm) : null,
          complexion: missingPersonInputs.complexion || null,
          birthmarks: missingPersonInputs.birthmarks || null,
          identifying_marks: missingPersonInputs.birthmarks || null,
          clothing_last_seen: missingPersonInputs.clothingLastSeen || null,
          last_seen_datetime: missingPersonInputs.lastSeenDatetime || null,
          last_seen_location: missingPersonInputs.lastSeenLocation || null,
          relationship_to_complainant: missingPersonInputs.relationship || null,
          photo_filename: missingPersonInputs.imageFile ? missingPersonInputs.imageFile.name : null
        } : null,
        predicted_sections: (aiLegalResult && aiLegalResult.predictions) ? aiLegalResult.predictions : []
      };

      const res = await fetch(`${API_BASE_URL}/api/v1/complaints/email-draft?recipient_type=police_nodal`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!res.ok) throw new Error('Email draft service error');
      const data = await res.json();
      setEmailDraftModal({ open: true, data, loading: false });
    } catch (err) {
      console.error(err);
      setEmailDraftModal({ open: true, data: { error: 'Service unavailable' }, loading: false });
    }
  };


  const handleAddWitness = () => {
    setFormInputs(prev => ({
      ...prev,
      witnesses: [...prev.witnesses, { name: '', phone: '', address: '' }]
    }));
  };

  const handleRemoveWitness = (index) => {
    setFormInputs(prev => ({
      ...prev,
      witnesses: prev.witnesses.filter((_, idx) => idx !== index)
    }));
  };

  const handleWitnessChange = (index, field, value) => {
    setFormInputs(prev => {
      const updated = [...prev.witnesses];
      updated[index] = { ...updated[index], [field]: value };
      return { ...prev, witnesses: updated };
    });
  };

  // Complainant chooses to add the machine suggestions to the draft; they stay marked as machine-suggested.
  const applySuggestionsToDraft = () => {
    if (!aiLegalResult || !aiLegalResult.bnsSection) return;
    setFormInputs(prev => ({ ...prev, legalSections: `Machine-suggested, not legally reviewed: ${aiLegalResult.bnsSection}` }));
  };

  const handlePrint = () => {
    window.print();
  };

  const jurisdictionText = () => (jurisdiction.confirmed
    ? `${jurisdiction.stationName} (map-based estimate; police to confirm)`
    : JURISDICTION_CONFIRMATION_MESSAGE);

  const draftText = () => {
    const show = (v) => (v && String(v).trim() ? v : NOT_PROVIDED);
    const stationEmail = getStationEmail(jurisdiction.stationName || (assignedStation && assignedStation.name));

    if (isMissingPersonReport) {
      return `MISSING PERSON REPORT (CITIZEN DRAFT - NOT AN FIR)
STATUTORY MANDATE (Bachpan Bachao Andolan v. Union of India): Under Supreme Court directives, NO 24-HOUR OR 48-HOUR WAITING PERIOD IS APPLICABLE. Entry must be made immediately in the Station General Diary.

Report created: ${draftCreatedAt}
Jurisdiction: ${jurisdictionText()}
Station Official Email: ${stationEmail}
Informant / Complainant: ${show(formInputs.complainantName)}
Contact: ${show(formInputs.complainantContact)}
Relationship to Missing Person: ${show(missingPersonInputs.relationship)}

MISSING PERSON PHYSICAL PROFILE:
Full Name: ${show(missingPersonInputs.fullName)}
Age: ${show(missingPersonInputs.age)}
Gender: ${show(missingPersonInputs.gender)}
Height / Complexion: ${show(missingPersonInputs.heightCm)} cm / ${show(missingPersonInputs.complexion)}
Last Seen Location: ${show(missingPersonInputs.lastSeenLocation)}
Last Seen Date/Time: ${show(missingPersonInputs.lastSeenDatetime)}
Clothing Last Seen: ${show(missingPersonInputs.clothingLastSeen)}
Birthmarks / Distinguishing Marks: ${show(missingPersonInputs.birthmarks)}
Photograph: ${missingPersonInputs.imageFile ? missingPersonInputs.imageFile.name : NOT_PROVIDED}

Circumstances of Disappearance:
${show(missingPersonInputs.circumstances)}
`;
    }

    const witnesses = formInputs.witnesses.filter(w => w.name || w.phone || w.address);
    const witnessStr = witnesses.length > 0
      ? witnesses.map((w, i) => `${i + 1}. ${show(w.name)} (Ph: ${show(w.phone)}, Addr: ${show(w.address)})`).join('\n  ')
      : NOT_PROVIDED;
    return `COMPLAINT DRAFT (NOT AN FIR)
${DRAFT_NOTICE}

Draft created: ${draftCreatedAt}
Jurisdiction: ${jurisdictionText()}
Station Official Email: ${stationEmail}
Complainant: ${show(formInputs.complainantName)}
Contact: ${show(formInputs.complainantContact)}
Date/time of occurrence (as stated): ${show(formInputs.occurrenceTime)}
Place of occurrence (as stated): ${show(formInputs.placeOfOccurrence)}
Description (complainant's words):
${show(formInputs.incidentSummary)}
Witnesses:
  ${witnessStr}
Possibly relevant sections (not a legal determination): ${show(formInputs.legalSections)}
`;
  };


  const copyDraftText = () => {
    navigator.clipboard.writeText(draftText());
    setIsDraftCopied(true);
    setTimeout(() => setIsDraftCopied(false), 2000);
  };

  // Filter lists
  const filteredDirectory = stations.filter(s => 
    s.name.toLowerCase().includes(directorySearch.toLowerCase()) ||
    s.ward.toLowerCase().includes(directorySearch.toLowerCase())
  );

  // Station details only when containment is confirmed by the map check (never from a nearest-centre guess).
  const assignedStation = jurisdiction.confirmed
    ? (stations.find(s => s.name === jurisdiction.stationName) || { name: jurisdiction.stationName })
    : null;

  const jurisdictionReason = () => {
    if (!locationSelected) return t.noLocation;
    switch (jurisdiction.status) {
      case 'outside_all': return 'The selected point is outside all known jurisdiction areas.';
      case 'near_boundary': return `The selected point is close to a boundary (about ${localJurisdiction?.distanceToBoundaryM ?? '?'} m).`;
      case 'multiple': return 'The selected point falls in more than one area in the boundary data.';
      case 'conflict': return 'The map check and the server check disagree.';
      case 'data_unavailable': return 'Boundary data is not loaded.';
      default: return '';
    }
  };

  const groupedDirectory = {};
  filteredDirectory.forEach(s => {
    const ward = s.ward || 'Unknown';
    if (!groupedDirectory[ward]) {
      groupedDirectory[ward] = [];
    }
    groupedDirectory[ward].push(s);
  });

  return (
    <div className="dashboard-container">
      {/* Sidebar Panel */}
      <div className="sidebar">
        <div className="sidebar-header">
          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
            <div className="logo-section">
              <span className="logo-icon">🏛️</span>
              <div>
                <h1 className="logo-text">{t.logoTitle}</h1>
                <div className="logo-sub">{t.logoSub}</div>
              </div>
            </div>
            
            <div className="lang-toggle-group">
              <button 
                type="button"
                className={`lang-toggle-btn ${lang === 'en' ? 'active' : ''}`}
                onClick={() => setLang('en')}
              >
                EN
              </button>
              <button 
                type="button"
                className={`lang-toggle-btn ${lang === 'hi' ? 'active' : ''}`}
                onClick={() => setLang('hi')}
              >
                हिन्दी
              </button>
              <button 
                type="button"
                className={`lang-toggle-btn ${lang === 'mr' ? 'active' : ''}`}
                onClick={() => setLang('mr')}
              >
                मराठी
              </button>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="tabs-nav">
          <button 
            className={`tab-btn ${activeTab === 'locator' ? 'active' : ''}`}
            onClick={() => { setActiveTab('locator'); if (!draftCreated) setShowForm(false); }}
          >
            {t.tabLocator}
          </button>
          <button 
            className={`tab-btn ${activeTab === 'directory' ? 'active' : ''}`}
            onClick={() => { setActiveTab('directory'); if (!draftCreated) setShowForm(false); }}
          >
            {t.tabDirectory}
          </button>
          <button 
            className={`tab-btn ${activeTab === 'analytics' ? 'active' : ''}`}
            onClick={() => { setActiveTab('analytics'); if (!draftCreated) setShowForm(false); }}
          >
            {t.tabInsights}
          </button>
        </div>

        {/* Emergency Missing Person Quick Access Banner on Home Page */}
        <div className="missing-person-banner glass-panel" style={{margin: '12px 14px 10px 14px', borderLeft: '4px solid #dc2626', background: 'linear-gradient(135deg, rgba(254, 242, 242, 0.95), rgba(255, 255, 255, 0.95))', padding: '12px 14px', borderRadius: '8px', boxShadow: '0 2px 8px rgba(220, 38, 38, 0.08)'}}>
          <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px'}}>
            <div style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
              <span style={{fontSize: '20px'}}>🚨</span>
              <div>
                <div style={{fontWeight: 700, fontSize: '12px', color: '#991b1b'}}>
                  {lang === 'mr' ? 'बेपत्ता व्यक्ती नागरिक अहवाल' : lang === 'hi' ? 'लापता व्यक्ति नागरिक रिपोर्ट' : 'Missing Person Citizen Report'}
                </div>
                <div style={{fontSize: '10px', color: '#7f1d1d', lineHeight: 1.3}}>
                  {lang === 'mr' ? 'सर्वोच्च न्यायालय: कोणतीही २४/४८ तासांची वाट पाहू नका' : lang === 'hi' ? 'उच्चतम न्यायालय: कोई 24/48 घंटे की प्रतीक्षा नहीं' : 'SC Mandate: Zero waiting period. File immediately.'}
                </div>
              </div>
            </div>
            <button 
              type="button"
              className="btn-urgent"
              onClick={() => {
                setIsMissingPersonReport(true);
                setShowForm(true);
                setDraftCreated(false);
              }}
              style={{fontSize: '11px', padding: '6px 10px', background: '#dc2626', color: '#fff', border: 'none', borderRadius: '6px', fontWeight: 700, cursor: 'pointer', whiteSpace: 'nowrap'}}
            >
              {t.lodgeMissingBtn}
            </button>
          </div>
        </div>

        {/* Sidebar Body */}
        <div className="sidebar-content">
          
          {/* TAB 1: LOCATOR */}
          {activeTab === 'locator' && (
            <div>
              {/* Search */}
              <div className="search-box">
                <div className="input-glow-wrapper">
                  <span className="search-icon">🔍</span>
                  <input 
                    type="text" 
                    placeholder={t.searchPlaceholder}
                    value={searchText}
                    onChange={handleSearchChange}
                  />
                  {isSearching && <span style={{fontSize: '11px', color: 'var(--color-primary)'}}>...</span>}
                </div>
                {!EXTERNAL_GEOCODING_ENABLED && (
                  <div style={{fontSize: '11px', color: 'var(--text-muted)', marginTop: '6px'}}>{t.searchDisabled}</div>
                )}

                {suggestions.length > 0 && (
                  <div className="suggestions-dropdown">
                    {suggestions.map((item, idx) => (
                      <div 
                        key={idx} 
                        className="suggestion-row"
                        onClick={() => selectSuggestion(item)}
                      >
                        {item.display_name}
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="btn-group">
                <button className="btn-secondary" onClick={triggerGPSWithPrompt}>
                  {t.gpsPromptBtn || t.gpsBtn}
                </button>
                <button className="btn-secondary" onClick={clearLocation}>
                  {t.resetBtn}
                </button>
              </div>

              {/* Jurisdiction Result panel: a map-based estimate, never a confirmation */}
              <div className="glass-panel alert-card success">
                <div className="alert-header">
                  <span className="panel-title" style={{margin: 0, border: 0, padding: 0}}>{t.assignedTitle}</span>
                  <span className={`status-badge ${isCheckingJurisdiction ? 'searching' : 'assigned'}`}>
                    {isCheckingJurisdiction ? t.matching : (jurisdiction.confirmed ? t.estimate : t.unconfirmed)}
                  </span>
                </div>

                {assignedStation ? (
                  <div>
                    <h2 className="station-title">{assignedStation.name} jurisdiction area</h2>
                    <div style={{fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px'}}>
                      Based on the selected map point and boundary data whose source has not been verified. Police to confirm.
                    </div>

                    <div className="detail-row" style={{marginTop: '15px'}}>
                      <span className="label">{t.ward}</span>
                      <span className="value">{assignedStation.ward || NOT_AVAILABLE}</span>
                    </div>
                    <div className="detail-row">
                      <span className="label">{t.address}</span>
                      <span className="value">{assignedStation.address || NOT_AVAILABLE}</span>
                    </div>
                    <div className="detail-row">
                      <span className="label">{t.contact}</span>
                      <span className="value">{assignedStation.contact || NOT_AVAILABLE}</span>
                    </div>
                    <div className="detail-row">
                      <span className="label">{t.emailStation || 'Official Email'}</span>
                      <span className="value" style={{fontFamily: 'monospace', fontSize: '11px', color: 'var(--color-primary)'}}>
                        {assignedStation.email || getStationEmail(assignedStation.name)}
                      </span>
                    </div>
                    {localJurisdiction && Number.isFinite(localJurisdiction.distanceToBoundaryM) && (
                      <div className="detail-row">
                        <span className="label">Distance to boundary</span>
                        <span className="value">about {localJurisdiction.distanceToBoundaryM} m</span>
                      </div>
                    )}
                  </div>
                ) : (
                  <div style={{color: 'var(--text-muted)', padding: '12px 0'}}>
                    <div style={{fontWeight: 700, color: 'var(--text-main)'}}>{JURISDICTION_CONFIRMATION_MESSAGE}</div>
                    <div style={{fontSize: '12px', marginTop: '6px'}}>{jurisdictionReason()}</div>
                  </div>
                )}

                {locationSelected && (
                  <div className="detail-row" style={{borderTop: '1px solid var(--border-color)', paddingTop: '10px', marginTop: '10px'}}>
                    <span className="label">{t.coords}</span>
                    <span className="value" style={{fontFamily: 'monospace', fontSize: '11px', color: 'var(--text-muted)'}}>
                      {coords.lat.toFixed(5)}, {coords.lng.toFixed(5)}
                    </span>
                  </div>
                )}

                {!showForm && (
                  <div style={{display: 'flex', gap: '8px', marginTop: '15px'}}>
                    <button
                      className="btn-pink"
                      style={{flex: 1}}
                      onClick={() => {
                        setIsMissingPersonReport(false);
                        setShowForm(true);
                      }}
                    >
                      {t.lodgeBtn}
                    </button>
                    <button
                      className="btn-secondary"
                      style={{padding: '8px 12px', fontSize: '11px', borderColor: '#fca5a5', color: '#b91c1c', background: '#fef2f2', fontWeight: 600}}
                      onClick={() => {
                        setIsMissingPersonReport(true);
                        setShowForm(true);
                      }}
                    >
                      {t.lodgeMissingBtn}
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* TAB 2: OFFICE DIRECTORY */}
          {activeTab === 'directory' && (
            <div>
              <div className="search-box">
                <div className="input-glow-wrapper">
                  <span className="search-icon">🔍</span>
                  <input 
                    type="text" 
                    placeholder={t.dirSearchPlaceholder}
                    value={directorySearch}
                    onChange={(e) => setDirectorySearch(e.target.value)}
                  />
                </div>
              </div>

              <div className="station-list">
                {Object.keys(groupedDirectory).sort().map(ward => (
                  <div key={ward} className="ward-group">
                    <div className="ward-header">{t.ward} {ward}</div>
                    {groupedDirectory[ward].map(s => (
                      <div 
                        key={s.id} 
                        className="station-item-card"
                        onClick={() => focusOnStation(s)}
                      >
                        <div className="station-item-name">{s.name}</div>
                        <div className="station-item-desc" style={{display: 'flex', flexDirection: 'column', gap: '2px'}}>
                          <span>Contact: {s.contact || NOT_AVAILABLE}</span>
                          <span style={{fontFamily: 'monospace', fontSize: '10.5px', color: 'var(--color-primary)'}}>Email: {s.email || getStationEmail(s.name)}</span>
                          <span style={{color: 'var(--color-accent)', fontWeight: '700', marginTop: '2px'}}>Show on map</span>
                        </div>
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 3: ACT INSIGHTS */}
          {activeTab === 'analytics' && (
            <div>
              <div className="glass-panel">
                <div className="panel-title">{t.insTitle}</div>
                <div className="stats-grid">
                  <div className="stat-box">
                    <div className="stat-val">{stations.length}</div>
                    <div className="stat-lbl">{t.insActive}</div>
                  </div>
                  <div className="stat-box">
                    <div className="stat-val">24</div>
                    <div className="stat-lbl">{t.insWards}</div>
                  </div>
                </div>
              </div>

              <div className="glass-panel">
                <div className="panel-title">{t.insGis}</div>
                <p style={{fontSize: '12px', color: 'var(--text-muted)', lineHeight: 1.5}}>
                  {t.insGisText}
                </p>
              </div>
            </div>
          )}

        </div>
      </div>

      {/* Main Workspace (Map OR FIR Form) */}
      <div className="main-workspace">
        
        {!showForm ? (
          /* VIEW A: COLORFUL MAP VIEW */
          <div className="map-container-wrapper">
            {locationSelected && (
              <div className="map-overlay-badge">
                {assignedStation
                  ? <>Jurisdiction (map estimate, police to confirm): {assignedStation.name}</>
                  : <>{JURISDICTION_CONFIRMATION_MESSAGE}</>}
              </div>
            )}

            {/* Map Legend */}
            <div className="floating-legend">
              <div className="legend-title">JURISDICTION MAP (BOUNDARY SOURCE UNVERIFIED)</div>
              <div className="legend-item">
                <span className="legend-color" style={{backgroundColor: '#6366f1', opacity: 0.3, borderColor: '#334155'}}></span>
                <span>Jurisdiction boundaries</span>
              </div>
              <div className="legend-item">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="var(--color-primary)" style={{display: 'block'}}>
                  <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
                </svg>
                <span>Area centre (not a police station address)</span>
              </div>
              <div className="legend-item">
                <span className="user-pin-custom" style={{display: 'inline-block', width: '12px', height: '12px'}}></span>
                <span>Selected incident location (draggable)</span>
              </div>
            </div>

            <div id="map" ref={mapContainerRef}></div>
          </div>
        ) : (
          /* VIEW B: FIR COMPLAINT FORM WORKSPACE */
          <div className="form-workspace">
            
            {/* Header bar to toggle back */}
            <div className="workspace-header-bar" style={{borderRadius: '6px 6px 0 0', margin: '0 auto 20px auto', maxWidth: '900px'}}>
              <h3 style={{fontFamily: 'var(--font-heading)', color: 'var(--color-primary)'}}>
                {isMissingPersonReport ? t.formMissingTitle : t.formTitle}
              </h3>
              <button className="btn-secondary" style={{width: 'auto', padding: '6px 14px'}} onClick={closeComplaintModal}>
                ← Return to Map
              </button>
            </div>

            {!draftCreated ? (
              /* DRAFTING INTERFACE */
              isMissingPersonReport ? (
                /* DEDICATED MISSING PERSON CITIZEN REPORT FORM */
                <div className="form-paper">
                  <div className="form-header-title">
                    <div style={{display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', marginBottom: '6px'}}>
                      <span className="missing-badge-urgent">🚨 {t.tabMissing || 'Urgent Report'}</span>
                    </div>
                    <h2>🇮🇳 {t.formMissingTitle}</h2>
                    <p>{t.formMissingSub}</p>
                    <div style={{
                      marginTop: '12px',
                      padding: '12px 14px',
                      background: '#fef2f2',
                      border: '1.5px solid #fca5a5',
                      borderRadius: '8px',
                      fontSize: '12px',
                      color: '#991b1b',
                      lineHeight: 1.5,
                      textAlign: 'left'
                    }}>
                      <b>⚖️ {lang === 'mr' ? 'सर्वोच्च न्यायालय वैधानिक निर्देश' : lang === 'hi' ? 'उच्चतम न्यायालय वैधानिक निर्देश' : 'Supreme Court Statutory Mandate'} (Bachpan Bachao Andolan v. Union of India):</b> {t.secMissingDirective}
                    </div>
                  </div>

                  <form onSubmit={handleDraftSubmit}>
                    {/* Location & Jurisdiction */}
                    <div className="form-section-header">Location Details & Police Station Jurisdiction</div>
                    <div className="form-group-field">
                      <label>Police station jurisdiction (map-based estimate; police to confirm)</label>
                      <input type="text" readOnly value={jurisdictionText()} style={{borderColor: 'var(--color-accent)', fontWeight: 600}} />
                    </div>
                    <div className="form-group-field">
                      <label>{t.emailStation || 'Official Police Station Email'}</label>
                      <input type="text" readOnly value={getStationEmail(jurisdiction.stationName || (assignedStation && assignedStation.name))} style={{fontFamily: 'monospace', color: 'var(--color-primary)', background: '#f8fafc'}} />
                    </div>

                    {/* Section 1: Informant Details */}
                    <div className="form-section-header">{t.secComplainant}</div>
                    <div className="form-row two-cols">
                      <div className="form-group-field">
                        <label>{t.formComplainantName}</label>
                        <input 
                          type="text" 
                          required 
                          placeholder="Your Full Name" 
                          value={formInputs.complainantName}
                          onChange={(e) => setFormInputs({...formInputs, complainantName: e.target.value})}
                        />
                      </div>
                      <div className="form-group-field">
                        <label>{t.formComplainantContact}</label>
                        <input 
                          type="tel" 
                          required 
                          placeholder="Mobile Number" 
                          value={formInputs.complainantContact}
                          onChange={(e) => setFormInputs({...formInputs, complainantContact: e.target.value})}
                        />
                      </div>
                    </div>

                    <div className="form-row two-cols">
                      <div className="form-group-field">
                        <label>{t.formComplainantAddress}</label>
                        <input 
                          type="text" 
                          placeholder="Your Address" 
                          value={formInputs.complainantAddress}
                          onChange={(e) => setFormInputs({...formInputs, complainantAddress: e.target.value})}
                        />
                      </div>
                      <div className="form-group-field">
                        <label>{t.mpRelation}</label>
                        <input 
                          type="text" 
                          required
                          placeholder="e.g. Parent, Sibling, Guardian, Relative, Friend" 
                          value={missingPersonInputs.relationship}
                          onChange={(e) => setMissingPersonInputs({...missingPersonInputs, relationship: e.target.value})}
                        />
                      </div>
                    </div>

                    {/* Section 2: Missing Person Physical Profile */}
                    <div className="form-section-header">{t.secMissingProfile}</div>

                    <div className="form-row two-cols">
                      <div className="form-group-field">
                        <label>{t.mpName} *</label>
                        <input 
                          type="text" 
                          required 
                          placeholder="Full name of missing person" 
                          value={missingPersonInputs.fullName}
                          onChange={(e) => setMissingPersonInputs({...missingPersonInputs, fullName: e.target.value})}
                        />
                      </div>
                      <div className="form-group-field">
                        <label>{t.mpAge} *</label>
                        <input 
                          type="number" 
                          required 
                          min="0"
                          max="125"
                          placeholder="Age in years" 
                          value={missingPersonInputs.age}
                          onChange={(e) => setMissingPersonInputs({...missingPersonInputs, age: e.target.value})}
                        />
                      </div>
                    </div>

                    {/* Minor alert banner */}
                    {missingPersonInputs.age && parseInt(missingPersonInputs.age, 10) < 18 && (
                      <div style={{
                        padding: '10px 14px',
                        background: '#fef2f2',
                        border: '1.5px solid #ef4444',
                        borderRadius: '6px',
                        color: '#b91c1c',
                        fontSize: '12px',
                        fontWeight: 600,
                        marginBottom: '15px'
                      }}>
                        🚨 {t.minorAlert}
                      </div>
                    )}

                    <div className="form-row two-cols">
                      <div className="form-group-field">
                        <label>{t.mpGender}</label>
                        <select
                          value={missingPersonInputs.gender}
                          onChange={(e) => setMissingPersonInputs({...missingPersonInputs, gender: e.target.value})}
                        >
                          <option value="">Select gender</option>
                          <option value="Male">Male / पुरुष</option>
                          <option value="Female">Female / महिला</option>
                          <option value="Transgender">Transgender / तृतीयपंथी</option>
                          <option value="Other">Other / इतर</option>
                        </select>
                      </div>
                      <div className="form-group-field">
                        <label>{t.mpHeight}</label>
                        <input 
                          type="number" 
                          placeholder="e.g. 165" 
                          value={missingPersonInputs.heightCm}
                          onChange={(e) => setMissingPersonInputs({...missingPersonInputs, heightCm: e.target.value})}
                        />
                      </div>
                    </div>

                    <div className="form-row two-cols">
                      <div className="form-group-field">
                        <label>{t.mpComplexion}</label>
                        <input 
                          type="text" 
                          placeholder="e.g. Fair, Wheatish, Dark" 
                          value={missingPersonInputs.complexion}
                          onChange={(e) => setMissingPersonInputs({...missingPersonInputs, complexion: e.target.value})}
                        />
                      </div>
                      <div className="form-group-field">
                        <label>{t.mpClothing}</label>
                        <input 
                          type="text" 
                          placeholder="e.g. Blue shirt, black jeans, white shoes" 
                          value={missingPersonInputs.clothingLastSeen}
                          onChange={(e) => setMissingPersonInputs({...missingPersonInputs, clothingLastSeen: e.target.value})}
                        />
                      </div>
                    </div>

                    {/* Last seen location and date/time */}
                    <div className="form-row two-cols">
                      <div className="form-group-field">
                        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                          <label>{t.mpLastSeenLoc} *</label>
                          <button 
                            type="button" 
                            onClick={triggerGPSWithPrompt}
                            style={{
                              background: 'none',
                              border: 'none',
                              color: 'var(--color-primary)',
                              fontSize: '11px',
                              fontWeight: 700,
                              cursor: 'pointer',
                              textDecoration: 'underline',
                              padding: 0
                            }}
                          >
                            📍 {t.gpsPromptBtn || 'Use GPS'}
                          </button>
                        </div>
                        <input 
                          type="text" 
                          required 
                          placeholder="Street, landmark, station, or area" 
                          value={missingPersonInputs.lastSeenLocation}
                          onChange={(e) => setMissingPersonInputs({...missingPersonInputs, lastSeenLocation: e.target.value})}
                        />
                      </div>
                      <div className="form-group-field">
                        <label>{t.mpLastSeenAt} *</label>
                        <input 
                          type="datetime-local" 
                          required 
                          value={missingPersonInputs.lastSeenDatetime}
                          onChange={(e) => setMissingPersonInputs({...missingPersonInputs, lastSeenDatetime: e.target.value})}
                        />
                      </div>
                    </div>

                    {/* Birthmarks / Distinguishing marks */}
                    <div className="form-group-field">
                      <label>{t.mpBirthmarks} *</label>
                      <textarea 
                        required 
                        rows="2"
                        placeholder="Birthmarks, moles, scars, tattoos, surgical marks, or distinctive physical traits..." 
                        value={missingPersonInputs.birthmarks}
                        onChange={(e) => setMissingPersonInputs({...missingPersonInputs, birthmarks: e.target.value})}
                      />
                    </div>

                    {/* Photo / Image upload */}
                    <div className="form-group-field">
                      <label>{t.mpImage} (Photo of Missing Person)</label>
                      <div className="photo-upload-box">
                        <input 
                          type="file" 
                          id="missing-photo-input" 
                          accept="image/*" 
                          style={{display: 'none'}} 
                          onChange={handleMissingImageChange} 
                        />
                        <label htmlFor="missing-photo-input" style={{cursor: 'pointer', display: 'block'}}>
                          {missingPersonInputs.imagePreview ? (
                            <div style={{display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '15px'}}>
                              <img 
                                src={missingPersonInputs.imagePreview} 
                                alt="Missing Person Preview" 
                                className="photo-preview-thumbnail" 
                              />
                              <div style={{textAlign: 'left'}}>
                                <div style={{fontWeight: 700, fontSize: '12px', color: 'var(--color-primary)'}}>
                                  ✓ {missingPersonInputs.imageFile ? missingPersonInputs.imageFile.name : 'Photo Selected'}
                                </div>
                                <div style={{fontSize: '11px', color: 'var(--text-muted)'}}>
                                  Click here to choose a different photo
                                </div>
                              </div>
                            </div>
                          ) : (
                            <div>
                              <div style={{fontSize: '28px', marginBottom: '4px'}}>📷</div>
                              <div style={{fontWeight: 700, fontSize: '12px', color: 'var(--color-primary)'}}>
                                Upload Recent Photograph of Missing Person
                              </div>
                              <div style={{fontSize: '11px', color: 'var(--text-muted)'}}>
                                JPG, PNG format. Helps police patrol and PCR vans identify the person.
                              </div>
                            </div>
                          )}
                        </label>
                      </div>
                    </div>

                    {/* Circumstances of Disappearance */}
                    <div className="form-group-field">
                      <label>{t.mpCircumstances}</label>
                      <textarea 
                        rows="3"
                        placeholder="Describe how and when they were discovered missing, mental condition, possible destination, who they were with..." 
                        value={missingPersonInputs.circumstances}
                        onChange={(e) => setMissingPersonInputs({...missingPersonInputs, circumstances: e.target.value})}
                      />
                    </div>

                    {/* Truth Warning Box */}
                    <div className="legal-warning-box">
                      {t.truthNotice}
                    </div>

                    {/* Section 12: Informant Confirmation */}
                    <div className="form-section-header">{t.secSignatures}</div>
                    <div className="form-group-field">
                      <label>{t.formSign}</label>
                      <input
                        type="text"
                        required
                        placeholder="Type your name"
                        value={formInputs.typedName}
                        onChange={(e) => setFormInputs({...formInputs, typedName: e.target.value})}
                      />
                    </div>

                    <div className="checkbox-declaration">
                      <input type="checkbox" required id="missing-sanction-check" />
                      <label htmlFor="missing-sanction-check">{t.formSignText}</label>
                    </div>

                    <div className="wizard-footer">
                      <button type="button" className="btn-secondary" onClick={closeComplaintModal}>Cancel</button>
                      <button type="submit" className="btn-primary" style={{background: '#dc2626', borderColor: '#b91c1c'}}>
                        🚨 {t.formVerifyBtn}
                      </button>
                    </div>
                  </form>
                </div>
              ) : (
                /* REGULAR COMPLAINT DRAFTING INTERFACE */
                <div className="form-paper">
                <div className="form-header-title">
                  <h2>🇮🇳 {t.formTitle}</h2>
                  <p>{t.formSub}</p>
                </div>

                <form onSubmit={handleDraftSubmit}>
                  
                  {/* Automatic Geographic Details Section */}
                  <div className="form-section-header">Location Details (from the map point you selected)</div>

                  <div className="form-group-field">
                    <label>Police station jurisdiction (map-based estimate; police to confirm)</label>
                    <input type="text" readOnly value={jurisdictionText()} style={{borderColor: 'var(--color-accent)', fontWeight: 6}} />
                  </div>

                  <div className="form-row two-cols">
                    <div className="form-group-field">
                      <label>{t.formMode}</label>
                      <select
                        value={formInputs.intendedMode}
                        onChange={(e) => setFormInputs({...formInputs, intendedMode: e.target.value})}
                      >
                        <option value="">Not decided</option>
                        <option value="Written">{t.formModeWritten}</option>
                        <option value="Oral">{t.formModeOral}</option>
                        <option value="Electronic / Online">{t.formModeElectronic}</option>
                      </select>
                    </div>
                    <div className="form-group-field">
                      <label>Selected map point (Lat, Lng)</label>
                      <input type="text" readOnly value={locationSelected ? `${coords.lat.toFixed(5)}, ${coords.lng.toFixed(5)}` : NOT_PROVIDED} />
                    </div>
                  </div>

                  {/* Section 1 */}
                  <div className="form-section-header">{t.secComplainant}</div>
                  
                  <div className="form-group-field">
                    <label>{t.formComplainantName}</label>
                    <input 
                      type="text" 
                      required 
                      placeholder="Complainant Name" 
                      value={formInputs.complainantName}
                      onChange={(e) => setFormInputs({...formInputs, complainantName: e.target.value})}
                    />
                  </div>
                  
                  <div className="form-group-field">
                    <label>{t.formComplainantAddress}</label>
                    <input 
                      type="text" 
                      required 
                      placeholder="Address" 
                      value={formInputs.complainantAddress}
                      onChange={(e) => setFormInputs({...formInputs, complainantAddress: e.target.value})}
                    />
                  </div>

                  <div className="form-row two-cols">
                    <div className="form-group-field">
                      <label>{t.formComplainantContact}</label>
                      <input 
                        type="tel" 
                        required 
                        placeholder="Contact number" 
                        value={formInputs.complainantContact}
                        onChange={(e) => setFormInputs({...formInputs, complainantContact: e.target.value})}
                      />
                    </div>
                    <div className="form-group-field">
                      <label>{t.formComplainantId}</label>
                      <input
                        type="text"
                        placeholder="e.g. Driving licence (optional)"
                        value={formInputs.complainantId}
                        onChange={(e) => setFormInputs({...formInputs, complainantId: e.target.value})}
                      />
                    </div>
                  </div>

                  {/* Section 2 & 3 */}
                  <div className="form-section-header">{t.secIncident} & {t.secPlace}</div>
                  
                  <div className="form-row two-cols">
                    <div className="form-group-field">
                      <label>{t.formOccurrenceTime}</label>
                      <input 
                        type="datetime-local" 
                        required 
                        value={formInputs.occurrenceTime}
                        onChange={(e) => setFormInputs({...formInputs, occurrenceTime: e.target.value})}
                      />
                    </div>
                    <div className="form-group-field">
                      <label>{t.formPlaceOccurrence}</label>
                      <input 
                        type="text" 
                        required 
                        value={formInputs.placeOfOccurrence}
                        onChange={(e) => setFormInputs({...formInputs, placeOfOccurrence: e.target.value})}
                      />
                    </div>
                  </div>

                  {/* Section 8: Facts of the case (with BNS AI Scanner) */}
                  <div className="form-section-header">{t.secSummary}</div>
                  
                  <div className="form-group-field">
                    <label>{t.formSummaryIncident}</label>
                    <textarea 
                      required 
                      placeholder="Narrate details of the incident. The AI scanner will evaluate the text against the BNS act..." 
                      value={formInputs.incidentSummary}
                      onChange={handleIncidentNarrativeChange}
                    />
                  </div>

                  {/* AI Scanning Node */}
                  {isAiScanning && (
                    <div className="glass-panel ai-analysis-card" style={{borderStyle: 'dashed'}}>
                      <div className="ai-header">
                        <span style={{animation: 'pulse 1.5s infinite'}}>🤖</span>
                        <span className="ai-badge">{t.aiScanning}</span>
                      </div>
                    </div>
                  )}

                  {aiLegalResult && !isAiScanning && (
                    <div className="glass-panel ai-analysis-card">
                      <div className="ai-header">
                        <span>💡</span>
                        <span className="ai-badge">
                          {aiLegalResult.unavailable ? 'Automatic analysis' : t.aiTitle}
                        </span>
                      </div>
                      {aiLegalResult.unavailable ? (
                        <div style={{fontSize: '12px', color: 'var(--text-muted)', padding: '8px 0'}}>{aiLegalResult.message}</div>
                      ) : (
                      <div className="ai-scan-lines">
                        <div style={{fontSize: '11px', color: 'var(--text-muted)', marginBottom: '6px'}}>
                          Machine-generated from your description{aiLegalResult.inferenceStatus ? ` (mode: ${aiLegalResult.inferenceStatus})` : ''}. These are suggestions, not facts or a legal determination.
                        </div>
                        {/* Synonym mappings */}
                        {aiLegalResult.translations && aiLegalResult.translations.length > 0 && (
                          <div style={{
                            margin: '12px 0',
                            padding: '10px',
                            background: 'rgba(59, 130, 246, 0.05)',
                            border: '1.5px solid rgba(59, 130, 246, 0.2)',
                            borderRadius: '6px',
                          }}>
                            <div style={{
                              fontSize: '11px',
                              fontWeight: 700,
                              color: 'var(--color-primary)',
                              textTransform: 'uppercase',
                              letterSpacing: '0.05em',
                              marginBottom: '6px'
                            }}>
                              🔄 Synonym Translation Agent Mappings
                            </div>
                            <div style={{display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '8px'}}>
                              {aiLegalResult.translations.map((t, idx) => (
                                <span key={idx} style={{
                                  fontSize: '10px',
                                  padding: '3px 8px',
                                  background: '#ffffff',
                                  border: '1px solid #cbd5e1',
                                  borderRadius: '12px',
                                  color: 'var(--text-main)',
                                  fontWeight: 500
                                }}>
                                  <span style={{color: 'var(--color-danger)'}}>{t.synonym}</span> ➔ <span style={{color: 'var(--color-success)', fontWeight: 700}}>{t.standard_term}</span>
                                </span>
                              ))}
                            </div>
                            <div style={{fontSize: '11px', color: 'var(--text-muted)', fontStyle: 'italic', lineHeight: 1.4}}>
                              <strong>Standardized Format:</strong> "{aiLegalResult.standardizedNarrative}"
                            </div>
                          </div>
                        )}

                        <div className="detail-row">
                          <span className="label">{t.aiConsensus}</span>
                          <span className="value" style={{color: 'var(--color-success)', fontWeight: 7}}>{aiLegalResult.bnsSection}</span>
                        </div>
                        <div className="detail-row">
                          <span className="label">{t.aiAction}</span>
                          <span className="value">{aiLegalResult.bnssAction}</span>
                        </div>
                        
                        {/* RAG: Top predictions with scores */}
                        {aiLegalResult.predictions && aiLegalResult.predictions.length > 0 ? (
                          <div style={{marginTop: '10px'}}>
                            <div style={{fontSize: '10px', fontWeight: 700, color: 'var(--color-primary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '6px', borderBottom: '1px solid var(--border-color)', paddingBottom: '4px'}}>
                              Top Matching BNS Sections (from {aiLegalResult.model})
                            </div>
                            {aiLegalResult.predictions.map((pred, pidx) => (
                              <div key={pidx} style={{padding: '10px 12px', marginBottom: '8px', background: pidx === 0 ? 'var(--color-primary-light)' : '#f8fafc', borderRadius: '6px', border: pidx === 0 ? '1.5px solid var(--color-accent)' : '1px solid #e2e8f0'}}>
                                <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px'}}>
                                  <div>
                                    <span style={{fontWeight: 700, color: pidx === 0 ? 'var(--color-accent)' : 'var(--text-main)', fontSize: '13px'}}>
                                      Section {pred.section}
                                    </span>
                                    <span style={{fontSize: '12px', color: 'var(--text-muted)', marginLeft: '6px'}}>
                                      {pred.title}
                                    </span>
                                    {pred.chapter && (
                                      <span style={{fontSize: '9px', color: 'var(--text-dim)', marginLeft: '6px'}}>({pred.chapter})</span>
                                    )}
                                  </div>
                                  <div style={{display: 'flex', flexDirection: 'column', alignItems: 'flex-end'}}>
                                    <div style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
                                      <div style={{width: '60px', height: '6px', background: '#e2e8f0', borderRadius: '3px', overflow: 'hidden'}}>
                                        <div style={{width: `${Math.min(pred.score * 100, 100)}%`, height: '100%', background: pidx === 0 ? 'var(--color-accent)' : 'var(--color-primary)', borderRadius: '3px', transition: 'width 0.5s ease'}} />
                                      </div>
                                      <span style={{fontSize: '10px', fontWeight: 700, color: pidx === 0 ? 'var(--color-accent)' : 'var(--text-muted)', minWidth: '35px', textAlign: 'right'}}>
                                        {(pred.score * 100).toFixed(1)}%
                                      </span>
                                    </div>
                                    <div style={{fontSize: '8.5px', color: 'var(--text-muted)', marginTop: '2px', fontWeight: 500}}>
                                      Retrieval score: {(pred.rag_score * 100).toFixed(0)}%
                                    </div>
                                  </div>
                                </div>
                                {/* Reasoning block */}
                                {pred.reasoning && (
                                  <div style={{fontSize: '11px', color: 'var(--text-muted)', lineHeight: 1.6, padding: '8px 10px', background: '#ffffff', border: '1px solid #e2e8f0', borderLeft: `3px solid ${pidx === 0 ? 'var(--color-accent)' : 'var(--color-primary)'}`, borderRadius: '4px', marginTop: '4px'}}>
                                    <span style={{fontWeight: 700, fontSize: '9px', color: 'var(--color-primary)', textTransform: 'uppercase', letterSpacing: '0.05em'}}>REASONING: </span>
                                    {pred.reasoning}
                                  </div>
                                )}
                                {pred.punishment && (
                                  <div style={{fontSize: '10px', color: 'var(--color-danger)', fontWeight: 600, marginTop: '4px', padding: '4px 8px', background: '#fef2f2', borderRadius: '3px', border: '1px solid #fecaca'}}>
                                    ⚖️ {pred.punishment.length > 200 ? pred.punishment.slice(0, 200) + '...' : pred.punishment}
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        ) : null}
                        <button type="button" className="btn-secondary" style={{marginTop: '8px'}} onClick={applySuggestionsToDraft}>
                          Use suggestions in draft (marked as machine-suggested)
                        </button>
                      </div>
                      )}
                    </div>
                  )}

                  {/* Section 4 & 5 */}
                  <div className="form-section-header">{t.secNature} & {t.secLegal}</div>
                  
                  <div className="form-row two-cols">
                    <div className="form-group-field">
                      <label>{t.formNatureOffence}</label>
                      <select
                        value={formInputs.natureOfOffence}
                        onChange={(e) => setFormInputs({...formInputs, natureOfOffence: e.target.value})}
                      >
                        <option value="">Not specified</option>
                        <option value="Theft">Theft</option>
                        <option value="Assault">Assault</option>
                        <option value="Fraud">Fraud</option>
                        <option value="Accident">Accident</option>
                        <option value="Cyber Crime">Cyber Crime</option>
                        <option value="Other">Other</option>
                      </select>
                    </div>
                    <div className="form-group-field">
                      <label>Possibly relevant BNS sections (optional)</label>
                      <input
                        type="text"
                        placeholder="Optional – not a legal determination"
                        value={formInputs.legalSections}
                        onChange={(e) => setFormInputs({...formInputs, legalSections: e.target.value})}
                      />
                    </div>
                  </div>

                  {/* Section 6 & 7 */}
                  <div className="form-section-header">{t.formDetailsSuspect} & {t.formVictimsDetails}</div>

                  <div className="form-row two-cols">
                    <div className="form-group-field">
                      <label>{t.formSuspectName}</label>
                      <input
                        type="text"
                        placeholder="If known"
                        value={formInputs.suspectName}
                        onChange={(e) => setFormInputs({...formInputs, suspectName: e.target.value})}
                      />
                    </div>
                    <div className="form-group-field">
                      <label>{t.formVictimName}</label>
                      <input 
                        type="text" 
                        placeholder="Victim Name (if any)" 
                        value={formInputs.victimName}
                        onChange={(e) => setFormInputs({...formInputs, victimName: e.target.value})}
                      />
                    </div>
                  </div>

                  <div className="form-group-field">
                    <label>{t.formSuspectDesc}</label>
                    <input 
                      type="text" 
                      placeholder="Suspect identity physical traits..." 
                      value={formInputs.suspectDescription}
                      onChange={(e) => setFormInputs({...formInputs, suspectDescription: e.target.value})}
                    />
                  </div>

                  {/* Section 9: Property */}
                  <div className="form-section-header">{t.formPropertyInvolved}</div>
                  
                  <div className="form-row two-cols">
                    <div className="form-group-field">
                      <label>{t.formPropertyDesc}</label>
                      <input 
                        type="text" 
                        placeholder="Property item description" 
                        value={formInputs.propertyDescription}
                        onChange={(e) => setFormInputs({...formInputs, propertyDescription: e.target.value})}
                      />
                    </div>
                    <div className="form-group-field">
                      <label>{t.formPropertyValue}</label>
                      <input 
                        type="number" 
                        placeholder="Estimated Value in ₹" 
                        value={formInputs.propertyValue}
                        onChange={(e) => setFormInputs({...formInputs, propertyValue: e.target.value})}
                      />
                    </div>
                  </div>

                  {/* Section 10: Witnesses */}
                  <div className="form-section-header">{t.formWitnesses}</div>
                  {formInputs.witnesses && formInputs.witnesses.length > 0 ? (
                    formInputs.witnesses.map((witness, index) => (
                      <div key={index} className="witness-row-grid">
                        <div className="form-group-field" style={{ marginBottom: 0 }}>
                          <label>Witness Name</label>
                          <input 
                            type="text" 
                            placeholder="Name" 
                            value={witness.name} 
                            onChange={(e) => handleWitnessChange(index, 'name', e.target.value)}
                          />
                        </div>
                        <div className="form-group-field" style={{ marginBottom: 0 }}>
                          <label>Phone No.</label>
                          <input 
                            type="tel" 
                            placeholder="Phone No." 
                            value={witness.phone} 
                            onChange={(e) => handleWitnessChange(index, 'phone', e.target.value)}
                          />
                        </div>
                        <div className="form-group-field" style={{ marginBottom: 0 }}>
                          <label>Address</label>
                          <input 
                            type="text" 
                            placeholder="Address" 
                            value={witness.address} 
                            onChange={(e) => handleWitnessChange(index, 'address', e.target.value)}
                          />
                        </div>
                        <button 
                          type="button" 
                          className="btn-remove-witness" 
                          onClick={() => handleRemoveWitness(index)}
                          title="Remove Witness"
                        >
                          ✕
                        </button>
                      </div>
                    ))
                  ) : (
                    <div style={{ fontSize: '12px', color: 'var(--text-dim)', marginBottom: '10px' }}>
                      No witnesses added. Click the button below to add witnesses.
                    </div>
                  )}
                  <button 
                    type="button" 
                    className="btn-add-witness" 
                    onClick={handleAddWitness}
                  >
                    + Add Witness
                  </button>

                  {/* Supporting material (optional). Nothing is uploaded or verified. */}
                  <div className="form-section-header">Supporting Material (optional)</div>
                  <div style={{fontSize: '11px', color: 'var(--text-muted)', marginBottom: '8px'}}>{t.idNotice}</div>

                  <div className="form-group-field">
                    <label>{t.fileUploadMedicalTitle}</label>
                    <div className="file-upload-drag-area">
                      <input
                        type="file"
                        id="medical-proof-upload"
                        style={{display: 'none'}}
                        onChange={handleMedicalFileChange}
                      />
                      <label htmlFor="medical-proof-upload" style={{cursor: 'pointer'}}>
                        <div className="upload-icon">📎</div>
                        <div style={{fontWeight: 7, fontSize: '11px'}}>{t.fileUploadDrag}</div>
                      </label>
                    </div>
                    {uploadedMedicalFile && (
                      <div style={{marginTop: '6px', fontSize: '11px', color: 'var(--text-muted)', fontWeight: 6}}>
                        {attachmentLabel(uploadedMedicalFile)}
                      </div>
                    )}
                  </div>

                  <div className="legal-warning-box">
                    {t.truthNotice}
                  </div>

                  {/* Section 12: Complainant confirmation (typed name; not a digital signature) */}
                  <div className="form-section-header">{t.secSignatures}</div>

                  <div className="form-group-field">
                    <label>{t.formSign}</label>
                    <input
                      type="text"
                      required
                      placeholder="Type your name"
                      value={formInputs.typedName}
                      onChange={(e) => setFormInputs({...formInputs, typedName: e.target.value})}
                    />
                  </div>

                  <div className="checkbox-declaration">
                    <input type="checkbox" required id="sanction-check" />
                    <label htmlFor="sanction-check">{t.formSignText}</label>
                  </div>

                  <div className="wizard-footer">
                    <button type="button" className="btn-secondary" onClick={closeComplaintModal}>Cancel</button>
                    <button type="submit" className="btn-primary">
                      {t.formVerifyBtn}
                    </button>
                  </div>

                </form>
              </div>
              )
            ) : (
              /* COMPLAINT DRAFT VIEW: a draft only. Not submitted, not received, not registered. */
              <div className="form-paper" style={{padding: '30px'}}>

                {/* Draft Language Switcher Bar */}
                <div className="draft-lang-bar no-print">
                  <div style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
                    <span style={{fontSize: '12px', fontWeight: 700, color: 'var(--color-primary)'}}>🌐 {t.viewInLang}</span>
                  </div>
                  <div className="lang-toggle-group">
                    <button 
                      type="button" 
                      className={`lang-toggle-btn ${lang === 'en' ? 'active' : ''}`}
                      onClick={() => setLang('en')}
                    >
                      English
                    </button>
                    <button 
                      type="button" 
                      className={`lang-toggle-btn ${lang === 'hi' ? 'active' : ''}`}
                      onClick={() => setLang('hi')}
                    >
                      हिन्दी
                    </button>
                    <button 
                      type="button" 
                      className={`lang-toggle-btn ${lang === 'mr' ? 'active' : ''}`}
                      onClick={() => setLang('mr')}
                    >
                      मराठी
                    </button>
                  </div>
                </div>

                {isMissingPersonReport ? (
                  /* MISSING PERSON DRAFT SHEET */
                  <div id="printable-fir-sheet" className="printable-fir-page">
                    <div className="printable-fir-header">
                      <div style={{display: 'inline-block', padding: '2px 8px', background: '#fee2e2', border: '1px solid #ef4444', color: '#b91c1c', fontSize: '11px', fontWeight: 800, marginBottom: '4px'}}>
                        🚨 {lang === 'mr' ? 'तात्काळ पोलीस अहवाल' : lang === 'hi' ? 'तात्कालिक पुलिस रिपोर्ट' : 'IMMEDIATE POLICE REPORT'}
                      </div>
                      <h2 style={{fontFamily: 'var(--font-heading)', color: '#000000', fontSize: '18px', margin: '6px 0'}}>
                        {t.formMissingTitle}
                      </h2>
                      <div style={{fontSize: '11px', fontStyle: 'italic'}}>{DRAFT_NOTICE}</div>
                      <div style={{fontSize: '10.5px', color: '#991b1b', marginTop: '6px', fontWeight: 600, border: '1px dashed #ef4444', padding: '6px 8px'}}>
                        ⚖️ {t.secMissingDirective}
                      </div>
                    </div>

                    <div className="printable-fir-section">
                      <div className="printable-fir-section-title">{t.statusTitle}</div>
                      {statusLadder({ draft: { createdAt: draftCreatedAt } }).map(s => (
                        <div key={s.status}>
                          <b>{s.label}:</b> {s.recorded ? `${t.statusRecorded} (${draftCreatedAt})` : t.statusNotRecorded}
                        </div>
                      ))}
                    </div>

                    <div className="printable-fir-grid">
                      <div>
                        <b>Jurisdiction:</b> {jurisdictionText()}<br />
                        <b>Station Official Email:</b> {getStationEmail(jurisdiction.stationName || (assignedStation && assignedStation.name))}
                      </div>
                      <div style={{textAlign: 'right'}}>
                        <b>Report Type:</b> Missing Person Report (Immediate GD Entry)<br />
                        <b>Mode:</b> {formInputs.intendedMode || 'Written / Electronic Draft'}
                      </div>
                    </div>

                    <div className="printable-fir-section">
                      <div className="printable-fir-section-title">{t.secComplainant}</div>
                      <b>Name:</b> {formInputs.complainantName || NOT_PROVIDED}<br />
                      <b>Contact No:</b> {formInputs.complainantContact || NOT_PROVIDED}<br />
                      <b>Address:</b> {formInputs.complainantAddress || NOT_PROVIDED}<br />
                      <b>Relationship to Missing Person:</b> {missingPersonInputs.relationship || NOT_PROVIDED}
                    </div>

                    <div className="printable-fir-section">
                      <div className="printable-fir-section-title">{t.secMissingProfile}</div>
                      <div style={{display: 'flex', gap: '20px', alignItems: 'flex-start'}}>
                        {missingPersonInputs.imagePreview && (
                          <div style={{border: '1px solid #000', padding: '4px', textAlign: 'center'}}>
                            <img src={missingPersonInputs.imagePreview} alt="Missing Person" style={{width: '100px', height: '110px', objectFit: 'cover'}} />
                            <div style={{fontSize: '9px', fontWeight: 700, marginTop: '2px'}}>PHOTOGRAPH</div>
                          </div>
                        )}
                        <div style={{flex: 1, lineHeight: 1.6}}>
                          <b>Full Name:</b> {missingPersonInputs.fullName || NOT_PROVIDED}<br />
                          <b>Age:</b> {missingPersonInputs.age ? `${missingPersonInputs.age} years` : NOT_PROVIDED} {missingPersonInputs.age && parseInt(missingPersonInputs.age, 10) < 18 ? `(${t.minorAlert})` : ''}<br />
                          <b>Gender:</b> {missingPersonInputs.gender || NOT_PROVIDED}<br />
                          <b>Height & Complexion:</b> {missingPersonInputs.heightCm ? `${missingPersonInputs.heightCm} cm` : NOT_PROVIDED} / {missingPersonInputs.complexion || NOT_PROVIDED}<br />
                          <b>Clothing Last Seen:</b> {missingPersonInputs.clothingLastSeen || NOT_PROVIDED}<br />
                          <b>Birthmarks / Distinguishing Marks:</b> <span style={{fontWeight: 700}}>{missingPersonInputs.birthmarks || NOT_PROVIDED}</span>
                        </div>
                      </div>
                    </div>

                    <div className="printable-fir-section">
                      <div className="printable-fir-section-title">Last Seen Occurrence Details</div>
                      <b>Last Seen Location:</b> {missingPersonInputs.lastSeenLocation || NOT_PROVIDED}<br />
                      <b>Last Seen Date & Time:</b> {missingPersonInputs.lastSeenDatetime || NOT_PROVIDED}<br />
                      <b>Map Coordinates:</b> {locationSelected ? `Lat ${coords.lat.toFixed(5)}, Lng ${coords.lng.toFixed(5)}` : NOT_PROVIDED}
                    </div>

                    <div className="printable-fir-section">
                      <div className="printable-fir-section-title">{t.mpCircumstances}</div>
                      <div style={{whiteSpace: 'pre-wrap', lineHeight: 1.5}}>{missingPersonInputs.circumstances || NOT_PROVIDED}</div>
                    </div>

                    <div className="printable-fir-section">
                      <div className="printable-fir-section-title">{t.formPoliceUse}</div>
                      <b>Received by (Name, Rank, Station):</b> ______________________<br />
                      <b>General Diary (GD) Entry No:</b> ______________________<br />
                      <b>Date and Time Recorded:</b> ______________________<br />
                      <b>Immediate Broadcast / PCR Alert Reference:</b> ______________________
                    </div>

                    <div className="printable-fir-section">
                      <div className="printable-fir-section-title">{t.secSignatures}</div>
                      <b>Typed name (not a digital signature):</b> {formInputs.typedName || NOT_PROVIDED}<br />
                      <b>Photograph attached:</b> {missingPersonInputs.imageFile ? missingPersonInputs.imageFile.name : NOT_PROVIDED}
                    </div>
                  </div>
                ) : (
                  /* REGULAR COMPLAINT DRAFT SHEET */
                  <div id="printable-fir-sheet" className="printable-fir-page">
                    <div className="printable-fir-header">
                      <h2 style={{fontFamily: 'var(--font-heading)', color: '#000000', fontSize: '18px', margin: '6px 0'}}>COMPLAINT DRAFT (NOT AN FIR)</h2>
                      <div style={{fontSize: '11px', fontStyle: 'italic'}}>{DRAFT_NOTICE}</div>
                    </div>

                    <div className="printable-fir-section">
                      <div className="printable-fir-section-title">{t.statusTitle}</div>
                      {statusLadder({ draft: { createdAt: draftCreatedAt } }).map(s => (
                        <div key={s.status}>
                          <b>{s.label}:</b> {s.recorded ? `${t.statusRecorded} (${draftCreatedAt})` : t.statusNotRecorded}
                        </div>
                      ))}
                    </div>

                    <div className="printable-fir-grid">
                      <div>
                        <b>Jurisdiction:</b> {jurisdictionText()}<br />
                        <b>Station Official Email:</b> {getStationEmail(jurisdiction.stationName || (assignedStation && assignedStation.name))}
                      </div>
                      <div style={{textAlign: 'right'}}>
                        <b>Intended mode:</b> {formInputs.intendedMode || NOT_PROVIDED}
                      </div>
                    </div>

                    <div className="printable-fir-section">
                      <div className="printable-fir-section-title">{t.secComplainant}</div>
                      <b>Name:</b> {formInputs.complainantName || NOT_PROVIDED}<br />
                      <b>Address:</b> {formInputs.complainantAddress || NOT_PROVIDED}<br />
                      <b>Contact No:</b> {formInputs.complainantContact || NOT_PROVIDED}<br />
                      <b>ID document type:</b> {formInputs.complainantId || NOT_PROVIDED} (identity to be verified by police)
                    </div>

                    <div className="printable-fir-section">
                      <div className="printable-fir-section-title">{t.secIncident}</div>
                      {formInputs.occurrenceTime || NOT_PROVIDED}
                    </div>

                    <div className="printable-fir-section">
                      <div className="printable-fir-section-title">{t.secPlace}</div>
                      <b>Address:</b> {formInputs.placeOfOccurrence || NOT_PROVIDED}<br />
                      <b>Selected map point:</b> {locationSelected ? `Lat ${coords.lat.toFixed(5)}, Lng ${coords.lng.toFixed(5)}` : NOT_PROVIDED}
                    </div>

                    <div className="printable-fir-section">
                      <div className="printable-fir-section-title">{t.secNature}</div>
                      {formInputs.natureOfOffence || NOT_PROVIDED}
                    </div>

                    <div className="printable-fir-section">
                      <div className="printable-fir-section-title">{t.secLegal}</div>
                      {formInputs.legalSections || NOT_PROVIDED}
                    </div>

                    <div className="printable-fir-section">
                      <div className="printable-fir-section-title">{t.formDetailsSuspect}</div>
                      <b>Name:</b> {formInputs.suspectName || NOT_PROVIDED}<br />
                      <b>Address:</b> {formInputs.suspectAddress || NOT_PROVIDED}<br />
                      <b>Physical Description:</b> {formInputs.suspectDescription || NOT_PROVIDED}
                    </div>

                    <div className="printable-fir-section">
                      <div className="printable-fir-section-title">{t.formVictimsDetails}</div>
                      <b>Name:</b> {formInputs.victimName || NOT_PROVIDED}<br />
                      <b>Contact No:</b> {formInputs.victimContact || NOT_PROVIDED}<br />
                      <b>Address:</b> {formInputs.victimAddress || NOT_PROVIDED}
                    </div>

                    <div className="printable-fir-section">
                      <div className="printable-fir-section-title">{t.secSummary}</div>
                      <div style={{whiteSpace: 'pre-wrap', lineHeight: 1.5}}>{formInputs.incidentSummary || NOT_PROVIDED}</div>
                    </div>

                    <div className="printable-fir-section">
                      <div className="printable-fir-section-title">{t.formPropertyInvolved}</div>
                      <b>Description:</b> {formInputs.propertyDescription || NOT_PROVIDED}<br />
                      <b>Estimated Value:</b> {formInputs.propertyValue ? `₹ ${formInputs.propertyValue}` : NOT_PROVIDED}
                    </div>

                    <div className="printable-fir-section">
                      <div className="printable-fir-section-title">{t.formWitnesses}</div>
                      {formInputs.witnesses.some(w => w.name || w.phone || w.address) ? (
                        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px', marginTop: '6px' }}>
                          <thead>
                            <tr style={{ borderBottom: '1px solid #000' }}>
                              <th style={{ textAlign: 'left', padding: '4px 0', width: '30%' }}>Name</th>
                              <th style={{ textAlign: 'left', padding: '4px 0', width: '25%' }}>Phone No.</th>
                              <th style={{ textAlign: 'left', padding: '4px 0', width: '45%' }}>Address</th>
                            </tr>
                          </thead>
                          <tbody>
                            {formInputs.witnesses.filter(w => w.name || w.phone || w.address).map((w, idx) => (
                              <tr key={idx} style={{ borderBottom: '1px solid #eee' }}>
                                <td style={{ padding: '6px 0' }}>{w.name || NOT_PROVIDED}</td>
                                <td style={{ padding: '6px 0' }}>{w.phone || NOT_PROVIDED}</td>
                                <td style={{ padding: '6px 0' }}>{w.address || NOT_PROVIDED}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      ) : (
                        <span style={{ fontSize: '13px', fontStyle: 'italic' }}>{NOT_PROVIDED}</span>
                      )}
                    </div>

                    <div className="printable-fir-section">
                      <div className="printable-fir-section-title">{t.formPoliceUse}</div>
                      <b>Received by (name, rank):</b> ______________________<br />
                      <b>Date and time received:</b> ______________________<br />
                      <b>Action / reference:</b> ______________________
                    </div>

                    <div className="printable-fir-section">
                      <div className="printable-fir-section-title">{t.secSignatures}</div>
                      <b>Typed name (not a digital signature):</b> {formInputs.typedName || NOT_PROVIDED}<br />
                      <b>Supporting material:</b> {uploadedMedicalFile ? attachmentLabel(uploadedMedicalFile) : NOT_PROVIDED}
                    </div>
                  </div>
                )}

                {/* Structured record (machine-assisted). Shown on screen only; not part of the printed draft. */}
                <div className="no-print glass-panel" style={{marginTop: '24px'}}>
                  <div className="panel-title">Structured record (machine-assisted, nothing verified)</div>
                  {structured.state === 'loading' && <div style={{fontSize: '12px'}}>Preparing the structured record...</div>}
                  {structured.state === 'unavailable' && (
                    <div style={{fontSize: '12px', color: 'var(--text-muted)'}}>The structured record could not be prepared. Review status unavailable; human review required. The draft above is unaffected.</div>
                  )}
                  {structured.state === 'ok' && structured.summary && (
                    <div style={{fontSize: '12px', lineHeight: 1.6}}>
                      <div style={{color: 'var(--text-muted)'}}>{structured.summary.notice}</div>
                      <ReviewStatus summary={structured.summary} />
                      {structured.summary.reasons.length > 0 && (
                        <ul>{structured.summary.reasons.map((r, i) => <li key={i}>{r}</li>)}</ul>
                      )}
                      <div><b>Jurisdiction:</b> {structured.summary.jurisdiction}</div>
                      <div><b>Missing information:</b> {structured.summary.missing.length ? structured.summary.missing.join('; ') : 'None identified'}</div>
                      {structured.summary.questions.length > 0 && (
                        <div><b>Questions for the complainant:</b><ul>{structured.summary.questions.map((q, i) => <li key={i}>{q}</li>)}</ul></div>
                      )}
                      {structured.summary.contradictions.length > 0 && (
                        <div><b>Possible inconsistencies to clarify:</b><ul>{structured.summary.contradictions.map((c, i) => <li key={i}>{c}</li>)}</ul></div>
                      )}
                      <div><b>Supporting material:</b> {structured.summary.evidence.length ? structured.summary.evidence.join('; ') : NOT_PROVIDED}</div>
                      {structured.summary.draftText && (
                        <details style={{marginTop: '8px'}}>
                          <summary><b>Structured complaint draft and verification checklist</b></summary>
                          <pre className="structured-draft" style={{whiteSpace: 'pre-wrap', fontSize: '11px'}}>{structured.summary.draftText}</pre>
                        </details>
                      )}
                    </div>
                  )}
                </div>

                {/* Print and copy actions. Nothing is sent anywhere. */}
                <div className="no-print" style={{marginTop: '30px', borderTop: '1px solid #cbd5e1', paddingTop: '20px'}}>
                  <div style={{fontSize: '12px', color: 'var(--text-muted)', marginBottom: '12px'}}>{t.deliveryNotice}</div>
                  <div className="btn-group" style={{display: 'flex', flexWrap: 'wrap', gap: '8px'}}>
                    <button 
                      type="button"
                      className="btn-primary" 
                      onClick={handleDownloadPDF}
                      disabled={pdfDownloading}
                      style={{background: 'var(--color-accent)', borderColor: 'var(--color-accent)'}}
                    >
                      {pdfDownloading ? 'Generating PDF...' : `📥 ${t.downloadPdfBtn || 'Download Official PDF'}`}
                    </button>
                    <button 
                      type="button"
                      className="btn-secondary" 
                      onClick={handleDraftEmail}
                      style={{borderColor: 'var(--color-primary)', color: 'var(--color-primary)', fontWeight: 600}}
                    >
                      📧 {t.draftEmailBtn || 'Draft Police Email'}
                    </button>
                    <button 
                      type="button"
                      className="btn-secondary" 
                      onClick={handlePrint}
                    >
                      🖨️ {lang === 'en' ? 'Print complaint draft' : lang === 'hi' ? 'शिकायत प्रारूप प्रिंट करें' : 'तक्रारीचा मसुदा प्रिंट करा'}
                    </button>
                    <button 
                      type="button"
                      className="btn-secondary" 
                      onClick={copyDraftText}
                    >
                      {isDraftCopied ? t.draftCopied : t.copyDraftBtn}
                    </button>
                    <button 
                      type="button"
                      className="btn-secondary" 
                      onClick={closeComplaintModal}
                    >
                      Close and return to map
                    </button>
                  </div>
                </div>

              </div>
            )}

          </div>
        )}

      </div>

      {/* GPS Address Prompt Modal */}
      {gpsPrompt.open && (
        <div className="prompt-modal-overlay">
          <div className="prompt-modal-card">
            <div className="prompt-modal-header">
              <span style={{fontSize: '24px'}}>📍</span>
              <div>
                <div className="prompt-modal-title">GPS Address Detected</div>
                <div style={{fontSize: '11px', color: 'var(--text-muted)'}}>Confirm detected location for your complaint draft</div>
              </div>
            </div>

            <div className="prompt-address-box">
              <div style={{fontSize: '11px', fontWeight: 700, color: 'var(--color-primary)', marginBottom: '4px'}}>
                DETECTED ADDRESS & LANDMARK
              </div>
              <div>{gpsPrompt.detectedAddress}</div>
              <div style={{fontSize: '11px', color: 'var(--text-muted)', marginTop: '6px', fontFamily: 'monospace'}}>
                Coordinates: {gpsPrompt.lat?.toFixed(5)}, {gpsPrompt.lng?.toFixed(5)}
              </div>
            </div>

            <div style={{fontSize: '12px', color: 'var(--text-main)', marginBottom: '16px'}}>
              <b>Estimated Police Station Jurisdiction:</b> {jurisdictionText()}<br />
              <span style={{fontSize: '11px', color: 'var(--text-muted)'}}>Station Official Email: {getStationEmail(jurisdiction.stationName || (assignedStation && assignedStation.name))}</span>
            </div>

            <div style={{display: 'flex', gap: '10px', justifyContent: 'flex-end'}}>
              <button 
                type="button" 
                className="btn-secondary"
                onClick={() => setGpsPrompt({ open: false, detectedAddress: '', lat: null, lng: null, stationName: '' })}
              >
                Cancel / Edit Manually
              </button>
              <button 
                type="button" 
                className="btn-primary"
                onClick={acceptGpsAddress}
              >
                ✓ Accept & Use This Address
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Official Police Email Draft Modal */}
      {emailDraftModal.open && (
        <div className="prompt-modal-overlay">
          <div className="prompt-modal-card" style={{maxWidth: '650px'}}>
            <div className="prompt-modal-header">
              <span style={{fontSize: '24px'}}>📧</span>
              <div>
                <div className="prompt-modal-title">Official Police Station Email Draft</div>
                <div style={{fontSize: '11px', color: 'var(--text-muted)'}}>Pre-formatted draft for jurisdictional police station communication</div>
              </div>
            </div>

            {emailDraftModal.loading ? (
              <div style={{padding: '24px', textAlign: 'center', fontSize: '13px', color: 'var(--text-muted)'}}>
                Preparing official email draft for {jurisdiction.stationName || 'jurisdictional station'}...
              </div>
            ) : emailDraftModal.data && !emailDraftModal.data.error ? (
              <div>
                <div className="detail-row" style={{marginBottom: '8px'}}>
                  <span className="label">Jurisdictional Police Station</span>
                  <span className="value" style={{fontWeight: 700}}>{emailDraftModal.data.station_name || jurisdiction.stationName}</span>
                </div>
                <div className="detail-row" style={{marginBottom: '8px'}}>
                  <span className="label">Station Official Email</span>
                  <span className="value" style={{fontFamily: 'monospace', color: 'var(--color-primary)', fontWeight: 700}}>
                    {emailDraftModal.data.station_email || getStationEmail(jurisdiction.stationName)}
                  </span>
                </div>
                <div className="detail-row" style={{marginBottom: '10px'}}>
                  <span className="label">Subject</span>
                  <span className="value" style={{fontWeight: 600, fontSize: '12px'}}>{emailDraftModal.data.subject}</span>
                </div>

                <div style={{fontSize: '11px', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '4px'}}>
                  EMAIL BODY PREVIEW
                </div>
                <pre style={{
                  background: '#f8fafc',
                  border: '1px solid #cbd5e1',
                  borderRadius: '6px',
                  padding: '12px',
                  fontSize: '11.5px',
                  lineHeight: 1.5,
                  maxHeight: '260px',
                  overflowY: 'auto',
                  whiteSpace: 'pre-wrap',
                  fontFamily: 'inherit'
                }}>
                  {emailDraftModal.data.body}
                </pre>

                <div style={{display: 'flex', gap: '8px', justifyContent: 'flex-end', marginTop: '16px'}}>
                  <button 
                    type="button" 
                    className="btn-secondary"
                    onClick={() => {
                      navigator.clipboard.writeText(emailDraftModal.data.station_email || getStationEmail(jurisdiction.stationName));
                      alert('Station official email copied to clipboard!');
                    }}
                  >
                    📋 Copy Email Address
                  </button>
                  <button 
                    type="button" 
                    className="btn-primary"
                    onClick={() => {
                      navigator.clipboard.writeText(`Subject: ${emailDraftModal.data.subject}\n\nTo: ${emailDraftModal.data.station_email}\n\n${emailDraftModal.data.body}`);
                      alert('Email text copied to clipboard!');
                    }}
                  >
                    📋 Copy Full Email Draft
                  </button>
                  <button 
                    type="button" 
                    className="btn-secondary"
                    onClick={() => setEmailDraftModal({ open: false, data: null, loading: false })}
                  >
                    Close
                  </button>
                </div>
              </div>
            ) : (
              <div>
                <div style={{color: 'var(--color-danger)', fontSize: '13px', padding: '12px 0'}}>
                  Email draft service could not be contacted. You can use the printed draft or PDF.
                </div>
                <div style={{display: 'flex', justifyContent: 'flex-end'}}>
                  <button 
                    type="button" 
                    className="btn-secondary"
                    onClick={() => setEmailDraftModal({ open: false, data: null, loading: false })}
                  >
                    Close
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
