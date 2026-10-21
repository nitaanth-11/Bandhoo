// Run with: node --test src/
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import {
  COMPLAINT_STATUS, statusLadder, DRAFT_NOTICE, attachmentLabel, analysisUnavailableState,
  ANALYSIS_UNAVAILABLE_MESSAGE, EXTERNAL_GEOCODING_ENABLED, JURISDICTION_CONFIRMATION_MESSAGE,
  assessJurisdiction, reconcileJurisdiction, isPointInGeometry, structuredSummary,
  reviewStatusLabel, REVIEW_STATUS_UNAVAILABLE_MESSAGE,
} from './trustSafety.js';
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import ReviewStatus from './ReviewStatus.js';

const square = (name, x0, y0, size) => ({
  type: 'Feature',
  properties: { name },
  geometry: { type: 'Polygon', coordinates: [[[x0, y0], [x0 + size, y0], [x0 + size, y0 + size], [x0, y0 + size], [x0, y0]]] },
});
// Two adjacent ~2.2 km squares near Mumbai (synthetic).
const GEO = { type: 'FeatureCollection', features: [square('Alpha', 72.80, 19.00, 0.02), square('Beta', 72.82, 19.00, 0.02)] };

test('a draft does not establish any later status', () => {
  const ladder = statusLadder({ draft: { createdAt: '2026-10-21T10:00:00Z' } });
  assert.deepEqual(ladder.map((s) => s.recorded), [true, false, false, false]);
});

test('each status needs its own evidence; a registered FIR claim without evidence is not recorded', () => {
  const ladder = statusLadder({ fir_registered: { firNumber: 'X' } });
  assert.equal(ladder.find((s) => s.status === COMPLAINT_STATUS.FIR_REGISTERED).recorded, false);
  const receipt = statusLadder({ receipt_confirmed: { confirmedAt: 't', acknowledgementReference: 'a', confirmedBy: 'b' } });
  assert.equal(receipt.find((s) => s.status === 'receipt_confirmed').recorded, true);
  assert.equal(receipt.find((s) => s.status === 'submission_attempted').recorded, false);
  assert.equal(receipt.find((s) => s.status === 'fir_registered').recorded, false);
});

test('draft notice states it is not submitted, not confirmed and not an FIR', () => {
  assert.match(DRAFT_NOTICE, /not been submitted/);
  assert.match(DRAFT_NOTICE, /not a registered FIR/);
});

test('attachment label never claims verification', () => {
  const label = attachmentLabel({ name: 'photo.jpg', size: '12.0 KB' });
  assert.match(label, /not verified/);
  assert.doesNotMatch(label.replace(/not verified/g, ''), /verified/i);
});

test('backend unavailable state carries no legal sections or advice', () => {
  const s = analysisUnavailableState();
  assert.equal(s.unavailable, true);
  assert.equal(s.message, ANALYSIS_UNAVAILABLE_MESSAGE);
  assert.doesNotMatch(JSON.stringify(s), /Section \d|BNS|FIR|Cognizable|Register/i);
});

test('external geocoding is disabled by default', () => {
  assert.equal(EXTERNAL_GEOCODING_ENABLED, false);
});

test('containment: clearly inside one polygon', () => {
  const r = assessJurisdiction({ lat: 19.01, lng: 72.81 }, GEO);
  assert.equal(r.status, 'inside');
  assert.equal(r.polygonName, 'Alpha');
});

test('near a shared boundary needs confirmation', () => {
  const r = assessJurisdiction({ lat: 19.01, lng: 72.8195 }, GEO);
  assert.equal(r.status, 'near_boundary');
  assert.equal(reconcileJurisdiction(r, null).message, JURISDICTION_CONFIRMATION_MESSAGE);
});

test('outside all polygons and missing location need confirmation', () => {
  for (const loc of [{ lat: 18.9, lng: 72.7 }, null]) {
    const r = reconcileJurisdiction(assessJurisdiction(loc, GEO), { station: 'Alpha', method: 'nearest_centroid' });
    assert.equal(r.confirmed, false);
    assert.equal(r.stationName, null);
    assert.equal(r.message, JURISDICTION_CONFIRMATION_MESSAGE);
  }
});

test('backend result cannot override local containment', () => {
  const local = assessJurisdiction({ lat: 19.01, lng: 72.81 }, GEO);
  const conflict = reconcileJurisdiction(local, { station: 'Beta', status: 'inside', method: 'polygon_containment' });
  assert.equal(conflict.confirmed, false);
  assert.equal(conflict.stationName, null);
  const agree = reconcileJurisdiction(local, { station: 'Alpha', status: 'inside', method: 'polygon_containment' });
  assert.equal(agree.stationName, 'Alpha');
});

test('without local boundary data, only a backend polygon-containment result is accepted', () => {
  const local = assessJurisdiction({ lat: 19.01, lng: 72.81 }, null);
  assert.equal(reconcileJurisdiction(local, { station: 'Alpha', method: 'nearest_centroid' }).confirmed, false);
  assert.equal(reconcileJurisdiction(local, { station: 'Alpha', status: 'inside', method: 'polygon_containment' }).stationName, 'Alpha');
});

test('holes are excluded from containment', () => {
  const geom = { type: 'Polygon', coordinates: [
    [[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]],
    [[4, 4], [6, 4], [6, 6], [4, 6], [4, 4]],
  ] };
  assert.equal(isPointInGeometry([1, 1], geom), true);
  assert.equal(isPointInGeometry([5, 5], geom), false);
});

// ── Static checks on App.jsx: removed fabricated claims must not return ──
const app = readFileSync(new URL('./App.jsx', import.meta.url), 'utf8');

test('App.jsx contains no fabricated FIR numbers or registration claims', () => {
  assert.doesNotMatch(app, /Math\.random/);
  assert.doesNotMatch(app, /MUM-\$\{/);
  assert.doesNotMatch(app, /FIR No\.|FIR Number|FIR Registration Number/);
  assert.doesNotMatch(app, /registered electronically/i);
  assert.doesNotMatch(app, /Register FIR|LODGE ELECTRONIC FIR|Official Filing/i);
});

test('App.jsx contains no verified-upload, invented contact, officer or e-sign claims', () => {
  assert.doesNotMatch(app, /document verified/i);
  assert.doesNotMatch(app, /सत्यापित झाले/);
  assert.doesNotMatch(app, /mumbaipolice\.gov\.in|mailto:/);
  assert.doesNotMatch(app, /R\. K\. Patil|Investigation Started|Case registered online/);
  assert.doesNotMatch(app, /E-Signed|Authentically Digitally/i);
  assert.doesNotMatch(app, /'100 \/ 112'|\|\| '100'|Mumbai Headquarters/);
});

test('App.jsx has no hard-coded legal fallback or mandatory identity upload', () => {
  assert.doesNotMatch(app, /Initiate FIR registration immediately|Cognizable offense/i);
  assert.doesNotMatch(app, /Section 303 \(Theft\)/);
  assert.doesNotMatch(app, /Please upload an identity verification document/);
  assert.doesNotMatch(app, /id-proof-upload/);
  assert.doesNotMatch(app, /OpenAI|HuggingFace|LogReg/);
});

test('structured record: supplied evidence stays unverified unless the backend lists a police verification', () => {
  const report = {
    header: { notice: 'n' },
    review: { route: 'human_review_required', reasons: ['r'] },
    supporting_evidence_provided: [{ evidence_id: 'EV-1', evidence_type: 'photo' }, { evidence_id: 'EV-2', evidence_type: 'receipt' }],
    independently_verified: [{ evidence_id: 'EV-2' }],
    missing_information: [{ field: 'when', status: 'open' }, { field: 'witnesses', status: 'explicitly_denied' }],
    contradictions: [{ summary: 'different times' }],
    jurisdiction: { status: 'near_boundary', station: null },
  };
  const s = structuredSummary(report);
  assert.match(s.evidence[0], /not examined, not verified/);
  assert.match(s.evidence[1], /verified by police record/);
  assert.deepEqual(s.missing, ['when: not provided', 'witnesses: stated as not applicable by complainant']);
  assert.equal(s.jurisdiction, JURISDICTION_CONFIRMATION_MESSAGE);
  assert.equal(structuredSummary(null), null);
});

// ── D-1 / D-2: review status comes only from a valid backend decision ──
const READY_REPORT = {
  header: { notice: 'n' },
  review: { route: 'ready_for_police_review', reasons: [], validation_passed: true },
  processing_status: 'complete',
  errors: [],
};
const render = (summary) => renderToStaticMarkup(createElement(ReviewStatus, { summary }));

test('review status: a complete, validated ready decision is the only way to show ready', () => {
  const s = structuredSummary(READY_REPORT);
  assert.equal(s.route, 'ready_for_police_review');
  const html = render(s);
  assert.match(html, /Ready for police review/);
  assert.match(html, /not submitted/);
  assert.match(html, /not yet reviewed by police/);
});

test('review status: human review decision renders as needing human review', () => {
  const html = render(structuredSummary({ ...READY_REPORT, review: { route: 'human_review_required', reasons: ['r'], validation_passed: true } }));
  assert.match(html, /Needs human review/);
  assert.doesNotMatch(html, /Ready for police review/);
});

test('review status: missing, invalid or failed decisions render as unavailable, never ready', () => {
  const cases = [
    { ...READY_REPORT, review: undefined },
    { ...READY_REPORT, review: null },
    { ...READY_REPORT, review: { route: 'unknown' } },
    { ...READY_REPORT, review: { route: 'review_status_unavailable', reasons: [], validation_passed: false } },
    { ...READY_REPORT, review: 'ready_for_police_review' },
    { ...READY_REPORT, review: { route: 'ready_for_police_review', reasons: [], validation_passed: false } },
    { ...READY_REPORT, review: { route: 'ready_for_police_review', reasons: ['x'], validation_passed: true } },
    { ...READY_REPORT, errors: [{ node: 'police_review', error_type: 'RuntimeError' }] },
    { ...READY_REPORT, processing_status: 'incomplete' },
    { ...READY_REPORT, processing_status: undefined },
    { header: {} },
  ];
  for (const report of cases) {
    const s = structuredSummary(report);
    assert.equal(s.route, 'review_status_unavailable', JSON.stringify(report));
    const html = render(s);
    assert.match(html, /Review status unavailable; human review required/);
    assert.doesNotMatch(html, /Ready for police review/);
  }
  assert.match(render(null), /Review status unavailable; human review required/);
  assert.equal(reviewStatusLabel(undefined), REVIEW_STATUS_UNAVAILABLE_MESSAGE);
});

test('App.jsx renders the review status through ReviewStatus, with no default to ready', () => {
  assert.match(app, /<ReviewStatus summary=\{structured\.summary\} \/>/);
  assert.doesNotMatch(app, /'Needs human review' : 'Ready for police review'/);
});

test('structured record: fields the extractor could not read are not called missing', () => {
  const s = structuredSummary({ ...READY_REPORT, missing_information: [{ field: 'where', status: 'not_determined' }] });
  assert.deepEqual(s.missing, ['where: could not be determined automatically (needs a person to read the statement)']);
});

// ── D-8: any backend disagreement needs confirmation ──
test('backend disagreement by status alone needs confirmation', () => {
  const local = assessJurisdiction({ lat: 19.01, lng: 72.81 }, GEO);
  assert.equal(local.status, 'inside');
  for (const status of ['near_boundary', 'outside_all', 'multiple', 'no_location']) {
    const r = reconcileJurisdiction(local, { station: null, status, method: 'polygon_containment' });
    assert.equal(r.confirmed, false, status);
    assert.equal(r.stationName, null);
    assert.equal(r.message, JURISDICTION_CONFIRMATION_MESSAGE);
  }
  assert.equal(reconcileJurisdiction(local, null).stationName, 'Alpha');  // backend unreachable: local result stands
});

// ── Structured draft text ──
test('structured record: the backend draft text is passed through for display, and absent text stays empty', () => {
  const draft = 'COMPLAINT DRAFT – STRUCTURED RECORD (NOT AN FIR)\n7. VERIFICATION CHECKLIST';
  assert.equal(structuredSummary({ ...READY_REPORT, draft_text: draft }).draftText, draft);
  assert.equal(structuredSummary({ ...READY_REPORT }).draftText, '');
  assert.equal(structuredSummary({ ...READY_REPORT, draft_text: { not: 'text' } }).draftText, '');
  assert.match(app, /\{structured\.summary\.draftText\}/);
});
