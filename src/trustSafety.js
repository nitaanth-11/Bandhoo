// Trust-and-safety helpers for the Bandhoo frontend.
// Pure functions only (no React, no network) so they can be tested with `node --test`.

// ── Complaint status ──
// Each status is a separate fact that needs its own evidence. None implies another.
// Bandhoo has no police-submission integration, so the app itself can only ever record DRAFT.
export const COMPLAINT_STATUS = Object.freeze({
  DRAFT: 'draft',
  SUBMISSION_ATTEMPTED: 'submission_attempted',
  RECEIPT_CONFIRMED: 'receipt_confirmed',
  FIR_REGISTERED: 'fir_registered',
});

export const STATUS_LABELS = Object.freeze({
  draft: 'Draft created',
  submission_attempted: 'Submission attempted',
  receipt_confirmed: 'Receipt confirmed by police',
  fir_registered: 'FIR registered by police',
});

// Evidence required before each status may be shown as recorded.
const STATUS_EVIDENCE = Object.freeze({
  draft: ['createdAt'],
  submission_attempted: ['attemptedAt', 'channel'],
  receipt_confirmed: ['confirmedAt', 'acknowledgementReference', 'confirmedBy'],
  fir_registered: ['firNumber', 'registeredAt', 'registeringStation'],
});

// Returns one entry per status: recorded only when that status's own evidence is present.
export function statusLadder(evidence = {}) {
  return Object.values(COMPLAINT_STATUS).map((status) => {
    const record = evidence[status] || null;
    const recorded = Boolean(record) && STATUS_EVIDENCE[status].every((k) => record[k]);
    return { status, label: STATUS_LABELS[status], recorded };
  });
}

export const DRAFT_NOTICE =
  'This is a complaint draft prepared by the complainant. It has not been submitted to the police, ' +
  'its receipt has not been confirmed, and it is not a registered FIR. Bandhoo cannot submit complaints ' +
  'or register FIRs.';

// ── Evidence attachments ──
// Files stay in the browser; only the file name and size are shown. Nothing is checked.
export function attachmentLabel(file) {
  if (!file) return '';
  return `Attached to this draft: ${file.name} (${file.size}). Not sent anywhere and not verified.`;
}

// ── Legal-analysis unavailable state ──
export const ANALYSIS_UNAVAILABLE_MESSAGE =
  'Automatic analysis is unavailable right now. No legal sections have been suggested. ' +
  'You can continue writing the complaint.';

export function analysisUnavailableState() {
  return { unavailable: true, message: ANALYSIS_UNAVAILABLE_MESSAGE };
}

// ── External services ──
// Address search and reverse geocoding send location data to a third party (OpenStreetMap Nominatim).
// Disabled until a data-handling policy is approved.
export const EXTERNAL_GEOCODING_ENABLED = false;

// ── Jurisdiction ──
export const JURISDICTION_CONFIRMATION_MESSAGE = 'Police jurisdiction requires confirmation.';
export const NEAR_BOUNDARY_METERS = 100;

export function pointInRing(point, ring) {
  const [x, y] = point;
  let inside = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const [xi, yi] = ring[i];
    const [xj, yj] = ring[j];
    if ((yi > y) !== (yj > y) && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) inside = !inside;
  }
  return inside;
}

function polygons(geometry) {
  if (!geometry) return [];
  if (geometry.type === 'Polygon') return [geometry.coordinates];
  if (geometry.type === 'MultiPolygon') return geometry.coordinates;
  return [];
}

// Containment honours holes (inner rings).
export function isPointInGeometry(point, geometry) {
  return polygons(geometry).some(
    (rings) => pointInRing(point, rings[0]) && !rings.slice(1).some((hole) => pointInRing(point, hole))
  );
}

// Approximate distance in metres from a [lng, lat] point to the nearest boundary edge.
export function distanceToBoundaryMeters(point, geometry) {
  const [lng0, lat0] = point;
  const kx = 111320 * Math.cos((lat0 * Math.PI) / 180);
  const ky = 110540;
  let best = Infinity;
  for (const rings of polygons(geometry)) {
    for (const ring of rings) {
      for (let i = 0; i + 1 < ring.length; i++) {
        const ax = (ring[i][0] - lng0) * kx, ay = (ring[i][1] - lat0) * ky;
        const bx = (ring[i + 1][0] - lng0) * kx, by = (ring[i + 1][1] - lat0) * ky;
        const dx = bx - ax, dy = by - ay;
        const len2 = dx * dx + dy * dy;
        const t = len2 ? Math.max(0, Math.min(1, -(ax * dx + ay * dy) / len2)) : 0;
        best = Math.min(best, Math.hypot(ax + t * dx, ay + t * dy));
      }
    }
  }
  return best;
}

// Local (browser) polygon-containment assessment.
// status: 'no_location' | 'data_unavailable' | 'outside_all' | 'multiple' | 'near_boundary' | 'inside'
export function assessJurisdiction(location, geojson, nearBoundaryMeters = NEAR_BOUNDARY_METERS) {
  if (!location || !Number.isFinite(location.lat) || !Number.isFinite(location.lng)) {
    return { status: 'no_location', polygonName: null, distanceToBoundaryM: null };
  }
  if (!geojson || !Array.isArray(geojson.features) || geojson.features.length === 0) {
    return { status: 'data_unavailable', polygonName: null, distanceToBoundaryM: null };
  }
  const point = [location.lng, location.lat];
  const hits = geojson.features.filter((f) => isPointInGeometry(point, f.geometry));
  if (hits.length === 0) return { status: 'outside_all', polygonName: null, distanceToBoundaryM: null };
  if (hits.length > 1) return { status: 'multiple', polygonName: null, distanceToBoundaryM: null };
  const name = hits[0].properties && hits[0].properties.name;
  const distance = distanceToBoundaryMeters(point, hits[0].geometry);
  return {
    status: distance < nearBoundaryMeters ? 'near_boundary' : 'inside',
    polygonName: name || null,
    distanceToBoundaryM: Math.round(distance),
  };
}

// Combines the local result with the backend's. The backend can never override a local
// containment result; a disagreement means the jurisdiction needs confirmation.
// Returns { confirmed, stationName, status, message }.
export function reconcileJurisdiction(local, backend) {
  const needsConfirmation = (status) => ({
    confirmed: false,
    stationName: null,
    status,
    message: JURISDICTION_CONFIRMATION_MESSAGE,
  });
  const backendInside =
    backend && backend.method === 'polygon_containment' && backend.status === 'inside' && backend.station;

  if (local && local.status === 'inside') {
    // Any disagreement (a different station, or a non-inside status such as near_boundary) needs confirmation.
    // No backend result (unreachable) leaves the local result as it is.
    const disagrees = backend && ((backend.station && backend.station !== local.polygonName)
      || (backend.status && backend.status !== 'inside'));
    if (disagrees) return needsConfirmation('conflict');
    return { confirmed: true, stationName: local.polygonName, status: 'inside', message: '' };
  }
  if (local && local.status === 'data_unavailable' && backendInside) {
    return { confirmed: true, stationName: backend.station, status: 'inside', message: '' };
  }
  return needsConfirmation(local ? local.status : 'no_location');
}

// ── Review status ──
// Derived only from the backend's decision. "Ready" needs a complete run with a validated, reason-free
// ready decision and no errors; anything missing, invalid or failed is "review status unavailable".
export const REVIEW_STATUS_UNAVAILABLE_MESSAGE = 'Review status unavailable; human review required';
const REVIEW_LABELS = Object.freeze({
  ready_for_police_review: 'Ready for police review (not submitted; not yet reviewed by police)',
  human_review_required: 'Needs human review',
});

function reviewRoute(report) {
  const review = report.review;
  if (!review || typeof review !== 'object') return 'review_status_unavailable';
  if (review.route === 'human_review_required') return 'human_review_required';
  const errors = Array.isArray(report.errors) ? report.errors : [];
  const ready = review.route === 'ready_for_police_review' && review.validation_passed === true
    && Array.isArray(review.reasons) && review.reasons.length === 0
    && errors.length === 0 && report.processing_status === 'complete';
  return ready ? 'ready_for_police_review' : 'review_status_unavailable';
}

export function reviewStatusLabel(summary) {
  return (summary && REVIEW_LABELS[summary.route]) || REVIEW_STATUS_UNAVAILABLE_MESSAGE;
}

// ── Structured record (from /api/v1/complaints/structure) ──
// Turns the backend record into display lines. Evidence is only ever shown as verified when the
// backend lists it under `independently_verified` (which requires a police verification event).
export function structuredSummary(report) {
  if (!report || typeof report !== 'object') return null;
  const verifiedIds = new Set((report.independently_verified || []).map((x) => x.evidence_id || x.item_id));
  const evidence = (report.supporting_evidence_provided || []).map((e) =>
    verifiedIds.has(e.evidence_id)
      ? `${e.evidence_id} (${e.evidence_type}): verified by police record`
      : `${e.evidence_id} (${e.evidence_type}): supplied, not examined, not verified`);
  const missing = (report.missing_information || []).map((m) => {
    const state = m.status === 'explicitly_denied' ? 'stated as not applicable by complainant'
      : m.status === 'unknown_to_complainant' ? 'complainant says they do not know'
        : m.status === 'not_determined' ? 'could not be determined automatically (needs a person to read the statement)'
          : 'not provided';
    return `${m.field.replace(/_/g, ' ')}: ${state}`;
  });
  const j = report.jurisdiction;
  return {
    route: reviewRoute(report),
    reasons: report.review && Array.isArray(report.review.reasons) ? report.review.reasons : [],
    missing,
    questions: report.questions_for_complainant || [],
    contradictions: (report.contradictions || []).map((c) => c.summary),
    evidence,
    jurisdiction: j && j.status === 'inside' && j.station
      ? `${j.station} (map-based estimate; police to confirm)`
      : JURISDICTION_CONFIRMATION_MESSAGE,
    notice: report.header ? report.header.notice : '',
    // Standardised draft rendered by the backend from the same record (complainant's words in quotes).
    draftText: typeof report.draft_text === 'string' ? report.draft_text : '',
  };
}
