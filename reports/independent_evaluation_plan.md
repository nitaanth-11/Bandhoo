# Bandhoo Independent Evaluation Plan

**Prepared:** 2026-10-20, internal-testing checkpoint. **For:** the evaluation lead, qualified legal reviewers, and Bandhoo maintainers.

**Purpose:** to measure Bandhoo on new, legally reviewed cases that the development team has never seen. **No Gemini API calls were made in preparing this plan.**

## 1. What the current benchmark can and cannot show

| Fact | Consequence |
|---|---|
| `benchmark/bns_synthetic_benchmark_50.json` has 50 synthetic cases written during development. | It measures fit to cases the system was built against, not performance on unseen complaints. |
| Its 15 "holdout" cases were inspected in earlier reports (`dataset_splits.json`: "previously_inspected"). | There is **no untouched test set** today. |
| Two categories (missing material facts, paraphrased narrative) had no holdout cases. | Holdout figures do not cover all categories. |
| No case has a qualified legal review; 8 are `provisional_pending_legal_review` with documented label concerns. | Gold labels are themselves uncertain. |
| The latest reported figures (precision 18.70%, recall 56.25%, production candidate recall 65.62%, Recall@10 71.88%, procedural correctness 11/32) are **deterministic fallback** results. | They say nothing about Gemini-backed performance. No recent live Gemini benchmark exists; `evaluation_report_live.json` (5 cases) is stale. Mocked unit tests prove code paths, not performance. |

**Rule:** the existing 50 cases are permanently **development data**. They must never be reported as test results in any release decision.

### Current metric definitions are not interchangeable

| Metric (current evaluator) | What it actually measures |
|---|---|
| Prediction precision | Predicted sections in relevant **or** plausible labels ÷ all predictions (lenient). |
| Prediction recall | Relevant labels found ÷ all relevant labels (strict; plausible alternatives not credited). |
| Unsupported section rate | 1 − prediction precision. It is not a separate measure, and "unsupported" means "not in the labels", not "legally unsupported". |
| Production candidate recall | Relevant labels among the at most 8 candidates the service actually retrieves (clause-level retrieval). Upper bound on fallback recall. |
| Recall@10 | Relevant labels in the top 10 of a **different**, single-pass global retrieval. Diagnostic only; not achievable recall for the deployed pipeline. |
| Procedural correctness | Whether the **top-ranked** prediction's (cognizable, bailable) pair equals the label. Ignores the advice text and other candidates. |

These numbers must never be compared with each other, summed or averaged.

## 2. Roles and independence

| Role | Responsibilities | Independence requirement |
|---|---|---|
| Evaluation lead | Owns the protocol, data custody, splits and scoring runs. | Not a Bandhoo developer. |
| Case authors (2 or more) | Write or adapt narratives to the coverage matrix (Section 4). | Have not seen Bandhoo's code, prompts, rules or outputs. |
| Legal reviewers (2 or more) | Independently produce gold labels (Section 6). | Qualified in Indian criminal law; no involvement in Bandhoo development. |
| Adjudicator | Resolves reviewer disagreements. | Senior qualified criminal-law professional, not one of the two reviewers. |
| Bandhoo maintainers | Run development work on development data only. | **No access** to validation-set content or test-set content, labels or per-case results before the release decision. |

Conflicts of interest are declared in writing before work starts.

## 3. Data custody and splits

### 3.1 Splits

| Split | Purpose | Who may see cases | Use |
|---|---|---|---|
| Development | Engineering, debugging, prompt and rule changes | Everyone | Unlimited. The existing 50 cases go here. |
| Validation | Choosing between system versions or settings | Evaluation lead only; maintainers see **aggregate** metrics only | Limited runs, each logged. |
| Final test | One measurement per release candidate | Evaluation lead only | Sealed. Each run is logged with system version, date and mode. After a release decision the set is retired to development, and a new test set is built for the next release. |

### 3.2 Requirements

- **Stratification.** Split by category, language and difficulty so each split covers the full coverage matrix.
- **No leakage.**
  - Near-duplicate narratives (same template, paraphrases, translations of one another) stay in the same split. The evaluation lead checks this with text-similarity screening and manual review.
  - No test narrative may be derived from a development or benchmark case.
- **Freezing.** Gold labels are frozen before any scoring. The labels file is stored with a SHA-256 hash recorded in the evaluation log; any later change to a label creates a new version and is logged.
- **Storage.** Validation and test sets are kept outside the Bandhoo repository, in access-controlled storage. Only aggregate results are committed.

### 3.3 Size

The final test set must be large enough that each headline metric can be reported with a 95% confidence interval narrow enough for the release decision. The evaluation lead and project owners set the target width before data collection.

A **proposal only, for discussion**:
- at least 30 cases per major category in the test set;
- at least 15 cases per edge-case category (Section 4.2);
- coverage of all three languages in every category where it is realistic.

## 4. Case sourcing and coverage

### 4.1 Sources (in order of preference)

1. **New narratives** written by case authors from the coverage matrix, in realistic complainant language (including colloquial, incomplete and emotional accounts).
2. **Fact patterns adapted from published Indian court judgments**, paraphrased into first-person complaints. Record the judgment citation privately for the reviewers. Do not copy text verbatim.
3. **Real complaints**, only with documented consent or another lawful basis, after de-identification (Section 5), and only if the project owners and legal reviewers approve.

The following must **not** be used as case or label sources: the existing benchmark cases, `bns_finetune_dataset.json`, `bns_scenarios_dataset.json`, Bandhoo outputs, or text produced by any LLM without full human rewriting and review.

### 4.2 Coverage matrix

| Dimension | Required coverage |
|---|---|
| Offence families | Property (theft, snatching, robbery, dacoity, house-breaking, criminal breach of trust, cheating, misappropriation, mischief), hurt and grievous hurt, criminal intimidation, sexual offences, kidnapping, public-servant offences, and others in common police-station use. Each family includes clear, borderline and contradicted examples. |
| Non-penal narratives | Consumer pricing disputes, workplace grievances, figurative language ("daylight robbery", "stole my idea"), civil disputes (contract, tenancy, property title). |
| Vague complaints | Too little detail to identify any offence; very short or incoherent text. |
| Negation | "No weapon", "nobody was hurt", in English, Hindi and Hinglish; negation of one element with another element present (e.g. no weapon but a threat). |
| Attempted offences | Interrupted thefts, snatching and house-breaking, including cases where attempt-specific provisions exist and cases that may instead fit a different offence (e.g. force used on the person). |
| Multiple offenders | Two, four, five and more offenders (dacoity threshold), common intention, organised activity. |
| Multiple applicable provisions | Compound incidents (trespass plus theft, theft plus hurt), overlapping provisions (303 vs 305 vs 306; 316 sub-sections), and cognizable plus non-cognizable combinations (BNSS 174(4)). |
| Amount parsing | Rupees in lakh, crore, "k", "thousand", Indian and international digit grouping, decimals, Devanagari digits, Hindi number words, several amounts, unrelated amounts (purchase price, rent, loan), amounts near Rs 5,000, and overlapping items (wallet plus cash inside). |
| Restoration and conviction wording | "Returned home", "first time it happened", explicit return of property, return by a third party, and "no prior record" statements. |
| Uncertain facts | Unknown value, unknown entry method, unclear relationship (employee or former employee), unclear timing (night or day), unclear consent. |
| Procedural assertions in the narrative | Complainant demands for Section 173(3) or an FIR, and prompt-injection text. |
| Language | English, Hindi (Devanagari), Hinglish; Marathi if in scope for Mumbai deployment. |

Each case records its coverage tags so that results can be reported by slice.

## 5. De-identification (where real or judgment-derived material is used)

- **Remove or replace:** names, phone numbers, addresses, vehicle numbers, identity numbers, account numbers, exact dates, and any detail identifying a victim, accused or witness.
- **Sexual offences and offences against children:** use special care and follow applicable legal restrictions on disclosure of victim identity.
- **Second-person check:** a second person confirms de-identification before a case enters any split.
- **Raw originals:** never stored in the repository. Follow applicable Indian data-protection law and the project's data-handling approval.

## 6. Gold labels

### 6.1 Label schema (per case)

| Field | Content |
|---|---|
| `relevant_provisions` | BNS sections **and sub-sections** that a competent officer should consider applicable on the stated facts. |
| `acceptable_alternatives` | Provisions that are reasonable depending on unstated facts (credited only in lenient metrics). |
| `contradicted_provisions` | Provisions excluded by the stated facts (e.g. robbery where no force is stated). |
| `abstain_expected` | True for non-penal or insufficient narratives. |
| `missing_material_facts` | Facts needed before classification (value, entrustment, number of offenders, etc.). |
| `procedural_gold` | For each relevant provision: cognizable (yes / no / conditional, with the condition), bailable (same), and the Schedule I row relied on. For the case: route (173(1), 174, conditional, or clarification needed); Section 173(3) applicability (applicable / not applicable / conditional / legally unresolved). |
| `serious_error_triggers` | Outputs that would be serious errors for this case (Section 7.5). |
| `legal_basis` | Sections and any authority relied on, with the official-text version used. |
| `label_confidence` | High / medium / low, with reasons. |
| `review` | Reviewer IDs, dates, agreement result, adjudication notes, status: `draft`, `reviewed`, `adjudicated` or `provisional`. |

### 6.2 Review process

1. Two legal reviewers label each case **independently**, without seeing Bandhoo outputs or each other's labels.
2. The evaluation lead computes agreement:
   - Krippendorff's alpha or Cohen's kappa for categorical fields (abstain, cognizable, bailable, route);
   - Jaccard overlap for provision sets.
3. **Disagreements** go to the adjudicator, who records a decision and rationale.
4. **Unresolved disagreements** (unclear law, conflicting authority, or a question flagged in `reports/legal_review_checklist.md` that is still pending): the case is marked `provisional`. Provisional cases are **excluded from headline metrics** and reported separately with their counts.
5. Labels are frozen and hashed **before** any system output is scored.
6. Questions that depend on open legal issues (e.g. the 303(2) proviso at registration, the 173(3) range reading) are labelled "legally unresolved". They are scored only on whether Bandhoo preserves that uncertainty, not on a chosen answer.

## 7. Metrics

Each metric family is reported separately, with its numerator, denominator and 95% confidence interval (bootstrap over cases).

### 7.1 Offence prediction (final output)

| Metric | Definition |
|---|---|
| Strict precision | Predicted provisions in `relevant_provisions` ÷ all predicted provisions. |
| Lenient precision | Predicted provisions in `relevant_provisions` ∪ `acceptable_alternatives` ÷ all predicted provisions. |
| Recall | `relevant_provisions` predicted ÷ all `relevant_provisions`. |
| Strict F1 / lenient F1 | From the matching precision and recall; always labelled. |
| Unsupported prediction rate | Predicted provisions outside `relevant_provisions` ∪ `acceptable_alternatives` ÷ all predicted provisions (= 1 − lenient precision). Reported with that identity stated. |
| Contradicted-provision rate | Cases in which any `contradicted_provisions` item is predicted ÷ cases with at least one contradicted provision. |
| Top-1 accuracy | Top-ranked prediction in `relevant_provisions`. |
| Exact-set match | Cases whose predicted set equals `relevant_provisions`. |

Report micro (over provisions) and macro (over cases) averages, overall and by slice: category, language, coverage tag, single vs multiple applicable provisions.

### 7.2 Candidate retrieval

| Metric | Definition |
|---|---|
| Production candidate recall | `relevant_provisions` among the candidates the **deployed** pipeline passes to validation or to the model (currently at most 8, clause-level retrieval). |
| Recall@k (diagnostic) | `relevant_provisions` in the top k of a named, documented retrieval call. Always reported with the call and k, and never presented as system recall. |
| Candidate precision | Share of retrieved candidates in `relevant_provisions` ∪ `acceptable_alternatives`. |

### 7.3 Procedural advice

| Metric | Definition |
|---|---|
| Per-offence classification accuracy | For each correctly predicted relevant provision: cognizable and bailable compared with `procedural_gold`. "Unknown" counts as correct only where the gold is conditional or legally unresolved. |
| Route accuracy | The case-level route stated in the advice matches the gold route. |
| Section 173(3) handling | Correct statement of applicability; no assertion of a preliminary enquiry for non-cognizable offences, offences outside the range, or vague complaints; uncertainty preserved where the gold is "legally unresolved". |
| Advice quality (reviewer rubric) | Blinded legal reviewers score each advice text 0–2 on accuracy, appropriate qualification, absence of overclaiming, and clarity for a citizen. Two reviewers per case; disagreements adjudicated. |
| Top-prediction procedural correctness | Retained only as a legacy metric, comparable with earlier reports, and labelled as such. |

### 7.4 Abstention and uncertainty

| Metric | Definition |
|---|---|
| Correct abstention rate | Non-penal or insufficient cases where Bandhoo predicts no provisions and asks for clarification or explains the non-penal nature. |
| False abstention rate | Penal cases where Bandhoo predicts nothing. |
| Missing-fact coverage | Share of gold `missing_material_facts` that Bandhoo asks about. |
| Coverage–accuracy | Accuracy on cases where Bandhoo does not abstain, reported with the share of cases covered. |

### 7.5 Serious errors

Every serious error is listed individually (case ID, output excerpt, reviewer note), not only counted.

| Severity | Examples (the evaluation lead and legal reviewers finalise the list before scoring) |
|---|---|
| S1 critical | Advising a non-cognizable or NCR route when the case is clearly cognizable and serious; advising a Section 173(3) preliminary enquiry for an offence with a 7-year-or-more maximum or a non-cognizable offence; missing a clearly applicable serious offence (e.g. robbery, sexual offence, grievous hurt) while predicting only minor ones; citing a non-existent section or inventing punishment text; stating a disputed legal question as settled. |
| S2 major | Wrong cognizable or bailable value for a predicted relevant offence; predicting a contradicted provision; treating a non-penal grievance as an offence, or the reverse; wrong amount parsing that changes the classification. |
| S3 minor | Irrelevant extra provisions; incomplete missing-fact questions; awkward or unclear advice wording. |

## 8. Inference modes (always reported separately)

Each case result records how it was produced; the current evaluator already writes `inference_status` per case.

| Mode | Counts as | Requirements |
|---|---|---|
| Deterministic fallback | Fallback performance only | Run with the Gemini client disabled. |
| Mocked LLM | **Not performance.** Unit tests only. | Never reported in evaluation tables. |
| Cached LLM responses | Cached performance | Report cache creation date, model ID, prompt version (hash of `SYSTEM_PROMPT`) and the share of cases served from cache. Never merged with genuine live results. |
| Genuine live inference | Live performance | Explicit approval and a quota budget from the project owner before any run. Record model ID, date, prompt hash, temperature and retry settings. Run by an authorised operator with credentials supplied through the environment. No secrets in logs, reports or the repository. |
| Live run that fell back | Separate count | Cases where Gemini failed or was unavailable (`fallback_llm_failed`, `fallback_llm_unavailable`, `fallback_llm_not_invoked`) are counted and reported separately. They are excluded from live metrics. |

No table may mix modes. Every reported figure states its mode in the table heading.

## 9. Reporting template

Each evaluation report contains:

1. **Header:** system version (commit hash), corpus version (hash of `bns_rag_dataset.json`), label version (hash), split, mode, date, operator.
2. **A data provenance statement**, including that the original 50-case benchmark was used during development and is excluded from test results.
3. **Headline table:** every metric in Section 7 with numerator, denominator and confidence interval. Provisional cases are excluded and counted.
4. **Slice tables:** category, language and coverage tag.
5. **Serious-error list** (S1 and S2 in full).
6. **Provisional-case results**, shown separately.
7. **Inter-reviewer agreement statistics.**
8. **Known limitations**, including open legal questions from `reports/legal_review_checklist.md`.
9. **A statement that the results are not legal validation.** Bandhoo remains for internal testing until the project owners and legal reviewers decide otherwise.

## 10. Release criteria

Release criteria are set by the project owners with the legal reviewers **before** the final test set is scored, and are recorded in the evaluation log. A suggestion for discussion, not a decision:

- zero S1 errors on the final test set;
- S2 error rates and procedural metrics within agreed bounds;
- all P1 items in the legal review checklist resolved.

## 11. Steps

1. Approve this plan and the release criteria (project owners, legal reviewers).
2. Complete P1 items in `reports/legal_review_checklist.md`; record which legal questions remain unresolved.
3. Author and de-identify cases; screen for duplicates; tag coverage.
4. Double-label, measure agreement, adjudicate, mark provisional cases, freeze and hash labels.
5. Split into development, validation and test; seal the test set.
6. Extend the evaluator to compute the metrics in Section 7. Strict precision, abstention, per-offence procedural accuracy and serious-error tagging are not implemented yet, and must be built and tested on development data only.
7. Run the fallback evaluation on validation; then, with approval, the live evaluation.
8. Run the final test once per release candidate; publish the report in the Section 9 format.

## 12. Material not available when this plan was written

- No qualified legal review of any label, statutory passage or procedural template.
- No independent case set.
- No recent genuine live Gemini results.
- No authoritative second source for the statutory text (India Code could not be downloaded).
- No check of amendments after 25 December 2023.
- No verified copy of the *Lalita Kumari* judgment.
