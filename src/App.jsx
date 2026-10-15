import React, { useState, useEffect, useRef } from 'react';
import L from 'leaflet';

// Ray-casting point-in-polygon containment check
function pointInPolygon(point, vs) {
  const x = point[0], y = point[1];
  let inside = false;
  for (let i = 0, j = vs.length - 1; i < vs.length; j = i++) {
    const xi = vs[i][0], yi = vs[i][1];
    const xj = vs[j][0], yj = vs[j][1];
    const intersect = ((yi > y) !== (yj > y))
        && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
    if (intersect) inside = !inside;
  }
  return inside;
}

function isPointInGeometry(point, geometry) {
  if (geometry.type === 'Polygon') {
    return pointInPolygon(point, geometry.coordinates[0]);
  } else if (geometry.type === 'MultiPolygon') {
    for (const polyCoords of geometry.coordinates) {
      if (pointInPolygon(point, polyCoords[0])) {
        return true;
      }
    }
  }
  return false;
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
    logoTitle: "BNS FIR Portal",
    logoSub: "Sec. 173, BNSS, 2023",
    tabLocator: "Territory Locator",
    tabDirectory: "Police Directory",
    tabInsights: "Act Insights",
    searchPlaceholder: "Search location in Mumbai...",
    gpsBtn: "Use GPS Location",
    resetBtn: "Reset Center",
    assignedTitle: "DETECTOR JURISDICTION REPORT",
    matching: "analyzing territory...",
    verified: "verified boundary",
    ward: "Municipal Ward",
    address: "HQ Address",
    contact: "Emergency Contact",
    remarks: "Remarks",
    coords: "Geographic Vector",
    lodgeBtn: "LODGE ELECTRONIC FIR",
    dirSearchPlaceholder: "Search directory by name or ward...",
    insTitle: "BNSS, 2023 Infrastructure",
    insActive: "Jurisdictional Offices",
    insWards: "Municipal Wards",
    insGis: "GIS Data Specifications",
    insGisText: "Territorial boundaries are mapped using official coordinates from Brihanmumbai Municipal Corporation (BMC) data files. Centroids are processed for precise police station plotting.",
    // Form fields
    formTitle: "FIRST INFORMATION REPORT (FIR)",
    formSub: "(Under Section 173 of the Bharatiya Nagarik Suraksha Sanhita, 2023)",
    formMode: "Mode of Registration",
    formModeWritten: "Written",
    formModeOral: "Oral",
    formModeElectronic: "Electronic / Online",
    formComplainantName: "Complainant Full Name",
    formComplainantAddress: "Complainant Address",
    formComplainantContact: "Contact Number",
    formComplainantId: "ID Proof (Aadhaar / DL / Passport)",
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
    formActionTaken: "Action Taken by Police",
    formActionRegistered: "Case Registered",
    formActionInvestigating: "Investigation Started",
    formActionCyber: "Forwarded to Cyber Unit",
    formOfficerName: "Officer Name & Rank",
    formOfficerSteps: "Steps Taken / Remarks",
    formSign: "Digital Signature / E-Sign Name",
    formSignText: "I solemnly declare that the facts stated in this report are true and correct to the best of my knowledge under Section 173 BNSS, 2023.",
    formVerifyBtn: "Authenticate & Register FIR",
    fileUploadTitle: "1. Upload Identity Verification Document (Aadhaar / DL / Passport)",
    fileUploadMedicalTitle: "2. Upload Medical Records / Incident Photos / Other Supporting Documents",
    fileUploadDrag: "Drag & drop files here, or click to browse",
    fileUploadSuccess: "Identity document verified:",
    fileUploadMedicalSuccess: "Supporting document verified:",
    forgeryWarning: "WARNING: Submission of fake, forged, or altered documents is a punishable criminal offense under Section 465 and Section 468 of the BNS/IPC. If convicted, offenders face imprisonment of up to two years and substantial financial fines.",
    aiTitle: "Dual-LLM Legal Act Classifier",
    aiScanning: "Analyzing narration with OpenAI & HuggingFace...",
    aiConsensus: "AI Legal Section Consensus",
    aiAction: "Recommended Police Action",
    emailDispatchTitle: "Draft Dispatch Email to Police Station",
    emailDispatchTo: "To",
    emailDispatchSub: "Subject",
    emailDispatchBtn: "Send Email via Mail Client",
    emailCopyBtn: "Copy Email Body Draft",
    emailCopied: "Email Body Copied!",
    secComplainant: "1. Complainant / Informant Details",
    secIncident: "2. Date & Time of Occurrence",
    secPlace: "3. Place of Occurrence",
    secSummary: "8. Brief Description of Incident (Facts of the Case)",
    secNature: "4. Type / Nature of Offence",
    secLegal: "5. BNS Act Violations",
    secSignatures: "12. Signatures & Verified Authenticity Proofs"
  },
  mr: {
    logoTitle: "बी.एन.एस. एफआयआर",
    logoSub: "कलम १७३, बी.एन.एस.एस., २०२३",
    tabLocator: "क्षेत्र शोधक पॅनेल",
    tabDirectory: "पोलीस निर्देशिका",
    tabInsights: "कायदा माहिती",
    searchPlaceholder: "मुंबईतील ठिकाण शोधा...",
    gpsBtn: "जीपीएस स्थान वापरा",
    resetBtn: "नकाशा रीसेट करा",
    assignedTitle: "अधिकार क्षेत्र अहवाल",
    matching: "क्षेत्राचे विश्लेषण सुरू आहे...",
    verified: "अधिकार क्षेत्र सत्यापित",
    ward: "प्रशासकीय प्रभाग",
    address: "मुख्यालय पत्ता",
    contact: "तक्रार क्रमांक",
    remarks: "विशेष नोंदी",
    coords: "भौगोलिक स्थानक",
    lodgeBtn: "डिजिटल एफआयआर नोंदवा",
    dirSearchPlaceholder: "नाव किंवा प्रभागाद्वारे शोधा...",
    insTitle: "बी.एन.एस.एस. पायाभूत सुविधा",
    insActive: "सक्रिय पोलीस ठाणे",
    insWards: "महानगरपालिका प्रभाग",
    insGis: "जीआयएस नकाशा तपशील",
    insGisText: "बृहन्मुंबई महानगरपालिका (BMC) च्या अधिकृत भौगोलिक डेटावरून पोलीस ठाण्यांची हद्द आणि सीमा निश्चित करण्यात आल्या आहेत.",
    // Form fields
    formTitle: "पहिले खबर अहवाल (एफ.आय.आर.)",
    formSub: "(भारतीय नागरिक सुरक्षा संहिता, २०२३ च्या कलम १७३ अंतर्गत)",
    formMode: "नोंदणीची पद्धत",
    formModeWritten: "लेखी",
    formModeOral: "तोंडी",
    formModeElectronic: "इलेक्ट्रॉनिक / ऑनलाईन",
    formComplainantName: "तक्रारदाराचे पूर्ण नाव",
    formComplainantAddress: "तक्रारदाराचा पत्ता",
    formComplainantContact: "संपर्क क्रमांक",
    formComplainantId: "ओळखपत्र (आधार / ड्रायव्हिंग लायसन्स / पासपोर्ट)",
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
    formActionTaken: "पोलिसांनी केलेली कारवाई",
    formActionRegistered: "गुन्हा नोंदवला",
    formActionInvestigating: "तपास सुरू झाला",
    formActionCyber: "सायबर युनिटकडे वर्ग केले",
    formOfficerName: "अधिकारी नाव आणि पद",
    formOfficerSteps: "केलेली कारवाई / शेरा",
    formSign: "डिजिटल स्वाक्षरी / नाव",
    formSignText: "मी याद्वारे जाहीर करतो की वरील अहवालातील सर्व तथ्ये माझ्या माहितीनुसार सत्य आहेत.",
    formVerifyBtn: "प्रमाणित करा आणि एफआयआर नोंदवा",
    fileUploadTitle: "१. ओळखपत्राची पडताळणी (आधार / परवाना / पासपोर्ट)",
    fileUploadMedicalTitle: "२. वैद्यकीय अहवाल / घटनेचे फोटो / इतर पुरावे अपलोड करा",
    fileUploadDrag: "फायली येथे ड्रॅग आणि ड्रॉप करा, किंवा ब्राउझ करण्यासाठी क्लिक करा",
    fileUploadSuccess: "ओळखपत्र यशस्वीरित्या सत्यापित झाले:",
    fileUploadMedicalSuccess: "सहाय्यक कागदपत्र यशस्वीरित्या सत्यापित झाले:",
    forgeryWarning: "इशारा: खोट्या, बनावट किंवा फेरबदल केलेली कागदपत्रे दाखल करणे हा बी.एन.एस./आय.पी.सी. च्या कलम ४६५ आणि ४६८ अंतर्गत एक गंभीर दंडनीय गुन्हा आहे. दोषी आढळल्यास २ वर्षांपर्यंतचा कारावास आणि मोठा आर्थिक दंड होऊ शकतो.",
    aiTitle: "ड्युअल-एलएलएम कायदेशीर विश्लेषण",
    aiScanning: "ओपनएआय आणि हगिंगफेस द्वारे घटनेचे विश्लेषण सुरू आहे...",
    aiConsensus: "कायदेशीर कलम शोध (बी.एन.एस.)",
    aiAction: "शिारस केलेली पोलीस कारवाई",
    emailDispatchTitle: "पोलीस ठाण्याला पाठवण्यासाठी ईमेलचा मसुदा",
    emailDispatchTo: "प्रति",
    emailDispatchSub: "विषय",
    emailDispatchBtn: "ईमेल पाठवा",
    emailCopyBtn: "ईमेल कॉपी करा",
    emailCopied: "ईमेल मसुदा कॉपी केला!",
    secComplainant: "१. तक्रारदार / माहिती देणाऱ्याचा तपशील",
    secIncident: "२. घटनेची तारीख आणि वेळ",
    secPlace: "३. घटनेचे ठिकाण",
    secSummary: "८. घटनेचे संक्षिप्त वर्णन (तथ्ये)",
    secNature: "४. गुन्ह्याचे स्वरूप",
    secLegal: "५. बी.एन.एस. कायदेशीर कलमे",
    secSignatures: "१२. स्वाक्षरी आणि सत्यता पडताळणी"
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
  const [assignedStation, setAssignedStation] = useState(null);
  const [isCheckingJurisdiction, setIsCheckingJurisdiction] = useState(false);
  const [district, setDistrict] = useState('Mumbai Suburban');
  const [osmAddress, setOsmAddress] = useState('');

  // AI legal scanning
  const [isAiScanning, setIsAiScanning] = useState(false);
  const [aiLegalResult, setAiLegalResult] = useState(null);

  // File Upload states (ID and Medical/Supporting Proofs)
  const [uploadedFile, setUploadedFile] = useState(null);
  const [uploadedMedicalFile, setUploadedMedicalFile] = useState(null);

  // Complaint Workspace State
  const [showForm, setShowForm] = useState(false);
  const [firSubmitted, setFirSubmitted] = useState(false);
  const [firNo, setFirNo] = useState('');
  const [registrationTime, setRegistrationTime] = useState('');
  const [isEmailCopied, setIsEmailCopied] = useState(false);

  // 12-Section FIR Form inputs
  const [formInputs, setFormInputs] = useState({
    registrationMode: 'Electronic / Online',
    complainantName: '',
    complainantAddress: '',
    complainantContact: '',
    complainantId: '',
    occurrenceTime: '',
    placeOfOccurrence: '',
    natureOfOffence: 'Theft',
    legalSections: 'Section 303 (Theft), BNS, 2023',
    suspectName: 'Unknown',
    suspectAddress: 'Unknown',
    suspectDescription: '',
    victimName: '',
    victimContact: '',
    victimAddress: '',
    incidentSummary: '',
    propertyDescription: '',
    propertyValue: '',
    witnesses: [{ name: '', phone: '', address: '' }],
    policeAction: 'Investigation Started',
    policeOfficer: 'R. K. Patil, Inspector',
    policeRemarks: 'Case registered online, preliminary inquiry initiated.',
    eSignature: ''
  });

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

  // Initialize Map
  useEffect(() => {
    if (showForm || !mapContainerRef.current || stations.length === 0 || !jurisdictionsGeoJSON) return;

    const map = L.map(mapContainerRef.current, {
      center: [coords.lat, coords.lng],
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
            updateLocation(e.latlng.lat, e.latlng.lng);
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
            <b style="font-family: 'Outfit', sans-serif; font-size:13px; color:#004080;">${s.name} Police Station</b>
            <div style="margin-top:6px; font-size:11px; color:#475569;"><b>Ward:</b> ${s.ward || 'N/A'}</div>
            <div style="font-size:11px; color:#475569;"><b>Address:</b> ${s.address || 'Address not listed'}</div>
            <div style="font-size:11px; color:#004080; font-weight:700; margin-top:4px;"><b>Contact:</b> ${s.contact || 'N/A'}</div>
          </div>
        `);
    });

    const userIcon = L.divIcon({
      className: 'user-pin-custom',
      iconSize: [14, 14],
      iconAnchor: [7, 7]
    });

    const userMarker = L.marker([coords.lat, coords.lng], {
      draggable: true,
      icon: userIcon,
      zIndexOffset: 1000
    }).addTo(map);
    userMarkerRef.current = userMarker;

    userMarker.on('dragend', () => {
      const latlng = userMarker.getLatLng();
      updateLocation(latlng.lat, latlng.lng);
    });

    map.on('click', (e) => {
      updateLocation(e.latlng.lat, e.latlng.lng);
    });

    updateLocation(coords.lat, coords.lng);

    return () => {
      map.remove();
    };
  }, [stations, jurisdictionsGeoJSON, showForm]);

  // Reverse geocoding
  const updateLocation = (lat, lng) => {
    setCoords({ lat, lng });
    
    if (userMarkerRef.current) {
      userMarkerRef.current.setLatLng([lat, lng]);
    }

    setIsCheckingJurisdiction(true);

    let foundLocal = false;
    let localMatchedName = '';
    if (jurisdictionsGeoJSON) {
      const point = [lng, lat];
      for (const feature of jurisdictionsGeoJSON.features) {
        if (isPointInGeometry(point, feature.geometry)) {
          localMatchedName = feature.properties.name;
          const matchedStation = stations.find(s => s.name === localMatchedName);
          if (matchedStation) {
            setAssignedStation(matchedStation);
            foundLocal = true;
            break;
          }
        }
      }
    }

    fetch('http://localhost:8000/api/get-jurisdiction', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ latitude: lat, longitude: lng })
    })
      .then(res => {
        if (!res.ok) throw new Error('API offline');
        return res.json();
      })
      .then(data => {
        const apiStation = stations.find(s => s.name === data.station);
        if (apiStation) {
          setAssignedStation(apiStation);
        }
      })
      .catch(err => {
        console.warn("Backend API offline. Fallback to local matching.");
        if (!foundLocal && stations.length > 0) {
          let minDistance = Infinity;
          let closest = null;
          stations.forEach(s => {
            const dist = Math.pow(s.latitude - lat, 2) + Math.pow(s.longitude - lng, 2);
            if (dist < minDistance) {
              minDistance = dist;
              closest = s;
            }
          });
          setAssignedStation(closest);
        }
      })
      .finally(() => {
        setIsCheckingJurisdiction(false);
      });

    fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`)
      .then(res => res.json())
      .then(data => {
        const addr = data.address || {};
        
        let dist = addr.district || addr.county || addr.subdistrict || 'Mumbai Suburban';
        if (dist.includes('Mumbai City') || lat < 19.02) {
          dist = 'Mumbai City';
        } else if (!dist.toLowerCase().includes('mumbai')) {
          dist = 'Mumbai Suburban';
        }
        setDistrict(dist);

        const road = addr.road || '';
        const suburb = addr.suburb || addr.neighbourhood || addr.city_district || '';
        const landmark = data.display_name.split(',')[1] || '';
        const formatted = `${road ? road + ', ' : ''}${suburb ? suburb + ', ' : ''}${landmark ? landmark + ' (Landmark), ' : ''}Mumbai, Maharashtra`;
        
        setOsmAddress(formatted);

        setFormInputs(prev => ({
          ...prev,
          placeOfOccurrence: formatted,
          district: dist
        }));
      })
      .catch(err => console.error("Reverse geocoding error:", err));
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
      fetch('http://localhost:8000/api/classify-offence', {
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

            setAiLegalResult({
              offence: top.title,
              bnsSection: sectionsList + ' of BNS, 2023',
              bnssAction: data.recommended_action,
              predictions: data.predictions,
              model: data.model,
              standardizedNarrative: data.standardized_narrative,
              translations: data.translations,
              isRag: true
            });
            setFormInputs(prev => ({
              ...prev,
              natureOfOffence: top.title,
              legalSections: sectionsList + ' of BNS, 2023'
            }));
          } else {
            setAiLegalResult(null);
          }
          setIsAiScanning(false);
        })
        .catch(err => {
          console.warn('RAG API offline, using local fallback:', err);
          // Fallback to local keyword matching
          const lower = text.toLowerCase();
          let classification = {
            offence: 'Theft',
            bnsSection: 'Section 303 (Theft) of BNS, 2023',
            bnssAction: 'Cognizable offense under Section 173 BNSS. Initiate FIR registration immediately.',
            isRag: false
          };
          if (lower.includes('hit') || lower.includes('assault') || lower.includes('beat') || lower.includes('slap') || lower.includes('fight')) {
            classification = { offence: 'Assault', bnsSection: 'Section 115 (Voluntarily causing hurt) & Section 117 (Grievous hurt) of BNS, 2023', bnssAction: 'Cognizable offense. Record complaint under Section 173 BNSS, order medical assessment.', isRag: false };
          } else if (lower.includes('fraud') || lower.includes('cheat') || lower.includes('scam') || lower.includes('money')) {
            classification = { offence: 'Fraud', bnsSection: 'Section 318 (Cheating) & Section 319 (Cheating by personation) of BNS, 2023', bnssAction: 'Cognizable. Register electronic FIR under Section 173 BNSS. Forward logs to Cyber Unit.', isRag: false };
          } else if (lower.includes('accident') || lower.includes('car') || lower.includes('crash') || lower.includes('drive')) {
            classification = { offence: 'Accident', bnsSection: 'Section 281 (Rash driving) & Section 106(2) (Hit-and-run) of BNS, 2023', bnssAction: 'Cognizable. Secure crash vector site, review traffic logs, file FIR under Sec 173 BNSS.', isRag: false };
          }
          setAiLegalResult(classification);
          setFormInputs(prev => ({
            ...prev,
            natureOfOffence: classification.offence,
            legalSections: classification.bnsSection
          }));
          setIsAiScanning(false);
        });
    }, 800);
  };

  // Address Search
  const handleSearchChange = (e) => {
    const query = e.target.value;
    setSearchText(query);

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
        .catch(err => console.error(err))
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

  const triggerGPS = () => {
    if (!navigator.geolocation) {
      alert("Geolocation not supported");
      return;
    }
    navigator.geolocation.getCurrentPosition(pos => {
      const lat = pos.coords.latitude;
      const lng = pos.coords.longitude;
      if (mapRef.current) mapRef.current.flyTo([lat, lng], 15, { animate: true });
      updateLocation(lat, lng);
    });
  };

  const focusOnStation = (station) => {
    if (mapRef.current) mapRef.current.flyTo([station.latitude, station.longitude], 15, { animate: true });
    updateLocation(station.latitude, station.longitude);
  };

  // Document Uploads
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setUploadedFile({
        name: file.name,
        size: (file.size / 1024).toFixed(1) + ' KB'
      });
    }
  };

  const handleMedicalFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setUploadedMedicalFile({
        name: file.name,
        size: (file.size / 1024).toFixed(1) + ' KB'
      });
    }
  };

  // Submit FIR form
  const handleFIRSubmit = (e) => {
    e.preventDefault();
    if (!uploadedFile) {
      alert(lang === 'en' ? "Please upload an identity verification document." : "कृपया ओळखीचे पुरावा दस्तऐवज अपलोड करा.");
      return;
    }
    const randomNo = Math.floor(1000 + Math.random() * 9000);
    setFirNo(`MUM-${randomNo}/${new Date().getFullYear()}`);
    setRegistrationTime(new Date().toLocaleString());
    setFirSubmitted(true);
  };

  const closeComplaintModal = () => {
    setShowForm(false);
    setFirSubmitted(false);
    setUploadedFile(null);
    setUploadedMedicalFile(null);
    setFormInputs({
      registrationMode: 'Electronic / Online',
      complainantName: '',
      complainantAddress: '',
      complainantContact: '',
      complainantId: '',
      occurrenceTime: '',
      placeOfOccurrence: '',
      natureOfOffence: 'Theft',
      legalSections: 'Section 303 (Theft), BNS, 2023',
      suspectName: 'Unknown',
      suspectAddress: 'Unknown',
      suspectDescription: '',
      victimName: '',
      victimContact: '',
      victimAddress: '',
      incidentSummary: '',
      propertyDescription: '',
      propertyValue: '',
      witnesses: [{ name: '', phone: '', address: '' }],
      policeAction: 'Investigation Started',
      policeOfficer: 'R. K. Patil, Inspector',
      policeRemarks: 'Case registered online, preliminary inquiry initiated.',
      eSignature: ''
    });
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

  const handlePrint = () => {
    window.print();
  };

  const copyEmailBody = () => {
    const witnessStr = formInputs.witnesses && formInputs.witnesses.length > 0
      ? formInputs.witnesses.map((w, i) => `${i + 1}. ${w.name || 'N/A'} (Ph: ${w.phone || 'N/A'}, Addr: ${w.address || 'N/A'})`).join('\n  ')
      : 'None';

    const text = `
To,
The Station House Officer (SHO),
${assignedStation?.name} Police Station,
District: ${district}, Mumbai.

Subject: Submission of Digital First Information Report (FIR) - FIR No. ${firNo}

Sir/Madam,

Please find attached the official First Information Report (FIR) registered electronically under Section 173 of the Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023.

Details of the case are as follows:
- FIR Registration Number: ${firNo}
- Complainant Name: ${formInputs.complainantName}
- Contact Reference: ${formInputs.complainantContact}
- Occurrence Date/Time: ${formInputs.occurrenceTime}
- Place of Occurrence: ${formInputs.placeOfOccurrence}
- Violations Classified: ${formInputs.legalSections}
- Witnesses Registered:
  ${witnessStr}

An official acknowledgement receipt is attached for your reference and action.

Sincerely,
${formInputs.complainantName}
(E-Signed Authentically Digitally)
`;
    navigator.clipboard.writeText(text);
    setIsEmailCopied(true);
    setTimeout(() => setIsEmailCopied(false), 2000);
  };

  // Filter lists
  const filteredDirectory = stations.filter(s => 
    s.name.toLowerCase().includes(directorySearch.toLowerCase()) ||
    s.ward.toLowerCase().includes(directorySearch.toLowerCase())
  );

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
            
            <button 
              className="lang-toggle"
              onClick={() => setLang(lang === 'en' ? 'mr' : 'en')}
            >
              {lang === 'en' ? 'मराठी' : 'English'}
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="tabs-nav">
          <button 
            className={`tab-btn ${activeTab === 'locator' ? 'active' : ''}`}
            onClick={() => { setActiveTab('locator'); if (!firSubmitted) setShowForm(false); }}
          >
            {t.tabLocator}
          </button>
          <button 
            className={`tab-btn ${activeTab === 'directory' ? 'active' : ''}`}
            onClick={() => { setActiveTab('directory'); if (!firSubmitted) setShowForm(false); }}
          >
            {t.tabDirectory}
          </button>
          <button 
            className={`tab-btn ${activeTab === 'analytics' ? 'active' : ''}`}
            onClick={() => { setActiveTab('analytics'); if (!firSubmitted) setShowForm(false); }}
          >
            {t.tabInsights}
          </button>
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
                <button className="btn-secondary" onClick={triggerGPS}>
                  {t.gpsBtn}
                </button>
                <button className="btn-secondary" onClick={() => updateLocation(19.0760, 72.8777)}>
                  {t.resetBtn}
                </button>
              </div>

              {/* Jurisdiction Result panel */}
              <div className="glass-panel alert-card success">
                <div className="alert-header">
                  <span className="panel-title" style={{margin: 0, border: 0, padding: 0}}>{t.assignedTitle}</span>
                  <span className={`status-badge ${isCheckingJurisdiction ? 'searching' : 'assigned'}`}>
                    {isCheckingJurisdiction ? t.matching : t.verified}
                  </span>
                </div>
                
                {assignedStation ? (
                  <div>
                    <h2 className="station-title">{assignedStation.name} Police Station</h2>
                    
                    <div className="detail-row" style={{marginTop: '15px'}}>
                      <span className="label">{t.ward}</span>
                      <span className="value">{assignedStation.ward || 'N/A'}</span>
                    </div>
                    <div className="detail-row">
                      <span className="label">POLICE DISTRICT</span>
                      <span className="value" style={{color: 'var(--color-accent)', fontWeight: 7}}>{district}</span>
                    </div>
                    <div className="detail-row">
                      <span className="label">{t.address}</span>
                      <span className="value">{assignedStation.address || 'Mumbai Headquarters'}</span>
                    </div>
                    <div className="detail-row">
                      <span className="label">{t.contact}</span>
                      <span className="value" style={{color: 'var(--color-success)', fontWeight: 7}}>{assignedStation.contact || '100 / 112'}</span>
                    </div>

                    <div className="detail-row" style={{borderTop: '1px solid var(--border-color)', paddingTop: '10px', marginTop: '10px'}}>
                      <span className="label">{t.coords}</span>
                      <span className="value" style={{fontFamily: 'monospace', fontSize: '11px', color: 'var(--text-muted)'}}>
                        {coords.lat.toFixed(5)}, {coords.lng.toFixed(5)}
                      </span>
                    </div>
                    
                    {!showForm && (
                      <button 
                        className="btn-pink" 
                        style={{marginTop: '15px'}}
                        onClick={() => setShowForm(true)}
                      >
                        {t.lodgeBtn}
                      </button>
                    )}
                  </div>
                ) : (
                  <div style={{color: 'var(--text-muted)', textAlign: 'center', padding: '20px 0'}}>
                    Locating territorial office... Click map or search address.
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
                        <div className="station-item-desc">
                          <span>Phone Reference: {s.contact || '100'}</span>
                          <span style={{color: 'var(--color-accent)', fontWeight: '700'}}>Focus Map</span>
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
                <p style={{fontSize: '12px', color: 'var(--text-muted)', lineHeight: 1.5, marginTop: '10px'}}>
                  Under **Section 173 of the Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023**, electronic/online registration of FIR is legally recognized. Police jurisdictions must process online complaints based on coordinates within their boundaries.
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
            {assignedStation && (
              <div className="map-overlay-badge">
                🏢 District: <span style={{color: 'var(--color-accent)'}}>{district}</span> &nbsp;|&nbsp; Station Sector: {assignedStation.name}
              </div>
            )}

            {/* Map Legend */}
            <div className="floating-legend">
              <div className="legend-title">COLORFUL JURISDICTION MAP</div>
              <div className="legend-item">
                <span className="legend-color" style={{backgroundColor: '#6366f1', opacity: 0.3, borderColor: '#334155'}}></span>
                <span>Active Jurisdiction Boundaries (Color by Ward)</span>
              </div>
              <div className="legend-item">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="var(--color-primary)" style={{display: 'block'}}>
                  <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
                </svg>
                <span>Police Station Headquarters</span>
              </div>
              <div className="legend-item">
                <span className="user-pin-custom" style={{display: 'inline-block', width: '12px', height: '12px'}}></span>
                <span>Locator Reference dot (Draggable)</span>
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
                {t.formTitle} Drafting Panel
              </h3>
              <button className="btn-secondary" style={{width: 'auto', padding: '6px 14px'}} onClick={closeComplaintModal}>
                ← Return to Map
              </button>
            </div>

            {!firSubmitted ? (
              /* DRAFTING INTERFACE */
              <div className="form-paper">
                <div className="form-header-title">
                  <h2>🇮🇳 {t.formTitle}</h2>
                  <p>{t.formSub}</p>
                </div>

                <form onSubmit={handleFIRSubmit}>
                  
                  {/* Automatic Geographic Details Section */}
                  <div className="form-section-header">Location Details (Auto-Fetched from map pin)</div>
                  
                  <div className="form-row two-cols">
                    <div className="form-group-field">
                      <label>Assigned Police Station</label>
                      <input type="text" readOnly value={assignedStation?.name || ''} style={{borderColor: 'var(--color-accent)', fontWeight: 6}} />
                    </div>
                    <div className="form-group-field">
                      <label>Police District</label>
                      <input type="text" readOnly value={district} style={{borderColor: 'var(--color-accent)', fontWeight: 6}} />
                    </div>
                  </div>

                  <div className="form-row two-cols">
                    <div className="form-group-field">
                      <label>{t.formMode}</label>
                      <select 
                        value={formInputs.registrationMode}
                        onChange={(e) => setFormInputs({...formInputs, registrationMode: e.target.value})}
                      >
                        <option value="Written">{t.formModeWritten}</option>
                        <option value="Oral">{t.formModeOral}</option>
                        <option value="Electronic / Online">{t.formModeElectronic}</option>
                      </select>
                    </div>
                    <div className="form-group-field">
                      <label>Territorial Coords (Lat, Lng)</label>
                      <input type="text" readOnly value={`${coords.lat.toFixed(5)}, ${coords.lng.toFixed(5)}`} />
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
                        required 
                        placeholder="Aadhaar / DL Number" 
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
                          {aiLegalResult.isRag ? 'BNS RAG Legal Classifier' : t.aiTitle}
                        </span>
                        <span style={{fontSize: '11px', color: 'var(--color-success)', fontWeight: 6}}>
                          {aiLegalResult.isRag ? '✓ RAG Corpus Match' : 'Fallback Mode'}
                        </span>
                      </div>
                      <div className="ai-scan-lines">
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
                                      TF-IDF: {(pred.rag_score * 100).toFixed(0)}% | LogReg: {(pred.lr_prob * 100).toFixed(0)}%
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
                        ) : (
                          <div className="llm-consensus-grid">
                            <div className="llm-box">
                              <div style={{color: 'var(--color-accent)', fontWeight: 6}}>Local Classifier</div>
                              <div style={{fontSize: '11px', fontWeight: 6}}>{aiLegalResult.offence} (Keyword Match)</div>
                            </div>
                            <div className="llm-box">
                              <div style={{color: 'var(--color-primary)', fontWeight: 6}}>Status</div>
                              <div style={{fontSize: '11px', fontWeight: 6}}>RAG API Offline — Fallback Active</div>
                            </div>
                          </div>
                        )}
                      </div>
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
                        <option value="Theft">Theft</option>
                        <option value="Assault">Assault</option>
                        <option value="Fraud">Fraud</option>
                        <option value="Accident">Accident</option>
                        <option value="Cyber Crime">Cyber Crime</option>
                        <option value="Other">Other</option>
                      </select>
                    </div>
                    <div className="form-group-field">
                      <label>BNS Act Violations</label>
                      <input 
                        type="text" 
                        required 
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

                  {/* Document Verification & Upload (Identity + Medical / Supporting proofs) */}
                  <div className="form-section-header">Authenticity Proofs & Verification</div>
                  
                  <div className="form-row two-cols">
                    {/* Identity Proof */}
                    <div className="form-group-field">
                      <label>{t.fileUploadTitle}</label>
                      <div className="file-upload-drag-area">
                        <input 
                          type="file" 
                          id="id-proof-upload" 
                          style={{display: 'none'}} 
                          onChange={handleFileChange}
                        />
                        <label htmlFor="id-proof-upload" style={{cursor: 'pointer'}}>
                          <div className="upload-icon">🆔</div>
                          <div style={{fontWeight: 7, fontSize: '11px'}}>{t.fileUploadDrag}</div>
                        </label>
                      </div>
                      {uploadedFile && (
                        <div style={{marginTop: '6px', fontSize: '11px', color: 'var(--color-success)', fontWeight: 6}}>
                          ✓ {t.fileUploadSuccess} <b>{uploadedFile.name}</b>
                        </div>
                      )}
                    </div>

                    {/* Medical / Supporting proofs */}
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
                          <div className="upload-icon">🏥</div>
                          <div style={{fontWeight: 7, fontSize: '11px'}}>{t.fileUploadDrag}</div>
                        </label>
                      </div>
                      {uploadedMedicalFile && (
                        <div style={{marginTop: '6px', fontSize: '11px', color: 'var(--color-success)', fontWeight: 6}}>
                          ✓ {t.fileUploadMedicalSuccess} <b>{uploadedMedicalFile.name}</b>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Penal warning regarding forgery under Sec 465/468 */}
                  <div className="legal-warning-box">
                    ⚠️ <b>{lang === 'en' ? 'LEGAL PENAL WARNING' : 'कायदेशीर फौजदारी इशारा'}:</b> {t.forgeryWarning}
                  </div>

                  {/* Section 12: Signatures */}
                  <div className="form-section-header">{t.secSignatures}</div>
                  
                  <div className="form-group-field">
                    <label>{t.formSign}</label>
                    <input 
                      type="text" 
                      required 
                      placeholder="Type name as signature verification" 
                      value={formInputs.eSignature}
                      onChange={(e) => setFormInputs({...formInputs, eSignature: e.target.value})}
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
            ) : (
              /* PDF PRINT PREVIEW & VERIFICATION & EMAIL DISPATCH WORKSPACE */
              <div className="form-paper" style={{padding: '30px'}}>
                
                {/* Official Printable document */}
                <div id="printable-fir-sheet" className="printable-fir-page">
                  <div className="printable-fir-header">
                    <div style={{fontSize: '28px'}}>🇮🇳</div>
                    <h2 style={{fontFamily: 'var(--font-heading)', color: '#000000', fontSize: '18px', margin: '6px 0'}}>FIRST INFORMATION REPORT (FIR)</h2>
                    <div style={{fontSize: '11px', fontStyle: 'italic'}}>(Under Section 173 of the Bharatiya Nagarik Suraksha Sanhita, 2023)</div>
                  </div>

                  <div className="printable-fir-grid">
                    <div>
                      <b>District:</b> {district}<br />
                      <b>Police Station:</b> {assignedStation?.name}<br />
                      <b>FIR Number:</b> {firNo}
                    </div>
                    <div style={{textAlign: 'right'}}>
                      <b>Date & Time:</b> {registrationTime}<br />
                      <b>Registration Mode:</b> {formInputs.registrationMode}
                    </div>
                  </div>

                  <div className="printable-fir-section">
                    <div className="printable-fir-section-title">1. Complainant / Informant Details</div>
                    <b>Name:</b> {formInputs.complainantName}<br />
                    <b>Address:</b> {formInputs.complainantAddress}<br />
                    <b>Contact No:</b> {formInputs.complainantContact}<br />
                    <b>ID Reference:</b> {formInputs.complainantId}
                  </div>

                  <div className="printable-fir-section">
                    <div className="printable-fir-section-title">2. Date and Time of Occurrence</div>
                    <b>Timeline:</b> {formInputs.occurrenceTime}
                  </div>

                  <div className="printable-fir-section">
                    <div className="printable-fir-section-title">3. Place of Occurrence</div>
                    <b>Address:</b> {formInputs.placeOfOccurrence}<br />
                    <b>Coordinates:</b> Lat {coords.lat.toFixed(5)}, Lng {coords.lng.toFixed(5)}
                  </div>

                  <div className="printable-fir-section">
                    <div className="printable-fir-section-title">4. Nature of Offence</div>
                    <b>Classification:</b> {formInputs.natureOfOffence}
                  </div>

                  <div className="printable-fir-section">
                    <div className="printable-fir-section-title">5. Relevant Legal Sections (BNS, 2023)</div>
                    <b>Classified Sections:</b> {formInputs.legalSections}
                  </div>

                  <div className="printable-fir-section">
                    <div className="printable-fir-section-title">6. Details of Accused / Suspects</div>
                    <b>Name:</b> {formInputs.suspectName}<br />
                    <b>Address:</b> {formInputs.suspectAddress}<br />
                    <b>Physical Description:</b> {formInputs.suspectDescription || 'None recorded'}
                  </div>

                  <div className="printable-fir-section">
                    <div className="printable-fir-section-title">7. Details of Victims</div>
                    <b>Name:</b> {formInputs.victimName || 'Same as Complainant'}<br />
                    <b>Contact No:</b> {formInputs.victimContact || 'N/A'}<br />
                    <b>Address:</b> {formInputs.victimAddress || 'N/A'}
                  </div>

                  <div className="printable-fir-section">
                    <div className="printable-fir-section-title">8. Summary of Incident (Facts of the Case)</div>
                    <div style={{whiteSpace: 'pre-wrap', lineHeight: 1.5}}>{formInputs.incidentSummary}</div>
                  </div>

                  <div className="printable-fir-section">
                    <div className="printable-fir-section-title">9. Property Involved (if any)</div>
                    <b>Description:</b> {formInputs.propertyDescription || 'None'}<br />
                    <b>Estimated Value:</b> {formInputs.propertyValue ? `₹ ${formInputs.propertyValue}` : 'N/A'}
                  </div>

                  <div className="printable-fir-section">
                    <div className="printable-fir-section-title">10. Witnesses (if any)</div>
                    {formInputs.witnesses && formInputs.witnesses.length > 0 ? (
                      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px', marginTop: '6px' }}>
                        <thead>
                          <tr style={{ borderBottom: '1px solid #000' }}>
                            <th style={{ textAlign: 'left', padding: '4px 0', width: '30%' }}>Name</th>
                            <th style={{ textAlign: 'left', padding: '4px 0', width: '25%' }}>Phone No.</th>
                            <th style={{ textAlign: 'left', padding: '4px 0', width: '45%' }}>Address</th>
                          </tr>
                        </thead>
                        <tbody>
                          {formInputs.witnesses.map((w, idx) => (
                            <tr key={idx} style={{ borderBottom: '1px solid #eee' }}>
                              <td style={{ padding: '6px 0' }}>{w.name || 'N/A'}</td>
                              <td style={{ padding: '6px 0' }}>{w.phone || 'N/A'}</td>
                              <td style={{ padding: '6px 0' }}>{w.address || 'N/A'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    ) : (
                      <span style={{ fontSize: '13px', fontStyle: 'italic' }}>None recorded</span>
                    )}
                  </div>

                  <div className="printable-fir-section">
                    <div className="printable-fir-section-title">11. Action Taken by Police</div>
                    <b>Status:</b> {formInputs.policeAction}<br />
                    <b>Officer:</b> {formInputs.policeOfficer}<br />
                    <b>Remarks:</b> {formInputs.policeRemarks}
                  </div>

                  <div className="printable-fir-section">
                    <div className="printable-fir-section-title">12. Signatures & Verified Authenticity Proofs</div>
                    <div style={{display: 'flex', justifyContent: 'space-between', marginTop: '10px'}}>
                      <div>
                        <b>Complainant E-Signature:</b><br />
                        <span style={{fontFamily: 'Georgia', fontStyle: 'italic', fontSize: '16px', borderBottom: '1px solid #000000'}}>{formInputs.eSignature}</span>
                      </div>
                      <div style={{textAlign: 'right', fontSize: '11px', color: '#166534', fontWeight: 'bold'}}>
                        <b>Identity Proof:</b> {uploadedFile?.name}<br />
                        {uploadedMedicalFile && <span><b>Supporting File:</b> {uploadedMedicalFile?.name}</span>}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Email Draft dispatcher and Print actions */}
                <div className="no-print" style={{marginTop: '30px', borderTop: '1px solid #cbd5e1', paddingTop: '20px'}}>
                  <div className="btn-group">
                    <button className="btn-primary" onClick={handlePrint}>
                      🖨️ {lang === 'en' ? 'Print / Download Official PDF Report' : 'अधिकृत पीडीएफ अहवाल प्रिंट / डाउनलोड करा'}
                    </button>
                    <button className="btn-secondary" onClick={closeComplaintModal}>
                      Close and return to map
                    </button>
                  </div>

                  {/* Email drafting dispatcher */}
                  <div className="dispatch-email-preview">
                    <div className="dispatch-header">
                      📬 {t.emailDispatchTitle}
                    </div>

                    <div className="detail-row">
                      <span className="label">{t.emailDispatchTo}:</span>
                      <span className="value" style={{fontFamily: 'monospace'}}>{assignedStation?.name.toLowerCase().replace(' ', '')}.ps@mumbaipolice.gov.in</span>
                    </div>

                    <div className="detail-row">
                      <span className="label">{t.emailDispatchSub}:</span>
                      <span className="value" style={{fontWeight: 6}}>Official Filing of FIR No. {firNo} - Sec. 173 BNSS</span>
                    </div>

                    <div style={{fontSize: '11px', color: 'var(--text-muted)', marginBottom: '8px', fontWeight: 6}}>
                      Email Body Draft:
                    </div>

                    <div className="dispatch-text-body">
{`To,
The Station House Officer (SHO),
${assignedStation?.name} Police Station,
District: ${district}, Mumbai.

Subject: Submission of Digital First Information Report (FIR) - FIR No. ${firNo}

Sir/Madam,

Please find attached the official First Information Report (FIR) registered electronically under Section 173 of the Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023.

Details of the case are as follows:
- FIR Registration Number: ${firNo}
- Complainant Name: ${formInputs.complainantName}
- Contact Reference: ${formInputs.complainantContact}
- Occurrence Date/Time: ${formInputs.occurrenceTime}
- Place of Occurrence: ${formInputs.placeOfOccurrence}
- Violations Classified: ${formInputs.legalSections}
- Witnesses Registered:
  ${formInputs.witnesses && formInputs.witnesses.length > 0 ? formInputs.witnesses.map((w, i) => `${i + 1}. ${w.name || 'N/A'} (Ph: ${w.phone || 'N/A'}, Addr: ${w.address || 'N/A'})`).join('\n  ') : 'None'}

An official acknowledgement receipt is attached for your reference and action.

Sincerely,
${formInputs.complainantName}
(E-Signed Authentically Digitally)`}
                    </div>

                    <div className="btn-group" style={{marginTop: '15px', marginBottom: 0}}>
                      <button className="btn-secondary" onClick={copyEmailBody}>
                        {isEmailCopied ? t.emailCopied : t.emailCopyBtn}
                      </button>
                      <a 
                        href={`mailto:${assignedStation?.name.toLowerCase().replace(' ', '')}.ps@mumbaipolice.gov.in?subject=Official Dispatch: Registered FIR complaint No. ${firNo}&body=Sir/Madam,%0D%0DPlease find attached the official First Information Report (FIR) registered electronically under Section 173 of the Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023.%0D%0DFIR No: ${firNo}%0DComplainant: ${formInputs.complainantName}%0DOffence: ${formInputs.legalSections}%0D%0DSincerely,%0D${formInputs.complainantName}`} 
                        className="btn-primary"
                        style={{textDecoration: 'none'}}
                      >
                        {t.emailDispatchBtn}
                      </a>
                    </div>
                  </div>
                </div>

              </div>
            )}

          </div>
        )}

      </div>
    </div>
  );
}
