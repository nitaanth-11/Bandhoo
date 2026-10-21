import { createElement } from 'react';
import { reviewStatusLabel } from './trustSafety.js';

// Review line of the structured-record panel. Written with createElement (no JSX) so the same component
// can be rendered by `node --test` in src/trustSafety.test.js.
export default function ReviewStatus({ summary }) {
  return createElement('div', null, createElement('b', null, 'Review:'), ' ', reviewStatusLabel(summary));
}
