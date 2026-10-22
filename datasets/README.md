# Bandhoo Datasets Directory

This directory consolidates all statutory, benchmark, and geographical datasets utilized by the Bandhoo BNS Prediction and Complaint Structuring Engine.

---

## Dataset Inventory

| Dataset Filename | Format | Description / Provenance | Size | Records / Scope | Primary Operational Role |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`bns_rag_dataset.json`** | JSON | Bharatiya Nyaya Sanhita, 2023 statutory corpus (Gazette of India, cleaned) | 1.1 MB | 358 BNS sections | Inverted index for Okapi BM25 lexical candidate retrieval |
| **`bns_finetune_dataset.json`** | JSON | Instruction-tuning dataset pairing legal scenarios with applicable BNS sections | 806 KB | Prompt-completion pairs | Fine-tuning domain-specific legal LLMs |
| **`bns_scenarios_dataset.json`** | JSON | Synthetic citizen grievance and criminal scenario narratives | 190 KB | Narrative scenarios | Scenario testing and prompt engineering |
| **`mumbai_police_jurisdictions.geojson`** | GeoJSON | Polygons defining Mumbai municipal police station territorial jurisdictions | 423 KB | 102 station polygons | Point-in-polygon ray-casting and 100m boundary safety buffer |
| **`police_stations_data.json`** | JSON | Station directory with names, coordinates, and contact details | 27 KB | 91 station records | Police station lookup and official email dispatch mapping |
| **`mumbai_police_station.kml_`** | KML | Raw Keyhole Markup Language boundary export for Mumbai police stations | 442 KB | Raw KML placemarks | Reference geographical source data |
| **`bns_synthetic_benchmark_50.json`** | JSON | 50 synthetic test cases across English (26), Hindi (12), and Hinglish (12) | 100 KB | 50 benchmark cases | Legal section prediction, negation handling, and fallback evaluation |
| **`structuring_cases.json`** | JSON | 34 complaint structuring cases (220 gold facts) + 11 jurisdiction test cases | 41 KB | 34 complaints + 11 GIS | LangGraph fact extraction, span grounding, and draft integrity evaluation |
| **`dataset_splits.json`** | JSON | Benchmark split definitions (Development: 35 cases, Held-out: 15 cases) | 1.7 KB | Split ID mappings | Standardized train/dev/test partitioning |

---

## Data Usage & Safety Notice
1. **Statutory Integrity**: `bns_rag_dataset.json` has undergone statutory verification against the Gazette of India; raw scraper outputs should never overwrite this verified file directly.
2. **Synthetic Benchmarks**: The benchmark datasets in this directory (`bns_synthetic_benchmark_50.json` and `structuring_cases.json`) are synthetic test sets authored for algorithmic verification. They have not been audited or certified by qualified legal advocates.
3. **Geographic Boundaries**: `mumbai_police_jurisdictions.geojson` represents administrative municipal station boundaries used with a 100-meter safety buffer. In boundary ambiguity zones, the system routes complaints for manual officer confirmation.
