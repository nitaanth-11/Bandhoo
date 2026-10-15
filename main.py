import json
import os
import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from scipy.spatial import KDTree
import uvicorn
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Synonym Mapping & Translation Agent ──
# Maps common colloquial synonyms/descriptions to standard legal/factual words 
# found in the BNS descriptions and scenarios dataset.
SYNONYM_MAP = {
    # ── Theft / Snatching / Robbery / Burglary / Extortion ──
    "stole": "theft",
    "stolen": "theft",
    "stealing": "theft",
    "swipe": "theft",
    "swiped": "theft",
    "pilfer": "theft",
    "pilfered": "theft",
    "pocketed": "theft",
    "pickpocket": "theft",
    "pickpocketed": "theft",
    "snatched": "snatching",
    "snatching": "snatching",
    "robbed": "robbery",
    "robbery": "robbery",
    "looted": "dacoity",
    "loot": "dacoity",
    "burgled": "house-breaking",
    "burglary": "house-breaking",
    "housebreaking": "house-breaking",
    "housebroke": "house-breaking",
    "ransacked": "criminal trespass",
    "mugged": "robbery",
    "extorted": "extortion",
    "extortion": "extortion",
    "blackmailed": "extortion",
    
    # ── Hindi/Hinglish & Local Slang for Theft / Robbery / Extortion ──
    "chori": "theft",
    "chori kiya": "theft",
    "chora liya": "theft",
    "chor": "theft",
    "lootpat": "robbery",
    "dakaiti": "dacoity",
    "dacoity": "dacoity",
    "snatch kiya": "snatching",
    "hafta": "extortion",
    "hafta vasuli": "extortion",
    "haftavasuli": "extortion",
    "vasuli": "extortion",
    "gunda": "dacoity extortion",
    "patka": "robbery",
    
    # ── Violence / Assault / Murder / Hurt ──
    "killed": "murder",
    "murdered": "murder",
    "murder": "murder",
    "slain": "murder",
    "homicide": "murder",
    "poisoned": "poison",
    "stabbed": "grievous hurt",
    "slashed": "hurt",
    "shot": "gunshot",
    "gunned": "gunshot",
    "hit": "assault",
    "beat": "assault",
    "beaten": "assault",
    "thrashed": "assault",
    "punched": "assault",
    "slapped": "assault",
    "kicked": "assault",
    "fractured": "grievous hurt",
    "broken bone": "grievous hurt",
    "disfigured": "grievous hurt",
    "acid": "acid attack",
    
    # ── Hindi/Hinglish & Local Slang for Violence / Hurt / Murder ──
    "maarpeet": "assault hurt",
    "maar peet": "assault hurt",
    "marpeet": "assault hurt",
    "mara": "assault",
    "pit diya": "assault",
    "pita": "assault",
    "pitaai": "assault",
    "thappad": "assault slap",
    "ghusa": "assault punch",
    "khoon": "murder death",
    "maar dala": "murder",
    "maar daala": "murder",
    "jaan se marne": "criminal intimidation murder",
    "chaku": "knife weapon grievous hurt",
    "chhuri": "knife weapon grievous hurt",
    "danda": "stick weapon hurt",
    "lathi": "stick weapon hurt",
    "talwar": "sword weapon grievous hurt",
    "goli": "gunshot firearm murder",
    "lafda": "assault fight",
    "jhagda": "assault fight",
    
    # ── Sexual offences ──
    "raped": "rape",
    "rape": "rape",
    "molested": "outrage modesty",
    "molestation": "outrage modesty",
    "groped": "sexual harassment",
    "stalked": "stalking",
    "stalking": "stalking",
    "voyeurism": "voyeurism",
    "filmed secretly": "voyeurism",
    
    # ── Hindi/Hinglish & Local Slang for Sexual Offences ──
    "chedchad": "outrage modesty sexual harassment",
    "ched chad": "outrage modesty sexual harassment",
    "picha kiya": "stalking",
    "picha kar raha": "stalking",
    "galat tarike se chua": "sexual harassment outrage modesty",
    "sharamnak": "modesty outrage",
    "ganda bola": "obscene sexual harassment",
    
    # ── Fraud / Cheating / Forgery / Breach of trust ──
    "cheated": "cheating",
    "cheating": "cheating",
    "scammed": "cheating",
    "scam": "cheating",
    "defrauded": "cheating",
    "duped": "cheating",
    "swindled": "cheating",
    "forged": "forgery",
    "forgery": "forgery",
    "faked": "forgery",
    "fake": "forgery",
    "counterfeited": "counterfeit",
    "impersonated": "cheating by personation",
    "bribed": "bribe",
    "bribe": "bribe",
    "embezzled": "criminal breach of trust",
    "misappropriated": "criminal misappropriation of property",
    
    # ── Hindi/Hinglish & Local Slang for Fraud / Cheating / Scam ──
    "dhokha": "cheating",
    "dhokhadi": "cheating fraud",
    "dhokhadhadi": "cheating fraud",
    "dhokha diya": "cheating",
    "chuna lagaya": "cheating fraud",
    "chuna laga diya": "cheating fraud",
    "ghabla": "cheating fraud",
    "ghotala": "cheating fraud",
    "paisa kha gaya": "criminal breach of trust",
    "paisa hadap": "criminal breach of trust",
    "gaban": "embezzlement criminal breach of trust",
    "farzi": "forgery fake",
    "farziwara": "forgery fake",
    "farziwada": "forgery fake",
    "farzi document": "forgery fake",
    "nakli": "counterfeit fake forgery",
    "rishwat": "bribe corruption",
    
    # ── Kidnapping / Restraint ──
    "kidnapped": "kidnapping",
    "kidnapping": "kidnapping",
    "abducted": "abduction",
    "abduction": "abduction",
    "confined": "wrongful confinement",
    "confinement": "wrongful confinement",
    "locked up": "wrongful confinement",
    "blocked": "wrongful restraint",
    
    # ── Hindi/Hinglish & Local Slang for Kidnapping / Confinement ──
    "kidnap kiya": "kidnapping",
    "uthakar le gaya": "kidnapping",
    "bhaga le gaya": "abduction",
    "bandh liya": "wrongful confinement",
    "bandh banakar rakha": "wrongful confinement",
    "roka": "wrongful restraint",
    
    # ── Others ──
    "rioted": "rioting",
    "rioting": "rioting",
    "arson": "mischief by fire",
    "burned": "mischief by fire",
    "defamed": "defamation",
    "defamation": "defamation",
    "threatened": "criminal intimidation",
    "threat": "criminal intimidation",
    "intimidated": "criminal intimidation",
    
    # ── Hindi/Hinglish & Local Slang for Others ──
    "dhamki": "criminal intimidation threat",
    "dhamkiya": "criminal intimidation threat",
    "dhamki di": "criminal intimidation threat",
    "aag laga di": "mischief by fire arson",
    "jala diya": "mischief by fire arson",
    "dangai": "rioting",
    "danga": "rioting",
}

def translate_synonyms(text: str):
    """
    Scans the narrative text, locates matched synonyms, and outputs a 
    standardized format for classification (RAG & Logistic Regression).
    """
    if not text:
        return "", []
    
    translations = []
    standardized_text = text
    
    # Sort keys by length descending so that multi-word terms match before single words
    sorted_syns = sorted(SYNONYM_MAP.keys(), key=len, reverse=True)
    
    for syn in sorted_syns:
        pattern = r'\b' + re.escape(syn) + r'\b'
        if re.search(pattern, standardized_text, re.IGNORECASE):
            std_term = SYNONYM_MAP[syn]
            translations.append({
                "synonym": syn,
                "standard_term": std_term
            })
            standardized_text = re.sub(pattern, std_term, standardized_text, flags=re.IGNORECASE)
            
    return standardized_text, translations

# ── Load the police stations dataset ──
current_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(current_dir, "police_stations_data.json")

if not os.path.exists(json_path):
    raise FileNotFoundError(f"Required station dataset not found at: {json_path}")

with open(json_path, "r", encoding="utf-8") as f:
    stations_data = json.load(f)

# Filter for Subtype = 'Station' (actual police stations)
stations = [s for s in stations_data if s['subtype'] == 'Station']
coords = [[s['latitude'], s['longitude']] for s in stations]

# Create the spatial engine (lat, lng coords)
jurisdiction_tree = KDTree(coords)

# ── Load the BNS RAG Dataset & Build TF-IDF Index ──
bns_path = os.path.join(current_dir, "bns_rag_dataset.json")
bns_sections = []
tfidf_vectorizer = None
tfidf_matrix = None

if os.path.exists(bns_path):
    with open(bns_path, "r", encoding="utf-8") as f:
        bns_sections = json.load(f)
    print(f"[RAG] Loaded {len(bns_sections)} BNS sections from dataset.")

    # Build TF-IDF index
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine

        # Create a combined corpus: title + keywords + description text
        corpus = []
        for sec in bns_sections:
            doc = f"{sec.get('title', '')} {' '.join(sec.get('keywords', []))} {sec.get('text', '')}"
            corpus.append(doc)

        tfidf_vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=10000,
            ngram_range=(1, 2),
            sublinear_tf=True
        )
        tfidf_matrix = tfidf_vectorizer.fit_transform(corpus)
        print(f"[RAG] TF-IDF index built: {tfidf_matrix.shape[0]} docs × {tfidf_matrix.shape[1]} features")
    except ImportError:
        print("[RAG] WARNING: scikit-learn not installed. Install with: pip install scikit-learn")
        print("[RAG] The /api/classify-offence endpoint will not work without it.")
else:
    print(f"[RAG] BNS dataset not found at {bns_path}. Run scrape_bns.py first.")
    print("[RAG] The /api/classify-offence endpoint will return empty results.")

# ── Also load the scenarios dataset for enhanced matching ──
scenarios_path = os.path.join(current_dir, "bns_scenarios_dataset.json")
bns_scenarios = []
scenario_vectorizer = None
scenario_matrix = None

if os.path.exists(scenarios_path):
    with open(scenarios_path, "r", encoding="utf-8") as f:
        bns_scenarios = json.load(f)
    print(f"[RAG] Loaded {len(bns_scenarios)} scenario entries.")

    if tfidf_vectorizer is not None:
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer as TV2
            from sklearn.metrics.pairwise import cosine_similarity as cs2

            scenario_corpus = [s['scenario'] for s in bns_scenarios]
            scenario_vectorizer = TfidfVectorizer(
                stop_words='english',
                max_features=8000,
                ngram_range=(1, 2),
                sublinear_tf=True
            )
            scenario_matrix = scenario_vectorizer.fit_transform(scenario_corpus)
            print(f"[RAG] Scenario TF-IDF index built: {scenario_matrix.shape}")
        except Exception as e:
            print(f"[RAG] Could not build scenario index: {e}")

# ── Train Logistic Regression Classifier on Startup ──
lr_classifier = None
lr_vectorizer = None

def train_logistic_regression():
    global lr_classifier, lr_vectorizer
    if not bns_sections:
        print("[LR] Cannot train: BNS sections dataset not loaded.")
        return

    print("[LR] Training Logistic Regression model on BNS corpus and scenarios...")
    train_texts = []
    train_labels = []

    # 1. Add section texts (mapped to their section number)
    for sec in bns_sections:
        content = f"{sec.get('title', '')} {' '.join(sec.get('keywords', []))} {sec.get('text', '')}"
        std_content, _ = translate_synonyms(content)
        train_texts.append(std_content)
        train_labels.append(sec["section"])

    # 2. Add scenario texts (mapped to their section numbers)
    for sc in bns_scenarios:
        std_sc, _ = translate_synonyms(sc["scenario"])
        for sec_num in sc.get("sections", []):
            train_texts.append(std_sc)
            train_labels.append(sec_num)

    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression

        lr_vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            sublinear_tf=True
        )
        X_train = lr_vectorizer.fit_transform(train_texts)
        y_train = np.array(train_labels)

        # Train a Logistic Regression model
        # Use class_weight='balanced' to handle class imbalance across BNS sections
        lr_classifier = LogisticRegression(C=1.0, max_iter=1000, class_weight='balanced', solver='liblinear')
        lr_classifier.fit(X_train, y_train)
        print(f"[LR] Logistic Regression trained successfully on {len(train_texts)} samples across {len(set(train_labels))} unique classes.")
    except Exception as e:
        print(f"[LR] Error training Logistic Regression: {e}")

# Trigger training
train_logistic_regression()


# ── Pydantic Models ──

class Location(BaseModel):
    latitude: float
    longitude: float

class NarrativeInput(BaseModel):
    narrative: str


# ── Endpoints ──

@app.post("/api/get-jurisdiction")
async def get_jurisdiction(loc: Location):
    # Find the closest station to the input point
    dist, index = jurisdiction_tree.query([loc.latitude, loc.longitude])
    assigned_station = stations[index]
    return {
        "station": assigned_station["name"],
        "details": assigned_station
    }


@app.post("/api/classify-offence")
async def classify_offence(data: NarrativeInput):
    """
    Intelligent BNS legal section classifier.
    Translates colloquial synonyms to standard legal terms,
    then predicts matching sections using a combined approach:
    1. TF-IDF Cosine Similarity against the full BNS corpus (RAG)
    2. Logistic Regression probability trained on BNS and scenarios
    3. Scenario Cosine Similarity matching (scenario boost)
    """
    narrative = data.narrative.strip()

    if not narrative or len(narrative) < 5:
        return {
            "predictions": [],
            "recommended_action": "",
            "model": "N/A",
            "standardized_narrative": "",
            "translations": []
        }

    if tfidf_vectorizer is None or tfidf_matrix is None:
        return {
            "predictions": [],
            "recommended_action": "RAG engine not initialized. Run scrape_bns.py first.",
            "model": "Offline",
            "standardized_narrative": narrative,
            "translations": []
        }

    # ── Step 1: Translate Synonyms to Standard Legal Format ──
    standard_narrative, translations = translate_synonyms(narrative)

    from sklearn.metrics.pairwise import cosine_similarity

    # ── Step 2: TF-IDF Cosine Similarity (RAG) ──
    query_vec = tfidf_vectorizer.transform([standard_narrative])
    similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()

    # ── Step 3: Logistic Regression Classifier ──
    lr_probs = {}
    if lr_classifier is not None and lr_vectorizer is not None:
        try:
            q_lr = lr_vectorizer.transform([standard_narrative])
            probs = lr_classifier.predict_proba(q_lr)[0]
            classes = lr_classifier.classes_
            for cls, prob in zip(classes, probs):
                lr_probs[int(cls)] = float(prob)
        except Exception as e:
            print(f"[LR] Inference error: {e}")

    # ── Step 4: Scenario Matching Boost ──
    scenario_boost = {}
    matched_scenario_texts = {}
    if scenario_vectorizer is not None and scenario_matrix is not None:
        try:
            q2 = scenario_vectorizer.transform([standard_narrative])
            s2 = cosine_similarity(q2, scenario_matrix).flatten()
            top_scenario_indices = s2.argsort()[-5:][::-1]
            for si in top_scenario_indices:
                if s2[si] < 0.05:
                    continue
                matched_scenario = bns_scenarios[si]
                for sec_num in matched_scenario.get("sections", []):
                    if sec_num not in scenario_boost:
                        scenario_boost[sec_num] = float(s2[si])
                        matched_scenario_texts[sec_num] = matched_scenario.get("scenario", "")
                    else:
                        if float(s2[si]) > scenario_boost[sec_num]:
                            scenario_boost[sec_num] = float(s2[si])
                            matched_scenario_texts[sec_num] = matched_scenario.get("scenario", "")
        except Exception as e:
            print(f"[RAG] Scenario matching error: {e}")

    # ── Step 5: Merge Predictions (Specify all applicable sections) ──
    section_predictions = []
    
    # We iterate through all BNS sections to make sure we don't miss any matching sections
    for idx, sec in enumerate(bns_sections):
        sec_num = sec["section"]
        rag_score = float(similarities[idx])
        lr_prob = lr_probs.get(sec_num, 0.0)
        boost = scenario_boost.get(sec_num, 0.0)

        # Weighted combined score
        # 40% lexical RAG similarity + 40% Logistic Regression probability + 20% scenario similarity
        combined_score = (0.4 * rag_score) + (0.4 * lr_prob) + (0.2 * boost)

        # Include if combined score is positive or RAG/LR matches with confidence
        if combined_score > 0.015 or rag_score > 0.03 or lr_prob > 0.015:
            section_predictions.append({
                "section": sec["section"],
                "title": sec["title"],
                "chapter": sec.get("chapter", ""),
                "score": round(combined_score, 4),
                "rag_score": round(rag_score, 4),
                "lr_prob": round(lr_prob, 4),
                "scenario_match": round(boost, 4),
                "matched_scenario": matched_scenario_texts.get(sec_num, ""),
                "punishment": sec.get("punishment", ""),
                "keywords": sec.get("keywords", []),
                "text_snippet": sec.get("text", "")[:300]
            })

    # Sort by combined score descending
    section_predictions.sort(key=lambda x: x["score"], reverse=True)
    
    # Take the top 8 predictions to ensure comprehensive coverage without cluttering the screen
    top_predictions = section_predictions[:8]

    # ── Generate Reasoning for each prediction ──
    standard_narrative_lower = standard_narrative.lower()
    narrative_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', standard_narrative_lower))

    for pred in top_predictions:
        reasoning_parts = []

        # 1. Section overview
        reasoning_parts.append(
            f"Section {pred['section']} of BNS, 2023 deals with \"{pred['title']}\" "
            f"under {pred.get('chapter', 'the relevant chapter')}."
        )

        # 2. Keyword overlap analysis
        section_keywords = set(k.lower() for k in pred.get("keywords", []))
        overlap = narrative_words & section_keywords
        if overlap:
            reasoning_parts.append(
                f"Keyword match: The standardized narrative contains terms [{', '.join(sorted(overlap))}] "
                f"which directly relate to this section's legal scope."
            )

        # 3. Text-based contextual reasoning
        snippet = pred.get("text_snippet", "")
        if snippet:
            first_sentence = snippet.split('.')[0].strip() + '.' if '.' in snippet else snippet[:150]
            reasoning_parts.append(
                f"Legal definition: \"{first_sentence[:200]}\""
            )

        # 4. Scenario evidence
        if pred.get("matched_scenario"):
            reasoning_parts.append(
                f"Scenario evidence: The narrative closely matches a known crime pattern - "
                f"\"{pred['matched_scenario'][:150]}\" "
                f"(scenario similarity: {pred.get('scenario_match', 0) * 100:.1f}%)."
            )

        # 5. Combined score interpretation
        score_pct = pred["score"] * 100
        if score_pct > 50:
            confidence = "very high"
        elif score_pct > 30:
            confidence = "high"
        elif score_pct > 15:
            confidence = "moderate"
        else:
            confidence = "indicative"
            
        reasoning_parts.append(
            f"Confidence: {confidence} (Combined score: {score_pct:.1f}% based on TF-IDF match: {pred['rag_score']*100:.1f}% & Logistic Regression: {pred['lr_prob']*100:.1f}%)."
        )

        # 6. Punishment
        if pred.get("punishment"):
            reasoning_parts.append(
                f"Prescribed punishment: {pred['punishment'][:250]}"
            )

        pred["reasoning"] = " ".join(reasoning_parts)

    # Generate recommended action
    if top_predictions:
        top = top_predictions[0]
        sections_cited = ", ".join(
            f"Section {p['section']} ({p['title']})" for p in top_predictions[:3]
        )
        action = (
            f"Based on synonym-translated RAG and Logistic Regression analysis of the incident narrative against {len(bns_sections)} BNS sections, "
            f"the following sections are applicable: {sections_cited}. "
            f"This constitutes a cognizable offense. Register FIR under Section 173 of BNSS, 2023."
        )
        if top.get("punishment"):
            action += f" Primary punishment: {top['punishment'][:200]}"
    else:
        action = "Unable to classify. Please provide more details about the incident."

    return {
        "predictions": top_predictions,
        "recommended_action": action,
        "model": f"Synonym Agent + RAG Cosine Similarity + Logistic Regression (BNS: {len(bns_sections)} sections, {len(bns_scenarios)} scenarios)",
        "standardized_narrative": standard_narrative,
        "translations": translations
    }


@app.get("/api/bns-stats")
async def bns_stats():
    """Return statistics about the loaded BNS dataset."""
    return {
        "sections_loaded": len(bns_sections),
        "scenarios_loaded": len(bns_scenarios),
        "tfidf_ready": tfidf_vectorizer is not None,
        "scenario_index_ready": scenario_vectorizer is not None
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)